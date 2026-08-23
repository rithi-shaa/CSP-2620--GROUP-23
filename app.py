from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'mysecretkey'

#connecting to database
def connect_db() :
    conn = sqlite3.connect('booksession.db')
    conn.row_factory = sqlite3.Row 
    return conn

#register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor(
             'INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)',
             (username, email, password)
        )
        conn.commit()
        conn.close()

        return redirect('/login')
    return render_template('register.html')

#login page

        
