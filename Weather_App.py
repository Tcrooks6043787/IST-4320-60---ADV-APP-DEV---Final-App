import tkinter as tk
from tkinter import messagebox
import sqlite3
import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import quote
import math


sql_connect = sqlite3.connect("weather_history.db")
cur = sql_connect.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS weather_searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    search_type TEXT,
    weather_report TEXT,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

sql_connect.commit()


def get_weather(location=None):
    if location:
        location = quote(location)
        site = f"https://wttr.in/{location}?0"
    else:
        site = "https://wttr.in/?0"

    hdr = {"User-Agent": "Mozilla/5.0"}

    try:
        req = Request(site, headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page, "html.parser")

        text = soup.get_text()
        report_match = re.search(r"Weather report:.*", text, re.DOTALL)

        if report_match:
            return report_match.group(0)[:500]
        else:
            return "Error."

    except:
        return "Error."


def save_weather_search(location, search_type, weather_report):
    query = """
    INSERT INTO weather_searches (location, search_type, weather_report)
    VALUES (?, ?, ?)
    """

    cur.execute(query, (location, search_type, weather_report))
    sql_connect.commit()


def load_weather_history():
    history_listbox.delete(0, tk.END)

    query = """
    SELECT location, search_type, searched_at
    FROM weather_searches
    ORDER BY searched_at DESC
    LIMIT 10
    """

    cur.execute(query)
    records = cur.fetchall()

    if len(records) == 0:
        history_listbox.insert(tk.END, "No searches yet.")
    else:
        for record in records:
            location = record[0]
            search_type = record[1]
            searched_at = record[2]

            history_listbox.insert(
                tk.END,
                f"{searched_at} | {location} | {search_type}"
            )


def clear_weather_history():
    answer = messagebox.askyesno(
        "Clear History",
        "Delete all saved searches?"
    )

    if answer:
        cur.execute("DELETE FROM weather_searches")
        sql_connect.commit()
        history_listbox.delete(0, tk.END)
        history_listbox.insert(tk.END, "History cleared.")


def get_theme_color(weather_text):
    weather_lower = weather_text.lower()

    if "rain" in weather_lower or "shower" in weather_lower:
        return "#2f4f6f"
    elif "snow" in weather_lower:
        return "#d7ecff"
    elif "thunder" in weather_lower or "storm" in weather_lower:
        return "#3b3054"
    elif "fog" in weather_lower:
        return "#6f7f86"
    elif "sunny" in weather_lower or "clear" in weather_lower:
        return "#f4b942"
    elif "cloudy" in weather_lower or "overcast" in weather_lower:
        return "#6c7a89"
    else:
        return "#1f2933"


def draw_weather_icon(canvas, weather_text):
    canvas.delete("all")
    weather_lower = weather_text.lower()

    def draw_cloud(x, y, scale=1.0):
        canvas.create_oval(x, y, x + 35 * scale, y + 25 * scale, fill="gray", outline="gray")
        canvas.create_oval(x + 20 * scale, y - 15 * scale, x + 60 * scale, y + 20 * scale, fill="gray", outline="gray")
        canvas.create_oval(x + 50 * scale, y, x + 90 * scale, y + 30 * scale, fill="gray", outline="gray")
        canvas.create_rectangle(x + 15 * scale, y + 15 * scale, x + 80 * scale, y + 30 * scale, fill="gray", outline="gray")

    def draw_sun(x, y, r=22):
        canvas.create_oval(x - r, y - r, x + r, y + r, fill="yellow", outline="orange", width=2)

        for i in range(8):
            angle = math.radians(i * 45)
            x0 = x + r * math.cos(angle)
            y0 = y + r * math.sin(angle)
            x1 = x + (r + 15) * math.cos(angle)
            y1 = y + (r + 15) * math.sin(angle)

            canvas.create_line(x0, y0, x1, y1, fill="orange", width=2)

    def draw_rain(x, y):
        for dx in range(15, 80, 15):
            canvas.create_line(x + dx, y + 45, x + dx - 5, y + 65, fill="blue", width=3)

    def draw_snow(x, y):
        for dx in range(15, 80, 15):
            canvas.create_oval(x + dx, y + 48, x + dx + 6, y + 54, fill="white", outline="white")

    if "rain" in weather_lower or "shower" in weather_lower:
        draw_cloud(10, 25)
        draw_rain(10, 25)

    elif "snow" in weather_lower:
        draw_cloud(10, 25)
        draw_snow(10, 25)

    elif "thunder" in weather_lower or "storm" in weather_lower:
        draw_cloud(10, 25)
        canvas.create_polygon(
            45, 60,
            60, 60,
            45, 90,
            58, 90,
            38, 120,
            45, 80,
            fill="yellow",
            outline="orange"
        )

    elif "fog" in weather_lower:
        draw_cloud(10, 25)
        canvas.create_line(5, 75, 115, 75, fill="white", width=3)
        canvas.create_line(15, 90, 105, 90, fill="white", width=3)
        canvas.create_line(5, 105, 115, 105, fill="white", width=3)

    elif "sunny" in weather_lower or "clear" in weather_lower:
        draw_sun(60, 60)

    elif "cloudy" in weather_lower or "overcast" in weather_lower:
        draw_cloud(10, 40)

    else:
        draw_sun(75, 45, 18)
        draw_cloud(10, 55)


def update_theme(weather_text):
    theme_color = get_theme_color(weather_text)

    window.config(bg=theme_color)
    main_frame.config(bg=theme_color)
    input_frame.config(bg=theme_color)
    button_frame.config(bg=theme_color)
    history_frame.config(bg=theme_color)

    title_label.config(bg=theme_color)
    description_label.config(bg=theme_color)
    city_label.config(bg=theme_color)
    state_label.config(bg=theme_color)
    history_label.config(bg=theme_color)

    icon_canvas.config(bg=theme_color)

    draw_weather_icon(icon_canvas, weather_text)


