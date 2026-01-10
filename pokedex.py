import pandas as pd
import matplotlib as plt
import dearpygui.dearpygui as dpg
from importlib.metadata import version as pkg_version
from packaging import version
import sys

# check dependncies
def check_dependencies():
    outdated = []

    if version.parse(pd.__version__) < version.parse("2.3.3"):
        outdated.append("Pandas")

    if version.parse(plt.__version__) < version.parse("3.10.8"):
        outdated.append("Matplotlib")

    if version.parse(pkg_version("dearpygui")) < version.parse("2.1.1"):
        outdated.append("DearPyGui")

    return outdated

# loading back-end
loading_progress = 0.0
BAR_WIDTH = 400

def center_loading_group():
    if not dpg.does_item_exist("loading_group"):
        return

    vw = dpg.get_viewport_width()
    vh = dpg.get_viewport_height()

    x = (vw - BAR_WIDTH) // 2
    y = vh // 2 - 30

    dpg.set_item_pos("loading_group", (x, y))


def sync_loading_window():
    if not dpg.does_item_exist("Loading Window"):
        return

    vw = dpg.get_viewport_width()
    vh = dpg.get_viewport_height()

    dpg.set_item_pos("Loading Window", (0, 0))
    dpg.set_item_width("Loading Window", vw)
    dpg.set_item_height("Loading Window", vh)

    center_loading_group()


def viewport_resize_callback(sender, app_data):
    sync_loading_window()


def loading_frame_callback():
    global loading_progress

    if not dpg.does_item_exist("loading_bar"):
        return

    loading_progress += 0.002

    if loading_progress >= 1.0:
        dpg.set_value("loading_bar", 1.0)
        dpg.delete_item("Loading Window")
        dpg.configure_item("Main Window", show=True)
        return

    dpg.set_value("loading_bar", loading_progress)
    dpg.set_value(
        "loading_text",
        f"Loading... {int(loading_progress * 100)}%"
    )

    dpg.set_frame_callback(
        dpg.get_frame_count() + 1,
        loading_frame_callback
    )

# GUI setup
dpg.create_context()

outdated = check_dependencies()

if outdated:
    with dpg.window(label="Dependency Error", modal=True, no_resize=True):
        dpg.add_text("Application cannot continue.")
        dpg.add_separator()
        dpg.add_text("The following dependencies are outdated:")

        for dep in outdated:
            dpg.add_text(f"- {dep}")

        dpg.add_spacer(height=10)
        dpg.add_button(label="Exit", callback=lambda: sys.exit())

else:
    # loading front-end
    with dpg.window(
        tag="Loading Window",
        no_title_bar=True,
        no_resize=True,
        no_move=True,
        modal=True
    ):
        with dpg.group(tag="loading_group"):
            dpg.add_text("Initialising Pokedex...", tag="loading_text")
            dpg.add_spacer(height=8)
            dpg.add_progress_bar(
                tag="loading_bar",
                default_value=0.0,
                width=BAR_WIDTH
            )

    # main app (hidden before loading screen)
    with dpg.window(tag="Main Window", label="Pokedex", show=False):
        dpg.add_button(label="Button 1")
        dpg.add_button(label="Button 2")

        with dpg.group():
            dpg.add_button(label="Button 3")
            dpg.add_button(label="Button 4")

            with dpg.group(tag="group1"):
                pass

        dpg.add_button(label="Button 6", parent="group1")
        dpg.add_button(label="Button 5", parent="group1")

# running app
dpg.create_viewport(title="Pokedex.exe", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()

if not outdated:
    sync_loading_window()
    dpg.set_viewport_resize_callback(viewport_resize_callback)
    dpg.set_frame_callback(
        dpg.get_frame_count() + 1,
        loading_frame_callback
    )

dpg.start_dearpygui()
dpg.destroy_context()




