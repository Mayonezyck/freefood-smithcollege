from bs4 import BeautifulSoup

# Read the HTML file
with open("test.html", "r") as file:
    content = file.read()

# Parse the HTML content
soup = BeautifulSoup(content, 'html.parser')

# Now you can use BeautifulSoup to extract information
events = soup.find_all('tr', class_='twSimpleTableEventRow0')
for event in events:
    event_links = event.find('a', attrs={'eventid': True})
    event_ids = event_links['eventid']
    time = event.find('span', class_='twStartTime').text
    description = event.find('span', class_='twDescription').text
    location = event.find('span', class_='twLocation').text
    print(f"Time: {time}, Event: {description}, Location: {location}, EventID: {event_ids}")

