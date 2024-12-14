import mysql.connector
from mysql.connector import Error
import logging
import threading

class BookstoreDB:
    _instance = {}
    _lock = threading.Lock()

    def __init__(self):
        self._local = threading.local()
        self.db_config = {
            'host': 'localhost',
            'user': 'root',  # Replace with your MySQL username
            'password': '',   # Replace with your MySQL password
            'database': 'bookstore'
        }
        self.connect()
        self._initialize_db()

    def connect(self):
        """Ensure thread-local connection and cursor are initialized."""
        if not hasattr(self._local, 'conn'):
            self._local.conn = mysql.connector.connect(**self.db_config)
            self._local.cursor = self._local.conn.cursor(buffered=True)
        
    @property
    def cursor(self):
        """Return cursor for the current thread."""
        if not hasattr(self._local, 'conn') or not self._local.conn.is_connected():
            self.connect()
        return self._local.cursor

    @property
    def conn(self):
        """Return connection for the current thread."""
        if not hasattr(self._local, 'conn') or not self._local.conn.is_connected():
            self.connect()
        return self._local.conn

    def _initialize_db(self):
        """Create tables if they don't exist."""
        try:
            self.cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    genre VARCHAR(100) NOT NULL,
                    description TEXT,
                    location VARCHAR(100),
                    price DECIMAL(10,2) NOT NULL,
                    stock INT NOT NULL,
                    keywords TEXT
                )
            ''')
            self.conn.commit()
        except Error as e:
            logging.error(f"Database initialization error: {e}")
            raise

    def check_availability(self, book_title):
        query = """
            SELECT title, author, stock, location, price, genre, description 
            FROM books WHERE title = %s
        """
        self.cursor.execute(query, (book_title,))
        return self.cursor.fetchone()

    def get_price(self, book_title):
        query = """
            SELECT title, author, price 
            FROM books WHERE LOWER(title) LIKE LOWER(%s)
        """
        self.cursor.execute(query, (f"%{book_title}%",))
        return self.cursor.fetchone()

    def search_books(self, keyword):
        query = """
            SELECT title, author, genre, price, stock 
            FROM books 
            WHERE LOWER(keywords) LIKE LOWER(%s) 
            OR LOWER(title) LIKE LOWER(%s)
            OR LOWER(description) LIKE LOWER(%s)
        """
        search_term = f"%{keyword}%"
        self.cursor.execute(query, (search_term, search_term, search_term))
        return self.cursor.fetchall()

    def __del__(self):
        """Ensure proper cleanup of the connection and cursor."""
        if hasattr(self._local, 'conn') and self._local.conn.is_connected():
            self._local.cursor.close()
            self._local.conn.close()

