import pandas as pd
import matplotlib as plt
import dearpygui.dearpygui as dpg
from importlib.metadata import version as pkg_version
from packaging import version
import sys

print("Pandas Version:", pd.__version__)
print("Matplotlib Version:", plt.__version__)
print("DearPyGui Version:", pkg_version("dearpygui"))

outdated = []

if version.parse(pd.__version__) < version.parse("2.3.4"):
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