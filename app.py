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
                    {"id":"demo-72","designation":"Sandales à talons femme","prix":3000,"section":"chaussures_femme","image":"https://images.unsplash.com/photo-1515347619252-60a4bf4 stomach?auto=format&fit=crop&w=700&q=80","demo":True},
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