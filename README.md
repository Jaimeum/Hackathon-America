# ⚽ Sistema de Scouting Inteligente - Club América

> **Plataforma para identificación de talento, evaluación de compatibilidad táctica y proyección de rendimiento de jugadores en Liga MX**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![StatsBomb](https://img.shields.io/badge/Data-StatsBomb_API-red.svg)](https://statsbomb.com/)

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características Principales](#-características-principales)
- [Metodología](#-metodología)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Dataset](#-dataset)
- [Resultados](#-resultados)
- [Tecnologías](#-tecnologías)
- [Contribuciones](#-contribuciones)
- [Licencia](#-licencia)
- [Contacto](#-contacto)

---

## Descripción

Este proyecto desarrolla un **sistema de scouting basado en datos** que permite al Club América:

- 🔍 **Descubrir** jugadores infravalorados que se ajusten o rompan esquemas tácticos
- 📊 **Justificar** fichajes con evidencia cuantitativa: desempeño, habilidades y perfil táctico
- ⚖️ **Cuantificar y comparar** el impacto de jugadores (Jugador X vs. Jugador Y)
- 🔮 **Predecir** rendimiento en nuevos contextos: cambios de estilo de juego, entrenadores y alineaciones

### Preguntas clave que resuelve

> *"Si un jugador deja su equipo y firma en el Club América, ¿cómo cambiará su habilidad para progresar el balón?"*

> *"Para un jugador líder en duelos defensivos, ¿cómo cambiarían sus habilidades si es transferido al Club América según su estrategia de equipo?"*

---

## Características Principales

### Análisis de compatibilidad (Team Fit)
```python
Overall Fit Score = 0.35 × Technical Fit + 0.30 × Tactical Fit + 0.35 × Impact Score
```

- **Technical Fit**: Habilidades técnicas específicas por posición (0-100)
- **Tactical Fit**: Adaptabilidad al estilo de juego del América (0-100)
- **Impact Score**: Impacto proyectado en el equipo (0-100)

### Sistema de recomendación híbrido

- **Similitud técnica**: PCA + Cosine Similarity sobre 56 métricas normalizadas
- **Análisis contextual**: Experiencia, estabilidad, minutos jugados
- **Búsqueda por perfil**: Personalizable según necesidades tácticas

### On-Ball Value (OBV)™ Integration

- Evaluación de **todas las acciones**, no solo las que terminan en gol
- Análisis de jugadas a balón parado completas (incluye las que NO terminan en remate)
- Métricas de OBV por: pases, regates, tiros y acciones defensivas

---

## Metodología

### Pipeline de procesamiento
```
┌─────────────────┐
│  StatsBomb API  │
│   (4 temporadas)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extracción ETL  │
│  1,667 jugadores│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Normalización  │
│  (Z-score por   │
│   posición)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Perfilado Club  │
│     América     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Análisis de   │
│  Compatibilidad │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Recomendaciones │
│   Accionables   │
└─────────────────┘
```

### Datos utilizados

- **Fuente**: StatsBomb API (datos profesionales)
- **Competición**: Liga MX (ID: 73)
- **Temporadas**: 2021/2022, 2022/2023, 2023/2024, 2024/2025
- **Jugadores**: 740 únicos | 1,667 registros jugador-temporada
- **Variables**: 56 métricas por jugador (normalizadas y brutas)

---

## Instalación

### Requisitos Previos

- Python 3.9+
- pip
- Credenciales de StatsBomb API
- Docker 

### Pasos
```bash
# 1. Clonar el repositorio
git clone git@github.com:Jaimeum/Hackathon-America.git
cd Hackathon-America

# 2. Reabrir en contenedor (desde VS Code)
Ctrl + Shift + P : Reopen in Container

# 3. Sincronizar las librerias con uv
uv sync

# 4. Configurar credenciales
cp .env.example .env
# Editar .env con tus credenciales de StatsBomb:
# STATSBOMB_USERNAME=tu_usuario
# STATSBOMB_PASSWORD=tu_contraseña
```

### Dependencias principales
```
"dotenv>=0.9.9"
"ipykernel>=6.30.1"
"jupyter>=1.1.1"
"jupyterlab>=4.4.9"
"matplotlib>=3.10.6"
"openpyxl>=3.1.5"
"pandas>=2.3.2"
"pathlib>=1.0.1"
"pyarrow>=21.0.0"
"scikit-learn>=1.7.2"
"seaborn>=0.13.2"
"statsbombpy>=1.16.0"
```

---

## Uso

### Ejemplo Básico
```python
from src.utils.data_loader import DataLoader
from src.team_fit_analyzer import TeamFitAnalyzer
from src.recommender import PlayerRecommender

# 1. Cargar datos procesados
loader = DataLoader()
players_df = loader.get_players(min_minutes=500)

# 2. Cargar perfil del América
america_profile = loader.load_america_profile()

# 3. Analizar compatibilidad de un jugador
analyzer = TeamFitAnalyzer(america_profile)
analyzer.fit()

fit_score = analyzer.calculate_team_fit("Henry Martín")
# Output:
# ====================================
# ANÁLISIS DE COMPATIBILIDAD
# ====================================
# Henry Martín | Center Forward | América
# 
# Overall Fit:    82.5/100
# Technical Fit:  85.0/100
# Tactical Fit:   80.0/100
# Impact Score:   82.0/100
# ====================================

# 4. Obtener recomendaciones de fichajes
top_forwards = analyzer.recommend_best_fits(
    position='FWD',
    top_n=5,
    min_overall_fit=70.0
)
print(top_forwards)

# 5. Encontrar jugadores similares
recommender = PlayerRecommender()
recommender.fit()

similares = recommender.find_similar_players(
    player_name="Álvaro Fidalgo",
    same_position_only=True,
    top_n=10
)
```

### Notebooks interactivos

Explora los análisis completos en:

- 📓 `notebooks/procesamiento_datos.ipynb` - Pipeline ETL completo
- 📓 `notebooks/PCA.ipynb` - Analisis de componentes principales para estadisticas relevantes
- 📓 `notebooks/Analisis_America_fit_final.ipynb` - Analisis final de jugadores para el America y sus comparativas

---

## Estructura del Proyecto
```
Hackaton-America/
│
├── data/
│   ├── raw/                              # Datos crudos (no versionados)
│   └── processed/
│       ├── all_players_processed.csv     # Dataset principal de los jugadores con datos normalizados
│       ├── america_players.parquet       # Jugadores del América
│       └── america_profile.parquet       # Perfil táctico
│
├── notebooks/
│   ├── procesamiento_datos.ipynb         # ETL y normalización
│   ├── PCA.ipynb                         # Reduccion de dimensiones para optimizacion
|   ├── Prueba1.ipynb                     # Exploraciones iniciales
│   └── Analisis_America_fit_final.ipynb  # Uso de los metodos y modelos final
│
├── src/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── statsbomb_config.py           # Config API StatsBomb
│   │   ├── data_fetcher.py               # Extracción de datos
│   │   └── data_loader.py                # Carga y filtrado
|   |
│   ├── models/
│   │   ├── recommender.py                # Sistema de recomendación (primera versión)
│   │   ├── team_fit_analyzer.py          # Análisis de compatibilidad jugador-equipo
│   │   ├── team_profiler.py              # Perfilador de equipos
│   │   └── team_profiler_PCA.py          # Perfilador de equipos - versión optimizada con PCA
│   │
│   ├── __init__.py
│   └── config.py                         # Configuración general
│
├── .env.example                          # Template de variables de entorno
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Dataset

### Características del dataset procesado

| Característica | Valor |
|----------------|-------|
| **Registros totales** | 1,667 |
| **Jugadores únicos** | 740 |
| **Equipos** | 18 (Liga MX completa) |
| **Temporadas** | 4 (2021/22 - 2024/25) |
| **Variables** | 56 métricas |
| **Formato** | CSV, Parquet |

### Distribución por posición
```
Porteros (GK):        116 registros (7%)
Defensas (DEF):       305 registros (18%)
Mediocampistas (MED): 1,084 registros (65%)
Delanteros (FWD):     162 registros (10%)
```

### Métricas clave incluidas

**Ofensivas:**
- `player_season_goals_90` - Goles por 90 minutos
- `player_season_assists_90` - Asistencias por 90 minutos
- `player_season_np_xg_90` - Expected Goals (sin penales) por 90 min
- `player_season_shot_touch_ratio` - Ratio tiros/toques

**Técnicas:**
- `player_season_dribbles_90` - Regates por 90 minutos
- `player_season_passes_into_box_90` - Pases al área por 90 min
- `player_season_key_passes_90` - Pases clave por 90 min

**Defensivas:**
- `player_season_tackles_90` - Tackles por 90 minutos
- `player_season_interceptions_90` - Intercepciones por 90 min
- `player_season_pressures_90` - Presiones por 90 min

**On-Ball Value:**
- `player_season_obv_90` - OBV total por 90 minutos
- `player_season_obv_pass_90` - OBV generado en pases
- `player_season_obv_dribble_carry_90` - OBV en regates/conducción
- `player_season_obv_shot_90` - OBV en tiros
- `player_season_obv_defensive_action_90` - OBV en acciones defensivas

**Todas las métricas incluyen versión normalizada** (sufijo `_norm`) usando z-score por posición.

---

## Resultados

### Perfil del Club América (2024/2025)

#### Jugadores con más minutos

| Jugador | Posición | Minutos |
|---------|----------|---------|
| Luis Malagón | Portero | 4,237 |
| Israel Reyes | Defensa Central | 3,757 |
| Álvaro Fidalgo | Mediocampista Defensivo | 3,750 |
| Alejandro Zendejas | Extremo Derecho | 3,422 |

#### Estilo de Juego Identificado

- **Posesión**: Controlada
- **Presión**: Alta-Media intensidad
- **Ataque**: Predominantemente por bandas
- **Win Rate**: 53.7% (175 partidos en 4 temporadas)


### Ejemplo de Recomendación Generada
```
TOP 5 DELANTEROS RECOMENDADOS PARA CLUB AMÉRICA

1. [Jugador A] - [Equipo X]
   Overall Fit: 84.2/100
   Technical: 87 | Tactical: 82 | Impact: 85
   Goles/90: 0.72 | OBV: 0.64
   
2. [Jugador B] - [Equipo Y]
   Overall Fit: 79.8/100
   Technical: 82 | Tactical: 78 | Impact: 81
   Goles/90: 0.65 | OBV: 0.58
   
[...]
```

## Contacto

**Autores**: Andrés Guillermo Schafler Tenorio y Jaime Fernando Uria Medina

- 📧 Email: aschafle@itam.mx 
- 💼 LinkedIn: Andrés Schafler (www.linkedin.com/in/andres-schafler)

**Link del Proyecto**: https://github.com/Jaimeum/Hackathon-America.git

---

## 🙏 Agradecimientos

- [StatsBomb](https://statsbomb.com/) por proporcionar datos profesionales de fútbol
- [ITAM Hackathon](https://www.itam.mx/) por la oportunidad y el desafío
- Club América por ser la inspiración del proyecto

---

## 📚 Referencias

- [StatsBomb Open Data](https://github.com/statsbomb/open-data)
- [Friends of Tracking](https://www.youtube.com/channel/UCUBFJYcag8j2rm_9HkrrA7w) - Tutoriales de análisis deportivo
- [Soccermatics](https://www.soccermatics.com/) - David Sumpter
- [Paper: "On-Ball Value"](https://statsbomb.com/articles/soccer/on-ball-value-obv-evolved/) - StatsBomb


---

<div align="center">
  <sub>Desarrollado con ⚽ y 📊 por Andrés y Jaime</sub>
</div>
**Poner al toque el UV:**
   ```bash
   uv sync
   ```
