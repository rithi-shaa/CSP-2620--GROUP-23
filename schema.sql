--User table (MEMBER 1: authentication & profile)
CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    bio TEXT
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
