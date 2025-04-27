import sqlite3

# Collegamento al database esistente
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Inserimento di soggetti di prova
soggetti = [
    ('Mario', 'Rossi', '1990-05-15', '', 'Sospettato di traffico illecito.'),
    ('Luca', 'Bianchi', '1985-11-23', '', 'Membro di una banda organizzata.'),
    ('Giulia', 'Verdi', '1993-02-09', '', 'Possibili collegamenti con il crimine organizzato.'),
    ('Anna', 'Neri', '1997-08-30', '', 'Sospettata di furti seriali.'),
    ('Marco', 'Gialli', '1988-04-18', '', 'Associato a traffici internazionali.')
]

# Inserimento multiplo nel database
c.executemany('''
    INSERT INTO soggetti (nome, cognome, data_nascita, immagine, note)
    VALUES (?, ?, ?, ?, ?)
''', soggetti)

# Salvataggio delle modifiche e chiusura
conn.commit()
conn.close()

print("Soggetti inseriti con successo!")
