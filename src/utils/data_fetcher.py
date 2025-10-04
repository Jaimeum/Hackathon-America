"""
Módulo para obtener datos de StatsBomb
"""
import pandas as pd
from statsbombpy import sb
from typing import List, Dict, Optional
from .config import StatsBombConfig

class StatsBombDataFetcher:
    def __init__(self):
        
        self.config = StatsBombConfig()
        self.creds = self.config.get_credentials()
    
    def get_competitions(self, country: str = None, division: str = None, 
                        season: str = None, gender: str = None) -> pd.DataFrame:
        """
        Obtiene las competiciones disponibles con filtros opcionales
        
        Args:
            country: Filtrar por país (ej: "Mexico", "Spain", "England")
            division: Filtrar por división (ej: "1. Bundesliga", "La Liga")
            season: Filtrar por temporada (ej: "2019/2020", "2020/2021")
            gender: Filtrar por género ("male" o "female")
        
        Returns:
            DataFrame con las competiciones filtradas
        """
        try:
            print("Obteniendo competiciones...")
            competitions = sb.competitions(creds=self.creds)
            
            # Aplicar filtros
            if country:
                competitions = competitions[competitions['country_name'] == country]
                print(f"Filtrado por país: {country}")
            
            if division:
                competitions = competitions[competitions['competition_name'] == division]
                print(f"Filtrado por división: {division}")
            
            if season:
                competitions = competitions[competitions['season_name'] == season]
                print(f"Filtrado por temporada: {season}")
            
            if gender:
                competitions = competitions[competitions['competition_gender'] == gender]
                print(f"Filtrado por género: {gender}")

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
    
    def get_events(self, match_id: int, include_360_metrics: bool = False, 
                   split: bool = False, flatten_attrs: bool = True) -> pd.DataFrame:
        """
        Obtiene los eventos de un partido específico
        
        Args:
            match_id: ID del partido
            include_360_metrics: Incluir métricas 360 (solo para clientes con suscripción)
            split: Dividir eventos por tipo en dataframes separados
            flatten_attrs: Aplanar atributos de eventos en columnas separadas
        
        Returns:
            DataFrame con los eventos del partido o diccionario de DataFrames si split=True
        """
        try:
            print(f"Obteniendo eventos del partido {match_id}...")
            events = sb.events(
                match_id=match_id, 
                creds=self.creds, 
                include_360_metrics=include_360_metrics,
                split=split,
                flatten_attrs=flatten_attrs
            )
            
            if split:
                print(f"Eventos divididos obtenidos: {list(events.keys())}")
                for event_type, df in events.items():
                    print(f"  - {event_type}: {len(df)} eventos")
            else:
                print(f"{len(events)} eventos obtenidos")
            
            return events
            
        except Exception as e:
            print(f"Error obteniendo eventos del partido {match_id}: {e}")
            return pd.DataFrame() if not split else {}
    
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
    
    def get_frames(self, match_id: int, fmt: str = 'dataframe') -> pd.DataFrame:
        """
        Obtiene los frames 360 de un partido específico
        
        Args:
            match_id: ID del partido
            fmt: Formato de salida ('dataframe' o 'dict')
        
        Returns:
            DataFrame o diccionario con los frames 360 del partido
        """
        try:
            print(f"Obteniendo frames 360 del partido {match_id}...")
            frames = sb.frames(match_id=match_id, fmt=fmt, creds=self.creds)
            
            if fmt == 'dataframe':
                print(f"{len(frames)} frames 360 obtenidos")
            else:
                print(f"Frames 360 obtenidos en formato diccionario")
            
            return frames
            
        except Exception as e:
            print(f"Error obteniendo frames 360 del partido {match_id}: {e}")
            return pd.DataFrame() if fmt == 'dataframe' else {}
        
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
        matches = self.get_matches(competition_id, season_id)
        
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
    
    def get_competitions_raw(self) -> Dict:
        """
        Obtiene las competiciones en formato diccionario (raw JSON)
        
        Returns:
            Diccionario con las competiciones
        """
        try:
            print("Obteniendo competiciones en formato raw...")
            competitions = sb.competitions(fmt="dict", creds=self.creds)
            print(f"Competiciones raw obtenidas")
            return competitions
            
        except Exception as e:
            print(f"Error obteniendo competiciones raw: {e}")
            return {}
    
    def get_matches_raw(self, competition_id: int, season_id: int) -> Dict:
        """
        Obtiene los partidos en formato diccionario (raw JSON)
        
        Args:
            competition_id: ID de la competición
            season_id: ID de la temporada
        
        Returns:
            Diccionario con los partidos
        """
        try:
            print(f"Obteniendo partidos raw (Comp: {competition_id}, Temp: {season_id})...")
            matches = sb.matches(
                competition_id=competition_id, 
                season_id=season_id,
                fmt="dict",
                creds=self.creds
            )
            print(f"Partidos raw obtenidos")
            return matches
            
        except Exception as e:
            print(f"Error obteniendo partidos raw: {e}")
            return {}
    
    def get_lineups_raw(self, match_id: int) -> Dict:
        """
        Obtiene las alineaciones en formato diccionario (raw JSON)
        
        Args:
            match_id: ID del partido
        
        Returns:
            Diccionario con las alineaciones
        """
        try:
            print(f"Obteniendo alineaciones raw del partido {match_id}...")
            lineups = sb.lineups(match_id=match_id, fmt="dict", creds=self.creds)
            print(f"Alineaciones raw obtenidas")
            return lineups
            
        except Exception as e:
            print(f"Error obteniendo alineaciones raw: {e}")
            return {}
    
    def get_events_raw(self, match_id: int) -> Dict:
        """
        Obtiene los eventos en formato diccionario (raw JSON)
        
        Args:
            match_id: ID del partido
        
        Returns:
            Diccionario con los eventos
        """
        try:
            print(f"Obteniendo eventos raw del partido {match_id}...")
            events = sb.events(match_id=match_id, fmt="dict", creds=self.creds)
            print(f"Eventos raw obtenidos")
            return events
            
        except Exception as e:
            print(f"Error obteniendo eventos raw: {e}")
            return {}
    
    def get_frames_raw(self, match_id: int) -> Dict:
        """
        Obtiene los frames 360 en formato diccionario (raw JSON)
        
        Args:
            match_id: ID del partido
        
        Returns:
            Diccionario con los frames 360
        """
        try:
            print(f"Obteniendo frames 360 raw del partido {match_id}...")
            frames = sb.frames(match_id=match_id, fmt="dict", creds=self.creds)
            print(f"Frames 360 raw obtenidos")
            return frames
            
        except Exception as e:
            print(f"Error obteniendo frames 360 raw: {e}")
            return {}
    
    def get_player_match_stats_raw(self, match_id: int) -> Dict:
        """
        Obtiene estadísticas de jugadores del partido en formato diccionario (raw JSON)
        
        Args:
            match_id: ID del partido
        
        Returns:
            Diccionario con estadísticas de jugadores
        """
        try:
            print(f"Obteniendo estadísticas de jugadores raw del partido {match_id}...")
            stats = sb.player_match_stats(match_id=match_id, fmt="dict", creds=self.creds)
            print(f"Estadísticas de jugadores raw obtenidas")
            return stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas de jugadores raw: {e}")
            return {}
    
    def get_player_season_stats_raw(self, competition_id: int, season_id: int) -> Dict:
        """
        Obtiene estadísticas de jugadores de temporada en formato diccionario (raw JSON)
        
        Args:
            competition_id: ID de la competición
            season_id: ID de la temporada
        
        Returns:
            Diccionario con estadísticas de jugadores
        """
        try:
            print(f"Obteniendo estadísticas de jugadores raw (Comp: {competition_id}, Temp: {season_id})...")
            stats = sb.player_season_stats(
                competition_id=competition_id,
                season_id=season_id,
                fmt="dict",
                creds=self.creds
            )
            print(f"Estadísticas de jugadores raw obtenidas")
            return stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas de jugadores raw: {e}")
            return {}
    
    def get_team_match_stats_raw(self, match_id: int) -> Dict:
        """
        Obtiene estadísticas de equipos del partido en formato diccionario (raw JSON)
        
        Args:
            match_id: ID del partido
        
        Returns:
            Diccionario con estadísticas de equipos
        """
        try:
            print(f"Obteniendo estadísticas de equipos raw del partido {match_id}...")
            stats = sb.team_match_stats(match_id=match_id, fmt="dict", creds=self.creds)
            print(f"Estadísticas de equipos raw obtenidas")
            return stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas de equipos raw: {e}")
            return {}
    
    def get_team_season_stats_raw(self, competition_id: int, season_id: int) -> Dict:
        """
        Obtiene estadísticas de equipos de temporada en formato diccionario (raw JSON)
        
        Args:
            competition_id: ID de la competición
            season_id: ID de la temporada
        
        Returns:
            Diccionario con estadísticas de equipos
        """
        try:
            print(f"Obteniendo estadísticas de equipos raw (Comp: {competition_id}, Temp: {season_id})...")
            stats = sb.team_season_stats(
                competition_id=competition_id,
                season_id=season_id,
                fmt="dict",
                creds=self.creds
            )
            print(f"Estadísticas de equipos raw obtenidas")
            return stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas de equipos raw: {e}")
            return {}
    
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
                    events = self.get_events(first_match_id, include_360_metrics=True)
                    sample_data['events'] = events.head(100)  # Primeros 100 eventos
                    
                    # Obtener alineaciones del primer partido
                    lineups = self.get_lineups(first_match_id)
                    sample_data['lineups'] = lineups
            
            print("Datos de muestra obtenidos correctamente")
            return sample_data
            
        except Exception as e:
            print(f"Error obteniendo datos de muestra: {e}")
            return sample_data
    
    def get_competition_info(self, competition_id: int, season_id: int) -> Dict:
        """
        Obtiene información detallada de una competición específica
        
        Args:
            competition_id: ID de la competición
            season_id: ID de la temporada
        
        Returns:
            Diccionario con información de la competición
        """
        try:
            competitions = self.get_competitions()
            comp_info = competitions[
                (competitions['competition_id'] == competition_id) & 
                (competitions['season_id'] == season_id)
            ]
            
            if not comp_info.empty:
                return comp_info.iloc[0].to_dict()
            else:
                print(f"No se encontró la competición {competition_id} - {season_id}")
                return {}
                
        except Exception as e:
            print(f"Error obteniendo información de competición: {e}")
            return {}
    
    def get_match_info(self, match_id: int) -> Dict:
        """
        Obtiene información detallada de un partido específico
        
        Args:
            match_id: ID del partido
        
        Returns:
            Diccionario con información del partido
        """
        try:
            # Primero necesitamos encontrar en qué competición está el partido
            competitions = self.get_competitions()
            
            for _, comp in competitions.iterrows():
                matches = self.get_matches(comp['competition_id'], comp['season_id'])
                match_info = matches[matches['match_id'] == match_id]
                
                if not match_info.empty:
                    match_data = match_info.iloc[0].to_dict()
                    match_data['competition_name'] = comp['competition_name']
                    match_data['season_name'] = comp['season_name']
                    return match_data
            
            print(f"No se encontró el partido {match_id}")
            return {}
            
        except Exception as e:
            print(f"Error obteniendo información del partido: {e}")
            return {}
    
    def search_team_matches(self, team_name: str, competition_id: int = None, 
                           season_id: int = None) -> pd.DataFrame:
        """
        Busca partidos de un equipo específico
        
        Args:
            team_name: Nombre del equipo
            competition_id: ID de la competición (opcional)
            season_id: ID de la temporada (opcional)
        
        Returns:
            DataFrame con partidos del equipo
        """
        try:
            if competition_id and season_id:
                matches = self.get_matches(competition_id, season_id)
            else:
                # Buscar en todas las competiciones disponibles
                competitions = self.get_competitions()
                all_matches = []
                
                for _, comp in competitions.iterrows():
                    comp_matches = self.get_matches(comp['competition_id'], comp['season_id'])
                    if not comp_matches.empty:
                        all_matches.append(comp_matches)
                
                if all_matches:
                    matches = pd.concat(all_matches, ignore_index=True)
                else:
                    return pd.DataFrame()
            
            # Buscar partidos del equipo
            team_matches = matches[
                (matches['home_team'].str.contains(team_name, case=False, na=False)) |
                (matches['away_team'].str.contains(team_name, case=False, na=False))
            ]
            
            print(f"Encontrados {len(team_matches)} partidos para {team_name}")
            return team_matches
            
        except Exception as e:
            print(f"Error buscando partidos del equipo {team_name}: {e}")
            return pd.DataFrame()
    
    def get_available_data_summary(self) -> Dict:
        """
        Obtiene un resumen de todos los datos disponibles
        
        Returns:
            Diccionario con resumen de datos disponibles
        """
        try:
            print("Generando resumen de datos disponibles...")
            
            competitions = self.get_competitions()
            summary = {
                'total_competitions': len(competitions),
                'countries': competitions['country_name'].unique().tolist() if not competitions.empty else [],
                'divisions': competitions['competition_name'].unique().tolist() if not competitions.empty else [],
                'seasons': competitions['season_name'].unique().tolist() if not competitions.empty else [],
                'genders': competitions['competition_gender'].unique().tolist() if not competitions.empty else []
            }
            
            # Contar partidos totales
            total_matches = 0
            for _, comp in competitions.iterrows():
                matches = self.get_matches(comp['competition_id'], comp['season_id'])
                total_matches += len(matches)
            
            summary['total_matches'] = total_matches
            
            print(f"Resumen generado: {summary['total_competitions']} competiciones, {summary['total_matches']} partidos")
            return summary
            
        except Exception as e:
            print(f"Error generando resumen: {e}")
            return {}