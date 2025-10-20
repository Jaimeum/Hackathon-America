"""
Streamlit Application for Club América Scouting System
Sistema de Scouting Inteligente - Club América
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.models.america_analysis import AmericaAnalysis
from src.models.team_fit_analyzer import TeamFitAnalyzer
from src.models.recommender import PlayerRecommender
from src.utils.data_loader import DataLoader
from src.utils.data_processor import DataProcessor
from src.config import POSITION_FEATURES, NORMALIZED_FEATURES

# Page configuration
st.set_page_config(
    page_title="Club América Scouting System",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .recommendation-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache data"""
    try:
        data_loader = DataLoader()
        summary = data_loader.get_summary()
        return data_loader, summary
    except Exception as e:
        st.warning(f"⚠️ No se pudieron cargar los datos: {e}")
        st.info("💡 **Solución**: Asegúrate de que los datos procesados estén disponibles en la carpeta `data/processed/`")
        
        # Return dummy data to prevent complete failure
        dummy_summary = {
            'total_players': 0,
            'total_teams': 0,
            'total_seasons': 0,
            'avg_minutes': 0,
            'positions': {}
        }
        return None, dummy_summary

@st.cache_resource
def initialize_analysis():
    """Initialize and cache analysis components"""
    try:
        analysis = AmericaAnalysis()
        # Try to load existing profile first
        profile_path = Path("data/results/america_profile.json")
        if profile_path.exists():
            import json
            with open(profile_path, 'r') as f:
                analysis.america_profile = json.load(f)
            analysis.initialize_analyzers()
        else:
            # Build profile if it doesn't exist
            analysis.build_america_profile()
            analysis.initialize_analyzers()
        return analysis
    except Exception as e:
        st.warning(f"⚠️ Error inicializando análisis: {e}")
        st.info("💡 **Solución**: Asegúrate de que los datos procesados estén disponibles y las credenciales de StatsBomb estén configuradas")
        return None

