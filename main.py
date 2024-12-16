import requests
import sqlite3
import os
import datetime
import time
from bs4 import BeautifulSoup

def set_up_database(database_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + database_name)
    cursor = conn.cursor()
    return cursor, conn

def get_top_one_hundred_cities(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find_all("table", class_ = "wikitable")[1]
        
        cities_list = []
        top_one_hundred_cities = table.find_all("tr")[2:102]
        
        for row in top_one_hundred_cities:
            columns = row.find_all("td")
            city = columns[0].text.strip()
            if (city[-1] == ']'):
                city = city[0:len(city) - 3]
            cities_list.append(city)
    else:
        print("Error: Could not retrieve the top 100 cities")
    
    return cities_list

def find_latitude_longitude(cities_list, key):
    latitude_longitude_list = []
    for city in cities_list:
        url = f'https://api.api-ninjas.com/v1/geocoding?city={city}'
        response = requests.get(url, headers={'X-Api-Key': key})
        if response.status_code == 200:
            json_data = response.json()
            if len(json_data) > 0:
                json_data = json_data[0]
                latitude = json_data["latitude"]
                longitude = json_data["longitude"]
                latitude_longitude_tuple = latitude, longitude
                latitude_longitude_list.append(latitude_longitude_tuple)
        else:
            print(f"Error: Could not retrieve latitude/longitude data for {city}")
    
    return latitude_longitude_list

def cities_latitude_longitude_operation(cursor, conn, cities_list, latitude_longitude_list):
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Cities 
                   (id INTEGER PRIMARY KEY, 
                   city TEXT UNIQUE, 
                   latitude FLOAT, 
                   longitude FLOAT)
                   """)
    
    cursor.execute("""
                   SELECT COUNT(*) 
                   FROM Cities
                   """)
    existing_count = cursor.fetchone()[0]
    
    new_entries = cities_list[existing_count:existing_count + 25]
    for i, city in enumerate(new_entries):
        latitude, longitude = latitude_longitude_list[existing_count + i]
        cursor.execute("""
                       INSERT OR IGNORE INTO Cities (city, latitude, longitude) 
                       VALUES (?, ?, ?)
                       """, (city, latitude, longitude))
    
    conn.commit()

def weather_forecast_operation(cursor, conn, key):
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Weather 
                   (id INTEGER PRIMARY KEY, 
                   city_id INTEGER, 
                   high_temperature REAL, 
                   humidity INTEGER, 
                   air_pressure INTEGER, 
                   wind_speed REAL, 
                   forecast_date_id INTEGER, 
                   FOREIGN KEY (city_id) REFERENCES Cities(id), 
                   FOREIGN KEY (forecast_date_id) REFERENCES Dates(id))
                   """)
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Dates 
                   (id INTEGER PRIMARY KEY, 
                   forecast_date TEXT UNIQUE)
                   """)
    
    cursor.execute("""
                   SELECT id, latitude, longitude 
                   FROM Cities
                   """)
    cities = cursor.fetchall()
    
    for city_id, latitude, longitude in cities:
        query = f"https://api.openweathermap.org/data/2.5/forecast/daily?lat={latitude}&lon={longitude}&cnt=5&appid={key}&units=imperial"
        response = requests.get(query)
        
        if response.status_code == 200:
            weather_data = response.json()
            
            for daily_forecast in weather_data["list"]:
                forecast_date = datetime.datetime.fromtimestamp(daily_forecast["dt"], datetime.timezone.utc).strftime("%Y-%m-%d")
                high_temperature = daily_forecast["temp"]["max"]
                humidity = daily_forecast["humidity"]
                air_pressure = daily_forecast["pressure"]
                wind_speed = daily_forecast["speed"]
                
                cursor.execute("""
                               INSERT OR IGNORE INTO Dates (forecast_date) 
                               VALUES (?)
                               """, (forecast_date,))
                cursor.execute("""
                               SELECT id 
                               FROM Dates 
                               WHERE forecast_date = ?
                               """, (forecast_date,))
                forecast_date_id = cursor.fetchone()[0]
                
                cursor.execute("""
                               SELECT COUNT(*) 
                               FROM Weather 
                               WHERE city_id = ? AND forecast_date_id = ?
                               """, (city_id, forecast_date_id))
                exists = cursor.fetchone()[0]
                
                if not exists:
                    cursor.execute("""
                                   INSERT INTO Weather 
                                   (city_id, high_temperature, humidity, air_pressure, wind_speed, forecast_date_id) 
                                   VALUES (?, ?, ?, ?, ?, ?)
                                   """, (city_id, high_temperature, humidity, air_pressure, wind_speed, forecast_date_id))
        else:
            print(f"Error: Could not retrieve weather data for city with ID {city_id}, latitude {latitude}, and longitude {longitude}")
    
    conn.commit()

GEOCODING_API_KEY = "TwKQDgESethKPcrtL7ILAA==vhSXJAiFlQ5DWgHZ"
OPENWEATHER_API_KEY = "6712b9ccecf3c3cfc8b36b9b8c81cd25"

def main():
    cursor, conn = set_up_database("cities_weather_dates.db")
    cities_list = get_top_one_hundred_cities("https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population")
    latitude_longitude_list = find_latitude_longitude(cities_list, GEOCODING_API_KEY)
    cities_latitude_longitude_operation(cursor, conn, cities_list, latitude_longitude_list)
    weather_forecast_operation(cursor, conn, OPENWEATHER_API_KEY)
    conn.close()

main()