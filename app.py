import os
import requests
import cloudinary
import cloudinary.uploader
import json
import uuid
import html
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv

load_dotenv()

DEMO_CATALOG = {
    "demo-01": {
        "name": "Chemise homme blanche",
        "price": 2500,
        "section": "homme"
    },
    "demo-02": {
        "name": "Polo homme classique",
        "price": 2000,
        "section": "homme"
    },
    "demo-03": {
        "name": "Jean homme coupe droite",
        "price": 3000,
        "section": "homme"
    },
    "demo-04": {
        "name": "Pantalon chino homme",
        "price": 2500,
        "section": "homme"
    },
    "demo-05": {
        "name": "T-shirt homme essentiel",
        "price": 1500,
        "section": "homme"
    },
    "demo-06": {
        "name": "Veste urbaine homme",
        "price": 3000,
        "section": "homme"
    },
    "demo-07": {
        "name": "Robe élégante femme",
        "price": 3000,
        "section": "femme"
    },
    "demo-08": {
        "name": "Ensemble femme chic",
        "price": 3000,
        "section": "femme"
    },
    "demo-09": {
        "name": "Chemisier femme",
        "price": 2000,
        "section": "femme"
    },
    "demo-10": {
        "name": "Jupe midi femme",
        "price": 2000,
        "section": "femme"
    },
    "demo-11": {
        "name": "Jean femme",
        "price": 3000,
        "section": "femme"
    },
    "demo-12": {
        "name": "Top femme moderne",
        "price": 1500,
        "section": "femme"
    },
    "demo-13": {
        "name": "Ensemble enfant garçon",
        "price": 2500,
        "section": "enfant"
    },
    "demo-14": {
        "name": "Robe enfant fille",
        "price": 2500,
        "section": "enfant"
    },
    "demo-15": {
        "name": "T-shirt enfant",
        "price": 1000,
        "section": "enfant"
    },
    "demo-16": {
        "name": "Baskets lifestyle",
        "price": 10000,
        "section": "chaussures"
    },
    "demo-17": {
        "name": "Sandales femme",
        "price": 5000,
        "section": "chaussures"
    },
    "demo-18": {
        "name": "Chaussures habillées homme",
        "price": 12000,
        "section": "chaussures"
    },
    "demo-19": {
        "name": "Sac à main élégant",
        "price": 5000,
        "section": "sacs"
    },
    "demo-20": {
        "name": "Sac à dos urbain",
        "price": 4000,
        "section": "sacs"
    },
    "demo-21": {
        "name": "Sac de voyage",
        "price": 5000,
        "section": "sacs"
    },
    "demo-22": {
        "name": "Montre classique",
        "price": 7000,
        "section": "accessoires"
    },
    "demo-23": {
        "name": "Lunettes de soleil",
        "price": 3000,
        "section": "accessoires"
    },
    "demo-24": {
        "name": "Ceinture en cuir",
        "price": 3000,
        "section": "accessoires"
    },
    "demo-25": {
        "name": "Boubou traditionnel homme",
        "price": 3000,
        "section": "traditionnel"
    },
    "demo-26": {
        "name": "Ensemble africain femme",
        "price": 3000,
        "section": "traditionnel"
    },
    "demo-27": {
        "name": "Casquette urbaine",
        "price": 2500,
        "section": "accessoires"
    },
    "demo-28": {
        "name": "Sac à main tendance",
        "price": 4500,
        "section": "sacs"
    },
    "demo-29": {
        "name": "Sac à main petit format",
        "price": 3000,
        "section": "sacs"
    },
    "demo-30": {
        "name": "Sac à main bandoulière",
        "price": 4000,
        "section": "sacs"
    },
    "demo-31": {
        "name": "Sac cabas quotidien",
        "price": 3500,
        "section": "sacs"
    },
    "demo-32": {
        "name": "Petit sac chic",
        "price": 2500,
        "section": "sacs"
    },
    "demo-33": {
        "name": "Sac à dos scolaire",
        "price": 4500,
        "section": "sacs"
    },
    "demo-34": {
        "name": "Sac à dos compact",
        "price": 3500,
        "section": "sacs"
    },
    "demo-35": {
        "name": "Sac de sortie femme",
        "price": 3000,
        "section": "sacs"
    },
    "demo-36": {
        "name": "Pochette élégante",
        "price": 2000,
        "section": "sacs"
    },
    "demo-37": {
        "name": "Sac à main femme élégant",
        "price": 4500,
        "section": "sacs"
    },
    "demo-38": {
        "name": "Sac bandoulière femme",
        "price": 3500,
        "section": "sacs"
    },
    "demo-39": {
        "name": "Sac à main beige",
        "price": 4000,
        "section": "sacs"
    },
    "demo-40": {
        "name": "Petit sac de soirée",
        "price": 2500,
        "section": "sacs"
    },
    "demo-41": {
        "name": "Sac porté épaule femme",
        "price": 5000,
        "section": "sacs"
    },
    "demo-42": {
        "name": "Sac à main noir",
        "price": 3000,
        "section": "sacs"
    },
    "demo-43": {
        "name": "Sac à main rose",
        "price": 3500,
        "section": "sacs"
    },
    "demo-44": {
        "name": "Pochette de sortie femme",
        "price": 2000,
        "section": "sacs"
    },
    "demo-45": {
        "name": "Derbies homme en cuir ciré noir",
        "price": 3000,
        "section": "chaussures_homme"
    },
    "demo-46": {
        "name": "Mocassins homme en cuir ciré",
        "price": 3000,
        "section": "chaussures_homme"
    },
    "demo-47": {
        "name": "Richelieus homme en cuir ciré",
        "price": 3000,
        "section": "chaussures_homme"
    },
    "demo-48": {
        "name": "Chaussures homme en cuir ciré marron",
        "price": 3000,
        "section": "chaussures_homme"
    },
    "demo-49": {
        "name": "Derbies homme en cuir ciré bout carré",
        "price": 2500,
        "section": "chaussures_homme"
    },
    "demo-50": {
        "name": "Mocassins homme en cuir ciré à boucle",
        "price": 3000,
        "section": "chaussures_homme"
    },
    "demo-51": {
        "name": "Chaussures habillées homme cuir ciré noir",
        "price": 3000,
        "section": "chaussures_homme"
    },
    "demo-52": {
        "name": "Derbies homme cuir ciré élégants",
        "price": 3000,
        "section": "chaussures_homme"
    },
    "demo-53": {
        "name": "Chaussures homme cérémonie cuir ciré",
        "price": 3000,
        "section": "chaussures_homme"
    },
    "demo-54": {
        "name": "Mocassins homme cuir ciré classiques",
        "price": 2500,
        "section": "chaussures_homme"
    },
    "demo-55": {
        "name": "Richelieus homme cuir ciré à lacets",
        "price": 3000,
        "section": "chaussures_homme"
    },
    "demo-56": {
        "name": "Chaussures homme cuir ciré",
        "price": 2500,
        "section": "chaussures_homme"
    },
    "demo-57": {
        "name": "Derbies homme cuir ciré marron foncé",
        "price": 3000,
        "section": "chaussures_homme"
    },
    "demo-58": {
        "name": "Mocassins homme cuir ciré souples",
        "price": 2500,
        "section": "chaussures_homme"
    },
    "demo-59": {
        "name": "Chaussures homme cuir ciré brillantes",
        "price": 3000,
        "section": "chaussures_homme"
    },
    "demo-60": {
        "name": "Chaussures bébé premiers pas",
        "price": 1500,
        "section": "chaussures_bebe"
    },
    "demo-61": {
        "name": "Baskets bébé souples",
        "price": 2000,
        "section": "chaussures_bebe"
    },
    "demo-62": {
        "name": "Petits mocassins bébé",
        "price": 2500,
        "section": "chaussures_bebe"
    },
    "demo-63": {
        "name": "Chaussures bébé à scratch",
        "price": 1500,
        "section": "chaussures_bebe"
    },
    "demo-64": {
        "name": "Chaussons bébé fermés",
        "price": 2000,
        "section": "chaussures_bebe"
    },
    "demo-65": {
        "name": "Baskets bébé légères",
        "price": 2500,
        "section": "chaussures_bebe"
    },
    "demo-66": {
        "name": "Chaussures bébé garçon",
        "price": 1500,
        "section": "chaussures_bebe"
    },
    "demo-67": {
        "name": "Chaussures bébé fille",
        "price": 2000,
        "section": "chaussures_bebe"
    },
    "demo-68": {
        "name": "Petites chaussures bébé blanches",
        "price": 2500,
        "section": "chaussures_bebe"
    },
    "demo-69": {
        "name": "Chaussures bébé confort",
        "price": 1500,
        "section": "chaussures_bebe"
    },
    "demo-70": {
        "name": "Ballerines femme",
        "price": 2000,
        "section": "chaussures_femme"
    },
    "demo-71": {
        "name": "Escarpins femme classiques",
        "price": 2500,
        "section": "chaussures_femme"
    },
    "demo-72": {
        "name": "Sandales à talons femme",
        "price": 3000,
        "section": "chaussures_femme"
    },
    "demo-73": {
        "name": "Mules femme élégantes",
        "price": 2000,
        "section": "chaussures_femme"
    },
    "demo-74": {
        "name": "Baskets femme blanches",
        "price": 2500,
        "section": "chaussures_femme"
    },
    "demo-75": {
        "name": "Mocassins femme",
        "price": 3000,
        "section": "chaussures_femme"
    },
    "demo-76": {
        "name": "Chaussures plates femme",
        "price": 2000,
        "section": "chaussures_femme"
    },
    "demo-77": {
        "name": "Sandales plates femme",
        "price": 2500,
        "section": "chaussures_femme"
    },
    "demo-78": {
        "name": "Escarpins femme pointus",
        "price": 3000,
        "section": "chaussures_femme"
    },
    "demo-79": {
        "name": "Baskets femme tendance",
        "price": 2000,
        "section": "chaussures_femme"
    },
    "demo-80": {
        "name": "Babies femme",
        "price": 2500,
        "section": "chaussures_femme"
    },
    "demo-81": {
        "name": "Sandales compensées femme",
        "price": 3000,
        "section": "chaussures_femme"
    },
    "demo-82": {
        "name": "Chaussures femme de soirée",
        "price": 2000,
        "section": "chaussures_femme"
    },
    "demo-83": {
        "name": "Bottines femme",
        "price": 2500,
        "section": "chaussures_femme"
    },
    "demo-84": {
        "name": "Mules femme ouvertes",
        "price": 3000,
        "section": "chaussures_femme"
    },
    "demo-85": {
        "name": "Baskets femme sport",
        "price": 2000,
        "section": "chaussures_femme"
    },
    "demo-86": {
        "name": "Sandales à brides femme",
        "price": 2500,
        "section": "chaussures_femme"
    },
    "demo-87": {
        "name": "Chaussures femme habillées",
        "price": 3000,
        "section": "chaussures_femme"
    },
    "demo-88": {
        "name": "Ballerines femme chic",
        "price": 2000,
        "section": "chaussures_femme"
    },
    "demo-89": {
        "name": "Escarpins femme sobres",
        "price": 2500,
        "section": "chaussures_femme"
    }
}

