"""
Analizador de compatibilidad jugador-equipo (Team Fit Analysis)
Pesos: 35% Technical | 30% Tactical | 35% Impact
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from src.utils.data_loader import DataLoader
from src.config import NORMALIZED_FEATURES, TEAM_TO_PLAYER_MAPPING


class TeamFitAnalyzer:
    """Analiza compatibilidad de jugadores con el Club América"""
    
    def __init__(self, america_profile: Dict, data_loader: Optional[DataLoader] = None):
        self.america_profile = america_profile
        self.data_loader = data_loader or DataLoader()
        self.scaler = StandardScaler()
        self._fitted = False
        
    def fit(self, min_minutes: int = 500):
        """Prepara el analizador"""
        print(f"Preparando Team Fit Analyzer...")
        
        self.players_df = self.data_loader.get_players(min_minutes=min_minutes)
        self.features = self.players_df[NORMALIZED_FEATURES].fillna(0)
        self._features_scaled = self.scaler.fit_transform(self.features)
        
        self._fitted = True
        print(f"Listo para {len(self.players_df)} jugadores\n")
        
        return self
    
    def calculate_team_fit(self, player_name: str, position: Optional[str] = None) -> Dict:
        """Calcula fit de un jugador con el América"""
        if not self._fitted:
            raise ValueError("Ejecuta .fit() primero")
        
        player_data = self.data_loader.get_player_by_name(player_name)
        
        if player_data.empty:
            raise ValueError(f"'{player_name}' no encontrado")
        
        player = player_data.iloc[0]
        position = position or player['position_category']
        
        print(f"Analizando a {player['player_name']}")
        print(f"   Posición: {position} ({player['primary_position']})")
        print(f"   Equipo: {player['team_name']}\n")
        
        # Calcular scores
        technical_fit = self._calculate_technical_fit(player, position)
        tactical_fit = self._calculate_tactical_fit(player, position)
        impact_score = self._calculate_impact_score(player, position)
        
        # Score final: 35% Technical | 30% Tactical | 35% Impact
        overall_fit = (
            0.35 * technical_fit +
            0.30 * tactical_fit +
            0.35 * impact_score
        )
        
        fit_scores = {
            'player_name': player['player_name'],
            'position': position,
            'current_team': player['team_name'],
            'overall_fit': overall_fit,
            'technical_fit': technical_fit,
            'tactical_fit': tactical_fit,
            'impact_score': impact_score,
            'strengths': [],
            'concerns': [],
            'key_metrics': self._extract_key_metrics(player, position)
        }
        
        # Análisis cualitativo
        fit_scores['strengths'], fit_scores['concerns'] = self._analyze_fit(player, position, fit_scores)
        
        self._print_report(fit_scores)
        
        return fit_scores
    
    def recommend_best_fits(
        self,
        position: str,
        top_n: int = 3,
        min_overall_fit: float = 60.0,
        exclude_teams: List[str] = None
    ) -> pd.DataFrame:
        """Recomienda top N jugadores para el América"""
        if not self._fitted:
            raise ValueError("Ejecuta .fit() primero")
        
        print(f"Buscando top {top_n} {position}s para el América...")
        print(f"   Fit mínimo: {min_overall_fit:.1f}/100\n")
        
        candidates = self.players_df[self.players_df['position_category'] == position].copy()
        
        america_variants = ['América', 'America', 'CF América', 'Club América']
        for variant in america_variants:
            candidates = candidates[~candidates['team_name'].str.contains(variant, case=False, na=False)]

        if exclude_teams:
            candidates = candidates[~candidates['team_name'].isin(exclude_teams)]
        
        if candidates.empty:
            raise ValueError(f"Sin candidatos para {position}")
        
        results = []
        
        for idx, player in candidates.iterrows():
            try:
                technical = self._calculate_technical_fit(player, position)
                tactical = self._calculate_tactical_fit(player, position)
                impact = self._calculate_impact_score(player, position)
                
                overall = 0.35 * technical + 0.30 * tactical + 0.35 * impact
                
                results.append({
                    'player_name': player['player_name'],
                    'team_name': player['team_name'],
                    'primary_position': player['primary_position'],
                    'minutes': player['player_season_minutes'],
                    'overall_fit': overall,
                    'technical_fit': technical,
                    'tactical_fit': tactical,
                    'impact_score': impact,
                    'goals_90': player.get('player_season_goals_90', 0),
                    'assists_90': player.get('player_season_assists_90', 0),
                    'obv_90': player.get('player_season_obv_90', 0)
                })
            except:
                continue
        
        recs = pd.DataFrame(results)
        recs = recs[recs['overall_fit'] >= min_overall_fit]
        recs = recs.nlargest(top_n, 'overall_fit')
        
        print(f"{len(recs)} recomendaciones encontradas\n")
        
        return recs.reset_index(drop=True)
    
    def _calculate_technical_fit(self, player: pd.Series, position: str) -> float:
        """Habilidades técnicas del jugador (0-100)"""
        position_features = {
            'FWD': ['goals_90_norm', 'np_xg_90_norm', 'shot_touch_ratio_norm', 'obv_shot_90_norm'],
            'MED': ['assists_90_norm', 'key_passes_90_norm', 'obv_pass_90_norm', 'pressures_90_norm'],
            'DEF': ['tackles_90_norm', 'interceptions_90_norm', 'defensive_actions_90_norm', 'aerial_ratio_norm'],
            'GK': ['save_ratio_norm'],
            'Forward': ['goals_90_norm', 'np_xg_90_norm', 'shot_touch_ratio_norm', 'obv_shot_90_norm'],
            'Midfielder': ['assists_90_norm', 'key_passes_90_norm', 'obv_pass_90_norm', 'pressures_90_norm'],
            'Defender': ['tackles_90_norm', 'interceptions_90_norm', 'defensive_actions_90_norm', 'aerial_ratio_norm'],
            'Goalkeeper': ['save_ratio_norm']
        }
        
        features = position_features.get(position, position_features['MED']) #De nuevo, este es nuestro default
        features_full = [f'player_season_{f}' for f in features]
        
        scores = [player[f] for f in features_full if f in player.index]
        
        if not scores:
            return 50.0
        # Convertir percentil (0-1) a score más realista
        # Usar una función sigmoidea para comprimir valores extremos
        raw_score = np.mean(scores)
        
        # Escala: percentil 0.5 = 50pts, percentil 0.9 = 80pts, percentil 0.99 = 95pts
        # Fórmula: 100 * (1 / (1 + exp(-6*(x-0.5))))
        from math import exp
        scaled_score = 100 * (1 / (1 + exp(-6 * (raw_score - 0.5))))
        
        return scaled_score
    
    def _calculate_tactical_fit(self, player: pd.Series, position: str) -> float:
        """Adaptabilidad al estilo del América (0-100)"""
        # Métricas de versatilidad táctica
        tactical_metrics = [
            'player_season_pressures_90_norm',
            'player_season_obv_90_norm',
            'player_season_dribbles_90_norm',
            'player_season_passes_into_box_90_norm'
        ]
        
        scores = [player[m] for m in tactical_metrics if m in player.index]
    
        if not scores:
            return 50.0
        
        raw_score = np.mean(scores)
    
        # Aplicar misma transformación sigmoidea
        from math import exp
        base_score = 100 * (1 / (1 + exp(-6 * (raw_score - 0.5))))
        
        # Bonus moderado por match con perfil
        america_rankings = self.america_profile.get('rankings', {})
        
        bonus = 0.0
        if america_rankings.get('pressing_intensity', 0) > 60:
            pressing_score = player.get('player_season_pressures_90_norm', 0.5)
            if pressing_score > 0.7:
                bonus = 3.0  # Bonus pequeño
        
        return min(base_score + bonus, 100.0)
    
    def _calculate_impact_score(self, player: pd.Series, position: str) -> float:
        """Impacto esperado en el equipo (0-100)"""
        obv_norm = player.get('player_season_obv_90_norm', 0.5)
    
        # Transformación sigmoidea
        from math import exp
        obv_score = 100 * (1 / (1 + exp(-6 * (obv_norm - 0.5))))
        
        # Factor de confiabilidad
        minutes = player.get('player_season_minutes', 0)
        reliability = 0.8 + (0.2 * min(minutes / 2500, 1.0))
        
        final_score = obv_score * reliability
        
        return min(final_score, 100.0)
    
    def _extract_key_metrics(self, player: pd.Series, position: str) -> Dict:
        """Extrae métricas clave"""
        return {
            'minutes': player.get('player_season_minutes', 0),
            'goals_90': player.get('player_season_goals_90', 0),
            'assists_90': player.get('player_season_assists_90', 0),
            'xg_90': player.get('player_season_np_xg_90', 0),
            'obv_90': player.get('player_season_obv_90', 0),
            'pressures_90': player.get('player_season_pressures_90', 0)
        }
    
    def _analyze_fit(self, player: pd.Series, position: str, scores: Dict) -> tuple:
        """Análisis cualitativo"""
        strengths = []
        concerns = []
        
        if scores['technical_fit'] >= 75:
            strengths.append("Excelentes habilidades técnicas")
        elif scores['technical_fit'] < 60:
            concerns.append("Habilidades técnicas por debajo del estándar")
        
        if scores['tactical_fit'] >= 75:
            strengths.append("Alta adaptabilidad táctica")
        
        if scores['impact_score'] >= 70:
            strengths.append("Alto impacto proyectado")
        elif scores['impact_score'] < 55:
            concerns.append("Impacto limitado esperado")
        
        minutes = player.get('player_season_minutes', 0)
        if minutes >= 2000:
            strengths.append(f"Experiencia sólida ({minutes} minutos)")
        elif minutes < 1000:
            concerns.append(f"Experiencia limitada ({minutes} minutos)")
        
        return strengths, concerns
    
    def _print_report(self, scores: Dict):
        """Imprime reporte de compatibilidad"""
        print("=" * 70)
        print("ANÁLISIS DE COMPATIBILIDAD - CLUB AMÉRICA")
        print("=" * 70)
        
        print(f"\n{scores['player_name']}")
        print(f"{scores['position']} | {scores['current_team']}\n")
        
        print("SCORES DE COMPATIBILIDAD:")
        print(f"   Overall Fit:    {scores['overall_fit']:.1f}/100")
        print(f"   Technical Fit:  {scores['technical_fit']:.1f}/100 (35% peso)")
        print(f"   Tactical Fit:   {scores['tactical_fit']:.1f}/100 (30% peso)")
        print(f"   Impact Score:   {scores['impact_score']:.1f}/100 (35% peso)")
        
        if scores['strengths']:
            print(f"\nFORTALEZAS:")
            for s in scores['strengths']:
                print(f"   • {s}")
        
        if scores['concerns']:
            print(f"\nÁREAS DE ATENCIÓN:")
            for c in scores['concerns']:
                print(f"   • {c}")
        
        m = scores['key_metrics']
        print(f"\nMÉTRICAS:")
        print(f"   Minutos: {m['minutes']} | OBV: {m['obv_90']:.2f}")
        print(f"   Goles: {m['goals_90']:.2f} | Assists: {m['assists_90']:.2f}")
        
        print("\n" + "=" * 70 + "\n")