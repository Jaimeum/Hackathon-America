"""
Perfilador del Club América - Versión optimizada con PCA
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

from src.utils.data_fetcher import StatsBombDataFetcher
from src.config import AMERICA_CORE_METRICS, TEAM_CORE_FEATURES


class AmericaProfiler:
    """Crea perfil completo del América con rankings vs competencia"""
    
    def __init__(self):
        self.fetcher = StatsBombDataFetcher()
        self.profile = None
        self.seasons_data = None
        self.all_teams_data = None
        
    def build_profile(
        self,
        seasons: List[Tuple[int, int]],
        team_name: str = "América"
    ) -> Dict:
        """
        Construye perfil completo del América
        
        Args:
            seasons: Lista de (competition_id, season_id)
            team_name: Nombre del equipo
            
        Returns:
            Perfil completo con rankings
        """
        print(f"Construyendo perfil del {team_name}...")
        print(f"Analizando {len(seasons)} temporadas\n")
        
        # Recopilar datos
        all_team_stats = []
        america_stats = []
        all_matches = []
        
        for comp_id, season_id in seasons:
            print(f"Temporada {season_id}...")
            
            try:
                team_stats = self.fetcher.get_team_season_stats(comp_id, season_id)
                all_team_stats.append(team_stats)
                
                america_data = team_stats[
                    team_stats['team_name'].str.contains(team_name, case=False, na=False)
                ]
                
                if not america_data.empty:
                    america_stats.append(america_data.iloc[0])
                    print(f"Stats obtenidas")
                
                matches = self.fetcher.get_matches(comp_id, season_id)
                america_matches = matches[
                    (matches['home_team'].str.contains(team_name, case=False, na=False)) |
                    (matches['away_team'].str.contains(team_name, case=False, na=False))
                ]
                
                if not america_matches.empty:
                    all_matches.append(america_matches)
                    print(f"{len(america_matches)} partidos")
                    
            except Exception as e:
                print(f"Error: {e}")
        
        if not america_stats:
            raise ValueError("No se encontraron datos del América")
        
        # Consolidar
        self.all_teams_data = pd.concat(all_team_stats, ignore_index=True)
        self.seasons_data = pd.DataFrame(america_stats)
        matches_df = pd.concat(all_matches, ignore_index=True) if all_matches else pd.DataFrame()
        
        print(f"\nConsolidado: {len(self.seasons_data)} temporadas, {len(matches_df)} partidos")
        print(f"Total equipos en dataset: {self.all_teams_data['team_name'].nunique()}\n")
        
        # Construir perfil
        self.profile = self._build_comprehensive_profile(matches_df)
        
        self._print_summary()
        
        return self.profile
    
    def _build_comprehensive_profile(self, matches: pd.DataFrame) -> Dict:
        """Construye perfil con promedios, tendencias y rankings"""
        
        profile = {
            'metadata': {
                'n_seasons': len(self.seasons_data),
                'n_matches': len(matches),
                'team_name': 'Club América',
                'win_rate': self._calculate_win_rate(matches)
            },
            'averages': {},      # Promedios de 4 temporadas
            'trends': {},        # Tendencias temporales
            'consistency': {},   # Variabilidad
            'rankings': {},      # Percentiles vs otros equipos
            'dimensions': {}     # Scores por dimensión
        }
        
        # 1. PROMEDIOS por dimensión
        for dimension, metrics in AMERICA_CORE_METRICS.items():
            values = []
            for metric in metrics:
                if metric in self.seasons_data.columns:
                    values.append(self.seasons_data[metric].mean())
            
            profile['averages'][dimension] = np.mean(values) if values else 0.0
        
        # 2. TENDENCIAS (primera vs última temporada)
        if len(self.seasons_data) >= 2:
            first_season = self.seasons_data.iloc[0]
            last_season = self.seasons_data.iloc[-1]
            
            for dimension, metrics in AMERICA_CORE_METRICS.items():
                values_first = []
                values_last = []
                
                for metric in metrics:
                    if metric in self.seasons_data.columns:
                        values_first.append(first_season[metric])
                        values_last.append(last_season[metric])
                
                if values_first and values_last:
                    trend = np.mean(values_last) - np.mean(values_first)
                    profile['trends'][dimension] = {
                        'change': trend,
                        'direction': 'mejorando' if trend > 0 else 'empeorando' if trend < 0 else 'estable'
                    }
        
        # 3. CONSISTENCIA (desviación estándar)
        for dimension, metrics in AMERICA_CORE_METRICS.items():
            stds = []
            for metric in metrics:
                if metric in self.seasons_data.columns:
                    stds.append(self.seasons_data[metric].std())
            
            profile['consistency'][dimension] = np.mean(stds) if stds else 0.0
        
        # 4. RANKINGS (percentiles vs otros equipos)
        profile['rankings'] = self._calculate_rankings()
        
        # 5. SCORES POR DIMENSIÓN (0-100)
        for dimension in AMERICA_CORE_METRICS.keys():
            percentile = profile['rankings'].get(dimension, 50)
            profile['dimensions'][dimension] = percentile
        
        return profile
    
    def _calculate_rankings(self) -> Dict:
        """Calcula percentiles del América vs todos los equipos"""
        rankings = {}
        
        for dimension, metrics in AMERICA_CORE_METRICS.items():
            percentiles = []
            
            for metric in metrics:
                if metric in self.all_teams_data.columns:
                    # Valor promedio del América
                    america_value = self.seasons_data[metric].mean()
                    
                    # Distribución de todos los equipos
                    all_values = self.all_teams_data[metric].dropna()
                    
                    if len(all_values) > 0:
                        # Calcular percentil
                        percentile = (all_values <= america_value).sum() / len(all_values) * 100
                        percentiles.append(percentile)
            
            rankings[dimension] = np.mean(percentiles) if percentiles else 50.0
        
        return rankings
    
    def _calculate_win_rate(self, matches: pd.DataFrame) -> float:
        """Calcula % de victorias"""
        if matches.empty:
            return 0.0
        
        wins = 0
        for _, match in matches.iterrows():
            is_home = 'América' in str(match.get('home_team', ''))
            home_score = match.get('home_score', 0)
            away_score = match.get('away_score', 0)
            
            if is_home and home_score > away_score:
                wins += 1
            elif not is_home and away_score > home_score:
                wins += 1
        
        return (wins / len(matches)) * 100
    
    def get_position_requirements(self, position: str) -> Dict:
        """Define qué busca el América por posición según su perfil"""
        if not self.profile:
            raise ValueError("Construye el perfil primero")
        
        # Ajustar pesos según fortalezas del América
        offensive_strength = self.profile['rankings'].get('offensive_quality', 50)
        pressing_strength = self.profile['rankings'].get('pressing_intensity', 50)
        
        requirements = {
            'FWD': {
                'attacking_weight': 0.70,
                'defensive_weight': 0.10,
                'passing_weight': 0.20,
                'key_dimensions': ['offensive_quality', 'shot_quality']
            },
            'MED': {
                'attacking_weight': 0.35,
                'defensive_weight': 0.35,
                'passing_weight': 0.30,
                'key_dimensions': ['possession_control', 'pressing_intensity']
            },
            'DEF': {
                'attacking_weight': 0.10,
                'defensive_weight': 0.65,
                'passing_weight': 0.25,
                'key_dimensions': ['defensive_quality', 'pressing_intensity']
            },
            'GK': {
                'attacking_weight': 0.00,
                'defensive_weight': 0.85,
                'passing_weight': 0.15,
                'key_dimensions': ['defensive_quality']
            },
            'Forward': {
                'attacking_weight': 0.70,
                'defensive_weight': 0.10,
                'passing_weight': 0.20,
                'key_dimensions': ['offensive_quality', 'shot_quality']
            },
            'Midfilder': {
                'attacking_weight': 0.35,
                'defensive_weight': 0.35,
                'passing_weight': 0.30,
                'key_dimensions': ['possession_control', 'pressing_intensity']
            },
            'Defender': {
                'attacking_weight': 0.10,
                'defensive_weight': 0.65,
                'passing_weight': 0.25,
                'key_dimensions': ['defensive_quality', 'pressing_intensity']
            },
            'Goalkeeper': {
                'attacking_weight': 0.00,
                'defensive_weight': 0.85,
                'passing_weight': 0.15,
                'key_dimensions': ['defensive_quality']
            }
        }

        return requirements.get(position, requirements['Midfielder']) #Si hay un typo en la posicion, utiliza MED como default

    def _print_summary(self):
        """Imprime resumen del perfil"""
        if not self.profile:
            return
        
        print("=" * 70)
        print("PERFIL DEL CLUB AMÉRICA")
        print("=" * 70)
        
        meta = self.profile['metadata']
        print(f"\nMetadata:")
        print(f"   Temporadas: {meta['n_seasons']}")
        print(f"   Partidos: {meta['n_matches']}")
        print(f"   Win Rate: {meta['win_rate']:.1f}%")
        
        print(f"\nRANKINGS VS COMPETENCIA (Percentiles):")
        for dimension, percentile in sorted(self.profile['rankings'].items(), key=lambda x: x[1], reverse=True):
            if percentile >= 70:
                status = "[Alto]"
            elif percentile >= 50:
                status = "[Medio]"
            else:
                status = "[Bajo]"
            dimension_name = dimension.replace('_', ' ').title()
            print(f"   {status:10s} {dimension_name:25s}: {percentile:5.1f}%")

        if self.profile['trends']:
            print(f"\nTENDENCIAS (Primera vs Última Temporada):")
            for dimension, trend_data in self.profile['trends'].items():
                direction = trend_data['direction']
                change = trend_data['change']
                if direction == 'mejorando':
                    trend_label = "[Mejorando]"
                elif direction == 'empeorando':
                    trend_label = "[Empeorando]"
                else:
                    trend_label = "[Estable]"
                dimension_name = dimension.replace('_', ' ').title()
                print(f"   {trend_label:12s} {dimension_name:25s}: {direction} ({change:+.3f})")

        
        print("\n" + "=" * 70 + "\n")
    
    def export_profile(self, filepath: str = "data/results/america_profile.json"):
        """Exporta perfil a JSON"""
        import json
        from pathlib import Path
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.profile, f, indent=2, default=str)
        
        print(f"Perfil exportado: {filepath}")