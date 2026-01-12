import pandas as pd
import matplotlib as plt
import dearpygui.dearpygui as dpg
from importlib.metadata import version as pkg_version
from packaging import version
import sys

# Dependency check
def check_dependencies():
    outdated = []

    if version.parse(pd.__version__) < version.parse("2.3.3"):
        outdated.append("Pandas")

    if version.parse(plt.__version__) < version.parse("3.10.8"):
        outdated.append("Matplotlib")

    if version.parse(pkg_version("dearpygui")) < version.parse("2.1.1"):
        outdated.append("DearPyGui")

    return outdated

# Load CSV (Pandas)
try:
    pokemon_df = pd.read_csv("pokedata.csv")
except FileNotFoundError:
    print("pokedata.csv not found.")
    sys.exit()


pokemon_df.columns = pokemon_df.columns.str.strip()

pokemon_df = pokemon_df.rename(columns={
    "Type 1": "Type1",
    "Type 2": "Type2"
})

pokemon_df["Type1"] = pokemon_df["Type1"].str.strip()
pokemon_df["Type2"] = pokemon_df["Type2"].fillna("").str.strip()
pokemon_df["Generation"] = pokemon_df["Generation"].astype(int)

pokemon_df["Type"] = (
    pokemon_df["Type1"] +
    pokemon_df["Type2"].apply(lambda x: f"/{x}" if x else "")
)



# Matplotlib logic
def show_type_distribution():
    type_counts = pd.concat([
        pokemon_df["Type1"],
        pokemon_df["Type2"]
    ])
    type_counts = type_counts[type_counts != ""].value_counts()

    plt.figure(figsize=(9, 5))
    type_counts.plot(kind="bar")
    plt.title("Pokémon Type Distribution")
    plt.xlabel("Type")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()


def filter_by_type(sender, app_data):
    filtered = pokemon_df[
        (pokemon_df["Type1"] == app_data) |
        (pokemon_df["Type2"] == app_data)
    ]

    if filtered.empty:
        return

    counts = pd.concat([
        filtered["Type1"],
        filtered["Type2"]
    ])
    counts = counts[counts != ""].value_counts()

    plt.figure(figsize=(7, 4))
    counts.plot(kind="bar")
    plt.title(f"{app_data} Type Pokémon")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()


def filter_by_generation(sender, app_data):
    gen = int(app_data)
    filtered = pokemon_df[pokemon_df["Generation"] == gen]

    if filtered.empty:
        return

    counts = pd.concat([
        filtered["Type1"],
        filtered["Type2"]
    ])
    counts = counts[counts != ""].value_counts()

    plt.figure(figsize=(8, 4))
    counts.plot(kind="bar")
    plt.title(f"Generation {gen} Pokémon by Type")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()

# Loading backend
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
    dpg.set_value("loading_text", f"Loading... {int(loading_progress * 100)}%")

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

    with dpg.window(tag="Main Window", label="Pokedex", show=False):
        dpg.add_text("Pokédex Data Explorer")
        dpg.add_separator()

        dpg.add_button(
            label="Show Overall Type Distribution",
            callback=show_type_distribution
        )

        dpg.add_spacer(height=10)

        dpg.add_combo(
            label="Filter by Type",
            items=sorted(
                set(pokemon_df["Type1"]) | set(pokemon_df["Type2"])
            ),
            callback=filter_by_type,
            width=200
        )

        dpg.add_spacer(height=10)

        dpg.add_combo(
            label="Filter by Generation",
            items=sorted(pokemon_df["Generation"].unique()),
            callback=filter_by_generation,
            width=200
        )

# Run app
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
