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
    """
    Crea un gráfico de radar comparando múltiples jugadores
    
    Args:
        players_data: DataFrame con todos los jugadores
        player_names: Lista de nombres de jugadores a comparar
        features: Lista de features (columnas) a graficar
        title: Título del gráfico
        
    Returns:
        Figure de matplotlib
    """
    # Colores del Club América
    colors = ['#00529F', '#FDB913', '#E4002B', '#00A859']
    
    # Configurar el gráfico polar
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # Preparar categorías (nombres de las features limpiadas)
    categories = [
        f.replace('player_season_', '')
         .replace('_norm', '')
         .replace('_90', '')
         .replace('_', ' ')
         .title() 
        for f in features
    ]
    
    # Número de variables
    N = len(categories)
    
    # Calcular ángulos para cada eje
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Cerrar el círculo
    
    # Graficar cada jugador
    for idx, name in enumerate(player_names):
        # Obtener datos del jugador
        player = players_data[players_data['player_name'] == name]
        
        if player.empty:
            print(f"⚠️ Jugador '{name}' no encontrado")
            continue
        
        player = player.iloc[0]
        
        # Obtener valores de las features
        values = player[features].values.tolist()
        values += values[:1]  # Cerrar el círculo
        
        # Color para este jugador
        color = colors[idx % len(colors)]
        
        # Graficar
        ax.plot(angles, values, 'o-', linewidth=2, label=name, color=color)
        ax.fill(angles, values, alpha=0.15, color=color)
    
    # Configurar ejes
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_ylim(0, 1)
    ax.set_title(title, size=16, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)
    
    plt.tight_layout()
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