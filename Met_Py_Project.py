import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.units import units
import subprocess
import metpy.plots as plot


def create_meteogram():
    subprocess.call(["python", "Meteogram.py"])


def create_four_panel():
    subprocess.call(["python", "Four_Panel_Map.py"])


def create_isentropic_example():
    subprocess.call(["python", "isentropic_example.py"])


def calculate_relative_humidity():
    global result_text  # Declare result_text as a global variable

    try:
        temperature = float(temperature_entry.get())
        dewpoint = float(dewpoint_entry.get())

        # Calculate relative humidity
        relative_humidity = mpcalc.relative_humidity_from_dewpoint(
            temperature * units.degC, dewpoint * units.degC
        )

        # Format the result as a whole number percentage
        result_text.set(f"The relative humidity is {int(relative_humidity.magnitude * 100)}%")

    except ValueError:
        messagebox.showerror("Error", "Please enter valid temperature and dewpoint values.")


def create_skewt():
    def plot_skewt():
        # Load sample data
        col_names = ['pressure', 'height', 'temperature', 'dewpoint', 'direction', 'speed']
        df = pd.read_fwf(get_test_data('may4_sounding.txt', as_file_obj=False),
                         skiprows=5, usecols=[0, 1, 2, 3, 6, 7], names=col_names)
        df = df.dropna(subset=('temperature', 'dewpoint', 'direction', 'speed'), how='all').reset_index(drop=True)

        # Extract data from the DataFrame
        p = df['pressure'].values * units.hPa
        T = df['temperature'].values * units.degC
        Td = df['dewpoint'].values * units.degC
        wind_speed = df['speed'].values * units.knots
        wind_dir = df['direction'].values * units.degrees
        u, v = mpcalc.wind_components(wind_speed, wind_dir)

        # Create the Skew-T plot
        fig = plt.figure(figsize=(9, 9))
        skew = plot.SkewT(fig, rotation=45)

        # Plot data
        skew.plot(p, T, 'r')
        skew.plot(p, Td, 'g')
        skew.plot_barbs(p, u, v)
        skew.ax.set_ylim(1000, 100)
        skew.ax.set_xlim(-40, 60)

        skew.ax.set_xlabel(f'Temperature ({T.units:~P})')
        skew.ax.set_ylabel(f'Pressure ({p.units:~P})')

        lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
        skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')

        prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
        skew.plot(p, prof, 'k', linewidth=2)

        skew.shade_cin(p, T, prof, Td)
        skew.shade_cape(p, T, prof)

        skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)

        skew.plot_dry_adiabats()
        skew.plot_moist_adiabats()
        skew.plot_mixing_lines()

        # Create a FigureCanvasTkAgg instance
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    # Clear the plot frame before creating a new plot
    for widget in plot_frame.winfo_children():
        widget.destroy()

    plot_skewt()


def calculate_vapor_pressure_and_dewpoint():
    global vapor_pressure_result, dewpoint_result  # Declare result labels as global variables

    try:
        mixing_ratio = float(mixing_ratio_entry.get())

        # Calculate vapor pressure
        vapor_pressure = mpcalc.vapor_pressure(1000. * units.mbar, mixing_ratio * units('g/kg'))

        # Create vapor pressure label and result
        vapor_pressure_label = tk.Label(window, text="Vapor Pressure (mb):")
        vapor_pressure_label.pack()
        vapor_pressure_result = tk.Label(window, text=f"{vapor_pressure.to(units.mbar).m:.2f}")
        vapor_pressure_result.pack()

        # Calculate dewpoint
        dewpoint = mpcalc.dewpoint(vapor_pressure)

        # Create dewpoint label and result
        dewpoint_label = tk.Label(window, text="Dewpoint (°C):")
        dewpoint_label.pack()
        dewpoint_result = tk.Label(window, text=f"{dewpoint.m:.2f} °C")
        dewpoint_result.pack()

    except ValueError:
        messagebox.showerror("Error", "Please enter a valid mixing ratio value.")


# Create the main window
window = tk.Tk()
window.title("Brian's WX Page")
window.geometry("700x300")  # Set the window size here

# Create a frame to hold the plot
plot_frame = tk.Frame(window)
plot_frame.pack(side='right', fill='both', expand=True)

# Create a frame to hold the left-side buttons and inputs
left_frame = tk.Frame(window)
left_frame.pack(side='left')

# Create mixing ratio label and entry
mixing_ratio_label = tk.Label(left_frame, text="Mixing Ratio (g/kg):")
mixing_ratio_label.pack()
mixing_ratio_entry = tk.Entry(left_frame)
mixing_ratio_entry.pack()

# Create calculate button for vapor pressure and dewpoint
calculate_vapor_pressure_button = tk.Button(
    left_frame, text="Calculate Vapor Pressure and Dewpoint", command=calculate_vapor_pressure_and_dewpoint
)
calculate_vapor_pressure_button.pack()

# Create temperature label and entry
temperature_label = tk.Label(left_frame, text="Temperature (°C):")
temperature_label.pack()
temperature_entry = tk.Entry(left_frame)
temperature_entry.pack()

# Create dewpoint label and entry
dewpoint_label = tk.Label(left_frame, text="Dewpoint (°C):")
dewpoint_label.pack()
dewpoint_entry = tk.Entry(left_frame)
dewpoint_entry.pack()

# Create result label
result_text = tk.StringVar()
result_label = tk.Label(left_frame, textvariable=result_text)
result_label.pack()

# Create calculate button
calculate_button = tk.Button(left_frame, text="Calculate", command=calculate_relative_humidity)
calculate_button.pack()

# Create a button to create the Skew-T plot
skewt_button = tk.Button(left_frame, text="Create Skew-T Plot", command=create_skewt)
skewt_button.pack()

# Create a button to create the Meteogram
meteogram_button = tk.Button(left_frame, text="Create Meteogram", command=create_meteogram)
meteogram_button.pack()

# Create a button to create the Four Panel Map
four_panel_button = tk.Button(left_frame, text="Create Four Panel Map", command=create_four_panel)
four_panel_button.pack()

# Create a button to run the Isentropic Example
isentropic_button = tk.Button(left_frame, text="Run Isentropic Example", command=create_isentropic_example)
isentropic_button.pack()

# Run the Tkinter event loop
window.mainloop()