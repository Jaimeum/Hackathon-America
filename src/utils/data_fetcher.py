"""
Módulo para obtener datos de StatsBomb
"""
import pandas as pd
from statsbombpy import sb
from typing import List, Dict, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import StatsBombConfig

class StatsBombDataFetcher:
    def __init__(self):
        
        self.config = StatsBombConfig()
        self.creds = self.config.get_credentials()
    
    def get_competitions(self, country: str = None) -> pd.DataFrame:
        """
        Obtiene las competiciones disponibles
        
        Args:
            country: Filtrar por país (ej: "Mexico", "Spain", "England")
        
        Returns:
            DataFrame con las competiciones
        """
        try:
            print("Obteniendo competiciones...")
            competitions = sb.competitions(creds = self.creds)
            
            if country:
                competitions = competitions[competitions['country_name'] == country]
                print(f"Filtrado por país: {country}")

            print(f"{len(competitions)} competiciones obtenidas")
            return competitions
            
        except Exception as e:
            print(f"Error obteniendo competiciones: {e}")
            return pd.DataFrame()
    
    def get_matches(self, competition_id: int, season_id: int) -> pd.DataFrame:
        """
        Obtiene los partidos de una competición y temporada
        
        Args:
            competition_id: ID de la competición
            season_id: ID de la temporada
        
        Returns:
            DataFrame con los partidos
        """
        try:
            print(f"Obteniendo partidos (Comp: {competition_id}, Temp: {season_id})...")
            matches = sb.matches(
                competition_id=competition_id, 
                season_id=season_id,
                creds=self.creds
            )
            print(f"{len(matches)} partidos obtenidos")
            return matches
            
        except Exception as e:
            print(f"Error obteniendo partidos: {e}")
            return pd.DataFrame()
    
    def get_events(self, match_id: int, three: bool) -> pd.DataFrame:
        """
        Obtiene los eventos de un partido específico
        
        Args:
            match_id: ID del partido
        
        Returns:
            DataFrame con los eventos del partido
        """
        try:
            print(f"Obteniendo eventos del partido {match_id}...")
            events = sb.events(match_id=match_id, creds=self.creds, include_360_metrics=three)
            print(f"{len(events)} eventos obtenidos")
            return events
            
        except Exception as e:
            print(f"Error obteniendo eventos del partido {match_id}: {e}")
            return pd.DataFrame()
    
    def get_lineups(self, match_id: int) -> Dict:
        """
        Obtiene las alineaciones de un partido
        
        Args:
            match_id: ID del partido
        
        Returns:
            Diccionario con las alineaciones
        """
        try:
            print(f"Obteniendo alineaciones del partido {match_id}...")
            lineups = sb.lineups(match_id=match_id, creds=self.creds)
            print(f"Alineaciones obtenidas para {len(lineups)} equipos")
            return lineups
            
        except Exception as e:
            print(f"Error obteniendo alineaciones del partido {match_id}: {e}")
            return {}
        
    def get_player_season_stats(self, competition_id: int, season_id: int) -> pd.DataFrame:
        """
        Obtiene estadísticas de un jugador en una temporada específica
        
        Args:
            competition_id: ID de la competición
            season_id: ID de la temporada
        
        Returns:
            DataFrame con las estadísticas del jugador
        """
        try:
            print(f"Obteniendo estadísticas de los jugadores para (Comp: {competition_id}, Temp: {season_id})...")
            player_stats = sb.player_season_stats(
                competition_id=competition_id, 
                season_id=season_id,
                creds=self.creds
            )
            print(f"Estadísticas de {len(player_stats)} jugadores obtenidas")
            return player_stats

        except Exception as e:
            print(f"Error obteniendo estadísticas de jugadores: {e}")
            return pd.DataFrame()
        
    def get_player_match_stats(self, match_id: int) -> pd.DataFrame:
        """
        Obtiene estadísticas de jugadores para un partido específico
        
        Args:
            match_id: ID del partido
        
        Returns:
            DataFrame con estadísticas de jugadores del partido
        """
        try:
            print(f"Obteniendo estadísticas de jugadores del partido {match_id}...")
            
            player_match_stats = sb.player_match_stats(
                match_id=match_id,
                creds=self.creds
            )
            
            print(f"Estadísticas de {len(player_match_stats)} jugadores obtenidas")
            return player_match_stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas de jugadores del partido {match_id}: {e}")
            return pd.DataFrame()
        
    def get_team_season_stats(self, competition_id: int, season_id: int) -> pd.DataFrame:
        """
        Obtiene estadísticas de temporada de equipos
        
        Args:
            competition_id: ID de la competición
            season_id: ID de la temporada
        
        Returns:
            DataFrame con estadísticas de equipos
        """
        try:
            print(f"Obteniendo estadísticas de equipos (Comp: {competition_id}, Temp: {season_id})...")
            
            team_stats = sb.team_season_stats(
                competition_id=competition_id,
                season_id=season_id,
                creds=self.creds
            )
            
            print(f"Estadísticas de {len(team_stats)} equipos obtenidas")
            return team_stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas de equipos: {e}")
            return pd.DataFrame()
    
    def get_team_match_stats(self, match_id: int) -> pd.DataFrame:
        """
        Obtiene estadísticas de equipos para un partido específico
        
        Args:
            match_id: ID del partido
        
        Returns:
            DataFrame con estadísticas de equipos del partido
        """
        try:
            print(f"Obteniendo estadísticas de equipos del partido {match_id}...")
            
            team_match_stats = sb.team_match_stats(
                match_id=match_id,
                creds=self.creds
            )
            
            print(f"Estadísticas de {len(team_match_stats)} equipos obtenidas")
            return team_match_stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas de equipos del partido {match_id}: {e}")
            return pd.DataFrame()
    
    def find_club_america_matches(self, competition_id: int, season_id: int) -> pd.DataFrame:
        """
        Encuentra partidos específicos del Club América
        
        Args:
            competition_id: ID de la competición
            season_id: ID de la temporada
        
        Returns:
            DataFrame con partidos del Club América
        """
        matches = self.get_matches(competition_id, season_id, creds=self.creds)
        
        if matches.empty:
            return pd.DataFrame()
        
        # Buscar diferentes variaciones del nombre
        america_variants = ['Club América', 'America', 'CF América', 'Club America']
        
        america_matches = pd.DataFrame()
        for variant in america_variants:
            variant_matches = matches[
                (matches['home_team'] == variant) | 
                (matches['away_team'] == variant)
            ]
            america_matches = pd.concat([america_matches, variant_matches])
        
        # Eliminar duplicados
        america_matches = america_matches.drop_duplicates()
        
        print(f"Encontrados {len(america_matches)} partidos del Club América")
        return america_matches
    
    def get_sample_data(self) -> Dict:
        """
        Obtiene una muestra de datos para testing
        
        Returns:
            Diccionario con datos de muestra
        """
        print("Obteniendo datos de muestra...")
        
        sample_data = {
            'competitions': pd.DataFrame(),
            'matches': pd.DataFrame(),
            'events': pd.DataFrame(),
            'lineups': {}
        }
        
        try:
            # Obtener competiciones
            competitions = self.get_competitions()
            sample_data['competitions'] = competitions
            
            if not competitions.empty:
                # Tomar la primera competición disponible
                first_comp = competitions.iloc[0]
                comp_id = first_comp['competition_id']
                season_id = first_comp['season_id']
                
                print(f"Usando: {first_comp['competition_name']} - {first_comp['season_name']}")
                
                # Obtener partidos
                matches = self.get_matches(comp_id, season_id)
                sample_data['matches'] = matches.head(5)  # Solo 5 partidos para muestra
                
                if not matches.empty:
                    # Obtener eventos del primer partido
                    first_match_id = matches.iloc[0]['match_id']
                    events = self.get_events(first_match_id, three=True)
                    sample_data['events'] = events.head(100)  # Primeros 100 eventos
                    
                    # Obtener alineaciones del primer partido
                    lineups = self.get_lineups(first_match_id)
                    sample_data['lineups'] = lineups
            
            print("Datos de muestra obtenidos correctamente")
            return sample_data
            
        except Exception as e:
            print(f"Error obteniendo datos de muestra: {e}")
            return sample_data