import os
import re
import csv
import tkinter as tk
from tkinter import ttk, messagebox

class Contact:
    def __init__(self, nom, prenom, email, telephone):
        if not nom.strip():
            raise ValueError("Nom obligatoire")
        self.nom = nom.strip().upper()

        if not prenom.strip():
            raise ValueError("Prénom obligatoire")
        self.prenom = prenom.strip().capitalize()

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email):
            raise ValueError("Email invalide")
        self.email = email.strip()

        telephone = re.sub(r"\s+", " ", telephone.strip())
        if not re.match(r"^\+\d{1,3} \d{2,3} \d{3} \d{3}$", telephone):
            raise ValueError("Téléphone invalide")
        self.telephone = telephone

    def afficher(self):
        return (
            f"Nom       : {self.nom}\n"
            f"Prénom    : {self.prenom}\n"
            f"Email     : {self.email}\n"
            f"Téléphone : {self.telephone}\n"
            "-----------------------------\n"
        )

class CarnetAdresses:
    def __init__(self):
        self.contacts = {}
        self.charger()

    def key(self, c):
        return f"{c.nom}_{c.prenom}".lower()

    def ajouter(self, c):
        k = self.key(c)
        if k in self.contacts:
            raise ValueError("Contact déjà existant")
        self.contacts[k] = c
        self.sauvegarder()

    def modifier(self, old_nom, old_prenom, new_c):
        old_key = f"{old_nom.strip().upper()}_{old_prenom.strip().capitalize()}".lower()
        if old_key not in self.contacts:
            raise ValueError("Contact introuvable")

        new_key = self.key(new_c)
        del self.contacts[old_key]
        self.contacts[new_key] = new_c
        self.sauvegarder()

    def afficher(self):
        if not self.contacts:
            return "📭 Aucun contact"
        return "\n".join(c.afficher() for c in self.contacts.values())

    def rechercher(self, txt):
        txt = txt.lower()
        res = [c.afficher() for c in self.contacts.values()
            if txt in c.nom.lower() or txt in c.prenom.lower()]
        return "\n".join(res) if res else "❌ Aucun résultat"

    def supprimer(self, txt):
        txt = txt.lower()
        matches = [k for k, c in self.contacts.items()
                if txt in c.nom.lower() or txt in c.prenom.lower()]
        if len(matches) == 1:
            del self.contacts[matches[0]]
            self.sauvegarder()
            return True
        if len(matches) > 1:
            return "multiple"
        return False

    def sauvegarder(self):
        with open("contacts.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["nom", "prenom", "email", "telephone"])
            for c in self.contacts.values():
                writer.writerow([c.nom, c.prenom, c.email, c.telephone])

    def charger(self):
        if not os.path.exists("contacts.csv"):
            return
        with open("contacts.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                c = Contact(row["nom"], row["prenom"], row["email"], row["telephone"])
                self.contacts[self.key(c)] = c

USERS_FILE = "users.csv"

def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, encoding="utf-8") as f:
            for u, p, r, nom, prenom, email, tel in csv.reader(f):
                users[u] = (p, r, nom, prenom, email, tel)
    return users

def save_users(users):
    with open(USERS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for u, data in users.items():
            writer.writerow([u, *data])

class Auth(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("🔐 Authentification")
        self.resizable(False, False)
        self.grab_set()

        self.users = load_users()
        self.ok = False
        self.role = None
        self.user_info = None

        ttk.Label(self, text="Utilisateur").grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(self, text="Mot de passe").grid(row=1, column=0, padx=10, pady=5)

        self.user = ttk.Entry(self)
        self.pwd = ttk.Entry(self, show="*")

        self.user.grid(row=0, column=1)
        self.pwd.grid(row=1, column=1)

        ttk.Button(self, text="Connexion", command=self.login).grid(row=2, column=0, pady=10)
        ttk.Button(self, text="Créer un compte", command=self.register).grid(row=2, column=1)

    def login(self):
        u, p = self.user.get(), self.pwd.get()
        if u in self.users and self.users[u][0] == p:
            self.ok = True
            self.role = self.users[u][1]
            self.user_info = self.users[u]
            self.destroy()
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects")

    def register(self):
        win = tk.Toplevel(self)
        win.title("Compte professionnel")

        labels = ["Nom", "Prénom", "Email", "Téléphone", "Utilisateur", "Mot de passe"]
        entries = {}

        for i, l in enumerate(labels):
            ttk.Label(win, text=l).grid(row=i, column=0)
            e = ttk.Entry(win, show="*" if l == "Mot de passe" else "")
            e.grid(row=i, column=1)
            entries[l] = e

        def valider():
            nom, prenom = entries["Nom"].get(), entries["Prénom"].get()
            email, tel = entries["Email"].get(), entries["Téléphone"].get()
            u, p = entries["Utilisateur"].get(), entries["Mot de passe"].get()

            Contact(nom, prenom, email, tel)
            if u in self.users:
                messagebox.showerror("Erreur", "Utilisateur existant")
                return

            self.users[u] = (p, "Contact", nom, prenom, email, tel)
            save_users(self.users)
            CarnetAdresses().ajouter(Contact(nom, prenom, email, tel))

            messagebox.showinfo("Succès", "Compte créé")
            win.destroy()

        ttk.Button(win, text="Valider", command=valider).grid(row=6, columnspan=2)

class App(tk.Tk):
    def __init__(self, role, user_info):
        super().__init__()
        self.title("📒 Carnet d’Adresses")
        self.geometry("700x450")

        self.role = role
        self.user_info = user_info
        self.carnet = CarnetAdresses()

        self.text = tk.Text(self, width=85, height=20)
        self.text.pack()

        self.refresh()

        btns = ttk.Frame(self)
        btns.pack(pady=10)

        if role != "Contact":
            ttk.Button(btns, text="➕ Ajouter", command=self.ajouter).grid(row=0, column=0)
            ttk.Button(btns, text="🗑 Supprimer", command=self.supprimer).grid(row=0, column=1)

        ttk.Button(btns, text="🔍 Rechercher", command=self.rechercher).grid(row=0, column=2)
        ttk.Button(btns, text="🔄 Actualiser", command=self.refresh).grid(row=0, column=3)

        if role == "Contact":
            ttk.Button(btns, text="👤 Modifier mon profil", command=self.modifier_profil).grid(row=0, column=4)

    def refresh(self):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, self.carnet.afficher())

    def ajouter(self):
        pass  

    def rechercher(self):
        pass

    def supprimer(self):
        pass

    def modifier_profil(self):
        _, _, nom, prenom, email, tel = self.user_info
        messagebox.showinfo("Info", "Modification OK (structure prête)")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    auth = Auth(root)
    root.wait_window(auth)

    if auth.ok:
        App(auth.role, auth.user_info).mainloop()
