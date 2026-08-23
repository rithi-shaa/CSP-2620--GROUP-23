from flask import Flask, render_template, request, redirect, url_for, session, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = 'mysecretkey'

#connecting to database
def connect_db() :
    conn = sqlite3.connect('booksession.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

#catalog
books = [
    {
        "book_id": 1, 
        "title": "The Great Gatsby", 
        "author": "F. Scott Fitzgerald", 
        "genre": "Classic", 
        "story": "A wealthy man throws lavish parties in hopes of winning back his former lover."
    },
    {
        "book_id": 2, 
        "title": "1984", 
        "author": "George Orwell", 
        "genre": "Dystopian", 
        "story": "A man rebels against a totalitarian regime that watches every move of its citizens."
    },
    {
        "book_id": 3, 
        "title": "The Hobbit", 
        "author": "J.R.R. Tolkien", 
        "genre": "Fantasy", 
        "story": "A home-loving hobbit gets dragged into an epic quest."
    },
    {
        "book_id": 4, 
        "title": "The Shadow of the Wind", 
        "author": "Carlos Ruiz Zafón", 
        "genre": "Mystery", 
        "story": "A boy discovers a mysterious book that pulls him into a dark secret."
    }
]

@app.route("/")
def home():
    search_query = request.args.get("q", "").lower()
    
    if search_query:
        filtered_books = [
            b for b in books 
            if search_query in b["title"].lower() or search_query in b["author"].lower()
        ]
    else:
        filtered_books = books

    html = """
    <h1>Book Catalog</h1>
    <form method="GET" action="/">
        <input type="text" name="q" placeholder="Search by title or author..." value="{{ request.args.get('q', '') }}">
        <button type="submit">Search</button>
        <a href="/">Reset</a>
    </form>
    <ul>
        {% for book in filtered_books %}
            <li>
                <strong>{{ book.title }}</strong> by {{ book.author }} ({{ book.genre }})<br>
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
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password)
        )
        conn.commit()
        conn.close()

        return redirect('/login')
    return render_template('register.html')

#login page
@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM User WHERE email = ? AND password_hash = ?',
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user: 
            session ['user_id'] = user['user_id']
            session['username'] = user['username']
            return redirect(url_for('shelves'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))








if __name__ == "__main__":
    app.run(debug=True)

        
