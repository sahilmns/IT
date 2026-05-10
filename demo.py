from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

# 🔹 Upload Folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 🔥 IMPORTANT
# uploads folder automatically create karega
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔹 Database init
def init_db():
    with sqlite3.connect("users.db") as conn:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            fullname TEXT,
            email TEXT,
            bio TEXT,
            profile_pic TEXT
        )
        """)

        conn.commit()

init_db()

# 🔹 Home
@app.route('/')
def home():
    return render_template("index.html")

# 🔹 About
@app.route('/about')
def about():
    return render_template("about.html")

# 🔹 Courses
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
            with sqlite3.connect("users.db") as conn:

                cur = conn.cursor()

                cur.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_password)
                )

                conn.commit()

            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            return "Username already exists ❌"

        except sqlite3.OperationalError:
            return "Database busy, try again ⏳"

    return render_template("signup.html")

# 🔹 Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )

        user = cur.fetchone()

        conn.close()

        if user and check_password_hash(user[0], password):

            session['user'] = username

            return redirect(url_for('dashboard'))

        return "Invalid Credentials ❌"

    return render_template("login.html")

# 🔹 Dashboard
@app.route('/dashboard')
def dashboard():

    if 'user' in session:
        return render_template(
            "dashboard.html",
            name=session['user']
        )

    return redirect(url_for('login'))

# 🔹 Edit Profile
@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():

    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        bio = request.form['bio']

        file = request.files['profile_pic']

        filename = None

        # 🔥 Image Upload
        if file and file.filename != "":

            filename = secure_filename(file.filename)

            file_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )

            file.save(file_path)

        # Old image preserve
        cur.execute(
            "SELECT profile_pic FROM users WHERE username=?",
            (session['user'],)
        )

        old_data = cur.fetchone()

        old_pic = old_data[0] if old_data else None

        if filename is None:
            filename = old_pic

        # 🔥 Update User
        cur.execute("""
        UPDATE users
        SET fullname=?,
            email=?,
            bio=?,
            profile_pic=?
        WHERE username=?
        """, (
            fullname,
            email,
            bio,
            filename,
            session['user']
        ))

        conn.commit()

        conn.close()

        return redirect(url_for('profile'))

    # 🔹 Get User Data
    cur.execute("""
    SELECT fullname, email, bio, profile_pic
    FROM users
    WHERE username=?
    """, (session['user'],))

    user = cur.fetchone()

    conn.close()

    return render_template(
        "edit_profile.html",
        user=user
    )

# 🔹 Profile Page
@app.route('/profile')
def profile():

    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT username, fullname, email, bio, profile_pic
    FROM users
    WHERE username=?
    """, (session['user'],))

    user = cur.fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user
    )

# 🔹 Logout
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect(url_for('home'))

# 🔹 Faculty
@app.route('/faculty')
def faculty():

    faculty_list = [
        {"name": "Dr. Vikas", "subject": "Data Structures"},
        {"name": "Prof. Khan", "subject": "Web Development"},
        {"name": "Mrs. Gupta", "subject": "Python Programming"}
    ]

    return render_template(
        "faculty.html",
        faculty=faculty_list
    )

# 🔹 Notices
@app.route('/notices')
def notices():

    notice_list = [
        "Mid Semester Exam from 20th Sept 📅",
        "Workshop on AI this Friday 🤖",
        "Project submission deadline extended ⏳"
    ]

    return render_template(
        "notices.html",
        notices=notice_list
    )

# 🔹 Run App
if __name__ == '__main__':
    app.run(debug=True)