# app.py aggiornato
from flask import Flask, render_template, request, redirect, url_for, session, make_response
import sqlite3
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pdfkit
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

def create_tables():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS utenti (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, data_registrazione TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS soggetti (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cognome TEXT, data_nascita TEXT, citta TEXT, telefono TEXT, gang TEXT, reati TEXT, immagine TEXT, data_registrazione TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS veicoli (id INTEGER PRIMARY KEY AUTOINCREMENT, proprietario TEXT, modello TEXT, targa TEXT, note TEXT)''')
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
        c.execute('SELECT password FROM utenti WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()

        if result and check_password_hash(result[0], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login_error.html')

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
            c.execute('INSERT INTO utenti (username, password, data_registrazione) VALUES (?, ?, ?)', (username, hashed_password, data_registrazione))
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
    conn.close()
    return render_template('dashboard.html', totale_soggetti=totale_soggetti)

# 🔥 Ricerca soggetti con FILTRI AVANZATI
@app.route('/search', methods=['GET'])
@login_required
def search():
    nome = request.args.get('nome', '')
    cognome = request.args.get('cognome', '')
    citta = request.args.get('citta', '')
    gang = request.args.get('gang', '')
    reati = request.args.get('reati', '')
    risultati = []

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    query = "SELECT id, nome, cognome, data_nascita, citta, telefono, gang, reati, immagine FROM soggetti WHERE 1=1"
    params = []

    if nome:
        query += " AND nome LIKE ?"
        params.append(f"%{nome}%")
    if cognome:
        query += " AND cognome LIKE ?"
        params.append(f"%{cognome}%")
    if citta:
        query += " AND citta LIKE ?"
        params.append(f"%{citta}%")
    if gang:
        query += " AND gang LIKE ?"
        params.append(f"%{gang}%")
    if reati:
        query += " AND reati LIKE ?"
        params.append(f"%{reati}%")

    c.execute(query, params)
    risultati = c.fetchall()
    conn.close()

    richiesta_ricerca = any([nome, cognome, citta, gang, reati])

    return render_template('search.html', risultati=risultati, richiesta_ricerca=richiesta_ricerca)

# 🔥 Aggiungi nuovo soggetto
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        nome = request.form['nome']
        cognome = request.form['cognome']
        data_nascita = request.form['data_nascita']
        citta = request.form['citta']
        telefono = request.form['telefono']
        gang = request.form['gang']
        reati = request.form['reati']
        data_registrazione = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        foto = request.files['foto']
        filename = ''

        if foto and foto.filename != '':
            if allowed_file(foto.filename):
                filename = secure_filename(foto.filename)
                foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                return render_template('upload_error.html')

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('''
            INSERT INTO soggetti (nome, cognome, data_nascita, citta, telefono, gang, reati, immagine, data_registrazione)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, cognome, data_nascita, citta, telefono, gang, reati, filename, data_registrazione))

        conn.commit()
        conn.close()

        return redirect(url_for('search'))

    return render_template('add.html')

# 🔥 Ricerca veicoli
@app.route('/search_vehicle', methods=['GET'])
@login_required
def search_vehicle():
    proprietario = request.args.get('proprietario', '')
    modello = request.args.get('modello', '')
    targa = request.args.get('targa', '')
    note = request.args.get('note', '')
    risultati = []

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    query = "SELECT id, proprietario, modello, targa, note FROM veicoli WHERE 1=1"
    params = []

    if proprietario:
        query += " AND proprietario LIKE ?"
        params.append(f"%{proprietario}%")
    if modello:
        query += " AND modello LIKE ?"
        params.append(f"%{modello}%")
    if targa:
        query += " AND targa LIKE ?"
        params.append(f"%{targa}%")
    if note:
        query += " AND note LIKE ?"
        params.append(f"%{note}%")

    c.execute(query, params)
    risultati = c.fetchall()
    conn.close()

    return render_template('search_vehicle.html', risultati=risultati, proprietario=proprietario, modello=modello, targa=targa, note=note)

# 🔥 Aggiungi veicolo
@app.route('/add_vehicle', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    if request.method == 'POST':
        proprietario = request.form['proprietario']
        modello = request.form['modello']
        targa = request.form['targa']
        note = request.form['note']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO veicoli (proprietario, modello, targa, note) VALUES (?, ?, ?, ?)', (proprietario, modello, targa, note))
        conn.commit()
        conn.close()

        return redirect(url_for('search_vehicle'))

    return render_template('add_vehicle.html')

# 🔥 Modifica veicolo
@app.route('/edit_vehicle/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        proprietario = request.form['proprietario']
        modello = request.form['modello']
        targa = request.form['targa']
        note = request.form['note']

        c.execute('''
            UPDATE veicoli
            SET proprietario=?, modello=?, targa=?, note=?
            WHERE id=?
        ''', (proprietario, modello, targa, note, id))
        conn.commit()
        conn.close()

        return redirect(url_for('search_vehicle'))

    c.execute('SELECT proprietario, modello, targa, note FROM veicoli WHERE id=?', (id,))
    veicolo = c.fetchone()
    conn.close()

    if veicolo:
        return render_template('edit_vehicle.html', veicolo=veicolo, id=id)
    else:
        return "Veicolo non trovato.", 404

# 🔥 Elimina veicolo
@app.route('/delete_vehicle/<int:id>')
@login_required
def delete_vehicle(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM veicoli WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('search_vehicle'))

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
