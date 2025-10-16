"""
Configuración principal para el MVP Club América
"""
import os
from dotenv import load_dotenv
from statsbombpy import sb

# Cargar variables de entorno
load_dotenv()

class StatsBombConfig:
    def __init__(self):
        """Inicializa la configuración de StatsBomb"""
        self.username = os.getenv('STATSBOMB_USERNAME')
        self.password = os.getenv('STATSBOMB_PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError(
                "Las credenciales de StatsBomb no están configuradas."
            )
        
        print(f"Usuario configurado: {self.username}")
    
    def get_credentials(self):
        """Devuelve las credenciales de StatsBomb"""
        return {
            "user": self.username,
            "passwd": self.password
        }

    def test_connection(self):
        """Prueba la conexión con la API de StatsBomb"""
        try:

            creds = self.get_credentials()

            print("Probando conexión con StatsBomb API...")
            competitions = sb.competitions(creds=creds)
            print(f"Conexión exitosa - {len(competitions)} competiciones disponibles")

            # Mostrar competiciones mexicanas si las hay
            mx_competitions = competitions[competitions['country_name'] == 'Mexico']
            if not mx_competitions.empty:
                print(f"{len(mx_competitions)} competiciones mexicanas encontradas:")
                for _, comp in mx_competitions.iterrows():
                    print(f"   - {comp['competition_name']} ({comp['season_name']})")
            else:
                print("No se encontraron competiciones mexicanas")
            
            return competitions
            
        except Exception as e:
            print(f"Error de conexión: {e}")
            return None