# --- CLIENT VERCEL KV (UPSTASH REDIS REST) ---
class VercelKVClient:
    def __init__(self):
        self.url = (os.getenv("KV_REST_API_URL") or "").strip().rstrip("/")
        self.token = (os.getenv("KV_REST_API_TOKEN") or "").strip()
        self.last_error = ""

    def _command(self, command):
        if not self.url or not self.token:
            raise RuntimeError("Variables KV_REST_API_URL ou KV_REST_API_TOKEN absentes.")
        res = requests.post(
            self.url,
            headers={"Authorization": f"Bearer {self.token}"},
            json=command,
            timeout=8
        )
        res.raise_for_status()
        payload = res.json()
        if isinstance(payload, dict) and payload.get("error"):
            raise RuntimeError(str(payload["error"])[:240])
        return payload.get("result") if isinstance(payload, dict) else None

    def get(self, key):
        try:
            value = self._command(["GET", str(key)])
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except (ValueError, TypeError):
                    return value
            return value
        except Exception as exc:
            print(f"[KV] GET impossible pour {key}: {type(exc).__name__}: {str(exc)[:240]}")
            return None

    def set(self, key, value):
        try:
            result = self._command(["SET", str(key), json.dumps(value, ensure_ascii=False)])
            if result == "OK":
                return True
            print(f"[KV] SET refusé pour {key}: résultat inattendu ({result!r})")
            return False
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {str(exc)[:240]}"
            print(f"[KV] SET impossible pour {key}: {self.last_error}")
            return False

