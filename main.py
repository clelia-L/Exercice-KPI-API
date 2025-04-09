import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from math import pi
from matplotlib.colors import LinearSegmentedColormap
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

    required_cols = {'kpi_name', 'value'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Colonnes manquantes: {missing}")

    stats = df.groupby('kpi_name').agg(
        moyenne=('value', 'mean'),
        min=('value', 'min'),
        max=('value', 'max')
    ).reset_index()

    # Normalisation pour le dégradé
    stats['normalized'] = (stats['moyenne'] - stats['moyenne'].min()) / (
                stats['moyenne'].max() - stats['moyenne'].min())
    print(stats)
    return stats


def creer_radar_grade(df):
    """Crée un radar chart avec dégradé de couleurs et gestion correcte de la colorbar"""
    print("\n🎨 Génération du diagramme radar avec dégradé...")

    # Création du dégradé (rouge -> jaune -> vert)
    cmap = LinearSegmentedColormap.from_list('perf', ['#FF0000', '#FFFF00', '#00FF00'])

    # Configuration du style
    plt.style.use('default')
    plt.rcParams.update({
        'axes.facecolor': 'white',
        'axes.edgecolor': 'gray',
        'axes.grid': True,
        'grid.color': 'lightgray',
        'font.size': 12
    })

    # Initialisation avec espace dédié pour la colorbar
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, polar=True)

    categories = df['kpi_name'].tolist()
    N = len(categories)
    angles = [n / N * 2 * pi for n in range(N)]
    angles += angles[:1]

    values = df['moyenne'].tolist()
    values += values[:1]

    # Création d'un mappable pour la colorbar
    norm = plt.Normalize(df['moyenne'].min(), df['moyenne'].max())
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  # Nécessaire pour Matplotlib > 3.3

    # Tracé avec dégradé
    for i in range(N):
        color = cmap(df['normalized'].iloc[i])
        line, = ax.plot([angles[i], angles[(i + 1) % N]],
                        [values[i], values[(i + 1) % N]],
                        color=color, linewidth=4, marker='o', markersize=12)

        # Zone colorée
        ax.fill([angles[i], angles[(i + 1) % N], 0],
                [values[i], values[(i + 1) % N], 0],
                color=color, alpha=0.15)

        # Étiquettes de valeur avec couleur adaptée
        text_color = 'black' if df['normalized'].iloc[i] < 0.7 else 'white'
        ax.text(angles[i], values[i] * 1.05, f"{values[i]:.1f}",
                ha='center', va='center', color=text_color,
                bbox=dict(facecolor=color, alpha=0.7, pad=3, edgecolor='none'))

    # Paramétrage
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # Ajout correct de la colorbar
    cbar = plt.colorbar(sm, ax=ax, pad=0.08, shrink=0.7)
    cbar.set_label('Performance relative', rotation=270, labelpad=25)

    plt.title("Performance des KPIs avec échelle chromatique", pad=40, fontsize=14)

    plt.savefig(CONFIG['output_file'], dpi=150, bbox_inches='tight')
    print(f"\n💾 Diagramme sauvegardé sous {CONFIG['output_file']} (150 DPI)")
    plt.close()


if __name__ == "__main__":
    if not verifier_connexion():
        print("❌ Impossible de se connecter à l'API. Vérifiez:")
        print(f"- Que l'URL {CONFIG['url']} est correcte")
        print("- Que le serveur est en cours d'exécution")
        sys.exit(1)

    raw_data = charger_donnees()

    if raw_data is None:
        sys.exit(1)

    try:
        df = pd.DataFrame(raw_data)
        stats = preparer_donnees(df)
        creer_radar_grade(stats)
        print("\n✅ Analyse terminée avec succès!")
    except Exception as e:
        print(f"❌ Erreur lors du traitement: {str(e)}")
        sys.exit(1)