def display_america_profile(analysis):
    """Display Club América profile information"""
    if not analysis or not analysis.america_profile:
        st.warning("Perfil del América no disponible")
        return
    
    profile = analysis.america_profile
    
    st.markdown('<div class="section-header">🏆 Perfil del Club América</div>', unsafe_allow_html=True)
    
    # Metadata
    meta = profile.get('metadata', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Temporadas", meta.get('n_seasons', 0))
    with col2:
        st.metric("Partidos", meta.get('n_matches', 0))
    with col3:
        st.metric("Win Rate", f"{meta.get('win_rate', 0):.1f}%")
    with col4:
        st.metric("Equipos Analizados", 18)
    
    # Rankings
    st.markdown("### 📊 Rankings vs Competencia")
    rankings = profile.get('rankings', {})
    
    if rankings:
        # Create ranking chart
        ranking_df = pd.DataFrame([
            {"Dimension": dim.replace('_', ' ').title(), "Percentile": percentile}
            for dim, percentile in rankings.items()
        ]).sort_values('Percentile', ascending=True)
        
        fig = px.bar(
            ranking_df, 
            x='Percentile', 
            y='Dimension', 
            orientation='h',
            title="Rankings del América vs Liga MX",
            color='Percentile',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display rankings in columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Fortalezas:**")
            for dim, percentile in sorted(rankings.items(), key=lambda x: x[1], reverse=True)[:3]:
                if percentile >= 60:
                    st.write(f"• {dim.replace('_', ' ').title()}: {percentile:.1f}%")
        
        with col2:
            st.markdown("**Áreas de Mejora:**")
            for dim, percentile in sorted(rankings.items(), key=lambda x: x[1])[:3]:
                if percentile < 50:
                    st.write(f"• {dim.replace('_', ' ').title()}: {percentile:.1f}%")

def normalize_text(text: str) -> str:
    """Normalize text for better matching (remove accents, lowercase)"""
    import unicodedata
    
    # Remove accents
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    return text.lower().strip()

def get_player_suggestions(data_loader, query: str, limit: int = 10):
    """Get player name suggestions based on query with improved matching"""
    if not query or len(query) < 2:
        return []
    
    try:
        # Get all players
        all_players = data_loader.get_players(min_minutes=0)
        
        # Normalize query
        query_normalized = normalize_text(query)
        suggestions = []
        
        for _, player in all_players.iterrows():
            player_name = str(player['player_name'])
            player_name_normalized = normalize_text(player_name)
            
            # Check if query matches (partial match)
            if query_normalized in player_name_normalized:
                # Calculate relevance score
                relevance_score = 0
                
                # Exact match gets highest score
                if query_normalized == player_name_normalized:
                    relevance_score = 100
                # Starts with query gets high score
                elif player_name_normalized.startswith(query_normalized):
                    relevance_score = 80
                # Contains query gets medium score
                elif query_normalized in player_name_normalized:
                    relevance_score = 60
                
                # Bonus for shorter names (more specific)
                if len(player_name) < 20:
                    relevance_score += 10
                
                suggestions.append({
                    'name': player_name,
                    'team': player['team_name'],
                    'position': player['position_category'],
                    'relevance': relevance_score
                })
        
        # Sort by relevance score (highest first)
        suggestions.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Remove duplicates and return top results
        seen_names = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion['name'] not in seen_names:
                seen_names.add(suggestion['name'])
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:limit]
    
    except Exception as e:
        st.error(f"Error getting suggestions: {e}")
        return []

def display_player_selection_interface(data_loader, session_key_prefix="player"):
    """Display player selection interface with suggestions"""
    
    # Initialize session state
    selected_key = f'selected_{session_key_prefix}'
    search_input_key = f'{session_key_prefix}_search_input'
    analysis_key = f'analyze_{session_key_prefix}'
    
    if selected_key not in st.session_state:
        st.session_state[selected_key] = None
    if analysis_key not in st.session_state:
        st.session_state[analysis_key] = None
    
    # Player search with autocomplete
    col1, col2 = st.columns([3, 1])
    
    with col1:
        player_input = st.text_input(
            "Buscar jugador:", 
            placeholder="Ej: Henry, Martín, Zendejas...",
            key=search_input_key
        )
    
    with col2:
        search_button = st.button("🔍 Buscar", key=f"search_{session_key_prefix}", type="primary")
    
    # Show suggestions if user is typing
    if player_input and len(player_input) >= 2:
        suggestions = get_player_suggestions(data_loader, player_input)
        
        if suggestions:
            st.markdown("**🔍 Jugadores encontrados:**")
            st.markdown("*Haz clic en un jugador para analizarlo directamente*")
            
            # Create a container for suggestions
            with st.container():
                for i, suggestion in enumerate(suggestions):
                    # Create a more attractive suggestion card
                    with st.expander(f"📋 {suggestion['name']}", expanded=False):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Equipo:** {suggestion['team']}")
                            st.write(f"**Posición:** {suggestion['position']}")
                        
                        with col2:
                            # Direct analysis button - no forms needed
                            button_key = f"analyze_{session_key_prefix}_{i}_{hash(suggestion['name'])}"
                            if st.button("✅ Analizar", key=button_key, type="primary"):
                                st.session_state[analysis_key] = suggestion['name']
                                st.rerun()
        else:
            st.warning(f"❌ No se encontraron jugadores que coincidan con '{player_input}'. Intenta con:")
            st.markdown("• Un nombre más corto (ej: 'Henry' en lugar de 'Henry Martín')")
            st.markdown("• Sin acentos (ej: 'Martin' en lugar de 'Martín')")
            st.markdown("• Solo el apellido o nombre")
    
    # Check if we should analyze a player
    if st.session_state[analysis_key]:
        player_to_analyze = st.session_state[analysis_key]
        st.success(f"✅ Analizando: **{player_to_analyze}**")
        
        # Clear the analysis state after showing the message
        if st.button("🔄 Cambiar jugador", key=f"change_{session_key_prefix}"):
            st.session_state[analysis_key] = None
            st.rerun()
        
        return player_to_analyze
    
    # Use direct input if search button is pressed
    if search_button and player_input:
        return player_input
    
    return None

def display_player_analysis(analysis):
    """Display player analysis interface"""
    st.markdown('<div class="section-header">🔍 Análisis de Jugadores</div>', unsafe_allow_html=True)
    
    if not analysis or not analysis.analyzer:
        st.warning("Analizador no disponible")
        return
    
    # Help text
    st.info("💡 **Consejo**: Escribe al menos 2 caracteres del nombre del jugador para ver sugerencias. El sistema funciona con nombres completos, parciales, con o sin acentos.")
    
    # Get data loader for suggestions
    from src.utils.data_loader import DataLoader
    data_loader = DataLoader()
    
    # Use the new selection interface
    player_name = display_player_selection_interface(data_loader, "player")
    
    if player_name:
        with st.spinner(f"Analizando a {player_name}..."):
            try:
                fit_result = analysis.analyze_player_fit(player_name)
                
                if fit_result:
                    st.markdown(f"### {fit_result['player_name']}")
                    
                    # Display fit scores
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Overall Fit", 
                            f"{fit_result['overall_fit']:.1f}/100",
                            delta=None
                        )
                    with col2:
                        st.metric(
                            "Technical Fit", 
                            f"{fit_result['technical_fit']:.1f}/100"
                        )
                    with col3:
                        st.metric(
                            "Tactical Fit", 
                            f"{fit_result['tactical_fit']:.1f}/100"
                        )
                    with col4:
                        st.metric(
                            "Impact Score", 
                            f"{fit_result['impact_score']:.1f}/100"
                        )
                    
                    # Fit breakdown chart
                    fit_data = {
                        'Component': ['Technical Fit', 'Tactical Fit', 'Impact Score'],
                        'Score': [
                            fit_result['technical_fit'],
                            fit_result['tactical_fit'],
                            fit_result['impact_score']
                        ],
                        'Weight': [0.35, 0.30, 0.35]
                    }
                    
                    fig = px.bar(
                        fit_data,
                        x='Component',
                        y='Score',
                        title="Breakdown de Compatibilidad",
                        color='Score',
                        color_continuous_scale='RdYlGn'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Strengths and concerns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if fit_result['strengths']:
                            st.markdown("**Fortalezas:**")
                            for strength in fit_result['strengths']:
                                st.write(f"• {strength}")
                    
                    with col2:
                        if fit_result['concerns']:
                            st.markdown("**Áreas de Atención:**")
                            for concern in fit_result['concerns']:
                                st.write(f"• {concern}")
                    
                    # Key metrics
                    metrics = fit_result.get('key_metrics', {})
                    if metrics:
                        st.markdown("### 📈 Métricas Clave")
                        metric_cols = st.columns(3)
                        
                        with metric_cols[0]:
                            st.metric("Minutos", f"{metrics.get('minutes', 0):.0f}")
                        with metric_cols[1]:
                            st.metric("OBV/90", f"{metrics.get('obv_90', 0):.2f}")
                        with metric_cols[2]:
                            st.metric("Goles/90", f"{metrics.get('goals_90', 0):.2f}")
            
            except Exception as e:
                st.error(f"Error analizando jugador: {e}")

def display_recommendations(analysis):
    """Display player recommendations"""
    st.markdown('<div class="section-header">🎯 Recomendaciones de Fichajes</div>', unsafe_allow_html=True)
    
    if not analysis or not analysis.analyzer:
        st.warning("Analizador no disponible")
        return
    
    # Position selector
    position = st.selectbox(
        "Seleccionar posición:",
        ['FWD', 'MED', 'DEF', 'GK'],
        format_func=lambda x: {
            'FWD': 'Delanteros',
            'MED': 'Mediocampistas', 
            'DEF': 'Defensas',
            'GK': 'Porteros'
        }[x]
    )
    
    # Parameters
    col1, col2 = st.columns(2)
    with col1:
        top_n = st.slider("Número de recomendaciones:", 1, 10, 5)
    with col2:
        min_fit = st.slider("Fit mínimo:", 0.0, 100.0, 60.0)
    
    if st.button("Obtener Recomendaciones", type="primary"):
        try:
            recommendations = analysis.get_position_recommendations(
                position=position,
                top_n=top_n,
                min_fit=min_fit
            )
            
            if not recommendations.empty:
                st.markdown(f"### Top {top_n} {position}s Recomendados")
                
                # Display recommendations
                for idx, player in recommendations.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="recommendation-card">
                            <h4>{player['player_name']}</h4>
                            <p><strong>Equipo:</strong> {player['team_name']}</p>
                            <p><strong>Posición:</strong> {player['primary_position']}</p>
                            <div style="display: flex; gap: 20px;">
                                <span><strong>Overall Fit:</strong> {player['overall_fit']:.1f}/100</span>
                                <span><strong>Technical:</strong> {player['technical_fit']:.1f}/100</span>
                                <span><strong>Tactical:</strong> {player['tactical_fit']:.1f}/100</span>
                                <span><strong>Impact:</strong> {player['impact_score']:.1f}/100</span>
                            </div>
                            <div style="display: flex; gap: 20px; margin-top: 10px;">
                                <span><strong>Minutos:</strong> {player['minutes']:.0f}</span>
                                <span><strong>Goles/90:</strong> {player['goals_90']:.2f}</span>
                                <span><strong>Assists/90:</strong> {player['assists_90']:.2f}</span>
                                <span><strong>OBV/90:</strong> {player['obv_90']:.2f}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Create comparison chart
                fig = px.scatter(
                    recommendations,
                    x='technical_fit',
                    y='tactical_fit',
                    size='impact_score',
                    color='overall_fit',
                    hover_data=['player_name', 'team_name', 'overall_fit'],
                    title="Comparación de Recomendaciones",
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.warning(f"No se encontraron jugadores para {position} con fit mínimo de {min_fit}")
        
        except Exception as e:
            st.error(f"Error obteniendo recomendaciones: {e}")

def display_similar_players(analysis):
    """Display similar players finder"""
    st.markdown('<div class="section-header">🔗 Jugadores Similares</div>', unsafe_allow_html=True)
    
    if not analysis or not analysis.recommender:
        st.warning("Recomendador no disponible")
        return
    
    # Help text
    st.info("💡 **Consejo**: Escribe al menos 2 caracteres del nombre del jugador de referencia para ver sugerencias. El sistema encuentra jugadores con estilos de juego similares.")
    
    # Get data loader for suggestions
    from src.utils.data_loader import DataLoader
    data_loader = DataLoader()
    
    # Use the new selection interface
    reference_player = display_player_selection_interface(data_loader, "similar_player")
    
    # Parameters
    col1, col2 = st.columns(2)
    with col1:
        top_n = st.slider("Número de similares:", 1, 10, 5)
    with col2:
        same_position = st.checkbox("Solo misma posición", value=True)
    
    if reference_player and st.button("Buscar Similares"):
        with st.spinner(f"Buscando jugadores similares a {reference_player}..."):
            try:
                similar_players = analysis.find_similar_players(
                    player_name=reference_player,
                    top_n=top_n,
                    same_position_only=same_position
                )
                
                if not similar_players.empty:
                    st.markdown(f"### Jugadores similares a {reference_player}")
                    
                    # Display similar players
                    for idx, player in similar_players.iterrows():
                        with st.container():
                            st.markdown(f"""
                            <div class="recommendation-card">
                                <h4>{player['player_name']}</h4>
                                <p><strong>Equipo:</strong> {player['team_name']}</p>
                                <p><strong>Posición:</strong> {player['position_category']}</p>
                                <div style="display: flex; gap: 20px;">
                                    <span><strong>Similitud:</strong> {player['similarity_score']:.3f}</span>
                                    <span><strong>Score Final:</strong> {player['final_score']:.3f}</span>
                                    <span><strong>Context Score:</strong> {player['context_score']:.3f}</span>
                                </div>
                                <div style="display: flex; gap: 20px; margin-top: 10px;">
                                    <span><strong>Minutos:</strong> {player['player_season_minutes']:.0f}</span>
                                    <span><strong>Goles/90:</strong> {player['player_season_goals_90']:.2f}</span>
                                    <span><strong>OBV/90:</strong> {player['player_season_obv_90']:.2f}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Create similarity chart
                    fig = px.scatter(
                        similar_players,
                        x='similarity_score',
                        y='context_score',
                        size='player_season_obv_90',
                        color='final_score',
                        hover_data=['player_name', 'team_name'],
                        title="Análisis de Similitud",
                        color_continuous_scale='viridis'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.warning(f"No se encontraron jugadores similares a {reference_player}")
            
            except Exception as e:
                st.error(f"Error buscando jugadores similares: {e}")

def display_dashboard(data_loader, summary):
    """Display main dashboard"""
    
    if not summary or summary['total_players'] == 0:
        st.error("❌ No se pudieron cargar los datos")
        st.markdown("""
        **Posibles soluciones:**
        
        1. **Verifica que los datos procesados estén disponibles** en la carpeta `data/processed/`
        2. **Ejecuta el pipeline de datos** usando `python main.py --data`
        3. **Verifica las credenciales de StatsBomb** en las variables de entorno
        """)
        return
    
    # Key metrics
    st.markdown('<div class="section-header">📊 Resumen del Dataset</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jugadores", summary['total_players'])
    with col2:
        st.metric("Total Equipos", summary['total_teams'])
    with col3:
        st.metric("Temporadas", summary['total_seasons'])
    with col4:
        st.metric("Minutos Promedio", f"{summary['avg_minutes']:.0f}")
    
    # Position distribution
    positions = summary['positions']
    if positions:
        fig = px.pie(
            values=list(positions.values()),
            names=list(positions.keys()),
            title="Distribución por Posición"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 No hay datos de distribución por posición disponibles")

def main():
    """Main application function"""
    
    # Startup message
    st.markdown('<div class="main-header">⚽ Club América Scouting System</div>', unsafe_allow_html=True)
    
    # Check environment setup
    env_file = Path(".env")
    if not env_file.exists():
        st.error("🚨 **Error de Configuración**")
        st.markdown("""
        **El archivo `.env` no está presente.** Para que la aplicación funcione correctamente:
        
        1. **En Streamlit Cloud**: Ve a Settings → Secrets y agrega:
           ```
           STATSBOMB_USERNAME=tu_usuario
           STATSBOMB_PASSWORD=tu_contraseña
           ```
        
        2. **Localmente**: Copia `env.example` a `.env` y configura tus credenciales
        
        3. **Datos**: Asegúrate de que los datos procesados estén disponibles en `data/processed/`
        """)
        return
    
    # Sidebar navigation
    st.sidebar.title("🏆 Club América Scouting")
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "Navegación",
        ["Dashboard", "Perfil del América", "Análisis de Jugadores", "Recomendaciones", "Jugadores Similares"]
    )
    
    # Load data
    data_loader, summary = load_data()
    
    # Initialize analysis
    analysis = initialize_analysis()
    
    # Display selected page
    if page == "Dashboard":
        display_dashboard(data_loader, summary)
    
    elif page == "Perfil del América":
        display_america_profile(analysis)
    
    elif page == "Análisis de Jugadores":
        display_player_analysis(analysis)
    
    elif page == "Recomendaciones":
        display_recommendations(analysis)
    
    elif page == "Jugadores Similares":
        display_similar_players(analysis)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **Sistema de Scouting Inteligente**
    
    Desarrollado para el Club América
    
    📊 Datos: StatsBomb API  
    🤖 ML: PCA + Similarity Analysis  
    ⚽ OBV: On-Ball Value Integration
    """)

if __name__ == "__main__":
    main()