kv = VercelKVClient()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# --- CONFIGURATION CLOUDINARY ---
cloudinary.config( 
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.environ.get("CLOUDINARY_API_KEY"), 
  api_secret = os.environ.get("CLOUDINARY_API_SECRET")
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
            if False and produits_dict:
                for p_id, p_data in produits_dict.items():
                    prods.append({
                        "id": p_id,
                        "designation": p_data.get("designation", ""),
                        "prix": float(p_data.get("prix", 0)),
                        "section": p_data.get("section", ""),
                        "image": p_data.get("image", ""),
                        "cloudinary_id": p_data.get("cloudinary_id", ""),
                        "demo": False
                    })
            else:
                # Catalogue de démonstration : prix indicatifs à confirmer avant toute vente.
                prods = [
                    {"id":"demo-01","designation":"Chemise homme blanche","prix":2500,"section":"homme","image":"https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-02","designation":"Polo homme classique","prix":2000,"section":"homme","image":"https://images.unsplash.com/photo-1625910513413-5fc45e7d6b3a?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-03","designation":"Jean homme coupe droite","prix":3000,"section":"homme","image":"https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-04","designation":"Pantalon chino homme","prix":2500,"section":"homme","image":"https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-05","designation":"T-shirt homme essentiel","prix":1500,"section":"homme","image":"https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-06","designation":"Veste urbaine homme","prix":3000,"section":"homme","image":"https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-07","designation":"Robe élégante femme","prix":3000,"section":"femme","image":"https://images.unsplash.com/photo-1539008835657-9e8e9680c956?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-08","designation":"Ensemble femme chic","prix":3000,"section":"femme","image":"https://images.unsplash.com/photo-1598554747436-c9293d6a588f?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-09","designation":"Chemisier femme","prix":2000,"section":"femme","image":"https://images.unsplash.com/photo-1566206091558-7f218b696731?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-10","designation":"Jupe midi femme","prix":2000,"section":"femme","image":"https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-11","designation":"Jean femme","prix":3000,"section":"femme","image":"https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-12","designation":"Top femme moderne","prix":1500,"section":"femme","image":"https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-13","designation":"Ensemble enfant garçon","prix":2500,"section":"enfant","image":"https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-14","designation":"Robe enfant fille","prix":2500,"section":"enfant","image":"https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-15","designation":"T-shirt enfant","prix":1000,"section":"enfant","image":"https://images.unsplash.com/photo-1503919005314-30d93d07d823?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-16","designation":"Baskets lifestyle","prix":10000,"section":"chaussures","image":"https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-17","designation":"Sandales femme","prix":5000,"section":"chaussures","image":"https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-18","designation":"Chaussures habillées homme","prix":12000,"section":"chaussures","image":"https://images.unsplash.com/photo-1614252369475-53139f2c1b1b?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-19","designation":"Sac à main élégant","prix":5000,"section":"sacs","image":"https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-20","designation":"Sac à dos urbain","prix":4000,"section":"sacs","image":"https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-21","designation":"Sac de voyage","prix":5000,"section":"sacs","image":"https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-22","designation":"Montre classique","prix":7000,"section":"accessoires","image":"https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-23","designation":"Lunettes de soleil","prix":3000,"section":"accessoires","image":"https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-24","designation":"Ceinture en cuir","prix":3000,"section":"accessoires","image":"https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-25","designation":"Boubou traditionnel homme","prix":3000,"section":"traditionnel","image":"https://images.unsplash.com/photo-1598033129183-c4f50c736f10?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-26","designation":"Ensemble africain femme","prix":3000,"section":"traditionnel","image":"https://images.unsplash.com/photo-1583391733956-6c78276477e8?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-27","designation":"Casquette urbaine","prix":2500,"section":"accessoires","image":"https://images.unsplash.com/photo-1588850561407-ed78c282e89b?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-28","designation":"Sac à main tendance","prix":4500,"section":"sacs","image":"https://images.unsplash.com/photo-1565026057447-bc90a3dceb87?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-29","designation":"Sac à main petit format","prix":3000,"section":"sacs","image":"https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-30","designation":"Sac à main bandoulière","prix":4000,"section":"sacs","image":"https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-31","designation":"Sac cabas quotidien","prix":3500,"section":"sacs","image":"https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-32","designation":"Petit sac chic","prix":2500,"section":"sacs","image":"https://images.unsplash.com/photo-1565026057447-bc90a3dceb87?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-33","designation":"Sac à dos scolaire","prix":4500,"section":"sacs","image":"https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-34","designation":"Sac à dos compact","prix":3500,"section":"sacs","image":"https://images.unsplash.com/photo-1622560480654-d96214fdc887?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-35","designation":"Sac de sortie femme","prix":3000,"section":"sacs","image":"https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-36","designation":"Pochette élégante","prix":2000,"section":"sacs","image":"https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-37","designation":"Sac à main femme élégant","prix":4500,"section":"sacs","image":"https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-38","designation":"Sac bandoulière femme","prix":3500,"section":"sacs","image":"https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-39","designation":"Sac à main beige","prix":4000,"section":"sacs","image":"https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-40","designation":"Petit sac de soirée","prix":2500,"section":"sacs","image":"https://images.unsplash.com/photo-1565026057447-bc90a3dceb87?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-41","designation":"Sac porté épaule femme","prix":5000,"section":"sacs","image":"https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-42","designation":"Sac à main noir","prix":3000,"section":"sacs","image":"https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-43","designation":"Sac à main rose","prix":3500,"section":"sacs","image":"https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-44","designation":"Pochette de sortie femme","prix":2000,"section":"sacs","image":"https://images.unsplash.com/photo-1565026057447-bc90a3dceb87?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-45","designation":"Derbies homme en cuir ciré noir","prix":3000,"section":"chaussures_homme","image":"https://iconsfootwear.com/cdn/shop/files/1_26eaefc0-a0ff-4e90-a9cc-f309056e16ed.png?v=1760876636&width=1080","demo":True},
                    {"id":"demo-46","designation":"Mocassins homme en cuir ciré","prix":3000,"section":"chaussures_homme","image":"https://gomilaintersole.pk/cdn/shop/products/99.jpg?v=1735003165&width=1200","demo":True},
                    {"id":"demo-47","designation":"Richelieus homme en cuir ciré","prix":3000,"section":"chaussures_homme","image":"https://y6fsbg-nc.myshopify.com/cdn/shop/files/PolishedBlackOxfordShoesShowcase.png?v=1791136682&width=720","demo":True},
                    {"id":"demo-48","designation":"Chaussures homme en cuir ciré marron","prix":3000,"section":"chaussures_homme","image":"https://gomilaintersole.pk/cdn/shop/products/99.jpg?v=1735003165&width=1200","demo":True},
                    {"id":"demo-49","designation":"Derbies homme en cuir ciré bout carré","prix":2500,"section":"chaussures_homme","image":"https://iconsfootwear.com/cdn/shop/files/1_26eaefc0-a0ff-4e90-a9cc-f309056e16ed.png?v=1760876636&width=1080","demo":True},
                    {"id":"demo-50","designation":"Mocassins homme en cuir ciré à boucle","prix":3000,"section":"chaussures_homme","image":"https://y6fsbg-nc.myshopify.com/cdn/shop/files/PolishedBlackOxfordShoesShowcase.png?v=1791136682&width=720","demo":True},
                    {"id":"demo-51","designation":"Chaussures habillées homme cuir ciré noir","prix":3000,"section":"chaussures_homme","image":"https://iconsfootwear.com/cdn/shop/files/1_26eaefc0-a0ff-4e90-a9cc-f309056e16ed.png?v=1760876636&width=1080","demo":True},
                    {"id":"demo-52","designation":"Derbies homme cuir ciré élégants","prix":3000,"section":"chaussures_homme","image":"https://gomilaintersole.pk/cdn/shop/products/99.jpg?v=1735003165&width=1200","demo":True},
                    {"id":"demo-53","designation":"Chaussures homme cérémonie cuir ciré","prix":3000,"section":"chaussures_homme","image":"https://y6fsbg-nc.myshopify.com/cdn/shop/files/PolishedBlackOxfordShoesShowcase.png?v=1791136682&width=720","demo":True},
                    {"id":"demo-54","designation":"Mocassins homme cuir ciré classiques","prix":2500,"section":"chaussures_homme","image":"https://gomilaintersole.pk/cdn/shop/products/99.jpg?v=1735003165&width=1200","demo":True},
                    {"id":"demo-55","designation":"Richelieus homme cuir ciré à lacets","prix":3000,"section":"chaussures_homme","image":"https://iconsfootwear.com/cdn/shop/files/1_26eaefc0-a0ff-4e90-a9cc-f309056e16ed.png?v=1760876636&width=1080","demo":True},
                    {"id":"demo-56","designation":"Chaussures homme cuir ciré","prix":2500,"section":"chaussures_homme","image":"https://y6fsbg-nc.myshopify.com/cdn/shop/files/PolishedBlackOxfordShoesShowcase.png?v=1791136682&width=720","demo":True},
                    {"id":"demo-57","designation":"Derbies homme cuir ciré marron foncé","prix":3000,"section":"chaussures_homme","image":"https://gomilaintersole.pk/cdn/shop/products/99.jpg?v=1735003165&width=1200","demo":True},
                    {"id":"demo-58","designation":"Mocassins homme cuir ciré souples","prix":2500,"section":"chaussures_homme","image":"https://iconsfootwear.com/cdn/shop/files/1_26eaefc0-a0ff-4e90-a9cc-f309056e16ed.png?v=1760876636&width=1080","demo":True},
                    {"id":"demo-59","designation":"Chaussures homme cuir ciré brillantes","prix":3000,"section":"chaussures_homme","image":"https://y6fsbg-nc.myshopify.com/cdn/shop/files/PolishedBlackOxfordShoesShowcase.png?v=1791136682&width=720","demo":True},
                    {"id":"demo-60","designation":"Chaussures bébé premiers pas","prix":1500,"section":"chaussures_bebe","image":"https://images.unsplash.com/photo-1519689680058-324335c77eba?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-61","designation":"Baskets bébé souples","prix":2000,"section":"chaussures_bebe","image":"https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-62","designation":"Petits mocassins bébé","prix":2500,"section":"chaussures_bebe","image":"https://images.unsplash.com/photo-1503919005314-30d93d07d823?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-63","designation":"Chaussures bébé à scratch","prix":1500,"section":"chaussures_bebe","image":"https://images.unsplash.com/photo-1519689680058-324335c77eba?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-64","designation":"Chaussons bébé fermés","prix":2000,"section":"chaussures_bebe","image":"https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-65","designation":"Baskets bébé légères","prix":2500,"section":"chaussures_bebe","image":"https://images.unsplash.com/photo-1503919005314-30d93d07d823?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-66","designation":"Chaussures bébé garçon","prix":1500,"section":"chaussures_bebe","image":"https://images.unsplash.com/photo-1519689680058-324335c77eba?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-67","designation":"Chaussures bébé fille","prix":2000,"section":"chaussures_bebe","image":"https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-68","designation":"Petites chaussures bébé blanches","prix":2500,"section":"chaussures_bebe","image":"https://images.unsplash.com/photo-1503919005314-30d93d07d823?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-69","designation":"Chaussures bébé confort","prix":1500,"section":"chaussures_bebe","image":"https://images.unsplash.com/photo-1519689680058-324335c77eba?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-70","designation":"Ballerines femme","prix":2000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-71","designation":"Escarpins femme classiques","prix":2500,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-72","designation":"Sandales à talons femme","prix":3000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-73","designation":"Mules femme élégantes","prix":2000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-74","designation":"Baskets femme blanches","prix":2500,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-75","designation":"Mocassins femme","prix":3000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1515347619252-60a4bf4e2c1?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-76","designation":"Chaussures plates femme","prix":2000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-77","designation":"Sandales plates femme","prix":2500,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-78","designation":"Escarpins femme pointus","prix":3000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1515347619252-60a4bf4e2c1?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-79","designation":"Baskets femme tendance","prix":2000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-80","designation":"Babies femme","prix":2500,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-81","designation":"Sandales compensées femme","prix":3000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1515347619252-60a4bf4e2c1?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-82","designation":"Chaussures femme de soirée","prix":2000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-83","designation":"Bottines femme","prix":2500,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-84","designation":"Mules femme ouvertes","prix":3000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1515347619252-60a4bf4e2c1?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-85","designation":"Baskets femme sport","prix":2000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-86","designation":"Sandales à brides femme","prix":2500,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-87","designation":"Chaussures femme habillées","prix":3000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1515347619252-60a4bf4e2c1?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-88","designation":"Ballerines femme chic","prix":2000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=700&q=80","demo":True},
                    {"id":"demo-89","designation":"Escarpins femme sobres","prix":2500,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&w=700&q=80","demo":True}
                ]
            # Ajouter les articles déjà enregistrés au catalogue de démonstration, sans doublons.
            # Ainsi, un catalogue KV non vide ne masque plus les catégories de démonstration.
            if produits_dict:
                demo_existing_ids = {str(p.get("id")) for p in prods}
                for p_id, p_data in produits_dict.items():
                    if str(p_id) not in demo_existing_ids:
                        prods.append({
                            "id": p_id,
                            "designation": p_data.get("designation", ""),
                            "prix": float(p_data.get("prix", 0)),
                            "section": p_data.get("section", ""),
                            "image": p_data.get("image", ""),
                            "cloudinary_id": p_data.get("cloudinary_id", ""),
                            "demo": False
                        })

            # Photos réelles de sacs pour le catalogue de démonstration.
            # Ces visuels ne représentent pas le stock réel de la boutique.
            bag_photos = [
                "https://images.unsplash.com/photo-1681747685985-a401c271156c?auto=format&fit=crop&w=900&q=85",
                "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=900&q=85",
                "https://imgv3.fotor.com/images/slider-image/a-white-bag-photo-denoised-and-de-grained-with-fotor-ai-image-denoiser.jpg",
                "https://d1a66n3120ol3x.cloudfront.net/blog/20260531/6a2403547f684119a68e98f7184321b4.jpg",
                "https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/3313a1156011881.635fc1747a498.png",
                "https://i.pinimg.com/originals/5a/1b/45/5a1b451c7baffbbc14e6db59ad02b0c1.jpg",
                "https://img.ruanwenpu.com/Public/upfiles/108904/202602/20260228150157107158.jpg",
                "https://tortoise.net.in/cdn/shop/files/2_251c84dd-3516-4dcd-b5c4-9fd80cd1b321.png?v=1779344435&width=1946",
                "https://baginning.com/media/catalog/product/cache/17f7930b9630993becbd36a7c8a76b30/g/e/genuine_leather_flap_square_bag_over_the_shoulder_bags_7_.jpg",
                "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=900&q=85",
                "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85",
                "https://images.unsplash.com/photo-1565026057447-bc90a3dceb87?auto=format&fit=crop&w=900&q=85",
                "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=900&q=85",
                "https://images.unsplash.com/photo-1681747685985-a401c271156c?auto=format&fit=crop&w=900&q=85",
                "https://d1a66n3120ol3x.cloudfront.net/blog/20260531/6a2403547f684119a68e98f7184321b4.jpg",
                "https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/3313a1156011881.635fc1747a498.png",
                "https://i.pinimg.com/originals/5a/1b/45/5a1b451c7baffbbc14e6db59ad02b0c1.jpg",
                "https://img.ruanwenpu.com/Public/upfiles/108904/202602/20260228150157107158.jpg",
                "https://tortoise.net.in/cdn/shop/files/2_251c84dd-3516-4dcd-b5c4-9fd80cd1b321.png?v=1779344435&width=1946",
                "https://baginning.com/media/catalog/product/cache/17f7930b9630993becbd36a7c8a76b30/g/e/genuine_leather_flap_square_bag_over_the_shoulder_bags_7_.jpg"
            ]
            bag_ids = ["demo-19", "demo-20", "demo-21"] + [f"demo-{i:02d}" for i in range(28, 45)]
            by_id = {str(p["id"]): p for p in prods}
            bag_names = [
                "Sac à main matelassé rose", "Sac à main rouge structuré", "Sac cabas beige",
                "Sac à main marron élégant", "Sac à main corail", "Sac à main vert",
                "Sac bandoulière chocolat", "Sac épaule camel", "Sac bandoulière marron",
                "Sac à main beige", "Sac bandoulière noir", "Petit sac chic",
                "Sac à main rouge", "Sac matelassé rose poudré", "Sac cabas caramel",
                "Sac à main corail", "Sac à main vert émeraude", "Sac bandoulière brun",
                "Sac épaule camel", "Sac de sortie marron"
            ]
            for idx, bag_id in enumerate(bag_ids):
                if bag_id in by_id:
                    by_id[bag_id]["image"] = bag_photos[idx]
                    by_id[bag_id]["designation"] = bag_names[idx]
            return render_template("section.html", name=name, produits=prods)
            
    except Exception as e:
        print(f"Erreur section dynamique: {e}")
    return redirect(url_for('home'))

# --- INTERCEPTIONS TELEGRAM ---

@app.route("/passer-commande", methods=["POST"])
def passer_commande():
    data = request.get_json(silent=True) or {}
    required = ["nom", "pays", "ville", "adresse", "telephone", "panier", "request_id"]
    if not all(data.get(k) for k in required) or not isinstance(data.get("panier"), list) or not data["panier"]:
        return jsonify({"success": False, "message": "Données de commande incomplètes."}), 400

    try:
        request_id = str(uuid.UUID(str(data["request_id"]).strip()))
    except (ValueError, TypeError, AttributeError):
        return jsonify({"success": False, "message": "Identifiant de commande invalide. Rechargez la page."}), 400

    order_id = "SS-" + uuid.uuid5(uuid.NAMESPACE_URL, "sahelshop:" + request_id).hex[:10].upper()
    order_key = "order:" + order_id
    existing_order = kv.get(order_key)

    if isinstance(existing_order, dict) and existing_order.get("notification_sent"):
        return jsonify({"success": True, "order_saved": True, "order_id": order_id, "notification_sent": True})

    order_saved = isinstance(existing_order, dict)
    if isinstance(existing_order, dict):
        order = existing_order
    else:
        items, total = [], 0
        produits_officiels = kv.get("dict:produits") or {}
        for item in data["panier"]:
            try:
                product_id = str(item.get("id", "")).strip()[:80]
                quantity = int(item.get("quantity", 0))
                if product_id in produits_officiels:
                    produit = produits_officiels[product_id]
                    name = str(produit.get("designation", "")).strip()[:160]
                    price = int(float(produit.get("prix", 0)))
                    image_url = str(produit.get("image", "")).strip()
                    category = str(produit.get("section", "")).strip()
                elif product_id in DEMO_CATALOG:
                    produit = DEMO_CATALOG[product_id]
                    name = str(produit["name"])[:160]
                    price = int(produit["price"])
                    image_url = str(item.get("image", "")).strip()
                    category = str(produit.get("section", "")).strip()
                else:
                    return jsonify({"success": False, "message": "Article indisponible. Actualisez le catalogue."}), 400
            except (TypeError, ValueError, KeyError, AttributeError):
                return jsonify({"success": False, "message": "Un article du panier est invalide."}), 400

            if not product_id or not name or price <= 0 or quantity < 1 or quantity > 50:
                return jsonify({"success": False, "message": "Un article du panier est invalide."}), 400

            subtotal = price * quantity
            total += subtotal
            if not image_url.startswith("https://"):
                image_url = ""
            items.append({"id": product_id, "name": name, "price": price, "quantity": quantity, "subtotal": subtotal, "image": image_url, "section": category})

        order = {
            "order_id": order_id, "status": "À confirmer", "notification_sent": False,
            "nom": str(data["nom"]).strip()[:120], "pays": str(data["pays"]).strip()[:80],
            "ville": str(data["ville"]).strip()[:100], "adresse": str(data["adresse"]).strip()[:240],
            "telephone": str(data["telephone"]).strip()[:40], "email": str(data.get("email", "")).strip()[:160],
            "livraison": str(data.get("livraison", "Livraison à domicile"))[:80],
            "paiement": str(data.get("paiement", "Paiement à la livraison"))[:80],
            "items": items, "subtotal": total, "delivery_fee": None, "total": total,
            "created_at": __import__("datetime").datetime.utcnow().isoformat() + "Z"
        }
        order_saved = kv.set(order_key, order)
        if not order_saved:
            print(f"[COMMANDE] Stockage KV indisponible pour {order_id}; tentative de notification Telegram maintenue.")

    safe = lambda value: html.escape(str(value))
    item_lines = "\n".join([
        "• <b>" + safe(x["name"]) + "</b>\n"
        + "   Référence : <code>" + safe(x["id"]) + "</code> | Catégorie : " + safe(x.get("section") or "Non précisée") + "\n"
        + "   Quantité : " + str(x["quantity"]) + " × " + format(x["price"], ",") + " F = <b>" + format(x["subtotal"], ",") + " F</b>"
        + ("\n   📷 <a href=\"" + safe(x["image"]) + "\">Voir la photo de cet article</a>" if x.get("image") else "\n   📷 Photo non disponible")
        for x in order["items"]
    ])
    message = (
        "📦 <b>NOUVELLE COMMANDE " + safe(order_id) + "</b>\n"
        + "👤 <b>Client :</b> " + safe(order["nom"]) + "\n"
        + "🌍 <b>Destination :</b> " + safe(order["pays"]) + " (" + safe(order["ville"]) + ")\n"
        + "📍 <b>Adresse :</b> " + safe(order["adresse"]) + "\n"
        + "📞 <b>Téléphone :</b> " + safe(order["telephone"]) + "\n"
        + "💳 <b>Paiement :</b> " + safe(order["paiement"]) + "\n"
        + "🚚 <b>Réception :</b> " + safe(order["livraison"]) + "\n"
        + "🛒 <b>Articles :</b>\n" + item_lines + "\n"
        + "💵 <b>Sous-total : " + format(order["subtotal"], ",") + " F CFA</b>\n"
        + "Livraison à confirmer"
    )
    telegram_response = envoyer_telegram(message)
    result = telegram_response.get_json(silent=True) or {}
    if result.get("success"):
        order["notification_sent"] = True
        order_saved = kv.set(order_key, order) or order_saved
        return jsonify({
            "success": True,
            "order_saved": bool(order_saved),
            "order_id": order_id,
            "notification_sent": True,
            "message": "Commande transmise au vendeur." if order_saved else "Commande transmise au vendeur par Telegram. Archivage administratif temporairement indisponible."
        })

    return jsonify({
        "success": False, "order_saved": True, "order_id": order_id,
        "notification_sent": False,
        "message": result.get("message") or "La commande est enregistrée, mais Telegram n'a pas confirmé la réception. Réessayez."
    }), 502

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
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        response = jsonify({"success": False, "status": "not_configured", "message": "Telegram n'est pas configuré sur le serveur."})
        response.status_code = 503
        return response

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        res = requests.post(
            url,
            json={"chat_id": chat_id, "text": texte, "parse_mode": mode, "disable_web_page_preview": True},
            timeout=12
        )
        try:
            payload = res.json()
        except ValueError:
            payload = {}
        ok = res.ok and payload.get("ok") is True
        if not ok:
            print(f"[TELEGRAM] Échec HTTP {res.status_code}: {str(payload.get('description', 'réponse invalide'))[:240]}")
        else:
            print("[TELEGRAM] Message accepté par l'API.")
        response = jsonify({
            "success": ok,
            "status": "success" if ok else "telegram_error",
            "message": "" if ok else str(payload.get("description", "Telegram a refusé le message."))[:300]
        })
        response.status_code = 200 if ok else 502
        return response
    except requests.RequestException as exc:
        print(f"[TELEGRAM] Erreur réseau: {type(exc).__name__}: {str(exc)[:240]}")
        response = jsonify({"success": False, "status": "network_error", "message": "Connexion à Telegram impossible."})
        response.status_code = 502
        return response

# --- PANNEAU D'ADMINISTRATION (/MEDJOGBE11) ---

@app.route("/MEDJOGBE11", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == os.environ.get("ADMIN_PWD"): 
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
                if not all(os.environ.get(k) for k in ('CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET')):
                    flash('Configuration des images indisponible. Les identifiants Cloudinary doivent être configurés.')
                    return redirect(url_for('admin_panel'))
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