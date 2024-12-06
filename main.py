import requests
import sqlite3
from bs4 import BeautifulSoup

# Scrape Wikipedia
url = "https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Extracting the table
table = soup.find_all("table", class_ = "wikitable")[1]

cities = []
rows = table.find_all("tr")[2:102]

for row in rows:
    columns = row.find_all("td")
    city = columns[0].text.strip()
    if (city[-1] == ']'):
        city = city[0:len(city) - 3]
    state = columns[1].text.strip()
    population = int(columns[2].text.strip().replace(",", ""))
    cities.append((city, state, population))

# Database setup
conn = sqlite3.connect("cities_states_weather.db")
cursor = conn.cursor()

cursor.execute("""
               CREATE TABLE IF NOT EXISTS Cities (
                   id INTEGER PRIMARY KEY,
                   city_name TEXT UNIQUE,
                   state_id INTEGER,
                   population INTEGER
               )
               """)

cursor.execute("""
               CREATE TABLE IF NOT EXISTS States (
                   id INTEGER PRIMARY KEY,
                   state_name TEXT UNIQUE
               )
               """)

cursor.execute("""
               CREATE TABLE IF NOT EXISTS Weather (
                   id INTEGER PRIMARY KEY,
                   city_id INTEGER,
                   avg_high_temp_fahrenheit_sep_1_2023,
                   rainfall_inches_sep_1_2023 REAL
               )
               """)

# Insert cities and states into the database
city_insertion_counter = 0
for city, state, population in cities:
    if city_insertion_counter >= 25:
        break
    cursor.execute("""
                    INSERT OR IGNORE INTO States (state_name)
                    VALUES (?)
                    """, (state,))
    cursor.execute("""
                    SELECT id FROM States
                    WHERE state_name = ?
                    """, (state,))
    state_id = cursor.fetchone()[0]
    cursor.execute("""
                    INSERT OR IGNORE INTO Cities (city_name, state_id, population)
                    VALUES (?, ?, ?)
                    """, (city, state_id, population))
    if cursor.rowcount > 0:
        city_insertion_counter += 1

conn.commit()
conn.close()

# WEATHER_KEY = "fc5c995b5bb54956b89191743240612"
# ACCUWEATHER_KEY = "BHpKgEB0PcMlge3GB9vrVTyeGni44wXd"

# def fetch_temperature_data():
#     conn = sqlite3.connect("cities_states_weather.db")
#     cursor = conn.cursor()
    
#     cursor.execute("""
#                    SELECT id, city_name, state_id
#                    FROM Cities
#                    WHERE id NOT IN (SELECT city_name FROM Cities) LIMIT 25
#                    """)
#     cities = cursor.fetchall()
    
#     temperature_insertion_counter = 0
#     for city_name, state_id, population in cities:
#         query = f"{city_name}"
#         weather_response = requests.get(f"http://api.weatherapi.com/v1/history.json?key=WEATHER_KEY&q=query&dt=2023-09-01")
#         avg_high_temperature_fahrenheit_sep_1_2023 = weather_response["current"]["temperature"]
#         cursor.execute("""
#                        INSERT INTO Weather (city_name, avg_high_temperature_fahrenheit_sep_1_2023)
#                        Values (?, ?)
#                        """, (city_name, avg_high_temperature_fahrenheit_sep_1_2023))
#         temperature_insertion_counter += 1
    
#     conn.commit()
#     conn.close()

# def fetch_rainfall_data():
#     conn = sqlite3.connect("cities_states_weather.db")
#     cursor = conn.cursor()
#     cursor.execute("""
#                    SELECT id, city_name, state_id
#                    FROM Cities
#                    WHERE id NOT IN (Select city_name FROM Cities) LIMIT 25
#                    """)
#     cities = cursor.fetchall()
    
#     for city_id, city_name, state in cities:
#         query = f"{city_name}, {state}"
#         rainfall_response = requests.get(f"http://dataservice.accuweather.com/currentconditions/v1/{query}", params={"apikey": ACCUWEATHER_KEY, "metric": "false"}).json()
#         rainfall = rainfall_response[0]["PrecipitationSummary"]["Precipitation"]["Imperial"]["Value"]
#         cursor.execute("""
#                        INSERT INTO Cities (city_id, rainfall)
#                        VALUES (?, ?)"""
#                        , (city_id, rainfall))
#     conn.commit()
#     conn.close()

# fetch_temperature_data()
# fetch_rainfall_data()