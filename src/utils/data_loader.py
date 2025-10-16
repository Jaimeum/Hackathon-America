"""Utilidades para carga de datos"""
import pandas as pd
from pathlib import Path
from typing import Optional
from src.config import PLAYERS_DATA

class DataLoader:
    """Clase para cargar y filtrar datos de jugadores"""
    
    def __init__(self, data_path: Optional[Path] = None):
        """
        Inicializa el cargador de datos
        
        Args:
            data_path: Ruta al CSV de jugadores (opcional)
        """
        self.data_path = data_path or PLAYERS_DATA
        self._df = None
    
    @property
    def df(self) -> pd.DataFrame:
        """Carga los datos solo cuando se necesitan (lazy loading)"""
        if self._df is None:
            print(f"Cargando datos desde: {self.data_path}")
            self._df = pd.read_csv(self.data_path)
            print(f"Cargados {len(self._df)} registros")
        return self._df
    
    def get_players(
        self,
        position: Optional[str] = None,
        min_minutes: int = 0,
    ) -> pd.DataFrame:
        """
        Filtra jugadores según criterios
        
        Args:
            position: Posición del jugador (Forward, Midfielder, Defender, Goalkeeper)
            min_minutes: Minutos mínimos jugados en la temporada
            
        Returns:
            DataFrame filtrado
        """
        df = self.df.copy()
        
        # Filtrar por minutos
        if min_minutes > 0:
            df = df[df['player_season_minutes'] >= min_minutes]
        
        # Filtrar por posición
        if position:
            df = df[df['position_category'] == position]
        
        return df
    
    def get_player_by_name(self, player_name: str) -> pd.DataFrame:
        """
        Busca un jugador por nombre (búsqueda parcial)
        
        Args:
            player_name: Nombre o parte del nombre del jugador
            
        Returns:
            DataFrame con jugadores que coinciden
        """
        df = self.df.copy()
        mask = df['player_name'].str.contains(player_name, case=False, na=False)
        return df[mask]
    
    def get_summary(self) -> dict:
        """
        Genera un resumen estadístico del dataset
        
        Returns:
            Diccionario con estadísticas básicas
        """
        df = self.df
        return {
            'total_players': len(df),
            'total_teams': df['team_name'].nunique(),
            'total_seasons': df['season_name'].nunique(),
            'positions': df['position_category'].value_counts().to_dict(),
            'avg_minutes': round(df['player_season_minutes'].mean(), 1)
        }