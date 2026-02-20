import sys
from importlib.metadata import version as pkg_version
from packaging import version
import pandas as pd
import matplotlib.pyplot as plt
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import threading
import time

# Dependency checks
REQUIRED = {
    "python": "3.10",
    "pandas": "2.3.3",
    "customtkinter": "5.2.0",
    "Pillow": "9.0.0",
    "matplotlib": "3.8.0"
}

def check_dependencies():
    issues = []

    if sys.version_info < tuple(map(int, REQUIRED["python"].split("."))):
        issues.append(f"Python {REQUIRED['python']}+")

    if version.parse(pd.__version__) < version.parse(REQUIRED["pandas"]):
        issues.append(f"Pandas {REQUIRED['pandas']}+")

    if version.parse(plt.matplotlib.__version__) < version.parse(REQUIRED["matplotlib"]):
        issues.append(f"Matplotlib {REQUIRED['matplotlib']}+")

    if version.parse(pkg_version("customtkinter")) < version.parse(REQUIRED["customtkinter"]):
        issues.append(f"CustomTkinter {REQUIRED['customtkinter']}+")

    try:
        import PIL
    except:
        issues.append("Pillow (PIL)")

    return issues

deps = check_dependencies()
if deps:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Dependency Error",
        "The application cannot start.\n\nOutdated or missing:\n• " + "\n• ".join(deps)
    )
    sys.exit()

# App setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.title("Pokedex")
app.geometry("1200x700")

# Loading screen
loading_frame = ctk.CTkFrame(app)
loading_frame.pack(fill="both", expand=True)

ctk.CTkLabel(loading_frame, text="Loading Pokedex...", font=("Segoe UI", 24)).pack(pady=50)
progress = ctk.CTkProgressBar(loading_frame, width=400)
progress.pack(pady=20)
progress.set(0.0)
app.update()

# Load CSV
try:
    df = pd.read_csv("pokedata.csv")
except FileNotFoundError:
    messagebox.showerror("Error", "pokedata.csv not found")
    app.destroy()
    raise SystemExit

df.columns = df.columns.str.strip()
df = df.rename(columns={
    "Type 1": "Type1",
    "Type 2": "Type2"
})
df["Type1"] = df["Type1"].str.strip()
df["Type2"] = df["Type2"].fillna("").str.strip()
df["Generation"] = df["Generation"].astype(int)

# Pokemon details
def display_pokemon_detail(pokemon):
    for widget in detail_frame.winfo_children():
        widget.destroy()

    name_label = ctk.CTkLabel(detail_frame, text=pokemon["Name"], font=("Segoe UI", 24))
    name_label.pack(pady=10)

    img_path = f"images/{pokemon['Name']}.png"
    if os.path.exists(img_path):
        img = Image.open(img_path).resize((150,150))
        img = ImageTk.PhotoImage(img)
        img_label = ctk.CTkLabel(detail_frame, image=img)
        img_label.image = img
        img_label.pack(pady=5)
    else:
        img_label = ctk.CTkLabel(detail_frame, text="[No Image]", width=15)
        img_label.pack(pady=5)

    stats_text = "\n".join([
        f"• HP: {pokemon['HP']}",
        f"• Attack: {pokemon['Attack']}",
        f"• Defense: {pokemon['Defense']}",
        f"• Sp. Atk: {pokemon['Sp. Atk']}",
        f"• Sp. Def: {pokemon['Sp. Def']}",
        f"• Speed: {pokemon['Speed']}",
        f"• Legendary: {pokemon['Legendary']}"
    ])
    ctk.CTkLabel(detail_frame, text=stats_text, justify="left").pack(pady=5, anchor="w")

# Main layout (empty)
top_frame = ctk.CTkFrame(app)
main_frame = ctk.CTkFrame(app)

# Populating Pokémon list & filters
def populate_list(filtered_df=None):
    for widget in list_frame.winfo_children():
        widget.destroy()

    data = filtered_df if filtered_df is not None else df

    for g in sorted(data["Generation"].unique()):
        frame = ctk.CTkFrame(list_frame)
        frame.pack(fill="x", pady=5, padx=5)

        def make_toggle(f=frame, gen=g):
            def toggle():
                for w in f.winfo_children()[1:]:
                    w.destroy()
                gen_data = data[data["Generation"] == gen].sort_values("Name")
                for idx, row in gen_data.iterrows():
                    ctk.CTkButton(
                        f, text=row["Name"], width=250,
                        command=lambda r=row: display_pokemon_detail(r)
                    ).pack(pady=1)
            return toggle

        ctk.CTkButton(frame, text=f"Generation {g}", command=make_toggle()).pack(fill="x")

