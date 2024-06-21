import sqlite3

def add_sample_data():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    sample_data = [
        ("Campus Center", "12:00 PM", "Pizza Party"),
        ("Neilson Library", "1:00 PM", "Guest Lecture"),
        ("Seelye Hall", "2:00 PM", "Ice Cream Social"),
        ("Ford Hall", "3:00 PM", "Club Meeting")
    ]
    cursor.executemany('INSERT INTO events (location, time, description) VALUES (?, ?, ?)', sample_data)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_sample_data()

