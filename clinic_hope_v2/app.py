from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
import sqlite3
import hashlib
import os
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "cle_secrete_super_securisee"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ton_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'ton_mot_de_passe_application'
app.config['MAIL_DEFAULT_SENDER'] = 'ton_email@gmail.com'
mail = Mail(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password, salt=None):
    if salt is None: salt = os.urandom(16).hex()
    pwd_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return salt, pwd_hash

def check_password_complexity(password):
    if len(password) < 8: return False, "8 caractères minimum."
    if not re.search(r"[a-z]", password): return False, "Manque une minuscule."
    if not re.search(r"[A-Z]", password): return False, "Manque une MAJUSCULE."
    if not re.search(r"\d", password): return False, "Manque un chiffre."
    return True, ""

def login_required(role_required=None):
    if 'user_id' not in session: return False
    if role_required and session.get('role') != role_required: return False
    return True

def clean_phone_for_whatsapp(phone):
    if not phone: return ""
    return re.sub(r'\D', '', phone)

app.jinja_env.globals.update(clean_phone=clean_phone_for_whatsapp)

HORAIRES_BASE = ["09:00","09:30","10:00","10:30","11:00","11:30",
                "14:00","14:30","15:00","15:30","16:00","16:30","17:00"]

# ── PAGE D'ACCUEIL ──
@app.route('/')
def home():
    if 'user_id' in session:
        role = session['role']
        if role == 'superadmin': return redirect(url_for('super_admin'))
        if role == 'admin': return redirect(url_for('dashboard'))
        if role == 'patient': return redirect(url_for('patient_home'))
    return render_template('index.html')

# ── LOGOUT ──
@app.route('/logout')
def logout():
    session.clear()
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('home'))

# ══════════════════════════════════════════
# CONNEXIONS SÉPARÉES PAR RÔLE
# ══════════════════════════════════════════

@app.route('/login/patient', methods=['GET', 'POST'])
def login_patient():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND role = ?', (email, 'patient')).fetchone()
        conn.close()
        if user:
            _, check = hash_password(password, user['salt'])
            if check == user['hash']:
                session['user_id'] = user['id']
                session['role'] = user['role']
                session['nom'] = user['nom']
                session['email'] = user['email']
                return redirect(url_for('patient_home'))
        flash('Email ou mot de passe incorrect.', 'danger')
    return render_template('login_patient.html')

@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND role = ?', (email, 'admin')).fetchone()
        conn.close()
        if user:
            _, check = hash_password(password, user['salt'])
            if check == user['hash']:
                session['user_id'] = user['id']
                session['role'] = user['role']
                session['nom'] = user['nom']
                session['email'] = user['email']
                return redirect(url_for('dashboard'))
        flash('Email ou mot de passe incorrect.', 'danger')
    return render_template('login_admin.html')

@app.route('/login/superadmin', methods=['GET', 'POST'])
def login_superadmin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND role = ?', (email, 'superadmin')).fetchone()
        conn.close()
        if user:
            _, check = hash_password(password, user['salt'])
            if check == user['hash']:
                session['user_id'] = user['id']
                session['role'] = user['role']
                session['nom'] = user['nom']
                session['email'] = user['email']
                return redirect(url_for('super_admin'))
        flash('Accès refusé.', 'danger')
    return render_template('login_superadmin.html')

# Ancienne route /login → redirige vers choix
@app.route('/login')
def login():
    return redirect(url_for('home'))

