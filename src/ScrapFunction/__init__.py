import logging
import azure.functions as func
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
import os

def main(timer: func.TimerRequest) -> None:
    """Azure Function entry point - must accept timer parameter"""
    logging.info('Python timer trigger function started')
    
    if timer.past_due:
        logging.info('The timer is past due!')
    
    try:
        # Call your scraping logic
        run_scraping()
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution: {str(e)}")
        raise

def run_scraping():
    """Your main scraping logic"""
    df = scrap_ollama_models()
    logging.info("Données récupérées avec succès. Début de validation de la donnée")
    
    check_data_quality(df)
    
    today_str = date.today().strftime("%Y%m%d") + "_" + pd.Timestamp.now().strftime("%H")
    filename = f"ollama_models_{today_str}.parquet"
    
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    blob_name = os.getenv('AZURE_CONTAINER_NAME')
    
    df.to_parquet(
        f"abfss://{blob_name}/{filename}",
        engine="fastparquet",
        storage_options={"connection_string": connection_string}
    )
    
    logging.info(f"Les données ont été sauvegardées dans {filename}")




def scrap_ollama_models() -> pd.DataFrame:
    """
    Scrap all the models from the Ollama website and return a DataFrame with their details.

    Returns:
        pd.DataFrame: A DataFrame containing model names, pull counts, sizes, capabilities, and update information.

    """
    logging.info("Récupération des données depuis Ollama...")
    
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


def check_data_quality(df: pd.DataFrame) -> None:
    """
    check the data quality of the dataframe containing the raw data
    :param df: The dataframe to check
    """

    # Vérification des doublons sur le nom du modèle
    if df["name"].duplicated().any():
        logging.info(df[df["name"].duplicated(keep=False)][["name"]])
        raise ValueError("Doublons trouvés dans la colonne 'name'.")
    else:
        logging.info("Aucun doublon trouvé dans les modèles")

    # Vérification des types de données des colonnes 
    expected_types = {
        "name": str,
        "pulls": str,
        "sizes": list,
        "capability": list,
        "updated": str,
        "current_data": str
    }

    for column, expected_type in expected_types.items():
        if not df[column].apply(lambda x: isinstance(x, expected_type)).all():
            raise TypeError(f"Type de données incorrect pour la colonne '{column}'. Attendu {expected_type.__name__}, trouvé {df[column].apply(type).unique()}.")   
    
    logging.info("Vérification de la qualité des données terminée avec succès.")

# remove the part of the requirement function to use this block

"""
if __name__ == "__main__":
    main()
"""
