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
        return f"""
Nom       : {self.nom}
Prénom    : {self.prenom}
Email     : {self.email}
Téléphone : {self.telephone}
"""

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
        try:
            with open("contacts.csv", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    c = Contact(row["nom"], row["prenom"], row["email"], row["telephone"])
                    self.contacts[self.key(c)] = c
        except FileNotFoundError:
            pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📒 Carnet d’Adresses")
        self.geometry("650x450")
        self.resizable(False, False)

        self.carnet = CarnetAdresses()
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        ttk.Label(
            self,
            text="Carnet d’Adresses",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=10)

        frame = ttk.Frame(self)
        frame.pack()

        self.text = tk.Text(frame, width=70, height=15, font=("Consolas", 10))
        self.text.pack(side=tk.LEFT)

        scrollbar = ttk.Scrollbar(frame, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)

        btns = ttk.Frame(self)
        btns.pack(pady=15)

        ttk.Button(btns, text="➕ Ajouter", command=self.ajouter).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="🔍 Rechercher", command=self.rechercher).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="🗑 Supprimer", command=self.supprimer).grid(row=0, column=2, padx=5)
        ttk.Button(btns, text="🔄 Actualiser", command=self.refresh).grid(row=0, column=3, padx=5)
        ttk.Button(btns, text="❌ Quitter", command=self.quit).grid(row=0, column=4, padx=5)

    def refresh(self):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, self.carnet.afficher())

    def popup(self, title, labels, action):
        win = tk.Toplevel(self)
        win.title(title)
        win.resizable(False, False)

        entries = {}
        for i, lab in enumerate(labels):
            ttk.Label(win, text=lab).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            e = ttk.Entry(win, width=30)
            e.grid(row=i, column=1, padx=10)
            entries[lab] = e

        def valider():
            action(entries)
            win.destroy()

        ttk.Button(win, text="Valider", command=valider).grid(
            row=len(labels), column=0, columnspan=2, pady=10
        )

    def ajouter(self):
        def action(e):
            try:
                c = Contact(
                    e["Nom"].get(),
                    e["Prénom"].get(),
                    e["Email"].get(),
                    e["Téléphone"].get()
                )
                self.carnet.ajouter(c)
                self.refresh()
                messagebox.showinfo("Succès", "Contact ajouté")
            except Exception as err:
                messagebox.showerror("Erreur", err)

        self.popup("➕ Ajouter un contact",
                   ["Nom", "Prénom", "Email", "Téléphone"],
                   action)

    def rechercher(self):
        def action(e):
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, self.carnet.rechercher(e["Recherche"].get()))

        self.popup("🔍 Rechercher", ["Recherche"], action)

    def supprimer(self):
        def action(e):
            confirm = messagebox.askyesno(
                "Confirmation",
                "Voulez-vous vraiment supprimer ce contact ?"
            )
            if not confirm:
                return

            res = self.carnet.supprimer(e["Nom / Prénom"].get())
            if res == True:
                self.refresh()
                messagebox.showinfo("Supprimé", "✅ Contact supprimé avec succès")
            elif res == "multiple":
                messagebox.showwarning("Attention", "⚠️ Plusieurs contacts trouvés")
            else:
                messagebox.showerror("Erreur", "❌ Contact introuvable")

        self.popup("🗑 Supprimer", ["Nom / Prénom"], action)


if __name__ == "__main__":
    app = App()
    app.mainloop()