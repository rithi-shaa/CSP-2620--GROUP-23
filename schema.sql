--User table (MEMBER 1: authentication & profile)
CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    bio TEXT,
    is_verified INTEGER DEFAULT 0,
    verification_token TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shelf table (MEMBER 1: custom shelves)
CREATE TABLE IF NOT EXISTS Shelf (
    shelf_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shelf_name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

-- ShelfBook Table (MEMBER 1&2: Prevents adding same book + Reading Status)
CREATE TABLE IF NOT EXISTS ShelfBook (
    shelf_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    reading_status TEXT CHECK (reading_status IN ('Want to Read', 'Currently Reading', 'Completed' )) DEFAULT 'Want to Read',
    PRIMARY KEY (shelf_id, book_id),
    FOREIGN KEY (shelf_id) REFERENCES Shelf(shelf_id) ON DELETE CASCADE
);

-- Book table (Catalog & Metadata)
CREATE TABLE IF NOT EXISTS Book (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT,
    publication_year INTEGER,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES User(user_id) ON DELETE SET NULL
);

-- Ratings table (User ratings for books)
CREATE TABLE IF NOT EXISTS Rating (
    rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating_value INTEGER CHECK (rating_value BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    UNIQUE (book_id, user_id)
);

-- Reviews table (User written reviews for books)
CREATE TABLE IF NOT EXISTS Review (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    review_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);