"""
PCA Analysis module for team statistics dimensionality reduction
Extracted from notebooks/PCA.ipynb
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

from src.utils.data_fetcher import StatsBombDataFetcher


class PCAAnalyzer:
    """PCA analysis for team statistics to identify key dimensions"""
    
    def __init__(self):
        self.fetcher = StatsBombDataFetcher()
        self.scaler = StandardScaler()
        self.pca = PCA(random_state=42)
        self.team_data = None
        self.X_scaled = None
        self.X_pca = None
        self.feature_cols = None
        self.explained_variance_ratio = None
        
    def load_team_data(self, seasons: List[Tuple[int, int]]):
        """
        Carga datos de equipos para múltiples temporadas
        
        Args:
            seasons: Lista de (season_id, season_name) tuplas
        """
        all_teams = []
        
        for season_id, season_name in seasons:
            print(f"Cargando temporada {season_id} ({season_name})...")
            team_stats = self.fetcher.get_team_season_stats(competition_id=73, season_id=season_id)
            if not team_stats.empty:
                all_teams.append(team_stats)
                print(f"   {len(team_stats)} equipos cargados")
        
        if all_teams:
            self.team_data = pd.concat(all_teams, ignore_index=True)
            print(f"\nTotal: {len(self.team_data)} registros cargados")
            print(f"   Equipos únicos: {self.team_data['team_name'].nunique()}")
            print(f"   Temporadas: {self.team_data['season_name'].nunique()}")
        else:
            raise ValueError("No se pudieron cargar datos de equipos")
    
    def prepare_features(self):
        """
        Prepara las features para el análisis PCA
        """
        if self.team_data is None:
            raise ValueError("Carga los datos primero con load_team_data()")
        
        # Identificar columnas numéricas
        numeric_cols = self.team_data.select_dtypes(include=[np.number]).columns
        
        # Excluir IDs y metadatos
        exclude_cols = [
            'account_id', 'team_id', 'competition_id', 'season_id',
            'team_season_matches', 'team_season_minutes'
        ]
        
        self.feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        print(f"Features para PCA: {len(self.feature_cols)}")
        
        # Extraer features y limpiar NaNs
        X = self.team_data[self.feature_cols].fillna(0)
        
        print(f"\nShape de datos: {X.shape}")
        print(f"NaNs restantes: {X.isna().sum().sum()}")
        
        return X
    
    def fit_pca(self, n_components: Optional[int] = None):
        """
        Aplica PCA a los datos de equipos
        
        Args:
            n_components: Número de componentes principales (None para todos)
        """
        X = self.prepare_features()
        
        # Escalar features
        self.X_scaled = self.scaler.fit_transform(X)
        
        # PCA
        self.pca = PCA(n_components=n_components, random_state=42)
        self.X_pca = self.pca.fit_transform(self.X_scaled)
        
        # Varianza explicada
        self.explained_variance_ratio = self.pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(self.explained_variance_ratio)
        
        print("VARIANZA EXPLICADA POR COMPONENTE:\n")
        n_show = min(30, len(self.explained_variance_ratio))
        for i in range(n_show):
            print(f"   PC{i+1}: {self.explained_variance_ratio[i]:.2%} (acumulado: {cumulative_variance[i]:.2%})")
        
        return self.X_pca
    
    def get_top_features_by_component(self, n_components: int = 10, top_n: int = 5):
        """
        Identifica las features más importantes para cada componente principal
        
        Args:
            n_components: Número de componentes a analizar
            top_n: Número de features top por componente
            
        Returns:
            Diccionario con features importantes por componente
        """
        if self.pca is None:
            raise ValueError("Ejecuta fit_pca() primero")
        
        components_data = {}
        
        for i in range(min(n_components, self.pca.n_components_)):
            component_idx = i
            component_weights = self.pca.components_[component_idx]
            
            # Crear DataFrame con features y pesos
            feature_weights = pd.DataFrame({
                'feature': self.feature_cols,
                'weight': component_weights
            })
            
            # Obtener features más importantes (absoluto)
            feature_weights['abs_weight'] = np.abs(feature_weights['weight'])
            top_features = feature_weights.nlargest(top_n, 'abs_weight')
            
            components_data[f'PC{i+1}'] = {
                'explained_variance': self.explained_variance_ratio[i],
                'top_features': top_features[['feature', 'weight', 'abs_weight']].to_dict('records')
            }
        
        return components_data
    
    def analyze_team_positions(self, team_name: str = "América"):
        """
        Analiza la posición de un equipo específico en el espacio PCA
        
        Args:
            team_name: Nombre del equipo a analizar
            
        Returns:
            DataFrame con posiciones del equipo en componentes principales
        """
        if self.X_pca is None:
            raise ValueError("Ejecuta fit_pca() primero")
        
        # Filtrar datos del equipo
        team_mask = self.team_data['team_name'].str.contains(team_name, case=False, na=False)
        team_indices = self.team_data[team_mask].index
        
        if len(team_indices) == 0:
            print(f"No se encontraron datos para {team_name}")
            return pd.DataFrame()
        
        # Obtener posiciones PCA del equipo
        team_pca_data = self.X_pca[team_indices]
        
        # Crear DataFrame con resultados
        results = []
        for i, idx in enumerate(team_indices):
            team_record = self.team_data.loc[idx]
            pca_record = team_pca_data[i]
            
            record = {
                'season_name': team_record['season_name'],
                'team_name': team_record['team_name']
            }
            
            # Agregar componentes principales
            for j in range(min(10, len(pca_record))):
                record[f'PC{j+1}'] = pca_record[j]
            
            results.append(record)
        
        return pd.DataFrame(results)
    
    def plot_explained_variance(self, n_components: int = 20):
        """
        Grafica la varianza explicada por componente
        
        Args:
            n_components: Número de componentes a mostrar
        """
        if self.explained_variance_ratio is None:
            raise ValueError("Ejecuta fit_pca() primero")
        
        n_components = min(n_components, len(self.explained_variance_ratio))
        
        plt.figure(figsize=(12, 5))
        
        # Varianza explicada individual
        plt.subplot(1, 2, 1)
        plt.bar(range(1, n_components + 1), self.explained_variance_ratio[:n_components])
        plt.xlabel('Componente Principal')
        plt.ylabel('Varianza Explicada')
        plt.title('Varianza Explicada por Componente')
        plt.grid(True, alpha=0.3)
        
        # Varianza explicada acumulada
        plt.subplot(1, 2, 2)
        cumulative_variance = np.cumsum(self.explained_variance_ratio[:n_components])
        plt.plot(range(1, n_components + 1), cumulative_variance, 'bo-')
        plt.xlabel('Número de Componentes')
        plt.ylabel('Varianza Explicada Acumulada')
        plt.title('Varianza Explicada Acumulada')
        plt.grid(True, alpha=0.3)
        plt.axhline(y=0.8, color='r', linestyle='--', alpha=0.7, label='80%')
        plt.axhline(y=0.9, color='orange', linestyle='--', alpha=0.7, label='90%')
        plt.legend()
        
        plt.tight_layout()
        plt.show()
    
    def plot_team_comparison(self, teams: List[str], components: Tuple[int, int] = (1, 2)):
        """
        Grafica la posición de equipos en el espacio de componentes principales
        
        Args:
            teams: Lista de nombres de equipos
            components: Tupla con los componentes a graficar (PC1, PC2)
        """
        if self.X_pca is None:
            raise ValueError("Ejecuta fit_pca() primero")
        
        pc1, pc2 = components[0] - 1, components[1] - 1  # Convertir a índices base 0
        
        plt.figure(figsize=(12, 8))
        
        # Graficar todos los equipos en gris
        plt.scatter(self.X_pca[:, pc1], self.X_pca[:, pc2], 
                   alpha=0.3, color='gray', s=20, label='Otros equipos')
        
        # Graficar equipos específicos
        colors = plt.cm.Set1(np.linspace(0, 1, len(teams)))
        
        for i, team_name in enumerate(teams):
            team_mask = self.team_data['team_name'].str.contains(team_name, case=False, na=False)
            team_indices = self.team_data[team_mask].index
            
            if len(team_indices) > 0:
                team_pca_data = self.X_pca[team_indices]
                plt.scatter(team_pca_data[:, pc1], team_pca_data[:, pc2], 
                           color=colors[i], s=60, label=team_name, alpha=0.8)
        
        plt.xlabel(f'PC{components[0]} ({self.explained_variance_ratio[pc1]:.1%} varianza)')
        plt.ylabel(f'PC{components[1]} ({self.explained_variance_ratio[pc2]:.1%} varianza)')
        plt.title(f'Posición de Equipos en PC{components[0]} vs PC{components[1]}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def get_team_clusters(self, n_clusters: int = 5, n_components: int = 10):
        """
        Identifica clusters de equipos basado en componentes principales
        
        Args:
            n_clusters: Número de clusters
            n_components: Número de componentes a usar
            
        Returns:
            DataFrame con asignaciones de cluster
        """
        from sklearn.cluster import KMeans
        
        if self.X_pca is None:
            raise ValueError("Ejecuta fit_pca() primero")
        
        # Usar solo los primeros n_components
        X_cluster = self.X_pca[:, :n_components]
        
        # Aplicar K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(X_cluster)
        
        # Crear DataFrame con resultados
        results = self.team_data.copy()
        results['cluster'] = cluster_labels
        
        # Mostrar distribución de clusters
        print(f"\nDistribución de clusters:")
        cluster_dist = results['cluster'].value_counts().sort_index()
        for cluster, count in cluster_dist.items():
            print(f"   Cluster {cluster}: {count} equipos")
        
        return results
    
    def export_pca_results(self, output_dir: str = "data/results"):
        """
        Exporta resultados del análisis PCA
        
        Args:
            output_dir: Directorio de salida
        """
        if self.X_pca is None:
            raise ValueError("Ejecuta fit_pca() primero")
        
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Exportar datos PCA
        pca_df = self.team_data.copy()
        for i in range(min(10, self.X_pca.shape[1])):
            pca_df[f'PC{i+1}'] = self.X_pca[:, i]
        
        pca_file = output_path / "team_pca_results.csv"
        pca_df.to_csv(pca_file, index=False)
        print(f"Resultados PCA guardados: {pca_file}")
        
        # Exportar importancia de features
        feature_importance = self.get_top_features_by_component()
        feature_file = output_path / "pca_feature_importance.json"
        
        import json
        with open(feature_file, 'w') as f:
            json.dump(feature_importance, f, indent=2, default=str)
        print(f"Importancia de features guardada: {feature_file}")
        
        return {
            'pca_data': pca_file,
            'feature_importance': feature_file
        }


def run_pca_analysis():
    """
    Función de conveniencia para ejecutar análisis PCA completo
    """
    analyzer = PCAAnalyzer()
    
    # Definir temporadas
    seasons = [
        (317, '2024/2025'),
        (281, '2023/2024'),
        (235, '2022/2023'),
        (108, '2021/2022')
    ]
    
    # Cargar datos
    analyzer.load_team_data(seasons)
    
    # Aplicar PCA
    analyzer.fit_pca()
    
    # Análisis de América
    america_data = analyzer.analyze_team_positions("América")
    print(f"\nPosición del América en PCA:")
    print(america_data)
    
    # Obtener features importantes
    feature_importance = analyzer.get_top_features_by_component()
    print(f"\nFeatures más importantes:")
    for pc, data in feature_importance.items():
        print(f"\n{pc} (Varianza: {data['explained_variance']:.2%}):")
        for feature in data['top_features']:
            print(f"   {feature['feature']}: {feature['weight']:.3f}")
    
    # Exportar resultados
    files = analyzer.export_pca_results()
    
    return analyzer, files


if __name__ == "__main__":
    analyzer, files = run_pca_analysis()
