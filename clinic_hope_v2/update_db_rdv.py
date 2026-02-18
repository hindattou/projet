import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Création de la table rendez_vous
cursor.execute('''
    CREATE TABLE IF NOT EXISTS rendez_vous (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,       -- Format YYYY-MM-DD
        heure TEXT NOT NULL,      -- Format HH:MM
        nom_patient TEXT NOT NULL,
        motif TEXT
    )
''')

print("✅ Table 'rendez_vous' créée avec succès.")
conn.commit()
conn.close()