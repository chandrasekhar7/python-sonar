"""
helium.py

This module provides functionality to read and process data from the Helium Analyzer.
It likely interacts with the Helium Analyzer device through serial communication or
other appropriate interfaces.

Key Functions:
- read_data_from_helium(repository, root): Function to read and process data from the Helium Analyzer.

Dependencies:
- The specific dependencies for this module are not provided, but it may rely on libraries
  for serial communication, data processing, and potentially tkinter for GUI-related functionality.

Usage:
This module is typically imported, and the `read_data_from_helium` function is called
when the application needs to read and process data from the Helium Analyzer.
The function likely takes the Repository object and the root Tkinter window as arguments
for database interaction and potential GUI updates.
"""
import serial.tools.list_ports
from tkinter import messagebox
import serial
import re
import logging

def read_data_from_helium(repository, root):
    logging.info("Enter into read data from helium")

    def read_from_serial(ser):
        try:
            if ser.in_waiting > 0:
                data = ser.readline().decode().strip()
                parse_data(data, root)
            read_from_serial(ser)
        except serial.SerialException as e:
            logging.info(f"Serial Exception Occurred: {str(e)}, while reading Helium Analyzer")
            print(f"Serial Exception Occurred: {str(e)}, while reading Helium Analyzer")
            messagebox.showerror("Error", "Helium Analyzer Port disconnected.", parent=root)

    helium_analyzer_config = repository.get_device_info_by('Helium Analyzer')
    port = helium_analyzer_config.port
    if port:
        try:
            baud_rate = helium_analyzer_config.baudrate
            ser = serial.Serial(port, baud_rate)
            read_from_serial(ser)
        except serial.SerialException as e:
            logging.info(f"Serial Exception Occurred: {str(e)}, while reading Helium Analyzer")
            print(f"Serial Exception Occurred: {str(e)}, while reading Helium Analyzer")
            messagebox.showerror("Error", "Failed to open Helium Analyzer.", parent=root)
    else:
        messagebox.showwarning("Warning", "Please specify a COM Port for Helium Analyzer.", parent=root)

    def parse_data(self, data, root):
        # Define regular expression pattern to match required values
        pattern = r"He\s+(\d+\.\d+)\s*%\s*O2\s+(\d+\.\d+)\s*%\s*Ti\s+(\d+\.\d+)\s*~C\s+(\d+\.\d+)\s*hPa\s+(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})"

        # Match the pattern in the data string
        match = re.search(pattern, data)
        if match:
            # Extract values from the matched groups
            he_value = match.group(1)
            O2_value = match.group(2)
            Ti_value = match.group(3)
            hPa_value = match.group(4)
            timestamp = match.group(5)
            logging.info("Received: {}\n".format(data))
            return he_value
        else:
            messagebox.showwarning("Warning", "Invalid data format.", parent=root)
            return 0