import sqlite3
import csv

def calculate_averages(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT c.city, c.latitude, AVG(w.temperature), AVG(w.humidity), AVG(w.air_pressure), AVG(w.uvi) 
                   FROM Cities c 
                   JOIN Weather w on c.id = w.city_id 
                   GROUP BY c.city
                   """)
    rows = cursor.fetchall()
    conn.close()
    
    with open("calculations.csv", 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(["City", "Latitude", "Longitude", "Average Temperature (degrees Fahrenheit), Average Humidity (%), Average Air Pressure (hPa), Average UVI"])
        writer.writerow(rows)

def main():
    database = "cities_weather_dates.db"
    calculate_averages(database)

main()