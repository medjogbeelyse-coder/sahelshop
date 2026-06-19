import os
import requests
import cloudinary
import cloudinary.uploader
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv

load_dotenv()

# --- CLIENT VERCEL KV (API REST) ---
class VercelKVClient:
    def __init__(self):
        self.url = os.getenv("KV_REST_API_URL")
        self.token = os.getenv("KV_REST_API_TOKEN")

    def get(self, key):
        if not self.url or not self.token: return None
        try:
            res = requests.get(f"{self.url}/get/{key}", headers={"Authorization": f"Bearer {self.token}"})
            return res.json().get("result")
        except: return None

    def set(self, key, value):
        if not self.url or not self.token: return False
        try:
            requests.post(f"{self.url}/set/{key}", 
                          headers={"Authorization": f"Bearer {self.token}"}, 
                          data=json.dumps(value))
            return True
        except: return False

kv = VercelKVClient()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "prime_business_2026_vercel_key")

# --- CONFIGURATION CLOUDINARY ---
cloudinary.config( 
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME", "ds5exviel"), 
  api_key = os.environ.get("CLOUDINARY_API_KEY", "128277898241178"), 
  api_secret = os.environ.get("CLOUDINARY_API_SECRET", "VhODvT9UTr0wim4SZuFPR-UmixE")
)

# --- INJECTION DES FLAGS ---
@app.context_processor
def inject_flags():
    try:
        commerce = kv.get("flag:commerce")
        investissement = kv.get("flag:investissement")
        recrutement = kv.get("flag:recrutement")
        
        return {
            'flags': {
                'commerce': commerce if commerce is not None else True,
                'investissement': investissement if investissement is not None else True,
                'recrutement': recrutement if recrutement is not None else True
            }
        }
    except:
        return {'flags': {'commerce': True, 'investissement': True, 'recrutement': True}}

# --- ROUTES DE NAVIGATION ---

@app.route("/")
def presentation():
    return render_template("presentation.html")

@app.route("/accueil")
def home():
    return render_template("index.html")

@app.route("/section/<name>")
def view_section(name):
    try:
        name = str(name).strip().lower()
        
        # Gestion dynamique et harmonisation de la clé de flag (commerce ou boutique -> commerce)
        flag_key = "commerce" if name in ["commerce", "boutique"] else name
        is_active = kv.get(f"flag:{flag_key}")
        
        # Si l'administrateur a désactivé cette section, on renvoie la page indisponible
        if is_active is False:
            # name.capitalize() permet de mettre une majuscule (ex: "Commerce", "Investissement")
            return render_template("indisponible.html", section_name=name.capitalize())
        
        # Affichage normal si la section est active
        if name == "investissement":
            return render_template("section_investissement.html")
            
        if name == "recrutement":
            postes_list = kv.get("list:postes") or []
            postes = [{"id": i, "titre": p} for i, p in enumerate(postes_list)]
            return render_template("section_recrutement.html", postes=postes)
        
        if name in ["commerce", "boutique"]:
            produits_dict = kv.get("dict:produits") or {}
            prods = []
            for p_id, p_data in produits_dict.items():
                prods.append({
                    "id": p_id,
                    "designation": p_data.get("designation", ""),
                    "prix": float(p_data.get("prix", 0)),
                    "section": p_data.get("section", ""),
                    "image": p_data.get("image", ""),
                    "cloudinary_id": p_data.get("cloudinary_id", "")
                })
            return render_template("section.html", name=name, produits=prods)
            
    except Exception as e:
        print(f"Erreur section dynamique: {e}")
    return redirect(url_for('home'))

# --- INTERCEPTIONS TELEGRAM ---

@app.route("/passer-commande", methods=["POST"])
def passer_commande():
    data = request.get_json()
    if not data or not all([data.get("nom"), data.get("pays"), data.get("ville"), data.get("telephone"), data.get("panier")]):
        return jsonify({"success": False, "message": "Données incomplètes"}), 400

    texte_panier = ""
    total_financier = 0
    for item in data['panier']:
        sous_total = item['price'] * item['quantity']
        total_financier += sous_total
        texte_panier += f"• <b>{item['name']}</b> (x{item['quantity']}) — {sous_total:,} F\n"

    message = (
        f"📦 <b>NOUVELLE COMMANDE REÇUE !</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Client :</b> {data['nom']}\n📧 <b>E-mail :</b> {data.get('email', 'Non renseigné')}\n"
        f"🌍 <b>Destination :</b> {data['pays']} ({data['ville']})\n📞 <b>Tél 1 :</b> {data['telephone']}\n"
        f"🛒 <b>Détails :</b>\n{texte_panier}\n💵 <b>TOTAL : {total_financier:,} F</b>\n━━━━━━━━━━━━━━━━━━━━━"
    )
    return envoyer_telegram(message)

