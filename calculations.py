import sqlite3
import csv

def calculate_averages(database, output_file):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT c.city, c.latitude, c.longitude, AVG(w.high_temperature), AVG(w.humidity), AVG(w.air_pressure), AVG(w.wind_speed) 
                   FROM Cities c 
                   JOIN Weather w ON c.id = w.city_id 
                   GROUP BY c.city
                   """)
    rows = cursor.fetchall()
    conn.close()
    
    header_row = ["City", "Latitude", "Longitude", "Average High Temperature (degrees Fahrenheit)", "Average Humidity (%)", "Average Air Pressure (hectopascals)", "Average Wind Speed (miles/hour)"]

    with open(output_file, 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(header_row)
        writer.writerows(rows)
    
    print(f"Averages have been calculated and saved to {output_file}")

def main():
    database = "cities_weather_dates.db"

    output_file = "average_calculations.csv"
    
    calculate_averages(database, output_file)

if __name__ == "__main__":
    main()