"""
Leakware Main Code

This code represents the main functionality of the Leakware software, which is used for leak testing and data analysis.
It integrates with various devices such as the Helium Leak Detector UL1000Fab, Mass Flow Controller FMA-2619-A Series,
Helium Analyzer by DiveSoft, and GD4200-USB Digital Pressure Transducer.

The code provides a graphical user interface (GUI) using the tkinter library, allowing users to perform leak tests,
view real-time measurements, and generate reports. It also incorporates data storage using an SQLite database to store
test data and related information.

The main features of the Leakware software include:
- Serial communication with the connected devices
- Graphical user interface for monitoring and controlling the leak testing process
- Data logging and visualization
- Database integration for storing and retrieving test data
- Report generation
- Language selection (English, German, Chinese)

The code is structured in a modular way, with separate functions handling different aspects of the leak testing process.
It also includes error handling, user input validation, and configuration management to ensure smooth operation
and data integrity.

Overall, the Leakware software provides a comprehensive solution for leak testing and analysis, streamlining the process
and enabling users to efficiently collect and interpret data.

Dependencies:
- tkinter
- logging
- sqlalchemy
- datetime
- db_model
- main_page
- repository
- strings_en (and other language files)
- check_serial

Usage:
This is the main entry point for the Leakware application. It sets up the necessary components,
creates the main application window, and delegates specific functionalities to other modules.
The application is typically run by executing this script.
"""

# import install_libraries # To install all the dependencies and libraries for Leakware.
import serial  # Module for serial port communication
import serial.tools.list_ports  # Helps list available serial ports
import os  # Operating system interactions (file paths, etc. )
import time
import tkinter as tk
import logging
from sqlalchemy import create_engine, orm
from main_page import main_page, set_stop_flag
from repository import Repository
from datetime import datetime
from db_model import Base

import strings_en as strings
from check_serial import check_serial_ports

# Connect to the database
engine = create_engine("sqlite:///leak_ware_db.db")
Base.metadata.create_all(engine)
session_pool = orm.sessionmaker(engine)
session = session_pool()
repository = Repository(session)

# create log file
logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: in %(filename)s %(message)s"
)


def on_closing():
    # Add code to handle closing here
    print("Window is being closed")
    set_stop_flag()
    # For example, you can destroy the window
    root.destroy()


def change_language(language):
    if language == "English":
        import strings_en as strings
    elif language == "Deutsch":
        import strings_de as strings
    elif language == "Mandarin":
        import strings_zh as strings

    quick_test.config(text=strings.strings["Quick Test"])
    serious_of_measurement.config(text=strings.strings["Series of Measurements"])
    he_c_label.config(text=strings.strings["Helium Concentration"])
    he_mass_flow_label.config(text=strings.strings["Helium Mass Flow"])


def toggle_mode_measurement():
    if mode.winfo_ismapped():
        mode.place_forget()
    else:
        mode.place(relx=0.40, rely=0.32, relheight=0.2, relwidth=0.5, anchor="nw")


root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", on_closing)

check_serial_ports(root, repository)

on_off = 0

leakDetector_available = repository.get_device_info_by("Leak Detector").is_available
massFlowController_available = repository.get_device_info_by("Mass Flow Controller").is_available
tb_clicked = False


def main_application(measurement_mode, measurement_type):
    global leakDetector_available
    global massFlowController_available

    logging.info("User selected the measurement type is: {}".format(measurement_type))
    logging.info("Mode of measurement is: {}".format(measurement_mode))

    # create leakware
    leakware_id = repository.create_leakware(datetime.now(), measurement_mode, measurement_type).leakware_id
    logging.info("Application Started and leakware id created and leakware_id is: {}".format(leakware_id))

    main_root = tk.Toplevel(root)
    main_page(
        tk,
        main_root,
        measurement_mode,
        leakware_id,
        tb_clicked,
        leakDetector_available,
        massFlowController_available,
        repository,
        measurement_type
    )


def display_active_message():
    message_frame.place_forget()