# Shared filter logic
def get_filtered_data():
    filtered = df.copy()

    name_filter = name_entry.get().strip().lower()
    if name_filter:
        filtered = filtered[filtered["Name"].str.lower().str.startswith(name_filter)]

    type1_filter = type1_box.get()
    if type1_filter:
        filtered = filtered[filtered["Type1"] == type1_filter]

    type2_filter = type2_box.get()
    if type2_filter:
        filtered = filtered[filtered["Type2"] == type2_filter]

    gen_filter = gen_box.get()
    if gen_filter:
        filtered = filtered[filtered["Generation"] == int(gen_filter)]

    if legendary_var.get():
        filtered = filtered[filtered["Legendary"] == True]

    return filtered

# Filters
def apply_filters():
    filtered = get_filtered_data()
    populate_list(filtered)

def show_chart():
    filtered = get_filtered_data()

    if filtered.empty:
        messagebox.showinfo("No Data", "No Pokémon match this filter")
        return

    types = pd.concat([filtered["Type1"], filtered["Type2"]])
    types = types[types != ""].value_counts()

    plt.figure(figsize=(9, 5))
    types.plot(kind="bar")
    plt.title("Pokémon Type Distribution")
    plt.xlabel("Type")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()

def show_all():
    name_entry.delete(0, tk.END)
    type1_box.set("")
    type2_box.set("")
    gen_box.set("")
    legendary_var.set(False)
    populate_list()

# Reset UI
def reset_ui():
    # Clear filters
    name_entry.delete(0, tk.END)
    type1_box.set("")
    type2_box.set("")
    gen_box.set("")
    legendary_var.set(False)

    # Clear detail panel
    for widget in detail_frame.winfo_children():
        widget.destroy()

    # Resets list
    populate_list()

# Initialize main app layout
def init_main_layout():
    loading_frame.destroy()

    # Filters + buttons
    top_frame.pack(fill="x", padx=10, pady=10)

    # Filters frame
    filters_frame = ctk.CTkFrame(top_frame)
    filters_frame.grid(row=0, column=0, padx=10, sticky="nw")

    ctk.CTkLabel(filters_frame, text="Search by Name").grid(row=0, column=0, padx=5, pady=2)
    global name_entry
    name_entry = ctk.CTkEntry(filters_frame, width=80)
    name_entry.grid(row=0, column=1, pady=2)

    ctk.CTkLabel(filters_frame, text="Type 1").grid(row=1, column=0, padx=5, pady=2)
    global type1_box
    type1_box = ctk.CTkComboBox(filters_frame, values=sorted(set(df["Type1"])))
    type1_box.grid(row=1, column=1, pady=2)
    type1_box.set("")

    ctk.CTkLabel(filters_frame, text="Type 2").grid(row=2, column=0, padx=5, pady=2)
    global type2_box
    type2_box = ctk.CTkComboBox(filters_frame, values=sorted(set(df["Type2"])))
    type2_box.grid(row=2, column=1, pady=2)
    type2_box.set("")

    ctk.CTkLabel(filters_frame, text="Generation").grid(row=3, column=0, padx=5, pady=2)
    global gen_box
    gen_box = ctk.CTkComboBox(filters_frame, values=[str(g) for g in sorted(df["Generation"].unique())])
    gen_box.grid(row=3, column=1, pady=2)
    gen_box.set("")

    global legendary_var
    legendary_var = tk.BooleanVar()
    ctk.CTkCheckBox(filters_frame, text="Legendary only", variable=legendary_var).grid(row=4, column=0, columnspan=2, pady=5)

    # Buttons
    buttons_frame = ctk.CTkFrame(top_frame)
    buttons_frame.grid(row=0, column=1, padx=20, sticky="nw")

    ctk.CTkButton(buttons_frame, text="Apply Filters", command=apply_filters).pack(pady=5)
    ctk.CTkButton(buttons_frame, text="Show All", command=show_all).pack(pady=5)
    ctk.CTkButton(buttons_frame, text="Show Chart", command=show_chart).pack(pady=5)
    ctk.CTkButton(buttons_frame, text="Reset", command=reset_ui).pack(pady=5)  # Added Reset UI button

    # Pokémon list & detail panels
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    global list_frame, detail_frame
    list_frame = ctk.CTkScrollableFrame(main_frame, width=300)
    list_frame.pack(side="left", fill="y", padx=5, pady=5)

    detail_frame = ctk.CTkFrame(main_frame)
    detail_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    populate_list()

# Simulate loading
def load_app():
    for i in range(101):
        progress.set(i / 100)
        app.update()
        time.sleep(0.01)
    init_main_layout()

threading.Thread(target=load_app).start()
app.mainloop()