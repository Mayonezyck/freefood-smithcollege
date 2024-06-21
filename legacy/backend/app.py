from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            time TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/events', methods=['GET'])
def get_events():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events')
    events = cursor.fetchall()
    conn.close()

    # Predict free food
    free_food_keywords = ["pizza", "ice cream", "refreshments", "snacks", "lunch", "dinner"]
    def predict_free_food(description):
        description = description.lower()
        for keyword in free_food_keywords:
            if keyword in description:
                return True
        return False

    events_list = []
    for event in events:
        event_dict = dict(event)
        event_dict['free_food'] = predict_free_food(event_dict['description'])
        events_list.append(event_dict)

    return jsonify(events_list)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

