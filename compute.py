import duckdb
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to DuckDB (in-memory by default)
con = duckdb.connect()

# Execute the INSTALL and LOAD commands
con.execute("INSTALL azure;")
con.execute("LOAD azure;")

# Configurer l'authentification avec votre chaîne de connexion
con.execute(f"CREATE SECRET azure_blob_storage_secret (TYPE AZURE, CONNECTION_STRING '{os.getenv('azure_blob_storage_secret')}');")

# Exécuter la requête et convertir les résultats en DataFrame pandas
query = f"SELECT * FROM 'az://{os.getenv('blob')}/dataollama/ollama_models_*.parquet'"
df = con.execute(query).fetch_df()

# Maintenant vous avez les données dans un DataFrame pandas
print(f"DataFrame shape: {df.shape}")
print("\nPremières lignes du DataFrame:")
print(df.head())

# Fermer la connexion
con.close()