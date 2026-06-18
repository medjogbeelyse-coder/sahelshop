import os
import requests
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "prime_business_2026_key")

# --- 1. CONFIGURATION DE LA BASE ---
uri = os.environ.get("DATABASE_URL", "sqlite:///prime_business.db")

# Sécurité supplémentaire : si l'URL commence par postgres:// (sans le ql), on corrige
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 2. MODÈLES ---
class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(100), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    section = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(255))
    cloudinary_id = db.Column(db.String(100))

class Poste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)

class FeatureFlag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)

# --- 3. CONFIGURATION CLOUDINARY SÉCURISÉE ---
cloudinary.config( 
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME", "ds5exviel"), 
  api_key = os.environ.get("CLOUDINARY_API_KEY", "128277898241178"), 
  api_secret = os.environ.get("CLOUDINARY_API_SECRET") # Va lire le secret de manière sécurisée sans l'afficher
)

# --- 4. INJECTION DES FLAGS ---
@app.context_processor
def inject_flags():
    try:
        flags = {f.key: f.active for f in FeatureFlag.query.all()}
        return {'flags': flags}
    except:
        return {'flags': {'commerce': True, 'investissement': True, 'recrutement': True}}

# --- 5. INITIALISATION DES TABLES ---
with app.app_context():
    try:
        db.create_all()
        if not FeatureFlag.query.first():
            for k in ["commerce", "investissement", "recrutement"]:
                db.session.add(FeatureFlag(key=k, active=True))
            db.session.commit()
    except Exception as e:
        print(f"⚠️ Erreur DB: {e}")

# --- ROUTES ---

@app.route("/")
def presentation():
    return render_template("presentation.html")

@app.route("/accueil")
def home():
    return render_template("index.html")

@app.route("/section/<name>")
def view_section(name):
    try:
        flag = FeatureFlag.query.filter_by(key=name).first()
        if flag and flag.active:
            if name == "investissement":
                return render_template("section_investissement.html")
            if name == "recrutement":
                postes_list = Poste.query.all()
                return render_template("section_recrutement.html", postes=postes_list)
            
            prods = Produit.query.all()
            return render_template("section.html", name=name, produits=prods)
    except:
        pass
    return redirect(url_for('home'))


# --- API COMMANDE BOUTIQUE VERS TELEGRAM ---
@app.route("/passer-commande", methods=["POST"])
def passer_commande():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Données invalides"}), 400

    nom = data.get("nom")
    email = data.get("email", "Non renseigné")  # Récupération de l'email (facultatif)
    pays = data.get("pays")
    ville = data.get("ville")
    telephone = data.get("telephone")
    telephone2 = data.get("telephone2", "Non renseigné")
    total_marchandise = data.get("total_marchandise", 0)
    panier = data.get("panier", [])

    if not all([nom, pays, ville, telephone, panier]):
        return jsonify({"success": False, "message": "Informations de livraison incomplètes"}), 400

    # Formatage de la liste des produits du panier en HTML pour Telegram
    texte_panier = ""
    total_financier = 0
    for item in panier:
        sous_total = item['price'] * item['quantity']
        total_financier += sous_total
        texte_panier += f"• <b>{item['name']}</b> (x{item['quantity']}) — {sous_total:,} F\n"

    # Construction du message structuré
    message_telegram = (
        f"📦 <b>NOUVELLE COMMANDE REÇUE !</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Client :</b> {nom}\n"
        f"📧 <b>E-mail :</b> {email}\n"
        f"🌍 <b>Destination :</b> {pays} ({ville})\n"
        f"📞 <b>Tél 1 :</b> {telephone}\n"
        f"📱 <b>Tél 2 :</b> {telephone2}\n\n"
        f"🛒 <b>Détails des articles :</b>\n{texte_panier}\n"
        f"🔢 <b>Nombre total d'articles :</b> {total_marchandise}\n"
        f"💵 <b>TOTAL À PERCEVOIR : {total_financier:,} F</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if bot_token and chat_id:
        url_telegram = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message_telegram,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url_telegram, json=payload)
            if response.status_code == 200:
                return jsonify({"success": True})
            else:
                return jsonify({"success": False, "message": "Échec de l'envoi de la notification Telegram"}), 500
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    else:
        return jsonify({"success": False, "message": "Configuration Telegram manquante sur le serveur"}), 500