@app.route("/api/investissement", methods=["POST"])
def api_investissement():
    data = request.get_json() or {}
    message = (
        "📈 *Nouvelle Demande d'Investissement* 📈\n\n"
        f"👤 *Nom :* {data.get('nom')}\n🌍 *Pays :* {data.get('pays')}\n"
        f"🏙️ *Ville :* {data.get('ville')}\n📞 *Téléphone :* {data.get('tel')}\n"
        f"💰 *Montant :* {data.get('montant')} FCFA\n"
    )
    return envoyer_telegram(message, mode="Markdown")

@app.route("/soumettre-candidature", methods=["POST"])
def soumettre_candidature():
    data = request.get_json() or {}
    message = (
        f"💼 *Nouvelle Candidature*\n"
        f"👤 *Nom :* {data.get('nom')}\n📅 *Année :* {data.get('annee')}\n"
        f"🌍 *Nationalité :* {data.get('nat')}\n🎯 *Poste :* {data.get('poste')}"
    )
    return envoyer_telegram(message, mode="Markdown")

def envoyer_telegram(texte, mode="HTML"):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        res = requests.post(url, json={"chat_id": chat_id, "text": texte, "parse_mode": mode})
        return jsonify({"success": res.status_code == 200, "status": "success" if res.status_code == 200 else "error"})
    except:
        return jsonify({"success": False, "status": "error"}), 500

# --- PANNEAU D'ADMINISTRATION (/MEDJOGBE11) ---

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

    if request.method == "POST":
        if "flag_key" in request.form:
            key = request.form.get("flag_key")
            current = kv.get(f"flag:{key}")
            current = True if current is None else current
            kv.set(f"flag:{key}", not current)
        
        elif "designation" in request.form:
            file = request.files.get('image_file')
            img_url, p_id = "", ""
            if file and file.filename != '':
                res = cloudinary.uploader.upload(file)
                img_url, p_id = res['secure_url'], res['public_id']
            
            import time
            new_id = str(int(time.time()))
            
            produits_dict = kv.get("dict:produits") or {}
            produits_dict[new_id] = {
                "designation": request.form.get("designation"),
                "prix": request.form.get("price"),
                "section": request.form.get("category"),
                "image": img_url,
                "cloudinary_id": p_id
            }
            kv.set("dict:produits", produits_dict)

        elif "delete_id" in request.form:
            del_id = request.form.get("delete_id")
            produits_dict = kv.get("dict:produits") or {}
            
            if del_id in produits_dict:
                p_data = produits_dict[del_id]
                if p_data.get("cloudinary_id"):
                    cloudinary.uploader.destroy(p_data.get("cloudinary_id"))
                del produits_dict[del_id]
                kv.set("dict:produits", produits_dict)

        elif "titre_poste" in request.form:
            postes_list = kv.get("list:postes") or []
            postes_list.append(request.form.get("titre_poste"))
            kv.set("list:postes", postes_list)

        elif "delete_poste_id" in request.form:
            try:
                idx = int(request.form.get("delete_poste_id"))
                postes_list = kv.get("list:postes") or []
                if 0 <= idx < len(postes_list):
                    postes_list.pop(idx)
                    kv.set("list:postes", postes_list)
            except:
                pass

        return redirect(url_for("admin_panel"))

    postes_list = kv.get("list:postes") or []
    postes = [{"id": i, "titre": p} for i, p in enumerate(postes_list)]
    
    produits_dict = kv.get("dict:produits") or {}
    produits = []
    for k, v in produits_dict.items():
        v["id"] = k
        try:
            v["prix"] = float(v.get("prix", 0))
        except:
            v["prix"] = 0.0
        produits.append(v)

    flags = {
        "commerce": kv.get("flag:commerce") if kv.get("flag:commerce") is not None else True,
        "investissement": kv.get("flag:investissement") if kv.get("flag:investissement") is not None else True,
        "recrutement": kv.get("flag:recrutement") if kv.get("flag:recrutement") is not None else True
    }

    return render_template("admin_panel.html", flags=flags, produits=produits, postes=postes)

@app.route("/MEDJOGBE11/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)