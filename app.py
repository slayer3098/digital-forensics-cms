from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_connection
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key'

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT UNIQUE NOT NULL,
            case_name TEXT NOT NULL,
            investigator TEXT,
            evidence TEXT,
            description TEXT,
            status TEXT,
            location TEXT,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB when app starts
init_db()

@app.route('/')
def index():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)""", (username, email, password_hash))
        conn.commit()
        conn.close()

        flash('Signup successful. Please log in.')
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if row and check_password_hash(row[1], password):
            session['user_id'] = row[0]
            session['email'] = email
            return redirect('/dashboard')
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/add-case', methods=['GET', 'POST'])
def add_case():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        case_id = request.form['case_id']
        case_name = request.form['case_name']
        investigator = request.form['investigator']
        evidence = request.form['evidence']
        description = request.form['description']
        status = request.form['status']
        location = request.form['location']
        user_id = session['user_id']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cases (case_id, case_name, investigator, evidence, description, status, location, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (case_id, case_name, investigator, evidence, description, status, location, user_id))
        conn.commit()
        conn.close()

        flash('Case added successfully.')
        return redirect('/dashboard')

    return render_template('add_case.html')

@app.route('/cases')
def view_cases():
    if 'user_id' not in session:
        return redirect('/login')

    selected_location = request.args.get('location')

    conn = get_connection()
    cursor = conn.cursor()

    if selected_location:
        cursor.execute("""
            SELECT id, case_id, case_name, investigator, status, location
            FROM cases
            WHERE user_id = ? AND location = ?
        """, (session['user_id'], selected_location))
    else:
        cursor.execute("""
            SELECT id, case_id, case_name, investigator, status, location
            FROM cases
            WHERE user_id = ?
        """, (session['user_id'],))

    cases = cursor.fetchall()

    cursor.execute("SELECT DISTINCT location FROM cases WHERE user_id = ?", (session['user_id'],))
    locations = [row[0] for row in cursor.fetchall()]

    conn.close()

    return render_template('cases.html', cases=cases, locations=locations, selected_location=selected_location)

@app.route('/cases/location/<location>')
def view_cases_by_location(location):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, case_id, case_name, investigator, status, location
        FROM cases
        WHERE user_id = ? AND location = ?""",
        (session['user_id'], location))
    cases = cursor.fetchall()
    conn.close()

    return render_template('cases.html', cases=cases, selected_location=location, locations=[location])

@app.route('/edit-case/<int:id>', methods=['GET', 'POST'])
def edit_case(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        case_id = request.form['case_id']
        case_name = request.form['case_name']
        investigator = request.form['investigator']
        evidence = request.form['evidence']
        description = request.form['description']
        status = request.form['status']
        location = request.form['location']

        cursor.execute("""
            UPDATE cases SET
                case_id = ?, case_name = ?, investigator = ?,
                evidence = ?, description = ?, status = ?, location = ?
            WHERE id = ? AND user_id = ?
        """, (case_id, case_name, investigator, evidence, description, status, location, id, session['user_id']))
        conn.commit()
        conn.close()
        flash('Case updated.')
        return redirect('/cases')

    cursor.execute("SELECT * FROM cases WHERE id = ? AND user_id = ?", (id, session['user_id']))
    case = cursor.fetchone()
    conn.close()
    return render_template('edit_case.html', case=case)

@app.route('/delete-case/<int:id>')
def delete_case(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cases WHERE id = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Case deleted.')
    return redirect('/cases')

if __name__ == '__main__':
    app.run(debug=True)