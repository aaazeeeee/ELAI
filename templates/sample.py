from flask import Flask, request, jsonify, render_template
import pyttsx3
import speech_recognition as sr
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, Embedding
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re

app = Flask(__name__)

# Enhanced book data with locations and detailed descriptions
books = [
    {
        "id": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "genre": "Classic",
        "description": "A story of decadence and excess in the Jazz Age.",
        "location": "Section A, Shelf 3",
        "price": 15.99,
        "stock": 5,
        "keywords": ["jazz age", "romance", "american dream", "wealth"]
    },
    {
        "id": 2,
        "title": "1984",
        "author": "George Orwell",
        "genre": "Dystopian",
        "description": "A novel about a totalitarian regime that controls every aspect of life.",
        "location": "Section B, Shelf 1",
        "price": 12.99,
        "stock": 8,
        "keywords": ["totalitarianism", "surveillance", "freedom", "government"]
    },
    {
        "id": 3,
        "title": "Atomic Habits",
        "author": "James Clear",
        "genre": "Self-help",
        "description": "A guide to building good habits and breaking bad ones.",
        "location": "Section C, Shelf 5",
        "price": 16.99,
        "stock": 12,
        "keywords": ["habits", "self-improvement", "productivity", "behavior"]
    },
    {
        "id": 4,
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "genre": "Fantasy",
        "description": "A journey of adventure and treasure through Middle-earth.",
        "location": "Section D, Shelf 2",
        "price": 14.99,
        "stock": 10,
        "keywords": ["adventure", "fantasy", "middle earth", "hobbits"]
    },
    {
        "id": 5,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "genre": "Historical Fiction",
        "description": "A gripping tale of racism and justice in the American South.",
        "location": "Section E, Shelf 4",
        "price": 18.99,
        "stock": 6,
        "keywords": ["justice", "racism", "american south", "coming-of-age"]
    },
    {
        "id": 6,
        "title": "Sapiens: A Brief History of Humankind",
        "author": "Yuval Noah Harari",
        "genre": "Non-fiction",
        "description": "An exploration of the history and impact of Homo sapiens on the world.",
        "location": "Section F, Shelf 7",
        "price": 19.99,
        "stock": 3,
        "keywords": ["history", "humanity", "evolution", "society"]
    },
    {
        "id": 7,
        "title": "Harry Potter and the Sorcerer's Stone",
        "author": "J.K. Rowling",
        "genre": "Fantasy",
        "description": "A young boy discovers he is a wizard and begins his journey at Hogwarts.",
        "location": "Section G, Shelf 9",
        "price": 9.99,
        "stock": 15,
        "keywords": ["magic", "wizardry", "hogwarts", "adventure"]
    },
    {
        "id": 8,
        "title": "Becoming",
        "author": "Michelle Obama",
        "genre": "Biography",
        "description": "The former First Lady's memoir, recounting her life and experiences.",
        "location": "Section H, Shelf 6",
        "price": 18.99,
        "stock": 4,
        "keywords": ["memoir", "inspiration", "politics", "life"]
    },
    {
        "id": 9,
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "genre": "Classic",
        "description": "The story of a troubled teenager's journey through New York City.",
        "location": "Section A, Shelf 2",
        "price": 13.99,
        "stock": 7,
        "keywords": ["teenager", "alienation", "new york", "rebellion"]
    },
    {
        "id": 10,
        "title": "The Art of War",
        "author": "Sun Tzu",
        "genre": "Philosophy",
        "description": "An ancient Chinese text on military strategy and tactics.",
        "location": "Section I, Shelf 8",
        "price": 11.99,
        "stock": 5,
        "keywords": ["strategy", "military", "philosophy", "war"]
    }
]

def parse_query_intent(query):
    query = query.lower()
    if any(word in query for word in ["where", "location", "find", "shelf"]):
        return "location"
    elif any(word in query for word in ["price", "cost", "how much"]):
        return "price"
    elif any(word in query for word in ["recommend", "suggestion", "like"]):
        return "recommendation"
    elif any(word in query for word in ["describe", "about", "tell me"]):
        return "description"
    return "general"

