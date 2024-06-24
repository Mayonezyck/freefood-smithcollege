# scripts/scraper.py

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

# URL of the Smith College event calendar

#https://25livepub.collegenet.com/s.aspx?hosted=1&calendar=scevents&widget=main&eventid=1104247816&seotitle=EXH-Hopinka-through-21Jul24&view=event&spudformat=xhr 

# Connect to the SQLite database
#conn = sqlite3.connect('../events.db')  # Adjust the path to your event.db if necessary
#cursor = conn.cursor()

# Function to calculate initial probability

keywords = {
    'private': -0.9,
    'exclusive': -0.8,
    'closed': -0.7,
    'members': -0.6,
    'restricted': -0.6,
    'invitation': -0.5,
    'meeting': -0.5,
    'conference': 0.5,
    'webinar': -0.2,
    'training': 0.4,
    'workshop': 0.5,
    'seminar': 0.5,
    'lecture': 0.4,
    'briefing': 0.3,
    'discussion': 0.5,
    'talk': 0.4,
    'presentation': 0.3,
    'panel': 0.6,
    'session': 0.2,
    'event': 0.2,
    'gathering': 0.4,
    'networking': 0.5,
    'open': 0.3,
    'public': 0.4,
    'reception': 0.7,
    'celebration': 0.7,
    'social': 0.8,
    'party': 0.8,
    'gala': 0.7,
    'mixer': 0.7,
    'festival': 0.8,
    'fair': 0.7,
    'picnic': 0.7,
    'cookout': 0.7,
    'barbecue': 0.7,
    'brunch': 0.7,
    'dinner': 0.7,
    'breakfast': 0.7,
    'lunch': 0.7,
    'meal': 0.7,
    'feast': 0.8,
    'buffet': 0.8,
    'banquet': 0.8,
    'refreshments': 0.8,
    'snacks': 0.8,
    'drinks': 0.8,
    'beverages': 0.8,
    'pizza': 0.9,
    'ice cream': 0.9,
    'cookies': 0.9,
    'cake': 0.9,
    'dessert': 0.9,
    'free': 1,
    'complimentary': 1,
    'giveaway': 1,
    'tasting': 1
}

meal_times = {
    'breakfast': {'start': 7, 'end': 10, 'adjustment': 0.3},
    'lunch': {'start': 11, 'end': 14, 'adjustment': 0.5},
    'dinner': {'start': 17, 'end': 20, 'adjustment': 0.4}
}

def check_meal_time(date_time):
    import re
    from datetime import datetime
    
    # Extract the time from the date_time string
    time_match = re.search(r'(\d{1,2}:\d{2}(am|pm))', date_time)
    if not time_match:
        return 0  # No time found, no adjustment
    
    time_str = time_match.group(1)
    event_time = datetime.strptime(time_str, '%I:%M%p').hour
    
    for meal, details in meal_times.items():
        if details['start'] <= event_time < details['end']:
            return details['adjustment']
    
    return 0  # No adjustment if not within any meal time

def calculate_possibility(description, details, date_time):
    words = description.lower().split()
    for detail in details:
        detailwords = detail.lower().split()
        for detailword in detailwords:
            words.append(detailword)
    total_score = 0
    count = 0
    print(words)
    for word in words:
        if word in keywords:
            total_score += keywords[word]
            count += 1
    
    # Normalize the score to be between 0 and 1
    if count > 0:
        possibility = total_score / count
    else:
        possibility = 0.5  # Neutral value if no keywords are found, setting it to 0.5 as a midpoint
    
    # Adjust possibility based on event time
    time_adjustment = check_meal_time(date_time)
    possibility += time_adjustment
    
    # Ensure the possibility remains within [0, 1]
    possibility = max(min(possibility, 1), 0)
    
    return possibility
    
def get_initial_possibility_of_food(description, date_time):
    # Connect to the SQLite database
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    
    # Query to find the initial possibility of food for the same description and date/time
    c.execute('''SELECT food_possibility FROM events 
                 WHERE description = ? AND date_time = ?''', 
              (description, date_time))
    
    result = c.fetchone()
    
    # Close the connection
    conn.close()
    
    if result:
        return result[0]
    else:
        return None
    
