import pandas as pd
import matplotlib as plt
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
from importlib.metadata import version as pkg_version
from packaging import version
import sys
import os
from time import sleep

def clear(): # clears terminal instantly
    os.system('cls' if os.name == 'nt' else 'clear')

def clear_terminal(): #clears terminal with a delay
    sleep(2)
    os.system('cls' if os.name == 'nt' else 'clear')

def clear_delay(): #clears terminal with a short delay
    sleep(0.3)
    os.system('cls' if os.name == 'nt' else 'clear')

clear()

#loading screen
print("Initializing...")
clear_delay()
load = 0
print("Loading - ", load, "%")
clear_delay()
while load <= 99:
    load = load + 25
    print("Loading - ", load, "%")
    clear_delay()
print("Loading - Complete!")
clear_terminal()

print("Checking app dependencies versions.")
sleep(2)
print("Pandas Version:", pd.__version__)
print("Matplotlib Version:", plt.__version__)
print("DearPyGui Version:", pkg_version("dearpygui"))
clear_terminal()

outdated = []

if version.parse(pd.__version__) < version.parse("2.3.3"):
    outdated.append("Pandas")

if version.parse(plt.__version__) < version.parse("3.10.8"):
    outdated.append("Matplotlib")

if version.parse(pkg_version("dearpygui")) < version.parse("2.1.1"):
    outdated.append("DearPyGui")

if outdated:
    print(
        "Application cannot continue due to outdated dependencies:",
        ", ".join(outdated),
        "\nPlease update the dependencies."
    )
    sys.exit()

print("All dependencies are up to date. Launching Pokedex...")

# GUI - Possibly add to seperate filelater

dpg.create_context()

# with dpg.window(tag="Primary Window"):
#     dpg.add_text("Hello, world")
#     dpg.add_button(label="Save")
#     dpg.add_input_text(label="string", default_value="Quick brown fox")
#     dpg.add_slider_float(label="float", default_value=0.273, max_value=1)

# dpg.create_viewport(title='Custom Title', width=600, height=200)
# dpg.setup_dearpygui()
# dpg.show_viewport()
# dpg.set_primary_window("Primary Window", True)
# dpg.start_dearpygui()
# dpg.destroy_context()

dpg.create_context()

with dpg.window(label="Pokedex"):
    dpg.add_button(label="Button 1")
    dpg.add_button(label="Button 2")
    with dpg.group():
        dpg.add_button(label="Button 3")
        dpg.add_button(label="Button 4")
        with dpg.group() as group1:
            pass
dpg.add_button(label="Button 6", parent=group1)
dpg.add_button(label="Button 5", parent=group1)

dpg.create_viewport(title='Pokedex.exe', width=600, height=400)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