# ── REGISTER ──
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        mdp = request.form['password']
        conn = get_db_connection()
        dossier = conn.execute("SELECT * FROM patients WHERE email = ?", (email,)).fetchone()
        if not dossier:
            flash("Aucun dossier trouvé pour cet email.", "danger")
        else:
            valid, msg = check_password_complexity(mdp)
            if not valid:
                flash(msg, 'danger')
            else:
                try:
                    salt, h_pwd = hash_password(mdp)
                    conn.execute("INSERT INTO users (email, salt, hash, role, nom, prenom, adresse, telephone) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (email, salt, h_pwd, 'patient', dossier['nom'], dossier['prenom'], dossier['adresse'], dossier['telephone']))
                    conn.commit()
                    flash("Compte activé ! Connectez-vous.", "success")
                    return redirect(url_for('login_patient'))
                except sqlite3.IntegrityError:
                    flash("Compte déjà activé.", "warning")
        conn.close()
    return render_template('register.html')

# ══════════════════════════════════════════
# SUPER ADMIN
# ══════════════════════════════════════════
@app.route('/super_admin', methods=['GET', 'POST'])
def super_admin():
    if not login_required('superadmin'): return redirect(url_for('login_superadmin'))
    conn = get_db_connection()
    if request.method == 'POST':
        try:
            nom = request.form['nom'].upper()
            prenom = request.form['prenom']
            email = request.form['email']
            tel = request.form['telephone']
            adresse = request.form['adresse']
            mdp = request.form['password']
            valid, msg = check_password_complexity(mdp)
            if not valid:
                flash(msg, 'danger')
            else:
                salt, h_pwd = hash_password(mdp)
                conn.execute("INSERT INTO users (email, salt, hash, role, nom, prenom, adresse, telephone) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (email, salt, h_pwd, 'admin', nom, prenom, adresse, tel))
                conn.commit()
                flash('Administrateur ajouté !', 'success')
        except sqlite3.IntegrityError:
            flash('Cet email existe déjà.', 'danger')
    admins = conn.execute("SELECT * FROM users WHERE role = 'admin'").fetchall()
    conn.close()
    return render_template('super_admin.html', admins=admins)

# ══════════════════════════════════════════
# ADMIN DASHBOARD
# ══════════════════════════════════════════
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not login_required('admin'): return redirect(url_for('login_admin'))
    conn = get_db_connection()
    if request.method == 'POST' and 'add_contact' in request.form:
        try:
            conn.execute(
                "INSERT INTO patients (categorie, nom, prenom, fonction, email, telephone, adresse, rdv) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (request.form['categorie'], request.form['nom'].upper(), request.form['prenom'],
                request.form['fonction'], request.form['email'], request.form['telephone'],
                request.form['adresse'], "")
            )
            conn.commit()
            flash('Contact ajouté avec succès.', 'success')
        except sqlite3.IntegrityError:
            flash('Un contact existe déjà avec cet email.', 'danger')
    search = request.args.get('search', '')
    if search:
        patients = conn.execute("SELECT * FROM patients WHERE nom LIKE ? OR email LIKE ? OR categorie LIKE ?",
                                (f'%{search}%', f'%{search}%', f'%{search}%')).fetchall()
    else:
        patients = conn.execute("SELECT * FROM patients").fetchall()
    conn.close()
    return render_template('dashboard.html', patients=patients)

@app.route('/edit_contact/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    if not login_required('admin'): return redirect(url_for('login_admin'))
    conn = get_db_connection()
    contact = conn.execute("SELECT * FROM patients WHERE id = ?", (id,)).fetchone()
    if request.method == 'POST':
        conn.execute("""UPDATE patients SET categorie=?, nom=?, prenom=?, fonction=?, telephone=?, adresse=?, rdv=? WHERE id=?""",
            (request.form['categorie'], request.form['nom'].upper(), request.form['prenom'],
            request.form['fonction'], request.form['telephone'], request.form['adresse'],
            request.form['rdv'], id))
        conn.commit()
        conn.close()
        flash("Informations modifiées.", "success")
        return redirect(url_for('dashboard'))
    conn.close()
    return render_template('edit_contact.html', contact=contact)

# ── ADMIN RDV ──
@app.route('/admin/rdv', methods=['GET', 'POST'])
def admin_rdv():
    if not login_required('admin'): return redirect(url_for('login_admin'))
    conn = get_db_connection()
    date_today = datetime.now().strftime('%Y-%m-%d')
    date_choisie = request.args.get('date', date_today)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'cancel_rdv':
            rdv_id = request.form.get('rdv_id')
            rdv = conn.execute("SELECT * FROM rendez_vous WHERE id = ?", (rdv_id,)).fetchone()
            if rdv:
                conn.execute("DELETE FROM rendez_vous WHERE id = ?", (rdv_id,))
                conn.execute("UPDATE patients SET rdv = '' WHERE email = ?", (rdv['email_patient'],))
                conn.commit()
                flash("Rendez-vous annulé.", "success")
        elif action == 'modify_rdv':
            rdv_id = request.form.get('rdv_id')
            new_date = request.form.get('new_date')
            new_heure = request.form.get('new_heure')
            rdv = conn.execute("SELECT * FROM rendez_vous WHERE id = ?", (rdv_id,)).fetchone()
            if rdv and new_date and new_heure:
                existing = conn.execute("SELECT id FROM rendez_vous WHERE date_rdv=? AND heure_rdv=? AND id!=?",
                                        (new_date, new_heure, rdv_id)).fetchone()
                if existing:
                    flash("Ce créneau est déjà occupé.", "danger")
                else:
                    conn.execute("UPDATE rendez_vous SET date_rdv=?, heure_rdv=? WHERE id=?", (new_date, new_heure, rdv_id))
                    conn.execute("UPDATE patients SET rdv=? WHERE email=?",
                                (f"{new_date} à {new_heure}", rdv['email_patient']))
                    conn.commit()
                    flash("Rendez-vous modifié.", "success")
        conn.close()
        return redirect(url_for('admin_rdv', date=date_choisie))

    rdvs_du_jour = conn.execute(
        "SELECT r.*, p.nom, p.prenom FROM rendez_vous r LEFT JOIN patients p ON r.email_patient = p.email WHERE r.date_rdv = ? ORDER BY r.heure_rdv",
        (date_choisie,)).fetchall()
    rdv_pris = {row['heure_rdv'] for row in rdvs_du_jour}
    creneaux = [{'heure': h, 'etat': 'occupe' if h in rdv_pris else 'libre'} for h in HORAIRES_BASE]
    tous_rdvs = conn.execute(
        "SELECT r.*, p.nom, p.prenom FROM rendez_vous r LEFT JOIN patients p ON r.email_patient = p.email WHERE r.date_rdv >= ? ORDER BY r.date_rdv, r.heure_rdv",
        (date_today,)).fetchall()
    conn.close()
    return render_template('admin_rdv.html', date_choisie=date_choisie, date_today=date_today,
        creneaux=creneaux, rdvs_du_jour=rdvs_du_jour, tous_rdvs=tous_rdvs, horaires_base=HORAIRES_BASE)

# ── SEND EMAIL ──
@app.route('/send_email/<email_patient>', methods=['GET', 'POST'])
def send_email_route(email_patient):
    if not login_required('admin'): return redirect(url_for('login_admin'))
    conn = get_db_connection()
    patient = conn.execute("SELECT * FROM patients WHERE email = ?", (email_patient,)).fetchone()
    conn.close()
    if request.method == 'POST':
        try:
            msg = Message(subject=request.form['subject'], recipients=[email_patient])
            msg.body = request.form['message']
            mail.send(msg)
            flash(f"Email envoyé à {patient['prenom']} !", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Erreur : {str(e)}", "danger")
    return render_template('send_email.html', patient=patient)

# ══════════════════════════════════════════
# PATIENT
# ══════════════════════════════════════════

# API JSON : créneaux disponibles pour une date
@app.route('/api/creneaux')
def api_creneaux():
    if not login_required('patient'): return jsonify([])
    date = request.args.get('date', '')
    if not date: return jsonify([])
    conn = get_db_connection()
    rdv_pris = conn.execute("SELECT heure_rdv FROM rendez_vous WHERE date_rdv = ?", (date,)).fetchall()
    email_patient = session['email']
    mon_rdv = conn.execute("SELECT heure_rdv FROM rendez_vous WHERE date_rdv = ? AND email_patient = ?",
                        (date, email_patient)).fetchone()
    conn.close()
    heures_prises = {row['heure_rdv'] for row in rdv_pris}
    result = []
    for h in HORAIRES_BASE:
        if h == (mon_rdv['heure_rdv'] if mon_rdv else None):
            result.append({'heure': h, 'etat': 'mon_rdv'})
        elif h in heures_prises:
            result.append({'heure': h, 'etat': 'occupe'})
        else:
            result.append({'heure': h, 'etat': 'libre'})
    return jsonify(result)

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if not login_required('patient'): return redirect(url_for('login_patient'))
    conn = get_db_connection()
    date_today = datetime.now().strftime('%Y-%m-%d')
    rdv_existant = conn.execute(
        "SELECT * FROM rendez_vous WHERE email_patient = ? ORDER BY date_rdv DESC LIMIT 1",
        (session['email'],)).fetchone()

    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'book_slot':
            date_finale = request.form.get('date_hidden', '')
            heure_finale = request.form.get('heure_hidden', '')
            email_patient = session['email']
            if rdv_existant:
                conn.execute("DELETE FROM rendez_vous WHERE email_patient = ?", (email_patient,))
            conn.execute("INSERT INTO rendez_vous (email_patient, date_rdv, heure_rdv) VALUES (?, ?, ?)",
                        (email_patient, date_finale, heure_finale))
            conn.execute("UPDATE patients SET rdv = ? WHERE email = ?",
                        (f"{date_finale} à {heure_finale}", email_patient))
            conn.commit()
            flash(f"✅ Rendez-vous confirmé : {date_finale} à {heure_finale}", "success")
            conn.close()
            return redirect(url_for('patient_home'))
        elif action == 'cancel_rdv':
            conn.execute("DELETE FROM rendez_vous WHERE email_patient = ?", (session['email'],))
            conn.execute("UPDATE patients SET rdv = '' WHERE email = ?", (session['email'],))
            conn.commit()
            flash("Rendez-vous annulé.", "info")
            conn.close()
            return redirect(url_for('patient_home'))

    conn.close()
    return render_template('appointment.html', date_today=date_today, rdv_existant=rdv_existant)

@app.route('/patient')
def patient_home():
    if not login_required('patient'): return redirect(url_for('login_patient'))
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    rdv = conn.execute("SELECT * FROM rendez_vous WHERE email_patient = ? ORDER BY date_rdv DESC LIMIT 1",
                    (user['email'],)).fetchone()
    conn.close()
    return render_template('patient.html', user=user, rdv=rdv)

@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session: return redirect(url_for('home'))
    conn = get_db_connection()
    if request.method == 'POST':
        user_id = session['user_id']
        conn.execute("UPDATE users SET adresse = ?, telephone = ? WHERE id = ?",
                    (request.form['adresse'], request.form['telephone'], user_id))
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user['role'] == 'patient':
            conn.execute("UPDATE patients SET telephone = ?, adresse = ? WHERE email = ?",
                        (request.form['telephone'], request.form['adresse'], user['email']))
        if request.form.get('password'):
            valid, msg = check_password_complexity(request.form['password'])
            if valid:
                salt, h_pwd = hash_password(request.form['password'])
                conn.execute("UPDATE users SET salt = ?, hash = ? WHERE id = ?", (salt, h_pwd, user_id))
        conn.commit()
        flash("Profil mis à jour.", "success")
        return redirect(url_for('home'))
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
