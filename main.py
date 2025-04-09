import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from math import pi
import sys

# Configuration
CONFIG = {
    'url': "http://10.101.1.116:8000/kpis",
    'timeout': 15,
    'output_file': "kpis_radar_pro.png"
}


def verifier_connexion():
    """Vérifie que l'API est accessible"""
    try:
        test = requests.get(CONFIG['url'], timeout=5)
        return test.status_code == 200
    except:
        return False


def charger_donnees():
    """Charge les données avec vérification approfondie"""
    print("\n🔎 Connexion à l'API en cours...")
    try:
        response = requests.get(CONFIG['url'], timeout=CONFIG['timeout'])
        response.raise_for_status()
        data = response.json()

        if not data:
            raise ValueError("Réponse API vide")
        print(f"✅ {len(data)} points de données reçus")
        return data
    except Exception as e:
        print(f"❌ Erreur de récupération: {str(e)}")
        return None


def preparer_donnees(df):
    """Prépare les données pour le radar chart"""
    print("\n📊 Préparation des données...")

    # Vérification des colonnes requises
    required_cols = {'kpi_name', 'value'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Colonnes manquantes: {missing}")

    # Agrégation
    stats = df.groupby('kpi_name').agg(
        moyenne=('value', 'mean'),
        min=('value', 'min'),
        max=('value', 'max')
    ).reset_index()

    print(stats)
    return stats


def creer_radar(df):
    """Crée un radar chart professionnel sans dépendance Seaborn"""
    print("\n🎨 Génération du diagramme radar...")

    # Configuration du style manuellement
    plt.rcParams.update({
        'axes.facecolor': 'white',
        'axes.edgecolor': 'black',
        'axes.grid': True,
        'grid.color': 'lightgray',
        'grid.linestyle': '--',
        'font.size': 12
    })

    # Initialisation
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, polar=True)

    # Paramétrage
    categories = df['kpi_name'].tolist()
    N = len(categories)
    angles = [n / N * 2 * pi for n in range(N)]
    angles += angles[:1]  # Fermer le cercle

    # Données
    values = df['moyenne'].tolist()
    values += values[:1]

    # Tracé
    ax.plot(angles, values, color='#1f77b4', linewidth=3, marker='o', markersize=10)
    ax.fill(angles, values, color='#1f77b4', alpha=0.1)

    # Étiquettes
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)

    # Valeurs
    for angle, value, label in zip(angles[:-1], values[:-1], categories):
        ax.text(angle, value * 1.05, f"{value:.1f}",
                ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.8, pad=3))

    # Paramètres visuels
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(30)
    plt.title("Performance des KPIs\n(moyennes calculées)", pad=30, fontsize=14)

    # Sauvegarde
    plt.savefig(CONFIG['output_file'], dpi=150, bbox_inches='tight')
    print(f"\n💾 Diagramme sauvegardé sous {CONFIG['output_file']} (150 DPI)")
    plt.close()


if __name__ == "__main__":
    # Vérification initiale
    if not verifier_connexion():
        print("❌ Impossible de se connecter à l'API. Vérifiez:")
        print(f"- Que l'URL {CONFIG['url']} est correcte")
        print("- Que le serveur est en cours d'exécution")
        print("- Votre connexion réseau")
        sys.exit(1)

    # Récupération des données
    raw_data = charger_donnees()

    if raw_data is None:
        sys.exit(1)

    try:
        df = pd.DataFrame(raw_data)
        stats = preparer_donnees(df)
        creer_radar(stats)
        print("\n✅ Analyse terminée avec succès!")
    except Exception as e:
        print(f"❌ Erreur lors du traitement: {str(e)}")
        sys.exit(1)
