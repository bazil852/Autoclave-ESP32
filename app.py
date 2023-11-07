from flask import Flask, render_template, request, jsonify
import socket
import json
import threading
import os
import serial
import struct
import time

app = Flask(__name__)
# ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

latest_data = None
data_lock = threading.Lock()
# def read_from_port(ser):
#     while True:
#         reading = ser.readline().decode()
#         if reading:
#             print("Message from ESP32:", reading)



def read_serial_data(serial_port='/dev/serial0', baud_rate=9600):
    global latest_data
    struct_format = '<ffIbBbb'  # Define the new structure format

    # Set up the serial connection
    ser = serial.Serial(serial_port, baud_rate, parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

    while True:
        try:
            # Wait for enough bytes to match our structure
            if ser.in_waiting >= struct.calcsize(struct_format):
                # Read data to match the size of our structure
                data = ser.read(struct.calcsize(struct_format))

                # Unpack the data into our structure format
                with data_lock:  # Acquire the lock before modifying `latest_data`
                    latest_data = struct.unpack(struct_format, data)

                # Optionally, print out the received data
                print(f"Data received: {latest_data}")
                ser.flush()

            time.sleep(0.01)  # short delay to avoid hammering the CPU

        except serial.SerialException as e:
            print(f"Serial exception: {e}")
            break  # Exit the thread if there's an issue with the serial connection
# Define the thread for reading serial data

# Example usage:
# read_serial_data('/dev/serial0', 9600)

# Define the thread for reading serial data
def start_serial_thread():
    thread = threading.Thread(target=read_serial_data)
    thread.daemon = True  # This will allow the thread to be closed when the main program exits
    thread.start()

@app.route('/save_recipe', methods=['POST'])
def save_recipe():
    new_data = request.get_json()
    # Define the file path
    file_path = 'Recipes/recipes.json'
    
    # Check if the file exists
    if os.path.isfile(file_path):
        # Read the existing data
        with open(file_path, 'r') as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                # File is empty or corrupted, start fresh
                data = {}
    else:
        data = {}

    # Update the data with the new recipe
    # Assuming new_data contains a single recipe with its name as the key
    recipe_name = next(iter(new_data))
    if recipe_name in data:
        # Handle the case where the recipe name already exists
        # For example, you might want to increment a counter, or append a timestamp
        # to the recipe name to avoid overwriting the existing one.
        pass
    data.update(new_data)

    # Write the updated data back to the file
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    return 'Recipe saved successfully', 200


@app.route('/')
def dashboard():
    with data_lock:  # Acquire the lock before reading `latest_data`
        data_to_render = latest_data
    if data_to_render is None:
        return 'Waiting for data...', 200  # Or you can use a waiting page if you have one
    # Otherwise, render the dashboard with the latest data
    remote_addr = request.remote_addr
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    if ip_address != remote_addr:
        return render_template('readonly_dashboard.html', data=data_to_render)
    return render_template('dashboard.html', data=data_to_render)


@app.route('/recipes')
def recipes():
    # Define the file path
    file_path = 'Recipes/recipes.json'
    
    # Initialize an empty list for recipes
    recipe_list = []

    # Check if the file exists
    if os.path.isfile(file_path):
        # Read the existing data
        with open(file_path, 'r') as json_file:
            try:
                data = json.load(json_file)
                # Convert the JSON data to the format expected by the template
                for name, details in data.items():
                    recipe_list.append({'name': name, 'details': json.dumps(details, indent=4)})
            except json.JSONDecodeError:
                # If JSON is invalid, pass an empty list to the template
                pass

    return render_template('recipes.html', recipes=recipe_list)

@app.route('/update_recipe', methods=['POST'])
def update_recipe():
    updated_recipe = request.get_json()
    # Code to load your existing JSON, update the recipe, and save it back to the file
    # ...

    return jsonify({"message": "Recipe updated successfully"}), 200


if __name__ == '__main__':
    start_serial_thread()
    app.run(host='0.0.0.0', port=8000, debug=True)
