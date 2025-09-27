import sqlite3
from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sirli-kalit'
socketio = SocketIO(app, cors_allowed_origins="*")

def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, message TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def save_message(msg):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (message, timestamp) VALUES (?, ?)", (msg, datetime.now()))
    conn.commit()
    conn.close()

def get_all_messages():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute("SELECT message FROM messages ORDER BY timestamp")
    messages = [row[0] for row in c.fetchall()]
    conn.close()
    return messages

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handleMessage(msg):
    print('Xabar:', msg)
    save_message(msg)
    send(msg, broadcast=True)

@socketio.on('connect')
def on_connect():
    messages = get_all_messages()
    emit('history', messages)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
