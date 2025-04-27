from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersegreto123'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or session.get('ruolo') != 'admin':
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def create_tables():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS utenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            data_registrazione TEXT,
            approvato INTEGER DEFAULT 0,
            ruolo TEXT DEFAULT 'user'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS soggetti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, cognome TEXT, data_nascita TEXT,
            citta TEXT, telefono TEXT, gang TEXT, reati TEXT, immagine TEXT, data_registrazione TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS veicoli (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proprietario TEXT, modello TEXT, targa TEXT, note TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_tables()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT password, approvato, ruolo FROM utenti WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()

        if result:
            db_password, approvato, ruolo = result
            if not approvato:
                return render_template('login_error.html', messaggio="Account non approvato. Attendi l'approvazione.")
            if check_password_hash(db_password, password):
                session['logged_in'] = True
                session['username'] = username
                session['ruolo'] = ruolo
                return redirect(url_for('dashboard'))

        return render_template('login_error.html', messaggio="Username o password errati.")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        data_registrazione = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO utenti (username, password, data_registrazione) VALUES (?, ?, ?)', 
                      (username, hashed_password, data_registrazione))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Errore: Username già esistente."

        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM soggetti')
    totale_soggetti = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM utenti WHERE approvato = 0')
    utenti_in_attesa = c.fetchone()[0]
    conn.close()
    return render_template('dashboard.html', totale_soggetti=totale_soggetti, utenti_in_attesa=utenti_in_attesa)

# 🛡️ GESTIONE UTENTI

@app.route('/manage_users')
@admin_required
def manage_users():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, username, data_registrazione, approvato, ruolo FROM utenti')
    utenti = c.fetchall()
    conn.close()
    return render_template('manage_users.html', utenti=utenti)

@app.route('/approve_user/<int:user_id>')
@admin_required
def approve_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE utenti SET approvato = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_users'))

@app.route('/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM utenti WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_users'))

@app.route('/promote_user/<int:user_id>')
@admin_required
def promote_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE utenti SET ruolo = "admin" WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_users'))

@app.route('/demote_user/<int:user_id>')
@admin_required
def demote_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE utenti SET ruolo = "user" WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_users'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
