import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date


print("Démarrage du scraping des modèles depuis Ollama...")

def scrap_ollama_models():
    """
    Scrap all the models from the Ollama website and return a DataFrame with their details.

    Returns:
        pd.DataFrame: A DataFrame containing model names, pull counts, sizes, capabilities, and update information.

    """
    print("Récupération des données depuis Ollama...")
    
    # URL de la page à scraper
    URL = "https://ollama.com/search"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Erreur de requête : {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    model_data = []

    for a_tag in soup.find_all("a", class_="group w-full"):
        # Nom du modèle
        title_tag = a_tag.find("div", title=True)
        if not title_tag:
            continue
        model_name = title_tag["title"]

        # Nombre de pulls
        pull_span = a_tag.find("span", attrs={"x-test-pull-count": True})
        pull_count = pull_span.text.strip() if pull_span else "N/A"

        # Labels de taille (ex: e2b, e4b)
        size_spans = a_tag.find_all("span", attrs={"x-test-size": True})
        sizes = [span.text.strip() for span in size_spans]

        # Label de catégorie (vision, etc.)
        capability_span = a_tag.find_all("span", attrs={"x-test-capability": True})
        capability = [span.text.strip() for span in capability_span] if capability_span else ["N/A"]


        # Informations de mise à jour
        update_span = a_tag.find("span", attrs={"x-test-updated": True})
        updated = update_span.text.strip() if update_span else "N/A"

        model_data.append({
            "name": model_name,
            "pulls": pull_count,
            "sizes": sizes,
            "capability": capability,
            "updated": updated,
            "current_data": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return pd.DataFrame(model_data)

df = scrap_ollama_models()


today_str = date.today().strftime("%Y%m%d")
filename = f"ollama_models_{today_str}.parquet"

print(f"Scraping terminé. Enregistrement des données dans {filename}...")
df.to_parquet(filename, index=False)
