from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# 🔹 Database init
def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# 🔹 Home
@app.route('/')
def home():
    return render_template("index.html")

# 🔹 About
@app.route('/about')
def about():
    return render_template("about.html")

# 🔹 courses
@app.route('/courses')
def courses():
    return render_template("courses.html")

# 🔹 Contact
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['username']
        return f"Hello {name} 👋"
    return render_template("contact.html")

# 🔹 Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("users.db")
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                        (username, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return "User already exists ❌"

    return render_template("signup.html")

# 🔹 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Credentials ❌"

    return render_template("login.html")

# 🔹 Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template("dashboard.html", name=session['user'])
    else:
        return redirect(url_for('login'))

# 🔹 Profile
@app.route('/profile')
def profile():
    if 'user' in session:
        return render_template("profile.html")
    else:
        return redirect(url_for('login'))

# 🔹 Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# 🔹 Run
if __name__ == '__main__':
    app.run(debug=True)