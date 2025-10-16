"""
Sistema de recomendación para Scouting de Jugadores
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from typing import List, Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

from src.config import NORMALIZED_FEATURES, POSITION_FEATURES
from src.utils.data_loader import DataLoader


class PlayerRecommender:
    """
    Sistema de recomendación híbrido para jugadores de fútbol
    
    Combina múltiples técnicas:
    - Similitud por métricas técnicas
    - Análisis contextual (edad, experiencia, liga)
    - Reducción dimensional con PCA
    - Score de compatibilidad personalizable
    """
    
    def __init__(self, data_loader: Optional[DataLoader] = None):
        self.data_loader = data_loader or DataLoader()
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=10, random_state=42)
        self._similarity_matrix = None
        self._features_scaled = None
        
    def fit(self, min_minutes: int = 500):
        """
        Prepara el sistema de recomendación
        
        Args:
            min_minutes: Minutos mínimos jugados para considerar jugador
        """
        # Cargar datos filtrados
        self.df = self.data_loader.get_players(min_minutes=min_minutes)
        
        # Preparar features
        self.features = self.df[NORMALIZED_FEATURES].fillna(0)
        
        # Escalar features
        self._features_scaled = self.scaler.fit_transform(self.features)
        
        # Aplicar PCA para reducir dimensionalidad y ruido
        self._features_pca = self.pca.fit_transform(self._features_scaled)
        
        # Pre-calcular matriz de similitud
        self._similarity_matrix = cosine_similarity(self._features_scaled)
        
        print(f"✅ Sistema entrenado con {len(self.df)} jugadores")
        print(f"📊 Varianza explicada por PCA: {self.pca.explained_variance_ratio_.sum():.2%}")
        
        return self
    
    def find_similar_players(
        self,
        player_name: str,
        position: Optional[str] = None,
        same_position_only: bool = True,
        top_n: int = 10,
        exclude_same_team: bool = True,
        min_similarity: float = 0.0
    ) -> pd.DataFrame:
        """
        Encuentra jugadores similares a uno dado
        
        Args:
            player_name: Nombre del jugador de referencia
            position: Filtrar por posición específica
            same_position_only: Solo buscar en la misma posición
            top_n: Número de recomendaciones
            exclude_same_team: Excluir jugadores del mismo equipo
            min_similarity: Similitud mínima requerida
            
        Returns:
            DataFrame con jugadores recomendados y sus scores
        """
        # Buscar jugador
        player_mask = self.df['player_name'].str.contains(player_name, case=False, na=False)
        
        if not player_mask.any():
            available = self.df['player_name'].str.contains(player_name.split()[0], case=False, na=False)
            if available.any():
                suggestions = self.df[available]['player_name'].unique()[:5]
                raise ValueError(f"Jugador '{player_name}' no encontrado. ¿Quisiste decir: {suggestions}?") #Para intentar frenar typos
            raise ValueError(f"Jugador '{player_name}' no encontrado")
        
        player_idx = player_mask.idxmax()
        player_data = self.df.loc[player_idx]
        
        # Filtrar por posición si se requiere
        if same_position_only:
            position = player_data['position_category']
        
        candidate_mask = pd.Series(True, index=self.df.index)
        
        if position:
            candidate_mask &= (self.df['position_category'] == position)
        
        if exclude_same_team:
            candidate_mask &= (self.df['team_name'] != player_data['team_name'])
        
        # Excluir al mismo jugador
        candidate_mask.loc[player_idx] = False
        
        # Obtener índices de candidatos
        candidate_indices = self.df[candidate_mask].index
        
        # Calcular similitudes
        player_df_idx = self.df.index.get_loc(player_idx)
        similarities = self._similarity_matrix[player_df_idx, :]
        
        # Filtrar candidatos
        candidate_df_indices = [self.df.index.get_loc(idx) for idx in candidate_indices]
        candidate_similarities = similarities[candidate_df_indices]
        
        # Crear DataFrame de resultados
        results = self.df.loc[candidate_indices].copy()
        results['similarity_score'] = candidate_similarities
        
        # Aplicar filtro de similitud mínima
        results = results[results['similarity_score'] >= min_similarity]
        
        # Calcular score contextual (edad, experiencia, etc) 
        # Esto solo basado en los datos del dataset, pero podria mejorar con metricas mas especificas
        results['context_score'] = self._calculate_context_score(results, player_data)
        
        # Score final combinado (escogimos asi la ponderacion por dedazo, pero podemos adecuarla de acuerdo a las necesidades)
        results['final_score'] = (
            0.7 * results['similarity_score'] + 
            0.3 * results['context_score']
        )
        
        # Ordenar y retornar top N
        results = results.nlargest(top_n, 'final_score')
        
        # Seleccionar columnas relevantes
        output_cols = [
            'player_name', 'team_name', 'position_category', 'primary_position',
            'player_season_minutes', 'final_score', 'similarity_score', 'context_score',
            'player_season_goals_90', 'player_season_assists_90',
            'player_season_np_xg_90', 'player_season_obv_90'
        ]
        
        return results[output_cols].reset_index(drop=True)
    
    def recommend_by_profile(
        self,
        position: str,
        attacking_weight: float = 0.5,
        defensive_weight: float = 0.3,
        passing_weight: float = 0.2,
        top_n: int = 10,
        min_minutes: int = 900
    ) -> pd.DataFrame:
        """
        Recomienda jugadores basado en un perfil personalizado
        
        Args:
            position: Posición deseada
            attacking_weight: Peso de habilidades ofensivas (0-1)
            defensive_weight: Peso de habilidades defensivas (0-1)
            passing_weight: Peso de habilidades de pase (0-1)
            top_n: Número de recomendaciones
            min_minutes: Minutos mínimos jugados
            
        Returns:
            DataFrame con jugadores recomendados
        """
        # Filtrar por posición y minutos
        candidates = self.df[
            (self.df['position_category'] == position) &
            (self.df['player_season_minutes'] >= min_minutes)
        ].copy()
        
        if candidates.empty:
            raise ValueError(f"No hay jugadores disponibles para posición '{position}'")
        
        # Definir features por categoría
        attacking_features = [
            'player_season_goals_90_norm',
            'player_season_np_xg_90_norm',
            'player_season_shot_touch_ratio_norm',
            'player_season_obv_shot_90_norm'
        ]
        
        defensive_features = [
            'player_season_tackles_90_norm',
            'player_season_interceptions_90_norm',
            'player_season_defensive_actions_90_norm',
            'player_season_obv_defensive_action_90_norm'
        ]
        
        passing_features = [
            'player_season_assists_90_norm',
            'player_season_key_passes_90_norm',
            'player_season_passes_into_box_90_norm',
            'player_season_obv_pass_90_norm'
        ]
        
        # Calcular scores por categoría
        candidates['attacking_score'] = candidates[attacking_features].mean(axis=1)
        candidates['defensive_score'] = candidates[defensive_features].mean(axis=1)
        candidates['passing_score'] = candidates[passing_features].mean(axis=1)
        
        # Score final ponderado
        candidates['profile_score'] = (
            attacking_weight * candidates['attacking_score'] +
            defensive_weight * candidates['defensive_score'] +
            passing_weight * candidates['passing_score']
        )
        
        # Normalizar a 0-100
        candidates['profile_score'] = (candidates['profile_score'] * 100).round(1)
        
        # Ordenar y retornar
        results = candidates.nlargest(top_n, 'profile_score')
        
        output_cols = [
            'player_name', 'team_name', 'primary_position',
            'player_season_minutes', 'profile_score',
            'attacking_score', 'defensive_score', 'passing_score',
            'player_season_goals_90', 'player_season_assists_90',
            'player_season_tackles_90', 'player_season_obv_90'
        ]
        
        return results[output_cols].reset_index(drop=True)
    
    def find_replacements(
        self,
        player_name: str,
        budget_tier: str = 'medium',  # 'low', 'medium', 'high'
        age_preference: str = 'any',  # 'young', 'experienced', 'any'
        top_n: int = 5
    ) -> pd.DataFrame:
        """
        Encuentra reemplazos potenciales considerando restricciones
        
        Args:
            player_name: Jugador a reemplazar
            budget_tier: Nivel de presupuesto esperado
            age_preference: Preferencia de edad
            top_n: Número de opciones
            
        Returns:
            DataFrame con opciones de reemplazo
        """
        # Buscar jugador original
        similar = self.find_similar_players(
            player_name=player_name,
            same_position_only=True,
            top_n=top_n * 3,  # Obtener más para luego filtrar
            exclude_same_team=True
        )
        
        # Aplicar filtros de contexto según preferencias
        # (Aquí podrías agregar datos de mercado, edad, etc si los tienes)
        
        return similar.head(top_n)
    
    def _calculate_context_score(
        self,
        candidates: pd.DataFrame,
        reference_player: pd.Series
    ) -> pd.Series:
        """
        Calcula score contextual basado en experiencia, minutos, etc
        
        Args:
            candidates: DataFrame de jugadores candidatos
            reference_player: Serie con datos del jugador de referencia
            
        Returns:
            Serie con scores contextuales (0-1)
        """
        # Normalizar minutos jugados (más minutos = más confiable)
        minutes_score = candidates['player_season_minutes'] / candidates['player_season_minutes'].max()
        
        # Normalizar OBV (on-ball value) como proxy de impacto
        obv_score = candidates['player_season_obv_90'] / candidates['player_season_obv_90'].max()
        
        # Score combinado
        context_score = 0.6 * minutes_score + 0.4 * obv_score
        
        return context_score
    
    def get_feature_importance(self, player_name: str, top_n: int = 10) -> pd.Series:
        """
        Identifica las características más distintivas de un jugador
        
        Args:
            player_name: Nombre del jugador
            top_n: Top N features a mostrar
            
        Returns:
            Serie con importancia de features
        """
        player_mask = self.df['player_name'].str.contains(player_name, case=False)
        if not player_mask.any():
            raise ValueError(f"Jugador '{player_name}' no encontrado")
        
        player_idx = player_mask.idxmax()
        player_features = self.features.loc[player_idx]
        
        # Comparar con promedio de su posición
        position = self.df.loc[player_idx, 'position_category']
        position_avg = self.features[self.df['position_category'] == position].mean()
        
        # Diferencia vs promedio
        importance = (player_features - position_avg).abs()
        importance = importance.sort_values(ascending=False)
        
        # Limpiar nombres
        importance.index = importance.index.str.replace('player_season_', '').str.replace('_norm', '').str.replace('_', ' ').str.title()
        
        return importance.head(top_n)