"""
check_serial.py

This module contains functions to check and manage serial ports for connecting to various devices,
such as the Inficon Leak Detector, Helium Analyzer, Mass Flow Controller, and Relay Switch.
It identifies available serial ports, detects connected devices based on vendor IDs, and updates
device information in the database.

Key Functions:
- check_serial_ports(root, repository): Main function to check and manage serial ports and devices.
- stop_gas_flow(port): Function to stop gas flow through the Mass Flow Controller.
- get_serial_devices(): Function to retrieve a list of available serial devices.

Dependencies:
- time
- serial
- serial.tools.list_ports
- tkinter
- tkinter.ttk
- denkovi_relay
- logging

Usage:
This module is typically imported and the `check_serial_ports` function is called during the
application startup or when managing serial device connections.
"""
import time
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
from denkovi_relay import RelaySwitch
import logging

INFICON_LEAK_DETECTOR_VID = 1240
HELIUM_ANALYZER_VID = 42496
SERIAL_PORT_VID = 1027


def check_serial_ports(root, repository):

    def stop_gas_flow(port):
        logging.info("Stop Gas Flow")
        mass_flow_config = repository.get_device_info_by("Mass Flow Controller")
        settingsdict_mass_flow_controller = {
            'baudrate': mass_flow_config.baudrate,
            'bytesize': int(mass_flow_config.bytesize),
            'parity': mass_flow_config.parity,
            'stopbits': int(mass_flow_config.stopbits),
            'xonxoff': False,
            'dsrdtr': False,
            'rtscts': False,
            'timeout': 1,
            'write_timeout': None,
            'inter_byte_timeout': None
        }
        try:
            mass_flow_controller = serial.Serial(port=str(port))
            mass_flow_controller.apply_settings(settingsdict_mass_flow_controller)
            mass_flow_controller.write("*@=B\r".encode())  # Assuming '"*@=B\r"' is the command to stop gas flow
            response = mass_flow_controller.readline().decode().strip()
            if response == "OK":  # Assuming 'OK' is the expected response
                logging.info(f"Mass flow Controller: {port}")

                logging.info("Gas flow stopped successfully")
                print("Gas flow stopped successfully.")
                return True
            else:
                logging.info(f"Failed to stop gas flow. Device Response is: {response}.")
                print(f"Failed to stop gas flow. Device Response is: {response}")
                return False
        except serial.SerialException as e:
            logging.info(f"Serial Exception, Failed to stop gas flow: {str(e)}")
            print(f"Serial Exception, Failed to stop gas flow: {str(e)}")
            return False

    def get_serial_devices():
        print("get serial devices")
        logging.info("=======================Check Serial Devices==========================")
        devices = []
        ports = serial.tools.list_ports.comports()

        # Scan for Relay Switch first
        relay_switch = None
        logging.info("----------------Scan for Relay-----------------")
        for port in ports:
            logging.info(f"Port: {port.device}")
            logging.info(f"Name: {port.name}")
            logging.info(f"Description: {port.description}")
            logging.info(f"Serial Number: {port.serial_number}")
            logging.info(f"Hardware ID: {port.hwid}")
            logging.info(f"Vendor ID: {port.vid}, Data type is: {type(port.vid)}")
            logging.info(f"Location: {port.location}")
            logging.info(f"Manufacturer: {port.manufacturer}")
            logging.info(f"Product: {port.product}")
            logging.info(f"Interface: {port.interface}")
            logging.info("-" * 80)
            if str(port.vid) == SERIAL_PORT_VID:
                relay_switch = RelaySwitch(repository)
                if relay_switch.connect(port.device):
                    relay_switch.config.port = port.device.strip()
                    relay_switch.config.is_available = True
                    logging.info(f"Relay Switch Connected via: {port.device.strip()}")
                    print("Relay Switch Connected via:", port.device.strip())
                    break

        # Turn on devices using Relay Switch
        if relay_switch:
            device_status = relay_switch.turn_on_devices()
            for device, status in device_status.items():
                if status:
                    logging.info(f"{device} turned on successfully")
                    print(f"{device} turned on successfully")
                else:
                    logging.error(f"Failed to turn on {device}")
                    print(f"Failed to turn on {device}")

            # Wait for devices to stabilize after turning on
            time.sleep(10)  # Adjust the delay as needed

        # Scan for remaining devices
        logging.info("--------- Scan for remaining devices ---------")
        for port in ports:
            devices.append({
                "name": port.description,
                "port": port.device,
            })
            logging.info(f"Port: {port.device}")
            logging.info(f"Name: {port.name}")
            logging.info(f"Description: {port.description}")
            logging.info(f"Serial Number: {port.serial_number}")
            logging.info(f"Hardware ID: {port.hwid}")
            logging.info(f"Vendor ID: {port.vid}, Data type is: {type(port.vid)}")
            logging.info(f"Location: {port.location}")
            logging.info(f"Manufacturer: {port.manufacturer}")
            logging.info(f"Product: {port.product}")
            logging.info(f"Interface: {port.interface}")
            logging.info("-" * 80)

            if port.vid == INFICON_LEAK_DETECTOR_VID:
                leak_detector_config = repository.get_device_info_by("Leak Detector")
                leak_detector_config.port = port.device.strip()
                leak_detector_config.is_available = True
                logging.info(f"Inficon Unit Connected via : {port.device.strip()}")
                print("Inficon Unit Connected via : ", port.device.strip())
            elif port.vid == HELIUM_ANALYZER_VID:
                helium_analyzer_config = repository.get_device_info_by("Helium Analyzer")
                helium_analyzer_config.port = port.device.strip()
                helium_analyzer_config.is_available = True
                logging.info(f"Helium Analyzer Connected via : {port.device.strip()}")
                print("Helium Analyzer Connected via : ", port.device.strip())
            elif port.vid == SERIAL_PORT_VID:
                if stop_gas_flow(port.device):
                    mass_flow_config = repository.get_device_info_by("Mass Flow Controller")
                    mass_flow_config.port = port.device.strip()
                    mass_flow_config.is_available = True
                    logging.info(f"Mass Flow Controller Connected via : {port.device.strip()}")
                    print("Mass Flow Controller Connected via : ", port.device.strip())
                else:
                    logging.info(f"Pressure Gauge Connected via : {port.device.strip()}")
                    print("Pressure Gauge Connected via : ", port.device.strip())
        repository.update_device_info()
        logging.info("======================= End Check Serial Devices ==========================")
        return devices

    def refresh_list():
        for row in tree.get_children():
            tree.delete(row)
        devices = get_serial_devices()
        for device in devices:
            tree.insert("", "end", values=(device["name"], device["port"]))

    external_root = tk.Toplevel(root)
    external_root.title("External Devices")
    external_root.geometry("+100+50")

    # Create a Treeview widget
    tree = ttk.Treeview(external_root, columns=("Name", "Port"), show="headings")
    tree.heading("Name", text="Name")
    tree.heading("Port", text="Port")

    # tree.heading("Byte Size", text="Byte Size")
    tree.pack(expand=True, fill="both")

    # Add a refresh button
    refresh_button = ttk.Button(external_root, text="Refresh", command=refresh_list)
    refresh_button.pack()

    # Populate the initial list of devices
    refresh_list()