# Function to parse the information from the calendar
def detailedURL(event):
    event_links = event.find('a', attrs={'eventid': True})
    event_id = event_links['eventid']
    time = event.find('span', class_='twStartTime').text
    description = event.find('span', class_='twDescription').text
    location = event.find('span', class_='twLocation').text if event.find('span', class_='twLocation') else 'N/A'
    event_anchor = event.find('a', href=True, onmouseover=True)
    seotitle = event_anchor['url.seotitle']
    event_url = f'https://25livepub.collegenet.com/s.aspx?hosted=1&calendar=scevents&widget=main&date={date}&&eventid={event_id}&seotitle={seotitle}&view=event&spudformat=xhr'
    #print(f"Time: {time}, Event: {description}, Location: {location}, EventID: {event_id}")
    #print(event_url)
    return event_url
    
def simmer(ingredients):
    detailedResponse = requests.get(detailedURL(ingredients))
    detailedResponse.raise_for_status()
    return BeautifulSoup(detailedResponse.text, 'html.parser')
    
def tasteOfSoup(cooked_soup):
    event_details = {}
    description_tag = cooked_soup.find('div', class_='twEDDescription')
    if description_tag:
        event_details['description'] = description_tag.text.strip()
    date_time_tag = cooked_soup.find('td', class_='twEventDetailData')
    if date_time_tag:
        event_details['date_time'] = date_time_tag.text.strip()
    
    # Extract location
    location_tag = date_time_tag.find_next('td', class_='twEventDetailData')
    if location_tag:
        event_details['location'] = location_tag.text.strip()

    # Extract additional info (like department, type, etc.)
    additional_info_tags = location_tag.find_next_siblings('td', class_='twEventDetailData')
    if additional_info_tags:
        additional_info = [tag.text.strip() for tag in additional_info_tags if tag.text.strip()]
        event_details['additional_info'] = additional_info

    # Extract event description detail
    detail_data_tags = cooked_soup.find_all('td', class_='twEventDetailData')
    detail_data = [tag.text.strip() for tag in detail_data_tags if tag.text.strip()]
    if detail_data:
        event_details['details'] = detail_data
        
    
    return event_details
    
# Function for Database
def create_table():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    
    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT,
                    date_time TEXT,
                    location TEXT,
                    details TEXT,
                    food_possibility REAL
                )''')
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def insert_event(event):

    existing_possibility = get_initial_possibility_of_food(event['description'], event['date_time'])
    
    if existing_possibility is not None:
        event['food_possibility'] = existing_possibility
    else:
        event['food_possibility'] = calculate_possibility(event['description'], event['details'], event['date_time'])
    # Connect to the SQLite database
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    
    # Insert the event into the table
    c.execute('''INSERT INTO events (description, date_time, location, details, food_possibility)
                 VALUES (?, ?, ?, ?, ?)''', 
              (event['description'], event['date_time'], event['location'], ", ".join(event['details']), event['food_possibility']))
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()    

def view_table():
    # Connect to the SQLite database
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    
    # Query all rows in the events table
    c.execute('SELECT * FROM events')
    rows = c.fetchall()
    
    # Print the rows
    for row in rows:
        print(row)
    
    # Close the connection
    conn.close()

def get_events_by_description(description):
    # Connect to the SQLite database
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    
    # Query rows with the same description
    c.execute('SELECT * FROM events WHERE description = ?', (description,))
    rows = c.fetchall()
    
    # Print the rows
    for row in rows:
        print(row)
    
    # Close the connection
    conn.close()

# Extract event details
#-------------------------------------------------------------------------------------------------------------
date = str(20240624)
url = f'https://25livepub.collegenet.com/s.aspx?hosted=1&calendar=scevents&widget=main&date={date}&spudformat=xhr'
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful
soup = BeautifulSoup(response.text, 'html.parser')
events = soup.find_all('tr', class_='twSimpleTableEventRow0')
#--------------------------------------------------------------------------------------------------------------
create_table()
all_bowls = []
for event in events:
    cooked_soup = simmer(event)
    detailedFlavor = tasteOfSoup(cooked_soup)
    all_bowls.append(detailedFlavor)
for bowl in all_bowls:
    insert_event(bowl)
    
view_table()
#Testing
description_to_search = "Exhibition: Nava Grunfeld '87"
print(f"\nEvents with description '{description_to_search}':")
get_events_by_description(description_to_search)
# Commit the changes and close the connection
#conn.commit()
#conn.close()

#print("Scraping completed and data stored in the database.")

