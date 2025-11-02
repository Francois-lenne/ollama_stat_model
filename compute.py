import duckdb
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


def retrieve_data_from_lake():
    # Connect to DuckDB (in-memory by default)
    con = duckdb.connect()

    # Execute the INSTALL and LOAD commands
    con.execute("INSTALL azure;")
    con.execute("LOAD azure;")

    # Configurer l'authentification avec votre chaîne de connexion
    con.execute(f"CREATE SECRET azure_blob_storage_secret (TYPE AZURE, CONNECTION_STRING '{os.getenv('azure_blob_storage_secret')}');")

    # Exécuter la requête et convertir les résultats en DataFrame pandas
    query = f"SELECT * FROM 'az://{os.getenv('blob')}/dataollama/ollama_models_20250808.parquet'"
    df = con.execute(query).fetch_df()

    # Maintenant vous avez les données dans un DataFrame pandas
    print(f"DataFrame shape: {df.shape}")
    print("\nPremières lignes du DataFrame:")
    print(df.head())

    df.to_csv('ollama_models_20250808.csv', index=False)

    # Fermer la connexion
    con.close()



retrieve_data_from_lake()



def compute_nb_models():
    con = duckdb.connect()

    # Execute the INSTALL and LOAD commands
    con.execute("INSTALL azure;")
    con.execute("LOAD azure;")

    # Configurer l'authentification avec votre chaîne de connexion
    con.execute(f"CREATE SECRET azure_blob_storage_secret (TYPE AZURE, CONNECTION_STRING '{os.getenv('azure_blob_storage_secret')}');")

    # Exécuter la requête et convertir les résultats en DataFrame pandas
    query = f"SELECT COUNt(DISTINCT NAME) AS NB_MODELS, current_data as date  FROM 'az://{os.getenv('blob')}/dataollama/ollama_models_2025090*.parquet' GROUP BY ALL"
    df = con.execute(query).fetch_df()

    print(df.head())


    return len(df)

compute_nb_models()