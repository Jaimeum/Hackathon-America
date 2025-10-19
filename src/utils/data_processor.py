"""
Data processing module for player statistics extraction and normalization
Extracted from notebooks/procesamiento_datos.ipynb
"""
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from src.utils.data_fetcher import StatsBombDataFetcher


class DataProcessor:
    """Main data processing class for player statistics ETL pipeline"""
    
    def __init__(self):
        self.fetcher = StatsBombDataFetcher()
        self.processed_data = None
        
    def extract_player_key_metrics(self, player_season_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extrae y calcula métricas clave de jugadores para el sistema de recomendación.
        
        Args:
            player_season_df: DataFrame con estadísticas de jugadores por temporada
            
        Returns:
            DataFrame con métricas procesadas y normalizadas
        """
        
        # Filtrar jugadores con minutos mínimos (al menos 450 minutos = ~5 partidos completos)
        df = player_season_df[player_season_df['player_season_minutes'] >= 450].copy()
        
        # Métricas básicas
        base_metrics = [
            'account_id', 'player_id', 'player_name', 'team_id', 'team_name',
            'season_id', 'season_name', 'country_id', 'player_season_minutes',
            'primary_position_id', 'primary_position'
        ]
        
        # Métricas ofensivas (por 90 minutos)
        offensive_metrics = [
            'player_season_goals_90',
            'player_season_assists_90',
            'player_season_np_xg_90',
            'player_season_xag_90',
            'player_season_np_shots_90',
            'player_season_np_xg_per_shot',
            'player_season_shot_touch_ratio',
            'player_season_dribbles_90',
            'player_season_dribble_ratio'
        ]
        
        # Métricas de pases y creación
        passing_metrics = [
            'player_season_passes_into_box_90',
            'player_season_cross_completion_ratio',
            'player_season_deep_completions_90',
            'player_season_key_passes_90',
            'player_season_pass_completion_ratio',
            'player_season_progressive_passes_90',
            'player_season_obv_pass_90'
        ]
        
        # Métricas defensivas
        defensive_metrics = [
            'player_season_pressures_90',
            'player_season_pressure_regains_90',
            'player_season_tackles_90',
            'player_season_interceptions_90',
            'player_season_blocks_90',
            'player_season_clearances_90',
            'player_season_defensive_actions_90',
            'player_season_aerial_ratio'
        ]
        
        # Métricas de portero
        gk_metrics = [
            'player_season_psxg_conceded',
            'player_season_save_ratio',
            'player_season_clean_sheet_ratio'
        ]
        
        # Métricas avanzadas (OBV, xG)
        advanced_metrics = [
            'player_season_obv_90',
            'player_season_obv_dribble_carry_90',
            'player_season_obv_defensive_action_90',
            'player_season_obv_shot_90'
        ]
        
        # Combinar todas las métricas disponibles
        all_metrics = base_metrics.copy()
        
        # Agregar solo las métricas que existen en el DataFrame
        for metric_list in [offensive_metrics, passing_metrics, defensive_metrics, 
                            gk_metrics, advanced_metrics]:
            for metric in metric_list:
                if metric in df.columns:
                    all_metrics.append(metric)
        
        # Seleccionar columnas disponibles
        available_metrics = [col for col in all_metrics if col in df.columns]
        df_processed = df[available_metrics].copy()
        
        # Rellenar NaN con 0 para métricas numéricas
        numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
        df_processed[numeric_cols] = df_processed[numeric_cols].fillna(0)
        
        return df_processed
    
    def classify_player_position(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clasifica jugadores en categorías de posición amplias.
        
        Args:
            df: DataFrame con datos de jugadores
            
        Returns:
            DataFrame con columna adicional 'position_category'
        """
        
        df = df.copy()
        
        # Mapeo de posiciones a categorías
        position_mapping = {
            # Porteros
            'Goalkeeper': 'GK',
            
            # Defensas
            'Right Back': 'DEF',
            'Left Back': 'DEF',
            'Right Center Back': 'DEF',
            'Left Center Back': 'DEF',
            'Center Back': 'DEF',
            'Right Wing Back': 'DEF',
            'Left Wing Back': 'DEF',
            
            # Mediocampistas
            'Right Defensive Midfield': 'MED',
            'Left Defensive Midfield': 'MED',
            'Center Defensive Midfield': 'MED',
            'Right Center Midfield': 'MED',
            'Left Center Midfield': 'MED',
            'Center Midfield': 'MED',
            'Right Midfield': 'MED',
            'Left Midfield': 'MED',
            'Right Attacking Midfield': 'MED',
            'Left Attacking Midfield': 'MED',
            'Center Attacking Midfield': 'MED',
            
            # Delanteros
            'Right Wing': 'FWD',
            'Left Wing': 'FWD',
            'Right Center Forward': 'FWD',
            'Left Center Forward': 'FWD',
            'Center Forward': 'FWD',
            'Secondary Striker': 'FWD'
        }
        
        if 'primary_position' in df.columns:
            df['position_category'] = df['primary_position'].map(position_mapping)
            df['position_category'] = df['position_category'].fillna('MED')  # Default a mediocampo
        
        return df
    
    def normalize_metrics_by_position(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza métricas usando z-score dentro de cada categoría de posición.
        Esto permite comparar jugadores entre diferentes posiciones.
        
        Args:
            df: DataFrame con métricas de jugadores
            
        Returns:
            DataFrame con métricas normalizadas (sufijo _norm)
        """
        
        df = df.copy()
        
        # Identificar columnas numéricas que terminan en _90
        metric_cols = [col for col in df.columns if col.endswith('_90') or col.endswith('_ratio')]
        
        # Normalizar por posición
        if 'position_category' in df.columns:
            for metric in metric_cols:
                if metric in df.columns:
                    # Calcular z-score por posición
                    df[f'{metric}_norm'] = df.groupby('position_category')[metric].transform(
                        lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
                    )
        
        return df
    
    def process_seasons_data(self, seasons: List[Tuple[int, int, str]], 
                           competition_id: int = 73) -> pd.DataFrame:
        """
        Procesa datos de múltiples temporadas
        
        Args:
            seasons: Lista de (season_id, season_name) tuplas
            competition_id: ID de la competencia (Liga MX = 73)
            
        Returns:
            DataFrame consolidado con todos los datos procesados
        """
        all_seasons_data = []
        
        for season_id, season_name in seasons:
            print(f"\n{'=' * 60}")
            print(f"Procesando temporada: {season_name}")
            print('=' * 60)
            
            # Obtener datos de jugadores
            player_data = self.fetcher.get_player_season_stats(competition_id, season_id)
            
            if player_data.empty:
                print(f"No hay datos para {season_name}")
                continue
            
            print(f"{len(player_data)} jugadores encontrados")
            
            # Extraer métricas clave
            processed_data = self.extract_player_key_metrics(player_data)
            print(f"Métricas extraídas: {len(processed_data)} jugadores con minutos suficientes")
            
            # Clasificar por posición
            processed_data = self.classify_player_position(processed_data)
            
            # Normalizar métricas
            processed_data = self.normalize_metrics_by_position(processed_data)
            
            print(f"Datos procesados y normalizados")
            print(f"   - Porteros: {len(processed_data[processed_data['position_category'] == 'GK'])}")
            print(f"   - Defensas: {len(processed_data[processed_data['position_category'] == 'DEF'])}")
            print(f"   - Mediocampistas: {len(processed_data[processed_data['position_category'] == 'MED'])}")
            print(f"   - Delanteros: {len(processed_data[processed_data['position_category'] == 'FWD'])}")
            
            all_seasons_data.append(processed_data)
        
        # Combinar todas las temporadas
        print(f"\n{'=' * 60}")
        print("CONSOLIDANDO DATOS DE TODAS LAS TEMPORADAS")
        print('=' * 60)
        
        if all_seasons_data:
            df_all_players = pd.concat(all_seasons_data, ignore_index=True)
            print(f"Total de registros: {len(df_all_players)}")
            print(f"Jugadores únicos: {df_all_players['player_id'].nunique()}")
            print(f"Equipos únicos: {df_all_players['team_name'].nunique()}")
            
            self.processed_data = df_all_players
            return df_all_players
        else:
            print("No se procesaron datos")
            return pd.DataFrame()
    
    def get_america_players(self) -> pd.DataFrame:
        """
        Extrae jugadores del Club América del dataset procesado
        
        Returns:
            DataFrame con jugadores del América
        """
        if self.processed_data is None:
            raise ValueError("No hay datos procesados. Ejecuta process_seasons_data() primero.")
        
        america_players = self.processed_data[
            self.processed_data['team_name'].str.contains('América', case=False, na=False)
        ].copy()
        
        print(f"\n{'=' * 60}")
        print("JUGADORES DEL CLUB AMÉRICA")
        print('=' * 60)
        print(f"Total de registros: {len(america_players)}")
        print(f"Jugadores únicos: {america_players['player_id'].nunique()}")
        
        # Jugadores por temporada
        print("\nDistribución por temporada:")
        print(america_players.groupby('season_name')['player_id'].count())
        
        # Jugadores por posición
        print("\nDistribución por posición:")
        print(america_players.groupby('position_category')['player_id'].count())
        
        return america_players
    
    def save_processed_data(self, output_dir: str = "data/processed"):
        """
        Guarda los datos procesados en archivos CSV y Parquet
        
        Args:
            output_dir: Directorio de salida
        """
        if self.processed_data is None:
            raise ValueError("No hay datos procesados para guardar")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Guardar datos principales
        csv_path = output_path / "all_players_processed.csv"
        parquet_path = output_path / "all_players_processed.parquet"
        
        self.processed_data.to_csv(csv_path, index=False)
        self.processed_data.to_parquet(parquet_path, index=False)
        
        print(f"\nDatos guardados:")
        print(f"  CSV: {csv_path}")
        print(f"  Parquet: {parquet_path}")
        
        # Guardar jugadores del América
        america_players = self.get_america_players()
        america_csv = output_path / "america_players.parquet"
        america_players.to_parquet(america_csv, index=False)
        print(f"  América: {america_csv}")
        
        return {
            'main_data': csv_path,
            'main_parquet': parquet_path,
            'america_players': america_csv
        }
    
    def get_summary_stats(self) -> Dict:
        """
        Genera estadísticas resumidas del dataset procesado
        
        Returns:
            Diccionario con estadísticas
        """
        if self.processed_data is None:
            raise ValueError("No hay datos procesados")
        
        df = self.processed_data
        
        summary = {
            'total_records': len(df),
            'unique_players': df['player_id'].nunique(),
            'unique_teams': df['team_name'].nunique(),
            'unique_seasons': df['season_name'].nunique(),
            'positions': df['position_category'].value_counts().to_dict(),
            'avg_minutes': df['player_season_minutes'].mean(),
            'seasons': df['season_name'].unique().tolist(),
            'teams': df['team_name'].unique().tolist()
        }
        
        return summary


def run_full_data_processing():
    """
    Función de conveniencia para ejecutar el pipeline completo de procesamiento
    """
    processor = DataProcessor()
    
    # Definir temporadas a procesar
    seasons = [
        (317, '2024/2025'),
        (281, '2023/2024'),
        (235, '2022/2023'),
        (108, '2021/2022')
    ]
    
    # Procesar datos
    df_all_players = processor.process_seasons_data(seasons)
    
    if not df_all_players.empty:
        # Guardar datos
        saved_files = processor.save_processed_data()
        
        # Mostrar resumen
        summary = processor.get_summary_stats()
        print(f"\n{'=' * 60}")
        print("RESUMEN FINAL")
        print('=' * 60)
        print(f"Total registros: {summary['total_records']}")
        print(f"Jugadores únicos: {summary['unique_players']}")
        print(f"Equipos únicos: {summary['unique_teams']}")
        print(f"Temporadas: {summary['unique_seasons']}")
        print(f"Minutos promedio: {summary['avg_minutes']:.1f}")
        
        return processor, saved_files
    else:
        print("Error: No se pudieron procesar los datos")
        return None, None


if __name__ == "__main__":
    processor, files = run_full_data_processing()