def update_timer():
    global remaining_time
    global timer_label
    if remaining_time <= 0:
        stop_timer()
    else:
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        timer_text = f"{minutes:02}:{seconds:02}"
        timer_label.configure(text=timer_text)
        remaining_time -= 1
        root.after(1000, update_timer)


def stop_timer():
    logging.info("====User started Manually====")
    timer_frame.place_forget()
    serious_of_measurement.config(state="normal", bg=color1)
    quick_test.config(state="normal", bg=color1)
    message_frame.place(relx=0.1, rely=0.49, relheight=0.06, relwidth=0.8)
    root.after(5000, display_active_message)


def get_power_on_time():
    leakware_config = repository.get_device_info_by("Leak Detector")

    if leakDetector_available:
        settingsdict_leakDetector = {'baudrate': leakware_config.baudrate, 'bytesize': int(leakware_config.bytesize),
                                     'parity': leakware_config.parity,
                                     'stopbits': int(leakware_config.stopbits), 'xonxoff': False, 'dsrdtr': False,
                                     'rtscts': False, 'timeout': 1,
                                     'write_timeout': None, 'inter_byte_timeout': None}

        try:
            serialPort_leakDetector = serial.Serial(port=leakware_config.port)
            serialPort_leakDetector.apply_settings(settingsdict_leakDetector)

            serialPort_leakDetector.flushInput()
            serialPort_leakDetector.write("*hour:pow?\r".encode())  # Send command to get the power on time
            time.sleep(0.05)

            time_pwron = int(serialPort_leakDetector.readline().decode())
            time.sleep(0.05)

            serialPort_leakDetector.flushOutput()
            time.sleep(1)

            return time_pwron
        except serial.SerialException as e:
            print(f"Serial Exception occurred: {str(e)}, while getting the power on time")
            logging.info(f"Serial Exception occurred: {str(e)}, while getting the power on time")
    return 0


# color1 = "#c4e4ff"
# color1 = "#c4cfff" # light blue
color2 = "#0533ff"  # full blue
color3 = "#e6efff"  # light color1
color4 = "#2049b0"  # profilblau?
color1 = color4
colorF = "#ffffff"  # font #white
fontsize1 = 10
fontsizeXY = 14
remaining_time = (20 - get_power_on_time()) * 60

root.title("Leakware")
root.configure(background="white")
root.geometry("500x450")
root.geometry("+550+50")

try:
    os.mkdir("./Data/")
    print("Directory /Data created.")
except FileExistsError:
    print("Directory already created.")
except Exception as e:
    print(f"An error occurred while creating ./Data/ : {e}")

# Measurement types
quick_test = tk.Button(
    root,
    text=strings.strings["Quick Test"],
    bg=color3,
    fg=colorF,
    command=lambda: main_application("PROFIL", "Quick Test"),
    state="disabled"
)
quick_test.place(relx=.10, rely=.16, relheight=0.08, relwidth=0.23, anchor="nw")
serious_of_measurement = tk.Button(
    root,
    text=strings.strings["Series of Measurements"],
    bg=color3,
    fg=colorF,
    command=toggle_mode_measurement,
    state="disabled"
)
serious_of_measurement.place(relx=.40, rely=.16, relheight=0.08, relwidth=0.5, anchor="nw")

# mode of measurement
mode = tk.Frame(root, bg="white")

# Mode buttons
pem_mode = tk.Frame(mode,  bg="black", border=1)
pem_mode.place(relx=.0, rely=.01, relheight=0.5, relwidth=0.48, anchor="nw")
pem_image = tk.PhotoImage(file="./Images/PEM_BTN.png")
tk.Button(
    pem_mode,
    image=pem_image,
    bg="white",
    bd=0,
    command=lambda: main_application(
        "PEM",
        "series of Measurement"
    )
).pack(fill="both", expand=True)

