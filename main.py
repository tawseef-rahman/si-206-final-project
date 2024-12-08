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

WEATHER_KEY = 'fc5c995b5bb54956b89191743240612'

def update_weather_data(db_file, api_key):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Fetch city and state information from the database
    cursor.execute("""
    SELECT Cities.id, Cities.city_name, States.state_name
    FROM Cities
    JOIN States ON Cities.state_id = States.id
    """)
    cities = cursor.fetchall()

    # Define base URL with placeholders for dynamic substitution
    base_url = "http://api.weatherapi.com/v1/history.json?key={api_key}&q={city},{state}&dt={date}"

    # Iterate through each city and fetch weather data
    for city_id, city_name, state_name in cities:
        try:
            # Construct the API URL dynamically
            formatted_url = base_url.format(
                api_key=api_key,
                city=city_name.replace(" ", "+"),  # Replace spaces with '+' for URL encoding
                state=state_name.replace(" ", "+"),
                date="2023-09-01"  # Use the specified date
            )

            # Fetch weather data from the API
            response = requests.get(formatted_url)
            response.raise_for_status()  # Raise exception for HTTP errors
            weather_data = response.json()

            # Extract the average high temperature (Fahrenheit)
            avg_high_temp = weather_data['forecast']['forecastday'][0]['day']['maxtemp_f']

            # Insert or update the weather data in the Weather table
            cursor.execute("""
            INSERT OR IGNORE INTO Weather (
                city_id, 
                avg_high_temp_fahrenheit_sep_1_2023
            ) VALUES (?, ?)
            """, (city_id, avg_high_temp))

        except Exception as e:
            print(f"Failed to fetch weather data for {city_name}, {state_name}: {e}")

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

update_weather_data("cities_states_weather.db", WEATHER_KEY)