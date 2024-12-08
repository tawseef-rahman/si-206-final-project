import sqlite3
import matplotlib.pyplot as plt
import numpy as np

def uvi_temperature(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT c.city, AVG(w.temperature), AVG(w.uvi) 
                   FROM Cities c 
                   JOIN Weather w on c.id = w.city_id 
                   GROUP BY c.city, AVG(w.temperature)
                   """)

    rows = cursor.fetchall()
    conn.close()
    
    average_temperatures = []
    average_uvi = []
    
    for row in rows:
        average_temperatures.append(row[0])
        average_uvi.append(row[1])
    
    plt.scatter(average_temperatures, average_uvi, color="blue", label="Average UVI")
    
    slope, intercept = np.polyfit(average_temperatures, average_uvi, 1)
    equation = f"y = {slope:.2f}x + {intercept:.2f}"
    plt.plot(average_temperatures, slope = np.array(average_temperatures) + intercept, color="orange", label=f"Trendline: {equation}")
    
    plt.xlabel("Average Temperature (degrees Fahrenheit)")
    plt.ylabel("Average UVI")
    plt.title("Average UVI vs. Average Temperature (degrees Fahrenheit) for Five Days")
    plt.legend()
    plt.show()

def humidity_temperature(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT c.city, AVG(w.temperature), AVG(w.humidity) 
                   FROM Cities c 
                   JOIN Weather w on c.id = w.city_id 
                   GROUP BY c.city, AVG(w.temperature)
                   """)
    
    rows = cursor.fetchall()
    conn.close()
    
    average_temperatures = []
    average_humidity = []
    
    for row in rows:
        average_temperatures.append(row[0])
        average_humidity.append(row[2])
    
    plt.scatter(average_temperatures, average_humidity, color="blue", label="Average Humidity")
    
    slope, intercept = np.polyfit(average_temperatures, average_humidity, 1)
    equation = f"y = {slope:.2f}x + {intercept:.2f}"
    plt.plot(average_temperatures, slope = np.array(average_temperatures) + intercept, color="orange", label=f"Trendline: {equation}")
    
    plt.xlabel("Average Temperature (degrees Fahrenheit)")
    plt.ylabel("Average Humidity (%)")
    plt.title("Average Humidity (%) vs Average Temperature (degrees Fahrenheit) for Five Days")
    plt.legend()
    plt.show()

def average_temperatures(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT c.city, AVG(w.temperature) 
                   FROM Cities c 
                   JOIN Weather w on c.id = w.city_id 
                   GROUP BY c.city
                   """)
    
    rows = cursor.fetchall()
    conn.close()
    
    average_temperatures = []
    for row in rows:
        average_temperatures.append(row[1])
    
    bins = [0, 20, 40, 60, 80, 100]
    colors = ["red", "orange", "green", "blue", "purple"]
    
    bin_data = []
    
    for i in range(len(bins) - 1):
        for temperature in average_temperatures:
            if bins[i] <= temperature < bins[i + 1]:
                bin_data.append(temperature)
            plt.hist(bin_data, bins=bins[i:i+2], color=colors[i])
    
    average = np.mean(average_temperatures)
    
    plt.xlabel("Average Temperature (degrees Fahrenheit)")
    plt.ylabel("Frequency")
    plt.title("Average Temperatures", weight="bold")
    plt.axvline(average, color='k', linestyle='--', linewidth=2, label=f"Average: {average:.2f}")
    plt.legend()
    plt.show()

def main():
    database = "cities_weather_dates.db"
    uvi_temperature(database)
    humidity_temperature(database)
    average_temperatures(database)

main()