import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import Calendar
import sqlite3
from datetime import datetime

class ApplicationRDV:
    def __init__(self, root):
        self.root = root
        self.root.title("🏥 Gestion des RDV - Clinic Hope")
        self.root.geometry("900x600")
        self.root.config(bg="#f0f2f5")

        # --- Base de données ---
        self.db_name = 'database.db'

        # --- TITRE ---
        lbl_title = tk.Label(root, text="📅 Prise de Rendez-vous", font=("Arial", 24, "bold"), bg="#f0f2f5", fg="#007cc3")
        lbl_title.pack(pady=20)

        # --- CONTENEUR PRINCIPAL ---
        main_frame = tk.Frame(root, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=20)

        # === GAUCHE : CALENDRIER ===
        left_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove")
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(left_frame, text="1. Choisissez une date", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        # Widget Calendrier
        today = datetime.now()
        self.cal = Calendar(left_frame, selectmode='day', 
                            year=today.year, month=today.month, day=today.day,
                            date_pattern='yyyy-mm-dd',
                            background='#007cc3', foreground='white', headersbackground='#005f96')
        self.cal.pack(padx=20, pady=20)
        
        # Bouton pour valider la date
        btn_refresh = tk.Button(left_frame, text="Voir les créneaux", command=self.charger_creneaux, 
                                bg="#00bfa5", fg="white", font=("Arial", 12, "bold"), width=20)
        btn_refresh.pack(pady=10)

        # === DROITE : CRÉNEAUX HORAIRES ===
        self.right_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.lbl_date_selected = tk.Label(self.right_frame, text="Aucune date sélectionnée", 
                                          font=("Arial", 16, "bold"), bg="white", fg="#333")
        self.lbl_date_selected.pack(pady=15)

        # Zone pour les boutons des heures (Grille)
        self.slots_frame = tk.Frame(self.right_frame, bg="white")
        self.slots_frame.pack(pady=10)

        # Liste des heures (08:00 à 17:30, par pas de 30 min)
        self.heures = [f"{h:02d}:{m:02d}" for h in range(8, 18) for m in (0, 30)]

    def get_rdv_pris(self, date_choisie):
        """Récupère la liste des heures déjà réservées pour une date"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT heure FROM rendez_vous WHERE date = ?", (date_choisie,))
        pris = [row[0] for row in cursor.fetchall()]
        conn.close()
        return pris

    def reserver(self, heure, date_choisie):
        """Fonction appelée quand on clique sur une heure libre"""
        # Demander le nom du patient
        nom = simpledialog.askstring("Réservation", f"Réserver le créneau de {heure} ?\n\nEntrez le Nom du Patient :")
        
        if nom:
            conn = sqlite3.connect(self.db_name)
            try:
                conn.execute("INSERT INTO rendez_vous (date, heure, nom_patient, motif) VALUES (?, ?, ?, ?)",
                             (date_choisie, heure, nom, "Consultation"))
                conn.commit()
                messagebox.showinfo("Succès", f"✅ RDV confirmé pour {nom} à {heure} !")
                self.charger_creneaux() # Recharger pour mettre le bouton en rouge
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
            finally:
                conn.close()

    def charger_creneaux(self):
        """Affiche les boutons d'heures en fonction de la date"""
        date_choisie = self.cal.get_date()
        self.lbl_date_selected.config(text=f"Horaires pour le : {date_choisie}")

        # Nettoyer les anciens boutons
        for widget in self.slots_frame.winfo_children():
            widget.destroy()

        # Récupérer les heures déjà prises en BDD
        heures_prises = self.get_rdv_pris(date_choisie)

        # Création de la grille de boutons
        row = 0
        col = 0
        for heure in self.heures:
            etat = "normal"
            couleur = "#e3f2fd" # Bleu clair (Libre)
            texte = heure
            cmd = lambda h=heure, d=date_choisie: self.reserver(h, d)

            # Si l'heure est prise
            if heure in heures_prises:
                etat = "disabled"
                couleur = "#ffcdd2" # Rouge clair (Occupé)
                texte = f"{heure}\n(Pris)"
                cmd = None

            btn = tk.Button(self.slots_frame, text=texte, state=etat, command=cmd,
                            bg=couleur, font=("Arial", 10), width=12, height=2)
            
            btn.grid(row=row, column=col, padx=5, pady=5)

            # Gestion de l'affichage en grille (4 colonnes)
            col += 1
            if col > 3:
                col = 0
                row += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationRDV(root)
    root.mainloop()