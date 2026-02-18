import sqlite3
import hashlib
import os

def hash_password(password):
    salt = os.urandom(16).hex()
    pwd_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return salt, pwd_hash

connection = sqlite3.connect('database.db')

with connection:
    # Table Users (Connexion)
    connection.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL,
            hash TEXT NOT NULL,
            role TEXT NOT NULL,
            nom TEXT,
            prenom TEXT,
            adresse TEXT,
            telephone TEXT
        )
    ''')

    # Table Patients/Contacts (Infos Dossier)
    connection.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categorie TEXT, 
            nom TEXT,
            prenom TEXT,
            fonction TEXT,
            email TEXT UNIQUE NOT NULL,
            telephone TEXT,
            adresse TEXT,
            rdv TEXT -- On garde ça pour l'affichage simple, mais on utilise la table rendez_vous pour la logique
        )
    ''')

    # NOUVELLE TABLE : Rendez-vous précis
    connection.execute('''
        CREATE TABLE IF NOT EXISTS rendez_vous (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_patient TEXT NOT NULL,
            date_rdv TEXT NOT NULL,  -- YYYY-MM-DD
            heure_rdv TEXT NOT NULL  -- HH:MM
        )
    ''')

    # Création Admin par défaut (si pas déjà là)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", ("admin@hope.com",))
    if not cursor.fetchone():
        salt, pwd_hash = hash_password("Admin@123")
        connection.execute(
            "INSERT INTO users (email, salt, hash, role, nom, prenom, adresse, telephone) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("admin@hope.com", salt, pwd_hash, "superadmin", "DIRECTEUR", "General", "Bureau Direction", "+00 000 000 000")
        )

print("✅ Base de données mise à jour avec la table 'rendez_vous'.")
connection.close()