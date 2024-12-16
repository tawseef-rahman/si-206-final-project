import sqlite3
import matplotlib.pyplot as plt
import numpy as np

def average_humidity_average_high_temperature_operation(database, output_file):
    plt.figure()

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT c.city, AVG(w.high_temperature), AVG(w.humidity) 
                   FROM Cities c 
                   JOIN Weather w ON c.id = w.city_id 
                   GROUP BY c.city
                   """)
    rows = cursor.fetchall()
    conn.close()
    
    average_high_temperatures = []
    average_humidities = []
    
    for row in rows:
        average_high_temperatures.append(row[1])
        average_humidities.append(row[2])
    
    average_high_temperatures = np.array(average_high_temperatures, dtype=np.float64)
    average_humidities = np.array(average_humidities, dtype=np.float64)
    
    plt.scatter(average_high_temperatures, average_humidities, color="blue", label="(Average High Temperature, Average Humidity)")
    
    slope, intercept = np.polyfit(average_high_temperatures, average_humidities, 1)
    equation = f"y = {slope:.2f}x + {intercept:.2f}"
    plt.plot(average_high_temperatures, slope * average_high_temperatures + intercept, color="orange", label=f"Trendline: {equation}")
    
    x_label = "Average High Temperature (degrees Fahrenheit)"
    y_label = "Average Humidity (%)"
    title = "Average Humidity vs. Average High Temperature (12/16/24-12/20/24)"
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend(loc='lower left', prop={'size': 7})

    plt.savefig(output_file, format='png', dpi=300)
    print(f"Scatter Plot: {title} saved to {output_file}")

def average_air_pressure_average_wind_speed_operation(database, output_file):
    plt.figure()

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT c.city, AVG(w.wind_speed), AVG(w.air_pressure) 
                   FROM Cities c 
                   JOIN Weather w ON c.id = w.city_id 
                   GROUP BY c.city
                   """)
    rows = cursor.fetchall()
    conn.close()
    
    average_wind_speeds = []
    average_air_pressures = []
    
    for row in rows:
        average_wind_speeds.append(row[1])
        average_air_pressures.append(row[2])
    
    average_wind_speeds = np.array(average_wind_speeds, dtype=np.float64)
    average_air_pressures = np.array(average_air_pressures, dtype=np.float64)
    
    plt.scatter(average_wind_speeds, average_air_pressures, color="red", label="(Average Wind Speed, Average Air Pressure)")
    
    slope, intercept = np.polyfit(average_wind_speeds, average_air_pressures, 1)
    equation = f"y = {slope:.2f}x + {intercept:.2f}"
    plt.plot(average_wind_speeds, slope * average_wind_speeds + intercept, color="green", label=f"Trendline: {equation}")
    
    x_label = "Average Wind Speed (miles/hour)"
    y_label = "Average Air Pressure (hectopascals)"
    title = "Average Air Pressure vs. Average Wind Speed (12/16/24-12/20/24)"
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend(loc='lower left', prop={'size': 7})
    
    plt.savefig(output_file, format='png', dpi=300)
    print(f"Scatter Plot: {title} saved to {output_file}")

def average_high_temperatures_operation(database, output_file):
    plt.figure()
    
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT c.city, AVG(w.high_temperature) 
                   FROM Cities c 
                   JOIN Weather w on c.id = w.city_id 
                   GROUP BY c.city
                   """)
    rows = cursor.fetchall()
    conn.close()
    
    average_high_temperatures = []
    for row in rows:
        average_high_temperatures.append(row[1])
    
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    colors = ["red", "orange", "green", "blue", "purple", "brown", "pink", "gray", "olive", "cyan", "black"]
    
    bin_data = []
    
    for i in range(len(bins) - 1):
        for high_temperature in average_high_temperatures:
            if bins[i] <= high_temperature < bins[i + 1]:
                bin_data.append(high_temperature)
            plt.hist(bin_data, bins=bins[i:i+2], color=colors[i])
    
    average_of_average_high_temperatures = np.mean(average_high_temperatures)
    
    x_label = "Average High Temperature (degrees Fahrenheit)"
    y_label = "Frequency"
    title = "Average High Temperatures (12/16/24-12/20/24)"
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.axvline(average_of_average_high_temperatures, color='k', linestyle='--', linewidth=2, label=f"Average of the Average High Temperatures: {average_of_average_high_temperatures:.2f} degrees Fahrenheit")
    plt.xticks(bins)
    plt.legend(loc='upper left', prop={'size': 5})
    
    plt.savefig(output_file, format='png', dpi=300)
    print(f"Histogram: {title} saved to {output_file}")

def main():
    database = "cities_weather_dates.db"
    
    average_humidity_average_high_temperature_file = "average_humidity_vs_average_high_temperature.png"
    average_air_pressure_average_wind_speed_file = "average_air_pressure_vs_average_wind_speed.png"
    average_high_temperatures_file = "average_high_temperatures.png"

    average_humidity_average_high_temperature_operation(database, average_humidity_average_high_temperature_file)
    average_air_pressure_average_wind_speed_operation(database, average_air_pressure_average_wind_speed_file)
    average_high_temperatures_operation(database, average_high_temperatures_file)

main()