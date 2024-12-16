import sqlite3
import matplotlib.pyplot as plt
import numpy as np

def average_humidity_average_high_temperature_operation(database, output_file):
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

def main():
    database = "cities_weather_dates.db"
    
    average_humidity_average_high_temperature_file = "average_humidity_vs_average_high_temperature.png"

    average_humidity_average_high_temperature_operation(database, average_humidity_average_high_temperature_file)

main()