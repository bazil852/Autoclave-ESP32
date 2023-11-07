import serial
import struct
import time

# Define the new structure format in accordance with the new ESP32 sending format
# '<' means little-endian, 'ffIbB' stands for two floats, an unsigned int, a signed char (byte), and an unsigned char
struct_format = '<ffIbBbb'

# Set up the serial connection (the port will be different on Windows)
ser = serial.Serial('/dev/serial0', 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

# Loop to continuously read from the serial port
try:
    while True:
        # Wait for enough bytes to match our structure
        if ser.in_waiting >= struct.calcsize(struct_format):
            # Read data to match the size of our structure
            data = ser.read(struct.calcsize(struct_format))
            
            # Unpack the data into our structure format
            temperature, pressure, timestamp, state, id,x,y = struct.unpack(struct_format, data)
            
            # Print out the received data
            print(f"Temperature: {temperature} C, Pressure: {pressure} hPa, Time: {timestamp} ms, State: {state}, ID: {chr(id)}")
            ser.flush()
        time.sleep(0.01)  # short delay to avoid hammering the CPU

except KeyboardInterrupt:
    print("Program terminated!")

finally:
    ser.close()
