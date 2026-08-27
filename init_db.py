import sqlite3

def init_db():
    conn = sqlite3.connect('booksession.db')
    cursor = conn.cursor()
    with open ('schema.sql', 'r') as f:
        cursor.executescript(f.read())
        
    conn.commit()
    conn.close()
    print("Database initialized successfully from schema.sql!")

if __name__ == '__main__':
    init_db()