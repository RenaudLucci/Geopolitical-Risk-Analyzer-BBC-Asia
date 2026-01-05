import feedparser
import ollama
import csv
import json
import os

# CONFIGURATION
URL_FLUX = "https://feeds.bbci.co.uk/news/world/asia/rss.xml"
NOM_FICHIER = "veille_geopolitique.csv"

# 1. RECUPERATION
print("Connexion au flux BBC...")
flux = feedparser.parse(URL_FLUX)

if not flux.entries:
    print("Erreur : Aucun article trouvé.")
    exit()

# 2. INITIALISATION DU CSV (C'est ici qu'on crée le fichier Excel)
if not os.path.exists(NOM_FICHIER):
    with open(NOM_FICHIER, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Titre", "Score Risque", "Impact Japon", "Secteur"])

# 3. ANALYSE
print(f"Analyse de {len(flux.entries[:5])} articles...\n")

for entry in flux.entries[:5]:
    prompt = f"Analyse cette news : {entry.title}. Réponds EXCLUSIVEMENT en JSON pur avec cette structure : {{\"score_risque\": 0, \"impact_japon\": \"analyse\", \"secteur\": \"nom\"}}"
    
    try:
        response = ollama.chat(model='llama3.1', messages=[{'role': 'user', 'content': prompt}])
        raw_res = response['message']['content'].strip()
        
        # Nettoyage
        raw_res = raw_res.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_res)
        
        # 4. ECRITURE (On ajoute une ligne dans le fichier CSV)
        with open(NOM_FICHIER, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                entry.title, 
                data.get('score_risque', 0), 
                data.get('impact_japon', 'N/A'), 
                data.get('secteur', 'N/A')
            ])
        print(f"✅ Ajouté : {entry.title[:40]}...")
        
    except Exception as e:
        print(f"❌ Erreur sur : {entry.title[:20]} -> {e}")

print(f"\nTerminé ! Fichier : {NOM_FICHIER}")