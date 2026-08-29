from flask import Flask, render_template, request, redirect, url_for, session, render_template_string, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.secret_key = "my-secret-key-12345"

#connecting to database
def get_db_connection() :
    conn = sqlite3.connect('booksession.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/welcome')
def catalog():
    return render_template('index.html')


#Updated catalog data structure including years and genre
books = [
    {
        "book_id": 1, 
        "title": "The Great Gatsby", 
        "author": "F. Scott Fitzgerald", 
        "genre": "Classic", 
        "year": 1925,
        "story": "A wealthy man throws lavish parties in hopes of winning back his former lover."
    },
    {
        "book_id": 2, 
        "title": "1984", 
        "author": "George Orwell", 
        "genre": "Dystopian", 
        "year": 1949,
        "story": "A man rebels against a totalitarian regime that watches every move of its citizens."
    },
    {
        "book_id": 3, 
        "title": "The Hobbit", 
        "author": "J.R.R. Tolkien", 
        "genre": "Fantasy", 
        "year": 1937, 
        "story": "A home-loving hobbit gets dragged into an epic quest."
    },
    {
        "book_id": 4, 
        "title": "The Shadow of the Wind", 
        "author": "Carlos Ruiz Zafón", 
        "genre": "Mystery", 
        "year": 2001,
        "story": "A boy discovers a mysterious book that pulls him into a dark secret."
    }
]

@app.route("/")
def home():
    search_query = request.args.get("q", "").lower()
    selected_genre = request.args.get("genre", "").lower()
    selected_year = request.args.get("year", "")

    filtered_books = books
    
    if search_query:
        filtered_books = [
            b for b in books 
            if search_query in b["title"].lower() or search_query in b["author"].lower()
        ]
    if selected_genre: 
        filtered_books = [
            b for b in filtered_books
            if selected_genre == b.get ("genre","").lower() 
        ]

    if selected_year:
        filtered_books = [
            b for b in filtered_books
            if str(selected_year) == str(b.get("year",""))
        ]
        
    html = """
    <h1>Book Catalog</h1>
    <form method="GET" action="/">
        <input type="text" name="q" placeholder="Search by title or author..." value="{{ request.args.get('q', '') }}">

        <select name ="genre">
            <option value="">All Genres</option>
            <option value="Classic" {% if.request.args.get('genre') == 'Classic' %}selected{% end if %}>Classic</option>
            <option value="Dystopian" {% if.request.args.get('genre') == 'Dystopian' %}selected{% end if %}>Dystopian</option>
            <option value="Fantasy" {% if.request.args.get('genre') == 'Fantasy' %}selected{% end if %}>Fantasy</option>
            <option value="Mystery" {% if.request.args.get('genre') == ']Mystery' %}selected{% end if %}>Mystery</option>
        </select>

        <input type="number" name="year" placeholder="Year (e.g.1925)" value="{{ request.args.get('year', '') }}'>

        <button type="submit">Filter & Search</button>
        <a href="/">Reset</a>
    </form>
    <ul>
        {% for book in filtered_books %}
            <li>
                <strong>{{ book.title }}</strong> by {{ book.author }} 
                ({{ book.genre }} {% if.book.year %}. {{ book.year }}{% endif %}<br>
                <em>Story: {{ book.story }}</em>
            </li>
        {% else %}
            <p>No books found matching your search.</p>
        {% endfor %}
    </ul>
    """
    return render_template_string(html, filtered_books=filtered_books)

#register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name', '')

        if not username or not email or not password:
            flash("All required fields must be filled out.")
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        verification_token = secrets.token_urlsafe(16)

        conn = get_db_connection()
        try:
            conn.execute(
                """
                INSERT INTO User (username, email, password_hash, full_name, is_verified, verification_token)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (username, email, password_hash, full_name, 0, verification_token)
            )
            conn.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username or email already exists.")
        finally:
            conn.close()

    return render_template('register.html')

#login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM User WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            flash("Logged in successfully!")
            return redirect(url_for('profile'))
        else:
            flash("Invalid username or password.")

    return render_template('login.html')

#shelf
@app.route('/shelves')
def shelves():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Shelf WHERE user_id = ?' , (session['user_id'], ))
    my_shelves = cursor.fetchall()
    conn.close()

    return render_template('shelves.html', shelves=my_shelves, username=session.get('username'))

#add shelf
@app.route('/add_shelf', methods=['POST'])
def add_shelf():
    if 'user_id' in session:
        shelf_name = request.form['shelf_name']

        if shelf_name.strip():
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO Shelf (shelf_name, user_id) VALUES (?, ?)',
                (shelf_name.strip(), session['user_id'])
            )
            conn.commit()
            conn.close()

            return redirect(url_for('shelves'))

#adding book to shelf
@app.route('/add_to_shelf', methods=['POST'])
def add_to_shelf():
    if 'user_id' not in session:
        return redirect('/login')

    shelf_id = request.form.get('shelf_id')
    book_id = request.form.get('book_id')

    if shelf_id and book_id:
        conn = get_db_connection()
        cursor = conn.cursor()

        existing = cursor.execute(
            'SELECT * FROM ShelfBook WHERE shelf_id = ? AND book_id = ?',
            (shelf_id, book_id)
        ).fetchone()

        if not existing:
            cursor.execute(
                'INSERT INTO ShelfBook (shelf_id, book_id) VALUES (?, ?)',
                (shelf_id, book_id)
            )
            conn.commit()
        conn.close()
    return redirect(url_for('shelves'))

#profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        bio = request.form.get('bio')
        full_name = request.form.get('full_name')

        conn.execute(
            "UPDATE User SET bio = ?, full_name = ? WHERE user_id = ?",
            (bio, full_name, session['user_id'])
        )
        conn.commit()
        flash("Profile updated successfully!")
        return redirect(url_for('profile'))

    user = conn.execute(
        "SELECT * FROM User WHERE user_id = ?", (session['user_id'],)
    ).fetchone()
    conn.close()

    return render_template('profile.html', user=user)

#logout page
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
