import spacy
import requests
import json

from model import BookTitleExtractor
extractor = BookTitleExtractor()



def format_suggestions(suggestions):
    if not suggestions:
        return "No similar books found."
    return "Did you mean one of these?\n\n" + "\n".join(f"• '{title}' by {author}" for title, author in suggestions)

def handleQuery(query: str):
    result = extractor.handle_query(query)
    extractor.train()
    if result['type'] == 'faq':
        return result['response']
        
    if result['type'] == 'book':
        if result['found']:
            data = result['data']
            
            # Handle different types of book queries
            if result.get('intent') == 'synopsis':
                return f"Book: '{data['title']}'\nAuthor: {data['author']}\n\nSynopsis:\n{data['synopsis']}"
                
            elif result.get('intent') == 'genre':
                return f"Book: '{data['title']}'\nAuthor: {data['author']}\nGenre: {data['genre']}"
                
            elif result.get('intent') == 'publication':
                return f"Book: '{data['title']}'\nAuthor: {data['author']}\nPublication Year: {data['publication']}"
                
            elif result.get('intent') == 'reviews':
                return f"Book: '{data['title']}'\nAuthor: {data['author']}\n\nThis is a popular book in our collection."
                
            elif result.get('intent') == 'details':
                return (f"Book Details:\n\n"
                       f"Title: '{data['title']}'\n"
                       f"Author: {data['author']}\n"
                       f"Genre: {data['genre']}\n"
                       f"Published: {data['publication']}\n"
                       f"Available: {data['stock']} copies\n"
                       f"Location: {data['location']}\n"
                       f"Price: ${data['price']}")
                
            elif 'price' in query.lower() or 'how much' in query.lower() or 'cost' in query.lower():
                return (f"The Book: '{data['title']} costs ₱{data['price']}.\n")
            
            elif 'find' in query.lower():
                return (f"You can find the Book: '{data['title']} in {data['location']}'")
            else: return "I'm sorry, I don't understand your question. Please try again."
        else:
            return f"I couldn't find that exact book.\n\n{format_suggestions(result.get('suggestions'))}"
    
    return "I'm sorry, I don't understand your question. Please try again."



