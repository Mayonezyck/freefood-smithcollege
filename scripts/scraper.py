# scripts/scraper.py

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

# URL of the Smith College event calendar
date = str(20240623)
url = f'https://25livepub.collegenet.com/s.aspx?hosted=1&calendar=scevents&widget=main&date={date}&spudformat=xhr'

#https://25livepub.collegenet.com/s.aspx?hosted=1&calendar=scevents&widget=main&eventid=1104247816&seotitle=EXH-Hopinka-through-21Jul24&view=event&spudformat=xhr 
# Fetch the webpage
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# Parse the webpage content
soup = BeautifulSoup(response.text, 'html.parser')

# Connect to the SQLite database
#conn = sqlite3.connect('../events.db')  # Adjust the path to your event.db if necessary
#cursor = conn.cursor()

# Function to calculate initial probability
def calculate_probability(name, time):
    probability = 0.1  # default probability
    if 'pizza' in name.lower():
        probability = 0.9
    elif 'lunch' in time.lower():
        probability = 0.7
    return probability

# Extract event details
events = soup.find_all('tr', class_='twSimpleTableEventRow0')
for event in events:
    #print(event)
    event_links = event.find('a', attrs={'eventid': True})
    event_id = event_links['eventid']
    time = event.find('span', class_='twStartTime').text
    description = event.find('span', class_='twDescription').text
    location = event.find('span', class_='twLocation').text if event.find('span', class_='twLocation') else 'N/A'
    #https://25livepub.collegenet.com/s.aspx?hosted=1&calendar=scevents&widget=main&date=20240622&eventid=1152924094&seotitle=BELL-RINGING-summer-weekly-practice&view=event&spudformat=xhr
    event_url = f'https://25livepub.collegenet.com/s.aspx?hosted=1&calendar=scevents&widget=main&date={date}&&eventid={event_id}'
    print(f"Time: {time}, Event: {description}, Location: {location}, EventID: {event_id}")
    print(event_url)

# Commit the changes and close the connection
#conn.commit()
#conn.close()

#print("Scraping completed and data stored in the database.")