def get_book_by_title(title):
    title = title.lower()
    for book in books:
        if title in book['title'].lower():
            return book
    return None

def get_similar_books(query, n=3):
    sequence = tokenizer.texts_to_sequences([query])
    padded = pad_sequences(sequence, maxlen=20)
    predictions = model.predict(padded)[0]
    # Get top n similar books
    similar_indices = predictions.argsort()[-n:][::-1]
    return [books[i] for i in similar_indices]

def generate_response(query):
    intent = parse_query_intent(query)
    similar_books = get_similar_books(query)
    
    # Check for exact title match first
    for book in books:
        if book['title'].lower() in query.lower():
            if intent == "location":
                return f"You can find '{book['title']}' in {book['location']}. Would you like me to help you find something else?"
            elif intent == "price":
                return f"'{book['title']}' costs ${book['price']}. We have {book['stock']} copies available. Would you like to know more about it?"
            elif intent == "description":
                return f"'{book['title']}' by {book['author']} is {book['description']} You can find it in {book['location']}. Would you like to know the price?"
    
    # Use model predictions for general queries
    if intent == "recommendation":
        book = similar_books[0]  # Get the most similar book
        return f"Based on your query, I highly recommend '{book['title']}' by {book['author']}. {book['description']} You can find it in {book['location']} for ${book['price']}."
    
    # For general queries without specific intent, show multiple recommendations
    if intent == "general":
        response = "Here are some books you might be interested in:\n"
        for book in similar_books:
            response += f"- '{book['title']}' by {book['author']}: {book['description']}\n"
        return response
    
    return "I'm sorry, I couldn't find specific information about that. Could you please rephrase your question? You can ask about book locations, prices, or descriptions."

# Initialize tokenizer
tokenizer = Tokenizer()
tokenizer.fit_on_texts([book['description'] for book in books])

# Simple recommendation model
def create_model():
    model = tf.keras.Sequential([
        Embedding(len(tokenizer.word_index) + 1, 16),
        Dense(8, activation='relu'),
        Dense(len(books), activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy')
    return model

model = create_model()

# Book recommendation function
def get_book_recommendation(query):
    # Tokenize and pad the input query
    sequence = tokenizer.texts_to_sequences([query])
    padded = pad_sequences(sequence, maxlen=20)
    
    # Get prediction
    predictions = model.predict(padded)
    book_idx = np.argmax(predictions[0])
    
    return f"I recommend: {books[book_idx]['title']} by {books[book_idx]['author']}. Genre: {books[book_idx]['genre']}"

# Speech-to-Text (STT)
engine = None

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        # Increase timeout and phrase_time_limit for longer listening
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            return recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            return "No speech detected"
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError as e:
            return f"Error with the service: {e}"

# Text-to-Speech (TTS)
def text_to_speech(text):
    global engine
    if engine:
        engine.stop()
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine = None

@app.route("/stop_tts", methods=["POST"])
def stop_tts():
    global engine
    if engine:
        engine.stop()
        engine = None
    return jsonify({"message": "Speech stopped"})

# Route for home page
@app.route("/")
def index():
    return render_template("index.html")

# Update the chat route to use the new response system
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"response": "Please provide a message."}), 400
    
    response = generate_response(user_message)
    return jsonify({"response": response})

# Route for Speech-to-Text
@app.route("/stt", methods=["GET"])
def stt():
    transcription = speech_to_text()
    return jsonify({"transcription": transcription})

# Update TTS route to use the actual response
@app.route("/tts", methods=["POST"])
def tts():
    text = request.json.get("response")
    if text:
        text_to_speech(text)
        return jsonify({"message": "Playing response."})
    return jsonify({"error": "No response provided."}), 400

if __name__ == "__main__":
    app.run(debug=True)
