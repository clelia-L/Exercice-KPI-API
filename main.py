import requests
import json
import csv
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from datetime import datetime

# Configuration
URL = "http://10.101.1.116:8000/kpis"
OUTPUT_JSON = "kpis_data.json"
OUTPUT_CSV = "kpis_data.csv"


def fetch_data():
    try:
        response = requests.get(URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erreur de récupération : {str(e)}")
        return None


def save_data(data):
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(data, f, indent=4)

    if isinstance(data, list):
        df = pd.DataFrame(data)
        df.to_csv(OUTPUT_CSV, index=False)
        return df
    return pd.DataFrame(data)


def visualize_data(df):
    if df.empty:
        print("Aucune donnée à visualiser")
        return

    print("\nColonnes disponibles :", df.columns.tolist())

    # Conversion des dates
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])

    # Graphique Matplotlib (statique)
    plt.figure(figsize=(12, 6))

    if 'value' in df.columns and 'date' in df.columns:
        # Graphique temporel par KPI
        for kpi in df['kpi_name'].unique():
            subset = df[df['kpi_name'] == kpi]
            plt.plot(subset['date'], subset['value'], 'o-', label=kpi)

        plt.title("Évolution des KPIs dans le temps")
        plt.xlabel("Date")
        plt.ylabel("Valeur")
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("kpis_timeseries.png")
        print("\nGraphique temps-réel sauvegardé sous kpis_timeseries.png")

    # Graphique Plotly interactif
    try:
        if 'kpi_name' in df.columns and 'value' in df.columns:
            fig = px.line(df,
                          x='date',
                          y='value',
                          color='kpi_name',
                          title="Visualisation interactive des KPIs",
                          labels={'value': 'Valeur', 'date': 'Date'},
                          line_shape='linear')
            fig.write_html("kpis_interactive.html")
            print("Visualisation interactive sauvegardée sous kpis_interactive.html")
    except Exception as e:
        print(f"Erreur avec Plotly : {str(e)}. Vérifiez les types de données.")


if __name__ == "__main__":
    print("Récupération des données...")
    raw_data = fetch_data()

    if raw_data:
        print("Sauvegarde des données...")
        df = save_data(raw_data)

        print("Génération des visualisations...")
        visualize_data(df)

        print("Terminé ! Ouvrez les fichiers .png et .html générés")
    else:
        print("Échec de la récupération des données")
