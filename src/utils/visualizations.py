"""Utilidades para visualizaciones"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import List

# Configuración de estilo
plt.rcParams['figure.figsize'] = (10, 6)

def plot_comparison_radar(
    players_data: pd.DataFrame,
    player_names: List[str],
    features: List[str],
    title: str = "Comparación de Jugadores"
):
    colors = ['#00529F', '#FDB913', '#E4002B', '#00A859']

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

    # Limpiar nombres de features
    categories = [
        f.replace('player_season_', '')
         .replace('_norm', '')
         .replace('_90', '')
         .replace('_', ' ')
         .title() 
        for f in features
    ]
    
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    # Obtener valores globales para ajustar los límites
    selected = players_data[players_data['player_name'].isin(player_names)][features]
    global_min = selected.min().min()
    global_max = selected.max().max()
    margin = (global_max - global_min) * 0.1  # margen de 10%
    
    for idx, name in enumerate(player_names):
        player = players_data.loc[players_data['player_name'] == name]
        if player.empty:
            print(f"Jugador '{name}' no encontrado")
            continue
        
        player = player.iloc[0]
        values = player[features].astype(float).values.tolist()
        values += values[:1]
        color = colors[idx % len(colors)]

        ax.plot(angles, values, 'o-', linewidth=2, label=name, color=color)
        ax.fill(angles, values, alpha=0.15, color=color)

    # Configuración de ejes
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_yticklabels([])  # sin etiquetas radiales
    ax.set_ylim(global_min - margin, global_max + margin)

    # Estética
    ax.set_title(title, size=16, pad=30)
    ax.legend(loc='upper left', bbox_to_anchor=(1.1, 1.05))
    ax.grid(True)

    plt.subplots_adjust(left=0.05, right=0.85, top=0.9, bottom=0.05)
    plt.show()
    return fig

def plot_radar_chart(
    player_data: pd.Series,
    features: List[str],
    title: str = "Perfil del Jugador",
    color: str = '#00529F'
):
    """
    Crea un gráfico de radar para un solo jugador
    
    Args:
        player_data: Serie con los datos del jugador
        features: Lista de features a mostrar
        title: Título del gráfico
        color: Color del gráfico (por defecto azul América)
        
    Returns:
        Figure de matplotlib
    """
    # Preparar categorías
    categories = [
        f.replace('player_season_', '')
         .replace('_norm', '')
         .replace('_90', '')
         .replace('_', ' ')
         .title() 
        for f in features
    ]
    
    # Obtener valores
    values = player_data[features].values.tolist()
    
    # Número de variables
    N = len(categories)
    
    # Ángulos
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    values += values[:1]
    angles += angles[:1]
    
    # Plot
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    ax.plot(angles, values, 'o-', linewidth=2, color=color)
    ax.fill(angles, values, alpha=0.25, color=color)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 1)
    ax.set_title(title, size=16, pad=20)
    ax.grid(True)
    
    plt.tight_layout()
    return fig