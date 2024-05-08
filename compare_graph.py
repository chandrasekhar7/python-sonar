"""
compare_graph.py

This module provides functionality to compare and visualize measurements from different leak test sessions.
It creates a graphical user interface (GUI) window using Tkinter, allowing users to select and compare
multiple measurement graphs side by side.

Key Functions:
- compare(leakware_id, mode_of_measurement, root, repository): Main function to create the comparison window.
- comparison_graph(window, selected_index): Function to plot the selected measurement graphs.
- create_checkboxes(list_frame, compare_chart_frame): Function to create checkboxes for selecting measurements.
- on_checkbox_change(window): Function to handle checkbox state changes and update the comparison graph.
- load_data_from_database(repository, leakware_id): Function to load measurement data from the database.

Dependencies:
- tkinter
- matplotlib.animation
- matplotlib.pyplot
- matplotlib.backends.backend_tkagg
- json

Usage:
This module is typically imported and the `compare` function is called when the user requests
to compare measurements from different leak test sessions.
"""
import tkinter as tk
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

### compare method
def compare(leakware_id, mode_of_measurement, root, repository):
    global element_listx
    global element_listy
    global checkboxes

    load_data_from_database(repository, leakware_id)

    checkboxes = []
    selected_index = []

    compare = tk.Toplevel(root)
    compare.title("Compare Measurements")
    if mode_of_measurement == "PEM":
        compare.iconbitmap("favicon.ico")
    compare.configure(background="white")
    compare.geometry("900x600")
    ### measurement list checkbox
    measurement_list_frame = tk.Frame(compare, bg="white")
    measurement_list_frame.place(relx=0.001, rely=0.15, relheight=0.7, relwidth=0.2, anchor="nw")
    ### show Graph
    compare_chart_frame = tk.Frame(compare, bg="white")
    compare_chart_frame.place(relx=0.2, rely=0.15, relheight=0.7, relwidth=0.8, anchor="nw")
    for i in range(len(element_listx)):
        selected_index.append(i)
    comparison_graph(compare_chart_frame, selected_index)
    checkboxes = create_checkboxes(measurement_list_frame, compare_chart_frame)

### Create Compare Graph
def comparison_graph(window, selected_index):
    global element_listx
    global element_listy
    global Checkboxes

    for widget in window.winfo_children():
        widget.destroy()

    fig3 = plt.figure(figsize=(10,7))
    compare_graph = fig3.add_subplot(1,1,1)

    compare_graph.clear()
    compare_graph.grid()
    compare_graph.set_title('Course of the measurements')
    compare_graph.set_yscale("symlog")
    compare_graph.set_xlabel("Time2 [s]")
    compare_graph.set_ylabel("Leakrate [mbarˑl/s]")
    
    i=0
    for element_no_in_listy in element_listy:
        element_no_in_listx = element_listx[i]
        if i in selected_index:
            i+=1
            compare_graph.plot(element_no_in_listx[:-1], element_no_in_listy[:-1], label="specimen "+str(i))
        else:
            i+=1
    fig3.legend()

    canvas = FigureCanvasTkAgg(fig3, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

### Checkbox and onchange 
def create_checkboxes(list_frame, compare_chart_frame):
    global element_listx
    global element_listy
    global checkboxes
    colorF = "#ffffff"
    color1 = "#2049b0"

    if len(element_listx) > 0:
        for i in range(len(element_listx)):
            checkbox_var = tk.BooleanVar()
            checkbox = tk.Checkbutton(
                list_frame,
                text = f"specimen {i+1}",
                variable = checkbox_var,
                font=("arial"),
                anchor="nw",
                bg=colorF,
                fg=color1,
                command=lambda i=i, var=checkbox_var: on_checkbox_change(compare_chart_frame)
            )
            checkbox.pack() # Place the checkbox in the window
            checkbox.select()
            checkboxes.append(checkbox_var)
    return checkboxes

def on_checkbox_change(window):
    global element_listx
    global checkboxes
    selected_index = []

    for i in range(len(element_listx)):
        selected_index.append(i)

    for index, checkbox in enumerate(checkboxes):
        if not checkbox.get():
            selected_index.remove(index)
    comparison_graph(window, selected_index)

def load_data_from_database(repository, leakware_id):
    global element_listx
    global element_listy

    element_listx = []
    element_listy = []
    specimens = repository.get_all_specimens(leakware_id)
    for specimen in specimens:
        element_listx.append(json.loads(specimen.x_value))
        element_listy.append(json.loads(specimen.y_value))