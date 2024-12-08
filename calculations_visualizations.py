import sqlite3
import matplotlib.pyplot as plt
import numpy as np

def uvi_temperature(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT c.city, AVG(w.temperature), w.uvi 
                   FROM City c 
                   JOIN Weather w on c.id = w.city_id 
                   GROUP BY c.city, AVG(w.temperature)
                   """)

    rows = cursor.fetchall()
    conn.close()
    
    cities = []
    average_temperatures = []
    uvi = []
    
    for row in rows:
        cities.append(row[0])
        average_temperatures.append(row[1])
        uvi.append(row[2])
    
    plt.scatter(average_temperatures, uvi, color="blue", label="UVI")
    
    slope, intercept = np.polyfit(average_temperatures, uvi, 1)
    equation = f"y = {slope:.2f}x + {intercept:.2f}"
    plt.plot(average_temperatures, slope = np.array(average_temperatures) + intercept, color="orange", label=f"Trendline: {equation}")
    
    plt.xlabel('Average Temperature (degrees Fahrenheit)')
    plt.ylabel("UVI")
    plt.title("UVI vs. Average Temperature (degrees Fahrenheit) for Five Days")
    plt.legend()
    plt.show()