def display_weather(weather_text):
    update_theme(weather_text)

    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, weather_text)
    output_box.config(state="disabled")


def clear_fields():
    city_var.set("")
    state_var.set("")

    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, "Enter a city and state, or use location.")
    output_box.config(state="disabled")


def close_app():
    sql_connect.close()
    window.destroy()


def refresh_weather():
    city = city_var.get()
    state = state_var.get()

    if city.strip() == "" or state.strip() == "":
        messagebox.showwarning(
            "Missing Info",
            "Enter both city and state."
        )
    else:
        location = f"{city}, {state}"
        weather = get_weather(location)

        display_weather(weather)

        if "error" not in weather.lower():
            save_weather_search(location, "City and State", weather)
            load_weather_history()


def refresh_weather_by_location():
    answer = messagebox.askyesno(
        "Use Location",
        "Use approximate location?"
    )

    if answer:
        weather = get_weather()
        display_weather(weather)

        if "error" not in weather.lower():
            save_weather_search("Approximate Location", "Auto", weather)
            load_weather_history()
    else:
        output_box.config(state="normal")
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, "Location was not used.")
        output_box.config(state="disabled")


window = tk.Tk()
window.title("Weather App")
window.geometry("900x800")
window.minsize(850, 750)
window.config(bg="#1f2933")

city_var = tk.StringVar()
state_var = tk.StringVar()

main_frame = tk.Frame(window, bg="#1f2933")
main_frame.pack(fill="both", expand=True, padx=30, pady=20)

title_label = tk.Label(
    main_frame,
    text="Weather App",
    font=("Arial", 28, "bold"),
    bg="#1f2933",
    fg="white"
)
title_label.pack(pady=(5, 5))

description_label = tk.Label(
    main_frame,
    text="Enter a city and state. Searches save to SQLite.",
    font=("Arial", 12),
    bg="#1f2933",
    fg="white"
)
description_label.pack(pady=(0, 10))

icon_canvas = tk.Canvas(
    main_frame,
    width=130,
    height=130,
    bg="#1f2933",
    highlightthickness=0
)
icon_canvas.pack(pady=(0, 10))

input_frame = tk.Frame(main_frame, bg="#1f2933")
input_frame.pack(pady=5)

city_label = tk.Label(
    input_frame,
    text="City:",
    font=("Arial", 12),
    bg="#1f2933",
    fg="white",
    width=6,
    anchor="e"
)
city_label.grid(row=0, column=0, padx=6, pady=6)

city_entry = tk.Entry(
    input_frame,
    textvariable=city_var,
    font=("Arial", 12),
    width=15
)
city_entry.grid(row=0, column=1, padx=6, pady=6)

state_label = tk.Label(
    input_frame,
    text="State:",
    font=("Arial", 12),
    bg="#1f2933",
    fg="white",
    width=6,
    anchor="e"
)
state_label.grid(row=1, column=0, padx=6, pady=6)

state_entry = tk.Entry(
    input_frame,
    textvariable=state_var,
    font=("Arial", 12),
    width=15
)
state_entry.grid(row=1, column=1, padx=6, pady=6)

button_frame = tk.Frame(main_frame, bg="#1f2933")
button_frame.pack(pady=15)

button_options = {
    "bg": "#111827",
    "fg": "white",
    "font": ("Arial", 12),
    "width": 24,
    "height": 2
}

refresh_button = tk.Button(
    button_frame,
    text="Get Weather",
    command=refresh_weather,
    **button_options
)
refresh_button.grid(row=0, column=0, padx=8, pady=8)

location_button = tk.Button(
    button_frame,
    text="Use Location",
    command=refresh_weather_by_location,
    **button_options
)
location_button.grid(row=0, column=1, padx=8, pady=8)

clear_button = tk.Button(
    button_frame,
    text="Clear",
    command=clear_fields,
    **button_options
)
clear_button.grid(row=0, column=2, padx=8, pady=8)

history_button = tk.Button(
    button_frame,
    text="Load History",
    command=load_weather_history,
    **button_options
)
history_button.grid(row=1, column=0, padx=8, pady=8)

clear_history_button = tk.Button(
    button_frame,
    text="Clear History",
    command=clear_weather_history,
    **button_options
)
clear_history_button.grid(row=1, column=1, padx=8, pady=8)

exit_button = tk.Button(
    button_frame,
    text="Exit",
    command=close_app,
    **button_options
)
exit_button.grid(row=1, column=2, padx=8, pady=8)

output_box = tk.Text(
    main_frame,
    height=9,
    width=85,
    font=("Courier", 10),
    bg="white",
    fg="black",
    wrap="word",
    padx=10,
    pady=10
)
output_box.pack(pady=(5, 15))

output_box.insert(tk.END, "Enter a city and state, or use location.")
output_box.config(state="disabled")

history_frame = tk.Frame(main_frame, bg="#1f2933")
history_frame.pack(pady=(0, 10))

history_label = tk.Label(
    history_frame,
    text="Search History",
    font=("Arial", 14, "bold"),
    bg="#1f2933",
    fg="white"
)
history_label.pack(pady=(0, 5))

history_listbox = tk.Listbox(
    history_frame,
    width=105,
    height=7,
    font=("Courier", 9)
)
history_listbox.pack()

draw_weather_icon(icon_canvas, "")

window.protocol("WM_DELETE_WINDOW", close_app)
window.mainloop()