import sqlite3

# Connessione al database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Esegui l'update per promuovere l'utente a admin e approvarlo
c.execute("UPDATE utenti SET ruolo = 'admin', approvato = 1 WHERE username = 'Alvin_Olinksy'")
conn.commit()
conn.close()

print('✅ Utente Alvin_Olinksy promosso ad admin')
