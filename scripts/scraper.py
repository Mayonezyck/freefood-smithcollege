# scripts/scraper.py

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

# URL of the Smith College event calendar
url = 'https://25livepub.collegenet.com/s.aspx?hosted=1&calendar=scevents&widget=main&spudformat=xhr'


# Fetch the webpage
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# Parse the webpage content
soup = BeautifulSoup(response.text, 'html.parser')

print(soup)
# Connect to the SQLite database
conn = sqlite3.connect('../events.db')  # Adjust the path to your event.db if necessary
cursor = conn.cursor()

# Function to calculate initial probability
def calculate_probability(name, time):
    probability = 0.1  # default probability
    if 'pizza' in name.lower():
        probability = 0.9
    elif 'lunch' in time.lower():
        probability = 0.7
    return probability

# Extract event details
events = soup.find_all('div', class_='event')
for event in events:
    name = event.find('h3').text.strip()
    time = event.find('time').text.strip()
    location = event.find('span', class_='location').text.strip() if event.find('span', class_='location') else 'Unknown'
    
    # Convert time to a standard format (if necessary)
    try:
        time = datetime.strptime(time, '%b %d, %Y %I:%M %p')
    except ValueError:
        continue  # Skip events with invalid date formats

    # Check if the event already exists in the database
    cursor.execute('SELECT * FROM events WHERE name=? AND time=?', (name, time))
    if cursor.fetchone() is None:
        probability = calculate_probability(name, time.strftime('%H:%M'))
        cursor.execute('INSERT INTO events (name, time, location, probability) VALUES (?, ?, ?, ?)',
                       (name, time, location, probability))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Scraping completed and data stored in the database.")

