import sqlite3

# Connessione al database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Prendi tutti i soggetti
c.execute('SELECT * FROM soggetti')
soggetti = c.fetchall()

# Mostra tutti i soggetti
for soggetto in soggetti:
    print(soggetto)

conn.close()