profil_mode = tk.Frame(mode, bg="black", bd=1)
profil_mode.place(relx=.52, rely=.01, relheight=0.5, relwidth=0.48, anchor="nw")
profil_image = tk.PhotoImage(file="./Images/PROFIL_BTN.png")
tk.Button(
    profil_mode,
    image=profil_image,
    bd=0,
    bg="white",
    command=lambda: main_application(
        "PROFIL",
        "series of Measurement"
    )
).pack(fill="both", expand=True)

# Vacuum waiting time
timer_frame = tk.Frame(root, bg=color2)
timer_frame.place(relx=0.1, rely=0.3, relheight=0.23, relwidth=0.8)
timer_title = tk.Label(timer_frame, text="Vacuuming in process. Please wait for 20 minutes to start the test."
                                         "\nIf Vacuum is already prepared, please proceed with manual start.",
                       bg=color2, fg=colorF, font=("Arial", 9), justify='left')
timer_title.place(relx=0.04, rely=0, relwidth=0.9, relheight=0.6, anchor="nw")
remaining_title = tk.Label(timer_frame, text="Remaining time - ", bg=color2, fg=colorF, font=("Arial", 10))
remaining_title.place(relx=0.02, rely=0.6, relwidth=0.3)
timer_label = tk.Label(timer_frame, text="", font=("Arial", 12, "bold"), fg=colorF, bg=color2)
timer_label.place(relx=0.3, rely=0.6)
tk.Button(timer_frame, bg="green", fg=colorF, text="Manual Start", font=("Arial", 10, "bold"),
          command=stop_timer).place(relx=0.7, rely=0.6, relwidth=0.26, relheight=0.27)
message_frame = tk.Label(root, bg="green", fg="white", font=("Arial", 11, "bold"),
                         text="The system is ready to start the test!")
update_timer()

# Helium Concentration Analyzer
he_c_label = tk.Label(root, text=strings.strings["Helium Concentration"], font=("arial", 10), fg=colorF, bg=color1)
he_c_label.place(relx=0.10, rely=0.60, relheight=0.15, relwidth=0.3, anchor="nw")
tk.Frame(root,
         bg=colorF,
         bd=1,
         highlightbackground=color1,
         highlightthickness=1
         ).place(
    relx=0.4,
    rely=0.60,
    relheight=0.15,
    relwidth=0.3
)
tk.Label(root, text="%", bg=colorF, font=("Arial", 10)).place(relx=0.71, rely=0.65)

# Mass Flow Controller
he_mass_flow_label = tk.Label(root, text=strings.strings["Helium Mass Flow"], font=("arial", 10), fg=colorF, bg=color1)
he_mass_flow_label.place(relx=0.10, rely=0.79, relheight=0.1, relwidth=0.3, anchor="nw")
tk.Frame(
    root,
    bg=colorF,
    bd=1,
    highlightbackground=color1,
    highlightthickness=1
).place(relx=0.4, rely=0.79, relheight=0.1, relwidth=0.3)
tk.Label(root, text="SCCM", bg=colorF, font=("Arial", 10)).place(relx=0.71, rely=0.81)

# Language
english = tk.Button(
    root,
    text=strings.strings["English"],
    bg=color1,
    fg=colorF,
    command=lambda: change_language("English")
)  # font=("arial", 14, "bold")
english.place(relx=.10, rely=.01, relheight=0.08, relwidth=0.2, anchor="nw")

deustch = tk.Button(
    root,
    text=strings.strings["Deutsch"],
    bg=color1,
    fg=colorF,
    command=lambda: change_language("Deutsch")
)  # font=("arial", 14, "bold")
deustch.place(relx=.40, rely=.01, relheight=0.08, relwidth=0.2, anchor="nw")

mandarin = tk.Button(
    root,
    text=strings.strings["Mandarin"],
    bg=color1,
    fg=colorF,
    command=lambda: change_language("Mandarin")
)  # font=("arial", 14, "bold")
mandarin.place(relx=.70, rely=.01, relheight=0.08, relwidth=0.2, anchor="nw")
time.sleep(5)
repository.close_session()
root.mainloop()
