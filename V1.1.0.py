import re
class Contact:
    def __init__(self, nom, email, telephone):
        if not isinstance(nom, str) or not nom.strip():
            raise ValueError("Le nom doit être une chaîne non vide.")
        self.nom = nom.strip()

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
        print("Nom :", self.nom)
        print("Email :", self.email)
        print("Téléphone :", self.telephone)

class CarnetAdresses:
    def __init__(self):
        self.contacts = {}
        self.charger_contacts()

    def ajouter_contact(self, contact):
        self.contacts[contact.nom] = contact
        print("Contact ajouté.")
        self.sauvegarder_contacts()

    def afficher_contacts(self):
        if not self.contacts:
            print("Aucun contact.")
        else:
            for contact in self.contacts.values():
                print("\n----------------")
                contact.afficher()

    def rechercher_contact(self, nom):
        contact = self.contacts.get(nom)
        if contact:
            contact.afficher()
        else:
            print("Contact introuvable.")
            
    def sauvegarder_contacts(self):
        with open("contacts.txt", "w") as f:
            f.write('nom,email,telephone\n')
            for contact in self.contacts.values():
                f.write(contact.nom + "," + contact.email + "," + contact.telephone + "\n")

    def supprimer_contact(self, nom):
        if nom in self.contacts:
            del self.contacts[nom]
            print("Contact supprimé.")
            self.sauvegarder_contacts()
        else:
            print("Contact introuvable.")

    def charger_contacts(self):
        try:
            with open("contacts.txt", "r") as f:
                for ligne in f:
                    parts = ligne.strip().split(",")
                    if len(parts) == 3:
                        nom, email, tel = parts
                        try:
                            self.contacts[nom] = Contact(nom, email, tel)
                        except ValueError:
                            print(f"Erreur lors du chargement du contact {nom} : données invalides.")
        except FileNotFoundError:
            pass

    def menu(self):
        while True:
            print("\n--- Carnet d'Adresses (POO) ---")
            print("1. Ajouter")
            print("2. Afficher")
            print("3. Rechercher")
            print("4. Supprimer")
            print("5. Quitter")

            choix = input("Votre choix : ")

            if choix == "1":
                nom = input("Nom : ")
                email = input("Email : ")
                tel = input("Téléphone : ")
                try:
                    self.ajouter_contact(Contact(nom, email, tel))
                except ValueError as e:
                    print(f"Erreur : {e}")

            elif choix == "2":
                self.afficher_contacts()

            elif choix == "3":
                nom = input("Nom à rechercher : ")
                self.rechercher_contact(nom)

            elif choix == "4":
                nom = input("Nom à supprimer : ")
                self.supprimer_contact(nom)

            elif choix == "5":
                self.sauvegarder_contacts()
                print("Fin du programme.")
                break

            else:
                print("Choix invalide.")

carnet = CarnetAdresses()
carnet.menu()