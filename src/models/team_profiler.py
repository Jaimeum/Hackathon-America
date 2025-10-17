"""
Perfilador de equipos - Analiza el estilo de juego y características de un equipo
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

from src.utils.data_fetcher import StatsBombDataFetcher


class AmericaProfiler:
    """
    Crea un perfil completo del Club América basado en:
    - Estadísticas de múltiples temporadas
    - Estilo de juego promedio
    - Métricas clave por posición
    """
    
    def __init__(self):
        self.fetcher = StatsBombDataFetcher()
        self.profile = None
        self.seasons_data = []
        
    def build_profile(
        self,
        seasons: List[Tuple[int, int]],  # Lista de (competition_id, season_id)
        team_name: str = "América"
    ) -> Dict:
        """
        Construye el perfil del América analizando múltiples temporadas
        
        Args:
            seasons: Lista de tuplas (competition_id, season_id)
            team_name: Nombre del equipo (variaciones posibles)
            
        Returns:
            Diccionario con el perfil completo del equipo
        """
        print(f"Construyendo perfil del {team_name}...")
        print(f"Analizando {len(seasons)} temporadas\n")
        
        # Recopilar datos de todas las temporadas
        all_team_stats = []
        all_matches = []
        
        for comp_id, season_id in seasons:
            print(f"Temporada {season_id}...")
            
            # Estadísticas de temporada
            try:
                team_season_stats = self.fetcher.get_team_season_stats(comp_id, season_id)
                america_stats = team_season_stats[
                    team_season_stats['team_name'].str.contains(team_name, case=False, na=False)
                ]
                
                if not america_stats.empty:
                    all_team_stats.append(america_stats.iloc[0])
                    print(f"Estadísticas de temporada obtenidas")
                
            except Exception as e:
                print(f"Error en estadísticas de temporada: {e}")
            
            # Estadísticas de partidos individuales
            try:
                matches = self.fetcher.get_matches(comp_id, season_id)
                america_matches = matches[
                    (matches['home_team'].str.contains(team_name, case=False, na=False)) |
                    (matches['away_team'].str.contains(team_name, case=False, na=False))
                ]
                
                if not america_matches.empty:
                    all_matches.append(america_matches)
                    print(f" {len(america_matches)} partidos encontrados")
                    
            except Exception as e:
                print(f"Error en partidos: {e}")
        
        if not all_team_stats:
            raise ValueError("No se encontraron estadísticas del América en las temporadas especificadas")
        
        # Consolidar datos
        team_stats_df = pd.DataFrame(all_team_stats)
        matches_df = pd.concat(all_matches, ignore_index=True) if all_matches else pd.DataFrame()
        
        print(f"\nDatos consolidados: {len(team_stats_df)} temporadas, {len(matches_df)} partidos\n")
        
        # Construir perfil agregado
        self.profile = self._build_aggregated_profile(team_stats_df, matches_df)
        self.seasons_data = team_stats_df
        
        print("Perfil del América completado\n")
        self._print_profile_summary()
        
        return self.profile
    
    def _build_aggregated_profile(
        self,
        team_stats: pd.DataFrame,
        matches: pd.DataFrame
    ) -> Dict:
        """
        Agrega estadísticas de múltiples temporadas en un perfil único
        """
        profile = {
            'metadata': {
                'n_seasons': len(team_stats),
                'n_matches': len(matches),
                'team_name': 'América'
            },
            'playing_style': {},
            'offensive_metrics': {},
            'defensive_metrics': {},
            'possession_metrics': {},
            'key_stats': {}
        }
        
        # Identificar columnas numéricas
        numeric_cols = team_stats.select_dtypes(include=[np.number]).columns
        
        # Estilo de juego general
        if 'possession' in team_stats.columns:
            profile['playing_style']['avg_possession'] = team_stats['possession'].mean()
        
        if 'passes' in team_stats.columns and 'passes_completed' in team_stats.columns:
            profile['playing_style']['avg_pass_completion'] = (
                team_stats['passes_completed'].sum() / team_stats['passes'].sum()
            ) * 100
        
        # Métricas ofensivas
        offensive_cols = [col for col in numeric_cols if any(
            keyword in col.lower() for keyword in ['shot', 'goal', 'attack', 'offensive']
        )]
        
        for col in offensive_cols:
            profile['offensive_metrics'][col] = {
                'mean': team_stats[col].mean(),
                'std': team_stats[col].std(),
                'min': team_stats[col].min(),
                'max': team_stats[col].max()
            }
        
        # Métricas defensivas
        defensive_cols = [col for col in numeric_cols if any(
            keyword in col.lower() for keyword in ['tackle', 'intercept', 'defensive', 'block']
        )]
        
        for col in defensive_cols:
            profile['defensive_metrics'][col] = {
                'mean': team_stats[col].mean(),
                'std': team_stats[col].std(),
                'min': team_stats[col].min(),
                'max': team_stats[col].max()
            }
        
        # Métricas de posesión
        possession_cols = [col for col in numeric_cols if any(
            keyword in col.lower() for keyword in ['pass', 'possession', 'dribble']
        )]
        
        for col in possession_cols:
            profile['possession_metrics'][col] = {
                'mean': team_stats[col].mean(),
                'std': team_stats[col].std()
            }
        
        # Estadísticas clave agregadas
        profile['key_stats'] = {
            'avg_goals_per_game': team_stats.get('goals', pd.Series([0])).mean(),
            'avg_goals_conceded': team_stats.get('goals_conceded', pd.Series([0])).mean(),
            'avg_shots_per_game': team_stats.get('shots', pd.Series([0])).mean(),
            'win_rate': self._calculate_win_rate(matches) if not matches.empty else 0
        }
        
        return profile
    
    def _calculate_win_rate(self, matches: pd.DataFrame) -> float:
        """Calcula el % de victorias del América"""
        if matches.empty:
            return 0.0
        
        wins = 0
        for _, match in matches.iterrows():
            if match['home_team'] == 'América':
                if match.get('home_score', 0) > match.get('away_score', 0):
                    wins += 1
            else:
                if match.get('away_score', 0) > match.get('home_score', 0):
                    wins += 1
        
        return (wins / len(matches)) * 100
    
    def _print_profile_summary(self):
        """Imprime un resumen del perfil"""
        if not self.profile:
            return
        
        print("=" * 60)
        print("PERFIL DEL CLUB AMÉRICA")
        print("=" * 60)
        
        meta = self.profile['metadata']
        print(f"\nMetadata:")
        print(f"   Temporadas analizadas: {meta['n_seasons']}")
        print(f"   Partidos totales: {meta['n_matches']}")
        
        key_stats = self.profile['key_stats']
        print(f"\nEstadísticas Clave:")
        print(f"   Goles por partido: {key_stats.get('avg_goals_per_game', 0):.2f}")
        print(f"   Goles en contra: {key_stats.get('avg_goals_conceded', 0):.2f}")
        print(f"   Tiros por partido: {key_stats.get('avg_shots_per_game', 0):.2f}")
        print(f"   % Victorias: {key_stats.get('win_rate', 0):.1f}%")
        
        if self.profile['playing_style']:
            print(f"\nEstilo de Juego:")
            for key, value in self.profile['playing_style'].items():
                print(f"   {key}: {value:.2f}")
        
        print("\n" + "=" * 60 + "\n")
    
    def get_position_requirements(self, position: str) -> Dict:
        """
        Define qué busca el América en cada posición según su estilo
        
        Args:
            position: Posición del jugador
            
        Returns:
            Diccionario con pesos de características importantes
        """
        # Esto se puede ajustar basado en el análisis del perfil
        # Por ahora usamos valores por defecto inteligentes
        
        requirements = {
            'Forward': {
                'attacking_weight': 0.7,
                'defensive_weight': 0.1,
                'passing_weight': 0.2,
                'key_metrics': ['goals_90', 'xg_90', 'shot_touch_ratio']
            },
            'Midfielder': {
                'attacking_weight': 0.4,
                'defensive_weight': 0.3,
                'passing_weight': 0.3,
                'key_metrics': ['assists_90', 'key_passes_90', 'obv_pass_90']
            },
            'Defender': {
                'attacking_weight': 0.1,
                'defensive_weight': 0.7,
                'passing_weight': 0.2,
                'key_metrics': ['tackles_90', 'interceptions_90', 'aerial_ratio']
            },
            'Goalkeeper': {
                'attacking_weight': 0.0,
                'defensive_weight': 0.9,
                'passing_weight': 0.1,
                'key_metrics': ['save_ratio', 'obv_90']
            },
            'FWD': {
                'attacking_weight': 0.7,
                'defensive_weight': 0.1,
                'passing_weight': 0.2,
                'key_metrics': ['goals_90', 'xg_90', 'shot_touch_ratio']
            },
            'MED': {
                'attacking_weight': 0.4,
                'defensive_weight': 0.3,
                'passing_weight': 0.3,
                'key_metrics': ['assists_90', 'key_passes_90', 'obv_pass_90']
            },
            'DEF': {
                'attacking_weight': 0.1,
                'defensive_weight': 0.7,
                'passing_weight': 0.2,
                'key_metrics': ['tackles_90', 'interceptions_90', 'aerial_ratio']
            },
            'GK': {
                'attacking_weight': 0.0,
                'defensive_weight': 0.9,
                'passing_weight': 0.1,
                'key_metrics': ['save_ratio', 'obv_90']
            }
        }
        
        return requirements.get(position, requirements['MED'])
    
    def export_profile(self, filepath: str = "data/results/america_profile.json"):
        """Exporta el perfil a JSON"""
        import json
        from pathlib import Path
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.profile, f, indent=2, default=str)
        
        print(f"Perfil exportado a: {filepath}")