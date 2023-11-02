from flask import Flask, render_template, request
import socket
import json
# import serial
import threading
import os

app = Flask(__name__)
# ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)


# def read_from_port(ser):
#     while True:
#         reading = ser.readline().decode()
#         if reading:
#             print("Message from ESP32:", reading)
            


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
    remote_addr = request.remote_addr
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print (ip_address,remote_addr)
    if ip_address != remote_addr:  
        return render_template('readonly_dashboard.html')  # Render a read-only view for other IP addresses
    return render_template('dashboard.html')  # Render the regular interactive view for your system's IP


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
    app.run(host='0.0.0.0', port=8000, debug=True)
