import re
import tkinter as tk
from tkinter import messagebox

class Contact:
    def __init__(self, nom, prénom, email, telephone):
        if not isinstance(nom, str) or not nom.strip().upper():
            raise ValueError("Le nom doit être une chaîne non vide et majuscule.")
        self.nom = nom.strip().upper()

        if not isinstance(prénom, str) or not prénom.strip():
            raise ValueError("Le prénom doit être une chaîne non vide.")
        self.prénom = prénom.strip()

        email = email.strip()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Email invalide. Exemple : nom.prenom@gmail.com")
        self.email = email
        
        tel_pattern = r"^\+\d{1,3} \d{3} \d{3} \d{3}$"
        if not re.match(tel_pattern, telephone):
            raise ValueError("Numéro invalide. Format requis : +212 678 987 978")
        self.telephone = telephone

    def afficher(self):
        return f"Nom : {self.nom}\nPrénom : {self.prénom}\nEmail : {self.email}\nTéléphone : {self.telephone}"

class CarnetAdresses:
    def __init__(self):
        self.contacts = {}
        self.charger_contacts()

    def ajouter_contact(self, contact):
        self.contacts[contact.nom] = contact
        self.sauvegarder_contacts()

    def afficher_contacts(self):
        if not self.contacts:
            return "Aucun contact."
        result = ""
        for contact in self.contacts.values():
            result += "\n----------------\n" + contact.afficher()
        return result

    def rechercher_contact(self, valeur):
        valeur = valeur.lower().strip()
        if not valeur:
            return "Veuillez entrer un nom valide."
        for contact in self.contacts.values():
            if contact.nom.lower() == valeur:
                return contact.afficher()
        return "Contact introuvable."

    def sauvegarder_contacts(self):
        with open("contacts.csv", "w") as f:
            f.write('nom,prenom,email,telephone\n')
            for contact in self.contacts.values():
                f.write(f"{contact.nom},{contact.prénom},{contact.email},{contact.telephone}\n")

    def supprimer_contact(self, valeur):
        valeur = valeur.lower().strip()
        if not valeur:
            return False
        for key, contact in list(self.contacts.items()):
            if contact.nom.lower() == valeur:
                del self.contacts[key]
                self.sauvegarder_contacts()
                return True
        return False  

    def charger_contacts(self):
        try:
            with open("contacts.csv", "r") as f:
                lines = f.readlines()
                if lines and lines[0].strip() == 'nom,prenom,email,telephone':
                    lines = lines[1:]
                for ligne in lines:
                    parts = ligne.strip().split(",")
                    if len(parts) == 4:
                        nom, prénom, email, tel = parts
                        try:
                            self.contacts[nom] = Contact(nom, prénom, email, tel)
                        except ValueError as e:
                            messagebox.showerror("Erreur", f"Erreur lors du chargement du contact {nom} : {str(e)}")
        except FileNotFoundError:
            pass

class Application:
    def __init__(self, root, carnet):
        self.root = root
        self.carnet = carnet
        self.root.title("Carnet d'Adresses")
        self.root.geometry("500x400")

        self.text_affichage = tk.Text(root, height=15, width=60)
        self.text_affichage.pack(pady=10)

        tk.Button(root, text="Ajouter Contact", command=self.ajouter_contact).pack(side=tk.LEFT, padx=10)
        tk.Button(root, text="Afficher Contacts", command=self.afficher_contacts).pack(side=tk.LEFT, padx=10)
        tk.Button(root, text="Rechercher Contact", command=self.rechercher_contact).pack(side=tk.LEFT, padx=10)
        tk.Button(root, text="Supprimer Contact", command=self.supprimer_contact).pack(side=tk.LEFT, padx=10)
        tk.Button(root, text="Quitter", command=self.quitter).pack(side=tk.RIGHT, padx=10)

        self.afficher_contacts()

    def ajouter_contact(self):
        fenetre_ajout = tk.Toplevel(self.root)
        fenetre_ajout.title("Ajouter un Contact")
        fenetre_ajout.geometry("300x250")

        tk.Label(fenetre_ajout, text="Nom :").pack()
        entry_nom = tk.Entry(fenetre_ajout)
        entry_nom.pack()

        tk.Label(fenetre_ajout, text="Prénom :").pack()
        entry_prénom = tk.Entry(fenetre_ajout)
        entry_prénom.pack()

        tk.Label(fenetre_ajout, text="Email :").pack()
        entry_email = tk.Entry(fenetre_ajout)
        entry_email.pack()

        tk.Label(fenetre_ajout, text="Téléphone :").pack()
        entry_tel = tk.Entry(fenetre_ajout)
        entry_tel.pack()

        def valider():
            nom = entry_nom.get().strip()
            prénom = entry_prénom.get().strip()
            email = entry_email.get().strip()
            tel = entry_tel.get().strip()
            if not nom or not prénom or not email or not tel:
                messagebox.showerror("Erreur", "Tous les champs sont requis.")
                return
            try:
                contact = Contact(nom, prénom, email, tel)
                self.carnet.ajouter_contact(contact)
                messagebox.showinfo("Succès", "Contact ajouté.")
                fenetre_ajout.destroy()
                self.afficher_contacts()
            except ValueError as e:
                messagebox.showerror("Erreur", str(e))

        tk.Button(fenetre_ajout, text="Ajouter", command=valider).pack(pady=10)

    def afficher_contacts(self):
        self.text_affichage.delete(1.0, tk.END)
        self.text_affichage.insert(tk.END, self.carnet.afficher_contacts())

    def rechercher_contact(self):
        fenetre_recherche = tk.Toplevel(self.root)
        fenetre_recherche.title("Rechercher un Contact")
        fenetre_recherche.geometry("300x150")

        tk.Label(fenetre_recherche, text="Nom à rechercher :").pack()
        entry_nom = tk.Entry(fenetre_recherche)
        entry_nom.pack()

        def rechercher():
            nom = entry_nom.get()
            result = self.carnet.rechercher_contact(nom)
            self.text_affichage.delete(1.0, tk.END)
            self.text_affichage.insert(tk.END, result)
            fenetre_recherche.destroy()

        tk.Button(fenetre_recherche, text="Rechercher", command=rechercher).pack(pady=10)

    def supprimer_contact(self):
        fenetre_suppr = tk.Toplevel(self.root)
        fenetre_suppr.title("Supprimer un Contact")
        fenetre_suppr.geometry("300x150")

        tk.Label(fenetre_suppr, text="Nom du contact à supprimer :").pack()
        entry_nom = tk.Entry(fenetre_suppr)
        entry_nom.pack()

        def supprimer():
            nom = entry_nom.get()
            if self.carnet.supprimer_contact(nom):
                messagebox.showinfo("Succès", "Contact supprimé.")
                self.afficher_contacts()
            else:
                messagebox.showerror("Erreur", "Contact introuvable.")
            fenetre_suppr.destroy()

        tk.Button(fenetre_suppr, text="Supprimer", command=supprimer).pack(pady=10)

    def quitter(self):
        self.carnet.sauvegarder_contacts()
        self.root.quit()

carnet = CarnetAdresses()
root = tk.Tk()
app = Application(root, carnet)
root.mainloop()