import sqlite3

# Connessione al database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Crea la tabella 'utenti'
c.execute('''
CREATE TABLE IF NOT EXISTS utenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    data_registrazione TEXT NOT NULL
)
''')

# (Opzionale) Crea anche la tabella 'soggetti' se non l'hai già creata
c.execute('''
CREATE TABLE IF NOT EXISTS soggetti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    cognome TEXT,
    data_nascita TEXT,
    citta TEXT,
    telefono TEXT,
    gang TEXT,
    reati TEXT,
    immagine TEXT,
    data_registrazione TEXT
)
''')

conn.commit()
conn.close()

print("✅ Database e tabelle create correttamente!")
