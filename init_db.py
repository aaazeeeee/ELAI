import mysql.connector
from mysql.connector import Error

def init_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='',  # Replace with your MySQL password
            database='bookstore'  # Replace with your database name
        )
        
        c = conn.cursor()

        # Create database if not exists
        c.execute('CREATE DATABASE IF NOT EXISTS bookstore')
        c.execute('USE bookstore')

        # Create tables
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                genre VARCHAR(100) NOT NULL,
                description TEXT,
                location VARCHAR(100),
                price DECIMAL(10,2),
                stock INT,
                keywords TEXT
            )
        ''')

        # Insert admin user
        c.execute('INSERT IGNORE INTO users (email, password) VALUES (%s, %s)',
                 ('admin@gmail.com', 'admin123'))

        # Insert sample books
        sample_books = [
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "genre": "Classic",
                "description": "A story of decadence and excess in the Jazz Age.",
                "location": "Section A, Shelf 3",
                "price": 15.99,
                "stock": 5,
                "keywords": "jazz age, romance, american dream, wealth"
            },
            {
                "title": "1984",
                "author": "George Orwell",
                "genre": "Science Fiction",
                "description": "A dystopian novel about totalitarian surveillance.",
                "location": "Section B, Shelf 1",
                "price": 12.99,
                "stock": 8,
                "keywords": "dystopia, politics, surveillance, totalitarianism"
            },
            {
                "title": "To Kill a Mockingbird",
                "author": "Harper Lee",
                "genre": "Classic",
                "description": "A novel about racial injustice in the Deep South.",
                "location": "Section A, Shelf 4",
                "price": 10.99,
                "stock": 7,
                "keywords": "racism, justice, innocence, moral growth"
            },
            {
                "title": "Pride and Prejudice",
                "author": "Jane Austen",
                "genre": "Romance",
                "description": "A romantic novel about manners and matrimonial machinations.",
                "location": "Section C, Shelf 2",
                "price": 9.99,
                "stock": 6,
                "keywords": "romance, society, marriage, class"
            },
            {
                "title": "The Catcher in the Rye",
                "author": "J.D. Salinger",
                "genre": "Classic",
                "description": "A story about teenage rebellion and angst.",
                "location": "Section A, Shelf 5",
                "price": 8.99,
                "stock": 4,
                "keywords": "rebellion, adolescence, identity, alienation"
            },
            {
                "title": "Moby-Dick",
                "author": "Herman Melville",
                "genre": "Adventure",
                "description": "A narrative of the adventures of the wandering sailor Ishmael.",
                "location": "Section D, Shelf 1",
                "price": 11.99,
                "stock": 3,
                "keywords": "adventure, sea, obsession, revenge"
            },
            {
                "title": "War and Peace",
                "author": "Leo Tolstoy",
                "genre": "Historical",
                "description": "A novel that chronicles the history of the French invasion of Russia.",
                "location": "Section E, Shelf 2",
                "price": 14.99,
                "stock": 6,
                "keywords": "war, peace, history, Russia"
            },
            {
                "title": "The Odyssey",
                "author": "Homer",
                "genre": "Epic",
                "description": "An epic poem about the journey of Odysseus.",
                "location": "Section F, Shelf 1",
                "price": 13.99,
                "stock": 5,
                "keywords": "epic, journey, mythology, adventure"
            },
            {
                "title": "Crime and Punishment",
                "author": "Fyodor Dostoevsky",
                "genre": "Psychological",
                "description": "A novel about the mental anguish of a young man.",
                "location": "Section G, Shelf 3",
                "price": 11.99,
                "stock": 4,
                "keywords": "crime, punishment, psychology, guilt"
            },
            {
                "title": "The Brothers Karamazov",
                "author": "Fyodor Dostoevsky",
                "genre": "Philosophical",
                "description": "A novel about the spiritual drama of moral struggles.",
                "location": "Section G, Shelf 4",
                "price": 12.99,
                "stock": 5,
                "keywords": "philosophy, morality, family, faith"
            },
            {
                "title": "Brave New World",
                "author": "Aldous Huxley",
                "genre": "Science Fiction",
                "description": "A dystopian novel about a futuristic society.",
                "location": "Section B, Shelf 2",
                "price": 10.99,
                "stock": 7,
                "keywords": "dystopia, society, future, technology"
            },
            {
                "title": "Jane Eyre",
                "author": "Charlotte Brontë",
                "genre": "Romance",
                "description": "A novel about the experiences of the orphan Jane Eyre.",
                "location": "Section C, Shelf 3",
                "price": 9.99,
                "stock": 6,
                "keywords": "romance, orphan, independence, morality"
            },
            {
                "title": "Wuthering Heights",
                "author": "Emily Brontë",
                "genre": "Gothic",
                "description": "A novel about the intense and almost demonic love between Catherine and Heathcliff.",
                "location": "Section H, Shelf 1",
                "price": 8.99,
                "stock": 5,
                "keywords": "gothic, love, revenge, tragedy"
            },
            {
                "title": "The Hobbit",
                "author": "J.R.R. Tolkien",
                "genre": "Fantasy",
                "description": "A fantasy novel about the journey of Bilbo Baggins.",
                "location": "Section I, Shelf 2",
                "price": 10.99,
                "stock": 8,
                "keywords": "fantasy, adventure, journey, dragon"
            },
            {
                "title": "Fahrenheit 451",
                "author": "Ray Bradbury",
                "genre": "Science Fiction",
                "description": "A dystopian novel about a future where books are banned.",
                "location": "Section B, Shelf 3",
                "price": 9.99,
                "stock": 7,
                "keywords": "dystopia, censorship, books, future"
            },
            {
                "title": "The Divine Comedy",
                "author": "Dante Alighieri",
                "genre": "Epic",
                "description": "An epic poem about the journey through Hell, Purgatory, and Paradise.",
                "location": "Section F, Shelf 2",
                "price": 14.99,
                "stock": 4,
                "keywords": "epic, journey, afterlife, poetry"
            },
            {
                "title": "The Iliad",
                "author": "Homer",
                "genre": "Epic",
                "description": "An epic poem about the Trojan War.",
                "location": "Section F, Shelf 3",
                "price": 13.99,
                "stock": 5,
                "keywords": "epic, war, mythology, heroism"
            },
            {
                "title": "Anna Karenina",
                "author": "Leo Tolstoy",
                "genre": "Romance",
                "description": "A novel about the tragic love affair of Anna Karenina.",
                "location": "Section C, Shelf 4",
                "price": 12.99,
                "stock": 6,
                "keywords": "romance, tragedy, society, love"
            },
            {
                "title": "The Grapes of Wrath",
                "author": "John Steinbeck",
                "genre": "Historical",
                "description": "A novel about the struggles of a poor family during the Great Depression.",
                "location": "Section E, Shelf 3",
                "price": 11.99,
                "stock": 7,
                "keywords": "history, depression, family, struggle"
            },
            {
                "title": "The Lord of the Rings",
                "author": "J.R.R. Tolkien",
                "genre": "Fantasy",
                "description": "A fantasy novel about the quest to destroy the One Ring.",
                "location": "Section I, Shelf 3",
                "price": 15.99,
                "stock": 8,
                "keywords": "fantasy, adventure, quest, ring"
            }
        ]

        for book in sample_books:
            c.execute('''
                INSERT IGNORE INTO books 
                (title, author, genre, description, location, price, stock, keywords)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                book['title'], book['author'], book['genre'], 
                book['description'], book['location'], book['price'],
                book['stock'], book['keywords']
            ))

        conn.commit()
        conn.close()
        print("Database initialized successfully!")

    except Error as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    init_db()
