import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from math import pi

# Configuration
URL = "http://10.101.1.116:8000/kpis"
OUTPUT_FILE = "kpis_radar.png"


def fetch_data():
    try:
        response = requests.get(URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erreur : {str(e)}")
        return None


def create_radar_chart(df):
    # Préparation des données
    categories = df['kpi_name'].unique()
    N = len(categories)

    # Création des angles
    angles = [n / N * 2 * pi for n in range(N)]
    angles += angles[:1]  # Fermer le cercle

    # Initialisation
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'polar': True})

    # Configuration
    ax.set_theta_offset(pi / 2)  # Premier axe en haut
    ax.set_theta_direction(-1)  # Sens horaire

    # Ajout des catégories
    plt.xticks(angles[:-1], categories, color='darkblue', size=10)

    # Tracé des valeurs brutes (sans normalisation)
    values = df.groupby('kpi_name')['value'].mean().tolist()
    values += values[:1]

    # Dessin
    ax.plot(angles, values, 'o-', linewidth=2, color='royalblue', markersize=8)
    ax.fill(angles, values, color='royalblue', alpha=0.2)

    # Ajout des valeurs textuelles
    for angle, value, category in zip(angles[:-1], values[:-1], categories):
        ax.text(angle, value + 0.05 * max(values), f"{value:.1f}",
                ha='center', va='center', color='darkred', fontsize=10)

    # Configuration des axes radiaux
    max_val = max(values) * 1.2
    ax.set_rlabel_position(30)
    plt.yticks(np.linspace(0, max_val, 5),
               [f"{val:.1f}" for val in np.linspace(0, max_val, 5)],
               color="grey", size=8)
    plt.ylim(0, max_val)

    # Titre
    plt.title("Performance des KPIs\n(valeurs moyennes)", size=14, pad=20)

    # Légère rotation des labels pour meilleure lisibilité
    plt.tight_layout()

    # Sauvegarde
    plt.savefig(OUTPUT_FILE, dpi=120, bbox_inches='tight')
    print(f"Diagramme radar sauvegardé sous {OUTPUT_FILE}")
    plt.close()


if __name__ == "__main__":
    print("Récupération des données...")
    data = fetch_data()

    if data:
        df = pd.DataFrame(data)
        print("\nDonnées reçues :")
        print(df.head())

        create_radar_chart(df)
        print("\nDiagramme généré avec succès!")
    else:
        print("Échec de la récupération")
