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
        
        ciites_list = []
        rows = table.find_all("tr")[2:102]
        
        for row in rows:
            columns = row.find_all("td")
            city = columns[0].text.strip()
            if (city[-1] == ']'):
                city = city[0:len(city) - 3]
            ciites_list.append(city)
    else:
        print("Error: Could not retrieve the top 100 cities")
    
    return ciites_list

def find_lattitude_longitude(cities_list, key):
    lattitude_longitude_list = []
    for city in cities_list:
        url = f'https://api.api-ninjas.com/v1/geocoding?city={city}'
        response = requests.get(url, headers={'X-Api-Key': key})
        if response.status_code == 200:
            json_data = response.json()
            if len(json_data) > 0:
                json_data = json_data[0]
                lattitude = json_data["lattitude"]
                longitude = json_data["longitude"]
                lattitude_longitude_tuple = lattitude, longitude
                lattitude_longitude_list.append(lattitude_longitude_tuple)
        else:
            print(f"Could not retrieve lattitude/longitude data for {city}")
    return lattitude_longitude_list

def create_cities_table(cursor, conn, cities_list, lattitude_longitude_list):
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Cities 
                   (id INTEGER PRIMARY KEY, 
                   city TEXT, 
                   lattitude FLOAT, 
                   longitude FLOAT)
                   """)

    counter = 0
    index = 0

    while counter < 25 and index < len(cities_list):
        cursor.execute(f"""
                       SELECT city 
                       FROM Cities 
                       WHERE city = ?
                       """
                       , (cities_list[index]))
        if not cursor.fetchone():
            cursor.execute("""
                           INSERT OR IGNORE INTO Cities (city, lattitude, longitude) 
                           VALUES (?, ?, ?)
                           """
                           , (cities_list[index], lattitude_longitude_list[index][0], lattitude_longitude_list[index][1]))
            counter += 1
            index += 1
        else:
            index += 1

    conn.commit()

def weather_forecast(cursor, conn, key):
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Weather 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   city_id INTEGER, 
                   temperature REAL, 
                   humidity INTEGER, 
                   air_pressure INTEGER, 
                   uvi REAL, 
                   forecast_date_id INTEGER, 
                   FOREIGN KEY (forecast_date_id) REFERENCES Dates(id)
                   )
                   """)
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Dates 
                   (id INTEGER PRIMARY KEY, 
                   forecast_date TEXT UNIQUE)
                   """)
    
    cursor.execute("""
                   SELECT lattitude, longitude 
                   FROM Cities
                   """)
    rows = cursor.fetchall()

    counter = 0
    index = 0
    
    while counter < 5 and index < len(rows):
        lattitude, longitude = rows[index]
        cursor.execute(f"""
                       SELECT id 
                       FROM Cities 
                       WHERE lattitude = {lattitude} and longitude = {longitude}
                       """)
        city_id = cursor.fetchone()[0]
        
        cursor.execute(f"""
                       SELECT city_id 
                       FROM Weather 
                       WHERE city_id = '{city_id}'
                       """)
        results = cursor.fetchall()
        
        if len(results) != 5:
            counter += 1
            index += 1
            query = f"https://api.openweathermap.org/data/3.0/onecall?lat={lattitude}&lon={longitude}&exclude=current,minutely,hourly,alerts&units=imperial&appid={key}"
            response = requests.get(query)
            
            if response.status_code == 200:
                json_data = response.data()
                time.sleep(60 / 60)
                for i in range[5]:
                    day_data = json_data["daily"][i]
                    temperature = day_data["temp"]["day"]
                    humidity = day_data["humidity"]
                    air_pressure = day_data["pressure"]
                    uvi = day_data["uvi"]
                    forecast_date = datetime.datetime.utcfromtimestamp(day_data["dt"]).strftime("%Y-%m-%d")
                    
                    cursor.execute("""
                                   SELECT id 
                                   FROM Dates 
                                   WHERE forecast_date = ?
                                   """, (forecast_date,))
                    check_forecast_date = cursor.fetchone()
                    if check_forecast_date:
                        forecast_date_id = check_forecast_date[0]
                    else:
                        cursor.execute("""
                                       INSERT INTO Dates (forecast_date) 
                                       VALUES (?)
                                       """, (forecast_date,))
                        forecast_date_id = cursor.lastrowid
                    
                    cursor.execute("""
                                   INSERT INTO Weather (city_id, temperature, humidity, air_pressure, uvi, forecast_date_id)
                                   VALUES (?, ?, ?, ?, ?, ?)
                                   """, (city_id, temperature, humidity, air_pressure, uvi, forecast_date_id))
            else:
                print(f"Error for lattitude: {lattitude}, longitude: {longitude}")
        else:
            index += 1
    conn.commit()

GEOCODING_API_KEY = "TwKQDgESethKPcrtL7ILAA==vhSXJAiFlQ5DWgHZ"
OPENWEATHER_API_KEY = "71bca049ec2d03ed3e28ad1c89539085"

def main():
    cursor, conn = set_up_database("cities_weather_dates.db")
    cities_list = get_top_one_hundred_cities("https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population")
    lattitude_longitude_list = find_lattitude_longitude(cities_list, GEOCODING_API_KEY)
    create_cities_table(cursor, conn, cities_list, lattitude_longitude_list)
    weather_forecast(cursor, conn, OPENWEATHER_API_KEY)
    conn.close()

main()