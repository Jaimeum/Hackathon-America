"""
Comprehensive America team analysis module
Extracted from notebooks/Analisis_America_fit_final.ipynb
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

from src.models.team_profiler_PCA import AmericaProfiler
from src.models.team_fit_analyzer import TeamFitAnalyzer
from src.models.recommender import PlayerRecommender
from src.utils.data_loader import DataLoader


class AmericaAnalysis:
    """Comprehensive analysis system for Club América scouting"""
    
    def __init__(self):
        self.profiler = AmericaProfiler()
        self.data_loader = DataLoader()
        self.america_profile = None
        self.analyzer = None
        self.recommender = None
        
    def build_america_profile(self, seasons: List[Tuple[int, int]] = None) -> Dict:
        """
        Construye el perfil completo del Club América
        
        Args:
            seasons: Lista de (competition_id, season_id) tuplas
            
        Returns:
            Perfil completo del América
        """
        if seasons is None:
            seasons = [
                (73, 317),  # 2024/2025
                (73, 281),  # 2023/2024
                (73, 235),  # 2022/2023
                (73, 108),  # 2021/2022
            ]
        
        print("Construyendo perfil del Club América...")
        self.america_profile = self.profiler.build_profile(seasons=seasons)
        
        return self.america_profile
    
    def initialize_analyzers(self, min_minutes: int = 500):
        """
        Inicializa los analizadores con datos
        
        Args:
            min_minutes: Minutos mínimos para considerar jugadores
        """
        if self.america_profile is None:
            raise ValueError("Construye el perfil del América primero")
        
        print("Inicializando analizadores...")
        
        # Inicializar Team Fit Analyzer
        self.analyzer = TeamFitAnalyzer(america_profile=self.america_profile)
        self.analyzer.fit(min_minutes=min_minutes)
        
        # Inicializar Player Recommender
        self.recommender = PlayerRecommender()
        self.recommender.fit(min_minutes=min_minutes)
        
        print("Analizadores inicializados correctamente")
    
    def analyze_player_fit(self, player_name: str) -> Dict:
        """
        Analiza la compatibilidad de un jugador específico con el América
        
        Args:
            player_name: Nombre del jugador
            
        Returns:
            Diccionario con análisis de compatibilidad
        """
        if self.analyzer is None:
            raise ValueError("Inicializa los analizadores primero")
        
        print(f"Analizando compatibilidad de {player_name}...")
        fit_result = self.analyzer.calculate_team_fit(player_name=player_name)
        
        return fit_result
    
    def get_position_recommendations(self, position: str, top_n: int = 5, 
                                   min_fit: float = 60.0) -> pd.DataFrame:
        """
        Obtiene recomendaciones de jugadores para una posición específica
        
        Args:
            position: Posición ('FWD', 'MED', 'DEF', 'GK')
            top_n: Número de recomendaciones
            min_fit: Fit mínimo requerido
            
        Returns:
            DataFrame con recomendaciones
        """
        if self.analyzer is None:
            raise ValueError("Inicializa los analizadores primero")
        
        print(f"Buscando top {top_n} {position}s para el América...")
        recommendations = self.analyzer.recommend_best_fits(
            position=position,
            top_n=top_n,
            min_overall_fit=min_fit
        )
        
        return recommendations
    
    def find_similar_players(self, player_name: str, top_n: int = 10, 
                           same_position_only: bool = True) -> pd.DataFrame:
        """
        Encuentra jugadores similares a uno dado
        
        Args:
            player_name: Nombre del jugador de referencia
            top_n: Número de jugadores similares
            same_position_only: Solo buscar en la misma posición
            
        Returns:
            DataFrame con jugadores similares
        """
        if self.recommender is None:
            raise ValueError("Inicializa los analizadores primero")
        
        print(f"Buscando jugadores similares a {player_name}...")
        similar_players = self.recommender.find_similar_players(
            player_name=player_name,
            same_position_only=same_position_only,
            top_n=top_n
        )
        
        return similar_players
    
    def get_america_current_squad(self) -> pd.DataFrame:
        """
        Obtiene la plantilla actual del América
        
        Returns:
            DataFrame con jugadores actuales del América
        """
        america_players = self.data_loader.get_player_by_name("América")
        
        # Filtrar por la temporada más reciente
        if not america_players.empty:
            latest_season = america_players['season_name'].max()
            current_squad = america_players[america_players['season_name'] == latest_season]
            
            print(f"Plantilla actual del América ({latest_season}):")
            print(f"Total jugadores: {len(current_squad)}")
            
            # Mostrar por posición
            position_dist = current_squad['position_category'].value_counts()
            print("\nDistribución por posición:")
            for pos, count in position_dist.items():
                print(f"   {pos}: {count}")
            
            return current_squad
        
        return pd.DataFrame()
    
    def analyze_squad_needs(self) -> Dict:
        """
        Analiza las necesidades de la plantilla del América
        
        Returns:
            Diccionario con análisis de necesidades
        """
        current_squad = self.get_america_current_squad()
        
        if current_squad.empty:
            return {"error": "No se encontraron datos de la plantilla actual"}
        
        # Análisis por posición
        position_analysis = {}
        
        for position in ['GK', 'DEF', 'MED', 'FWD']:
            position_players = current_squad[current_squad['position_category'] == position]
            
            if len(position_players) > 0:
                # Calcular métricas promedio
                avg_minutes = position_players['player_season_minutes'].mean()
                avg_obv = position_players['player_season_obv_90'].mean()
                
                # Identificar áreas de mejora
                needs = []
                if avg_obv < 0.3:
                    needs.append("Impacto ofensivo bajo")
                if len(position_players) < 3:
                    needs.append("Profundidad limitada")
                if avg_minutes > 2500:
                    needs.append("Sobreuso de jugadores clave")
                
                position_analysis[position] = {
                    'players_count': len(position_players),
                    'avg_minutes': avg_minutes,
                    'avg_obv': avg_obv,
                    'needs': needs
                }
        
        return position_analysis
    
    def generate_recruitment_report(self, positions: List[str] = None, 
                                  top_n: int = 3) -> Dict:
        """
        Genera un reporte completo de fichajes recomendados
        
        Args:
            positions: Lista de posiciones a analizar
            top_n: Número de recomendaciones por posición
            
        Returns:
            Diccionario con reporte completo
        """
        if positions is None:
            positions = ['FWD', 'MED', 'DEF', 'GK']
        
        if self.analyzer is None:
            raise ValueError("Inicializa los analizadores primero")
        
        print("Generando reporte de fichajes...")
        
        report = {
            'america_profile': self.america_profile,
            'squad_needs': self.analyze_squad_needs(),
            'recommendations': {}
        }
        
        # Obtener recomendaciones por posición
        for position in positions:
            try:
                recommendations = self.get_position_recommendations(
                    position=position, 
                    top_n=top_n
                )
                
                if not recommendations.empty:
                    report['recommendations'][position] = recommendations.to_dict('records')
                else:
                    report['recommendations'][position] = []
                    
            except Exception as e:
                print(f"Error obteniendo recomendaciones para {position}: {e}")
                report['recommendations'][position] = []
        
        return report
    
    def compare_players(self, player1: str, player2: str) -> Dict:
        """
        Compara dos jugadores específicos
        
        Args:
            player1: Nombre del primer jugador
            player2: Nombre del segundo jugador
            
        Returns:
            Diccionario con comparación detallada
        """
        if self.analyzer is None:
            raise ValueError("Inicializa los analizadores primero")
        
        print(f"Comparando {player1} vs {player2}...")
        
        # Analizar fit de ambos jugadores
        fit1 = self.analyzer.calculate_team_fit(player_name=player1)
        fit2 = self.analyzer.calculate_team_fit(player_name=player2)
        
        # Obtener datos de jugadores
        player1_data = self.data_loader.get_player_by_name(player1)
        player2_data = self.data_loader.get_player_by_name(player2)
        
        comparison = {
            'player1': {
                'name': player1,
                'fit_scores': fit1,
                'data': player1_data.iloc[0].to_dict() if not player1_data.empty else {}
            },
            'player2': {
                'name': player2,
                'fit_scores': fit2,
                'data': player2_data.iloc[0].to_dict() if not player2_data.empty else {}
            },
            'summary': {
                'better_overall_fit': player1 if fit1['overall_fit'] > fit2['overall_fit'] else player2,
                'better_technical': player1 if fit1['technical_fit'] > fit2['technical_fit'] else player2,
                'better_tactical': player1 if fit1['tactical_fit'] > fit2['tactical_fit'] else player2,
                'better_impact': player1 if fit1['impact_score'] > fit2['impact_score'] else player2
            }
        }
        
        return comparison
    
    def export_analysis_results(self, output_dir: str = "data/results"):
        """
        Exporta resultados del análisis
        
        Args:
            output_dir: Directorio de salida
        """
        from pathlib import Path
        import json
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Exportar perfil del América
        if self.america_profile:
            profile_file = output_path / "america_profile.json"
            with open(profile_file, 'w') as f:
                json.dump(self.america_profile, f, indent=2, default=str)
            print(f"Perfil del América exportado: {profile_file}")
        
        # Generar y exportar reporte de fichajes
        recruitment_report = self.generate_recruitment_report()
        report_file = output_path / "america_recruitment_report.json"
        with open(report_file, 'w') as f:
            json.dump(recruitment_report, f, indent=2, default=str)
        print(f"Reporte de fichajes exportado: {report_file}")
        
        # Exportar plantilla actual
        current_squad = self.get_america_current_squad()
        if not current_squad.empty:
            squad_file = output_path / "america_current_squad.csv"
            current_squad.to_csv(squad_file, index=False)
            print(f"Plantilla actual exportada: {squad_file}")
        
        return {
            'profile': profile_file if self.america_profile else None,
            'recruitment_report': report_file,
            'current_squad': squad_file if not current_squad.empty else None
        }


def run_complete_america_analysis():
    """
    Función de conveniencia para ejecutar análisis completo del América
    """
    analysis = AmericaAnalysis()
    
    # 1. Construir perfil del América
    america_profile = analysis.build_america_profile()
    
    # 2. Inicializar analizadores
    analysis.initialize_analyzers()
    
    # 3. Analizar necesidades de la plantilla
    squad_needs = analysis.analyze_squad_needs()
    print(f"\nNecesidades de la plantilla:")
    for pos, needs in squad_needs.items():
        print(f"   {pos}: {needs}")
    
    # 4. Generar recomendaciones por posición
    positions = ['FWD', 'MED', 'DEF']
    recommendations = {}
    
    for position in positions:
        try:
            recs = analysis.get_position_recommendations(position, top_n=3)
            recommendations[position] = recs
            print(f"\nTop {position}s recomendados:")
            print(recs[['player_name', 'team_name', 'overall_fit', 'technical_fit', 'tactical_fit']].to_string(index=False))
        except Exception as e:
            print(f"Error obteniendo recomendaciones para {position}: {e}")
    
    # 5. Exportar resultados
    exported_files = analysis.export_analysis_results()
    
    return analysis, exported_files


if __name__ == "__main__":
    analysis, files = run_complete_america_analysis()
