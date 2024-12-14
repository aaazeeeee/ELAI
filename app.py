from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
import mysql.connector
from mysql.connector import Error
import pyttsx3
import speech_recognition as sr
from functools import wraps
from chatbotv1 import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '',   # Replace with your MySQL password
    'database': 'bookstore'
}

def get_db():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)  # This replaces the dict_factory
        return conn, cursor
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None, None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return send_from_directory('./', 'index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn, cursor = get_db()
        if cursor:
            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s',
                         (email, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['logged_in'] = True
                return redirect(url_for('admin'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        conn, cursor = get_db()
        if cursor:
            cursor.execute('SELECT * FROM books')
            books = cursor.fetchall()
            conn.close()
            return jsonify(books)
    return render_template('admin.html')

@app.route('/admin/add_book', methods=['POST'])
@login_required
def add_book():
    conn, cursor = get_db()
    if cursor:
        cursor.execute('''INSERT INTO books (title, author, genre, description, location, 
                      price, stock, keywords) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                   (request.form['title'], request.form['author'], request.form['genre'],
                    request.form['description'], request.form['location'], 
                    float(request.form['price']), int(request.form['stock']),
                    request.form['keywords']))
        conn.commit()
        conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/edit_book/<int:id>', methods=['POST'])
@login_required
def edit_book(id):
    conn, cursor = get_db()
    if cursor:
        cursor.execute('''UPDATE books 
                      SET title=%s, author=%s, genre=%s, description=%s, 
                          location=%s, price=%s, stock=%s, keywords=%s
                      WHERE id=%s''',
                   (request.form['title'], request.form['author'], 
                    request.form['genre'], request.form['description'],
                    request.form['location'], float(request.form['price']),
                    int(request.form['stock']), request.form['keywords'], id))
        conn.commit()
        conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/delete_book/<int:id>', methods=['POST'])
@login_required
def delete_book(id):
    conn, cursor = get_db()
    if cursor:
        cursor.execute('DELETE FROM books WHERE id=%s', (id,))
        conn.commit()
        conn.close()
    return redirect(url_for('admin'))

def text_to_speech(text):
    global engine
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine = None

# Add speech-to-text functionality
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            return recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            return "No speech detected"
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError as e:
            return f"Error with the service: {e}"

# Add new routes for speech functionality
@app.route("/stt", methods=["GET"])
def stt():
    transcription = speech_to_text()
    return jsonify({"transcription": transcription})

@app.route("/tts", methods=["POST"])
def tts():
    text = request.json.get("response")
    if text:
        text_to_speech(text)
        return jsonify({"message": "Playing response."})
    return jsonify({"error": "No response provided."}), 400

@app.route("/stop_tts", methods=["POST"])
def stop_tts():
    global engine
    if engine:
        engine.stop()
        engine = None
    return jsonify({"message": "Speech stopped"})

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"response": "Please provide a message."}), 400
    
    response = handleQuery(user_message)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
