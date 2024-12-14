# model.py
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from db import BookstoreDB
from typing import Dict, Union

class BookTitleExtractor:
    def __init__(self):
        self.db = BookstoreDB()
        self.vectorizer = TfidfVectorizer()
        self.classifier = RandomForestClassifier()
        self.title_vectors = None
        self.titles_list = None
        self.faq_data = {
            'hours': {
                'question': ['when does','opening hours', 'closing time', 'when open', 'when close', 'library hours'],
                'answer': 'We are open Monday-Friday 9:00 AM - 8:00 PM, Saturday 10:00 AM - 6:00 PM, and Sunday 12:00 PM - 5:00 PM'
            },
            'location': {
                'question': ['where located', 'address', 'direction', 'how to get there'],
                'answer': 'We are located at University of Cebu - Main, Ground Floor'
            },
            'borrowing': {
                'question': ['how to borrow', 'borrow books', 'lending period', 'loan duration'],
                'answer': 'You can borrow up to 5 books for 2 weeks with your library card. Renewals are available online.'
            },
            'membership': {
                'question': ['how to join', 'membership', 'library card', 'sign up'],
                'answer': 'To get a library card, bring your ID and proof of address to the front desk. Membership is free!'
            },
            'services': {
                'question': ['what services', 'facilities', 'what do you offer'],
                'answer': 'We offer book lending, study spaces, WiFi, printing services, and computer access.'
            }
        }
        self.book_query_types = {
            'synopsis': ['what is it about', 'tell me about', 'summary', 'plot', 'story', 'description'],
            'genre': ['genre', 'type of book', 'category', 'what kind of book'],
            'publication': ['when was','when published', 'publication date', 'release date', 'year'],
            'details': ['information', 'details', 'tell me more', 'info about'],
            'find': ['where can i find', 'where is', 'locate', 'which shelf', 'which section', 'book location', 'find book', 'get book'],
            'reviews': ['reviews', 'rating', 'what do people think', 'is it good'],
        }
        self.train()
        
    def _get_training_data(self):
        """Get book titles from database for training"""
        books = self.db.search_books("")
        self.books_data = {book[0].lower(): book for book in books}  # Store full book info
        titles = [book[0] for book in books]
        return titles

    def _create_training_samples(self, titles):
        """Create training samples with title queries and FAQ"""
        X, y = [], []
        
        # Positive examples (queries containing titles)
        patterns = [
            "Where can I find {}?",
            "Do you have {}?",
            "I'm looking for {}",
            "Price of {}?",
            "Is {} available?",
            "Do you have {} by {}?",  # New pattern with author
            "I want {} written by {}",  # New pattern with author
            "Looking for {}'s book {}",  # New pattern with author first
            "Anything by {}?",  # Author-only query
            "{} latest book?"  # Author's latest
        ]
        
        for title in self.books_data:
            book_info = self.books_data[title]
            title, author = book_info[0], book_info[1]
            
            # Add basic title patterns
            for pattern in patterns[:5]:
                query = pattern.format(title)
                X.append(query.lower())
                y.append(1)
            
            # Add author-related patterns
            X.extend([
                f"Do you have {title} by {author}?".lower(),
                f"I want {title} written by {author}".lower(),
                f"Looking for {author}'s book {title}".lower(),
                f"Anything by {author}?".lower(),
                f"{author}'s latest book?".lower()
            ])
            y.extend([1, 1, 1, 1, 1])
                
        # Add FAQ training samples
        for category, data in self.faq_data.items():
            for question in data['question']:
                X.append(question.lower())
                y.append(2)  # New class for FAQ queries
        
        # Negative examples (queries without titles)
        negative = [
            "Hello how are you?",
            "What time do you close?",
            "Do you offer delivery?",
            "Where is the store located?",
            "Thank you for help",
            "thank you",
            "goodbye",
            "see you later"
        ]
        
        X.extend(negative)
        y.extend([0] * len(negative))
        
        return X, y
    
    def train(self):
        """Train the title extractor"""
        titles = self._get_training_data()
        X, y = self._create_training_samples(titles)
        
        # Transform text to features for classification
        X_features = self.vectorizer.fit_transform(X)
        self.classifier.fit(X_features, y)
        
        # Create vectors for all titles for similarity matching
        self.titles_list = list(titles)
        self.title_vectors = self.vectorizer.transform(self.titles_list)
        self.known_titles = set(t.lower() for t in titles)

    def get_similar_titles(self, query, n=3):
        """Get n most similar titles using TF-IDF and cosine similarity"""
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.title_vectors).flatten()
        similar_indices = similarities.argsort()[-n:][::-1]
        similar_books = []
        for idx in similar_indices:
            if similarities[idx] > 0.4:
                title = self.titles_list[idx]
                book_info = self.books_data[title.lower()]
                similar_books.append({
                    'title': book_info[0],
                    'author': book_info[1],
                    'similarity': similarities[idx]
                })
        return similar_books

    def get_faq_response(self, query: str) -> Union[str, None]:
        """Get FAQ response based on query"""
        query = query.lower()
        
        # Check each FAQ category
        for category, data in self.faq_data.items():
            if any(q in query for q in data['question']):
                return data['answer']
        return None

    def extract_title(self, query):
        """Extract book title from query with ML-based suggestions"""
        query = query.lower()
        similar_books = self.get_similar_titles(query)
        results = {'exact_match': None, 'suggestions': []}
        
        if similar_books:
            results['exact_match'] = similar_books[0]['title']
            results['exact_match_author'] = similar_books[0]['author']
            results['suggestions'] = [(book['title'], book['author']) for book in similar_books[1:]]
        
        return results

    def get_query_intent(self, query: str) -> str:
        query = query.lower()
        for intent, patterns in self.book_query_types.items():
            if any(pattern in query for pattern in patterns):
                return intent
        return 'availability'  # default intent

    def handle_query(self, query: str) -> Dict:
        """Enhanced query handler with book information intents"""
        # First try FAQ
        faq_response = self.get_faq_response(query)
        if faq_response:
            return {'type': 'faq', 'response': faq_response}
            
        # Then try book search
        result = self.extract_title(query)
        if result['exact_match']:
            book_info = self.db.check_availability(result['exact_match'])
            intent = self.get_query_intent(query)
            
            return {
                'type': 'book',
                'found': True,
                'intent': intent,
                'data': {
                    'title': book_info[0],
                    'author': book_info[1],
                    'stock': book_info[2],
                    'location': book_info[3],
                    'price': book_info[4],
                    'genre': book_info[5] if len(book_info) > 5 else 'Unknown',
                    'synopsis': book_info[6] if len(book_info) > 6 else 'No synopsis available',
                    'publication': book_info[7] if len(book_info) > 7 else 'NA',
                },
                'suggestions': result['suggestions']
            }
        
        return {
            'type': 'book',
            'found': False,
            'suggestions': result['suggestions']
        }

    def _findBook(self, query):
        result = self.extract_title(query)
        print("Extracted title:", result)
        if result['exact_match']:
            book_info = self.db.check_availability(result['exact_match'])
            if book_info:
                return {
                    'found': True,
                    'title': book_info[0],
                    'author': book_info[1],
                    'stock': book_info[2],
                    'location': book_info[3],
                    'price': book_info[4],
                    'suggestions': []
                }
        # Return ML-based suggestions if no exact match
        return {
            'found': False,
            'suggestions': result['suggestions']
        }
