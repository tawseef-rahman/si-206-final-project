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
    index = cursor.fetchone()[0]
    
    counter = 0
    while counter < 25 and index < len(cities_list):
        cursor.execute("""
                       INSERT OR IGNORE INTO Cities (city, latitude, longitude) 
                       VALUES (?, ?, ?)
                       """,
                       (cities_list[index], latitude_longitude_list[index][0], latitude_longitude_list[index][1]))
        counter += 1
        index += 1
    
    conn.commit()

GEOCODING_API_KEY = "TwKQDgESethKPcrtL7ILAA==vhSXJAiFlQ5DWgHZ"

def main():
    cursor, conn = set_up_database("cities_weather_dates.db")
    cities_list = get_top_one_hundred_cities("https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population")
    latitude_longitude_list = find_latitude_longitude(cities_list, GEOCODING_API_KEY)
    cities_latitude_longitude_operation(cursor, conn, cities_list, latitude_longitude_list)
    conn.close()

main()