# --- API INVESTISSEMENT VERS TELEGRAM ---
@app.route("/api/investissement", methods=["POST"])
def api_investissement():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Données invalides"}), 400

    nom = data.get("nom", "Non spécifié")
    pays = data.get("pays", "Non spécifié")
    ville = data.get("ville", "Non spécifié")
    tel = data.get("tel", "Non spécifié")
    montant = data.get("montant", "Non spécifié")

    # Message formaté proprement pour Telegram
    message_telegram = (
        "📈 *Nouvelle Demande d'Investissement* 📈\n\n"
        f"👤 *Nom :* {nom}\n"
        f"🌍 *Pays :* {pays}\n"
        f"🏙️ *Ville :* {ville}\n"
        f"📞 *Téléphone :* {tel}\n"
        f"💰 *Montant :* {montant} FCFA\n"
    )

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if bot_token and chat_id:
        url_telegram = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message_telegram,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url_telegram, json=payload)
            if response.status_code == 200:
                return jsonify({"status": "success", "message": "Notification envoyée"})
            else:
                return jsonify({"status": "error", "message": "Échec de l'API Telegram"}), 500
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Configuration Telegram manquante"}), 500


# --- API RECRUTEMENT VERS TELEGRAM ---
@app.route("/soumettre-candidature", methods=["POST"])
def soumettre_candidature():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Données invalides"}), 400

    nom = data.get("nom")
    annee = data.get("annee")
    nat = data.get("nat")
    poste = data.get("poste")

    if not all([nom, annee, nat, poste]):
        return jsonify({"status": "error", "message": "Champs obligatoires manquants"}), 400

    # Formatage structuré de la fiche de candidature
    message_telegram = (
        f"🏛 *RÉSEAU MEDJOGBE | Nouvelle Candidature*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 *Nom & Prénom :* {nom}\n"
        f"📅 *Année de Naissance :* {annee}\n"
        f"🌍 *Nationalité :* {nat}\n"
        f"💼 *Poste Souhaité :* {poste}\n\n"
        f"⚖️ _Dossier enregistré via le portail web._\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if bot_token and chat_id:
        url_telegram = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message_telegram,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url_telegram, json=payload)
            if response.status_code == 200:
                return jsonify({"status": "success"})
            else:
                return jsonify({"status": "error", "message": "Échec de l'envoi de la candidature à Telegram"}), 500
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Configuration Telegram manquante sur le serveur"}), 500


# --- ROUTES D'ADMINISTRATION RE-SÉCURISÉES ---

@app.route("/MEDJOGBE11", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == os.environ.get("ADMIN_PWD", "Azouassi@11"): 
            session["admin_logged_in"] = True
            return redirect(url_for("admin_panel"))
        flash("Mot de passe incorrect")
    return render_template("admin_login.html")

@app.route("/MEDJOGBE11/panel", methods=["GET", "POST"])
def admin_panel():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    try:
        if request.method == "POST":
            if "flag_key" in request.form:
                f = FeatureFlag.query.filter_by(key=request.form.get("flag_key")).first()
                if f:
                    f.active = not f.active
                    db.session.commit()
            
            elif "designation" in request.form:
                file = request.files.get('image_file')
                img_url, p_id = "", ""
                if file and file.filename != '':
                    res = cloudinary.uploader.upload(file)
                    img_url, p_id = res['secure_url'], res['public_id']
                
                new_p = Produit(designation=request.form.get("designation"), 
                                prix=float(request.form.get("price")),
                                section=request.form.get("category"), 
                                image=img_url, cloudinary_id=p_id)
                db.session.add(new_p)
                db.session.commit()

            elif "delete_id" in request.form:
                p = Produit.query.get(int(request.form.get("delete_id")))
                if p:
                    if p.cloudinary_id: cloudinary.uploader.destroy(p.cloudinary_id)
                    db.session.delete(p)
                    db.session.commit()

            elif "titre_poste" in request.form:
                db.session.add(Poste(titre=request.form.get("titre_poste")))
                db.session.commit()

            elif "delete_poste_id" in request.form:
                po = Poste.query.get(int(request.form.get("delete_poste_id")))
                if po:
                    db.session.delete(po)
                    db.session.commit()

            return redirect(url_for("admin_panel"))

        return render_template("admin_panel.html", 
                               flags={f.key: f.active for f in FeatureFlag.query.all()}, 
                               produits=Produit.query.all(), 
                               postes=Poste.query.all())
    except Exception as e:
        return f"Erreur: {str(e)}"

@app.route("/MEDJOGBE11/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)