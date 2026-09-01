import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, render_template_string, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.secret_key = "my-secret-key-12345"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

from flask_mail import Mail, Message
mail = Mail(app)

#connecting to database
def get_db_connection() :
    conn = sqlite3.connect('booksession.db')
    conn.row_factory = sqlite3.Row
    return conn

#books
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/catalog")
def catalog():
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
            if selected_genre == b.get("genre", "").lower() 
        ]

    if selected_year:
        filtered_books = [
            b for b in filtered_books
            if str(selected_year) == str(b.get("year", ""))
        ]
        
    html = """
    <h1>Book Catalog</h1>
    <form method="GET" action="/">
        <input type="text" name="q" placeholder="Search by title or author..." value="{{ request.args.get('q', '') }}">

        <select name="genre">
            <option value="">All Genres</option>
            <option value="Classic" {% if request.args.get('genre') == 'Classic' %}selected{% endif %}>Classic</option>
            <option value="Dystopian" {% if request.args.get('genre') == 'Dystopian' %}selected{% endif %}>Dystopian</option>
            <option value="Fantasy" {% if request.args.get('genre') == 'Fantasy' %}selected{% endif %}>Fantasy</option>
            <option value="Mystery" {% if request.args.get('genre') == 'Mystery' %}selected{% endif %}>Mystery</option>
        </select>

        <input type="number" name="year" placeholder="Year (e.g. 1925)" value="{{ request.args.get('year', '') }}">

        <button type="submit">Filter & Search</button>
        <a href="/">Reset</a>
    </form>
    <ul>
        {% for book in filtered_books %}
            <li>
                <strong>{{ book.title }}</strong> by {{ book.author }} 
                ({{ book.genre }}{% if book.year %}, {{ book.year }}{% endif %})<br>
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
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name', '')

        if not username or not email or not password or not confirm_password:
            flash("All required fields must be filled out.")
            return redirect(url_for('register'))

        if password != confirm_password:
            flash("Password do not match.")
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

            verify_link = url_for('verify_email', token=verification_token, _external=True)
            msg = Message(
                subject="Verify your Booksession account",
                recipients=[email],
                body=f"Welcome to Booksession! Click the link to verify your account: {verify_link}"
            )
            mail.send(msg)

            flash("Registration successful! Check you email to verify your account before logging in.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username or email already exists.")
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/verify/<token>')
def verify_email(token):
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM User WHERE verification_token = ?" , (token,)
    ).fetchone()

    if not user:
        conn.close()
        flash("Invalid or expired verification link.")
        return redirect(url_for('login'))

    conn.execute(
        "UPDATE User SET is_verified = 1, verification_token = NULL WHERE user_id = ?",
        (user['user_id'],)
    )
    conn.commit()
    conn.close()

    flash("Your account has been verified! You can now log in.")
    return redirect(url_for('login'))

@app.route('/reset_password', defaults={'token': None}, methods=['GET', 'POST'])
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if token is None:
        if request.method == 'POST':
            email = request.form.get('email')

            if not email:
                flash("Please enter your email address.")
                return redirect(url_for('reset_password'))

            conn = get_db_connection()
            user = conn.execute(
                "SELECT * FROM User WHERE email = ?", (email,)
            ).fetchone()

            if user:
                reset_token = secrets.token_urlsafe(16)
                conn.execute(
                    "UPDATE User SET verification_token = ? WHERE email = ?",
                    (reset_token, email)
                )
                conn.commit()

                reset_link = url_for('reset_password', token=reset_token, _external=True)
                msg = Message(
                    subject="Reset your Booksession password",
                    recipients=[email],
                    body=f"Click the link to reset your password: {reset_link}"
                )
                mail.send(msg)

            conn.close()
            flash("If that email is registered, a reset link has been sent.")
            return redirect(url_for('login'))

        return render_template('reset_password.html', token=None)

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM User WHERE verification_token = ?", (token,)
    ).fetchone()

    if not user:
        conn.close()
        flash("Invalid or expired reset link.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('reset_password', token=token))

        password_hash = generate_password_hash(new_password)
        conn.execute(
            "UPDATE User SET password_hash = ?, verification_token = NULL WHERE user_id = ?",
            (password_hash, user['user_id'])
        )
        conn.commit()
        conn.close()

        flash("Password reset successful! Please log in.")
        return redirect(url_for('login'))

    conn.close()
    return render_template('reset_password.html', token=token)

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

    return render_template('index.html')

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

@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if 'user_id' not in session:
        flash('Please log in to add a book.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        publication_year = request.form['publication_year']
        created_by = session['user_id']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO Book (title, author, genre, publication_year, created_by) VALUES (?, ?, ?, ?, ?)',
            (title, author, genre, publication_year, created_by)
        )
        conn.commit()
        conn.close()
        
        flash('Book added successfully!')
        return redirect(url_for('index'))

    return render_template('add_book.html')

if __name__ == '__main__':
    app.run(debug=True)