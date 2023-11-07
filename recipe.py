import json
import serial
import struct

# JSON string
json_string = '''
{
    "150g": {
        "drainOption": "open",
        "steam": "open",
        "Temp": "100",
        "steam1": "close",
        "drainOption2": "closed",
        "air": "open",
        "pressure": "1",
        "air1": "close",
        "steam2": "open",
        "pressure2": "3",
        "Temp1": "121",
        "Time": "30",
        "steam3": "close",
        "Time2": "5",
        "water": "open",
        "Temp2": "100",
        "drainOption3": "open",
        "water1": "open",
        "Temp3": "60",
        "water2": "close"
    }
}
'''

# Function to convert value to byte
def value_to_byte(value):
    if value == "open":
        return 1
    elif value in ["closed", "close"]:
        return 0
    else:
        return int(value)

# Function to extract command number from key
def get_command_number(key):
    key = key.rstrip('0123456789')  # Strip numbers from the end
    command_mapping = {
        "drainOption": 1,
        "steam": 2,
        "Temp": 3,
        "air": 4,
        "pressure": 5,
        "Time": 6,
        "water": 7,
    }
    return command_mapping.get(key, 0)

# Parse the JSON string
data_dict = json.loads(json_string)

# Create the data_send_t list
data_list = []
for key, value in data_dict.items():
    command_number = get_command_number(key)
    if command_number != 0:  # Ignore keys without a command number
        data_list.append((command_number, value_to_byte(value)))

# Open serial port
ser = serial.Serial('/dev/serial0', 9600, timeout=1)

# Send each command-value pair over serial
for command, value in data_list:
    # Create a byte array
    data_bytes = struct.pack('BB', command, value)
    # Write to the serial port
    ser.write(data_bytes)

# Close serial port
ser.close()
