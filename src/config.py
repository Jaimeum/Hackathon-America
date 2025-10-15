"""Configuración de rutas y features para el sistema de recomendación"""
from pathlib import Path

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_PROCESSED = DATA_DIR / "processed"

# Archivo principal de datos
PLAYERS_DATA = DATA_PROCESSED / "all_players_processed.csv"

# Features normalizadas
NORMALIZED_FEATURES = [
    'player_season_goals_90_norm',
    'player_season_assists_90_norm',
    'player_season_np_xg_90_norm',
    'player_season_np_shots_90_norm',
    'player_season_shot_touch_ratio_norm',
    'player_season_dribbles_90_norm',
    'player_season_dribble_ratio_norm',
    'player_season_passes_into_box_90_norm',
    'player_season_deep_completions_90_norm',
    'player_season_key_passes_90_norm',
    'player_season_obv_pass_90_norm',
    'player_season_pressures_90_norm',
    'player_season_pressure_regains_90_norm',
    'player_season_tackles_90_norm',
    'player_season_interceptions_90_norm',
    'player_season_defensive_actions_90_norm',
    'player_season_aerial_ratio_norm',
    'player_season_obv_90_norm',
    'player_season_obv_dribble_carry_90_norm',
    'player_season_obv_defensive_action_90_norm',
    'player_season_obv_shot_90_norm'
]

# Features por posición
POSITION_FEATURES = {
    'Forward': [
        'player_season_goals_90_norm',
        'player_season_np_xg_90_norm',
        'player_season_assists_90_norm',
        'player_season_shot_touch_ratio_norm',
        'player_season_obv_shot_90_norm'
    ],
    'Midfielder': [
        'player_season_assists_90_norm',
        'player_season_key_passes_90_norm',
        'player_season_obv_pass_90_norm',
        'player_season_pressures_90_norm',
        'player_season_obv_90_norm'
    ],
    'Defender': [
        'player_season_tackles_90_norm',
        'player_season_interceptions_90_norm',
        'player_season_defensive_actions_90_norm',
        'player_season_obv_defensive_action_90_norm',
        'player_season_aerial_ratio_norm'
    ],
    'Goalkeeper': [
        'player_season_save_ratio_norm',
        'player_season_obv_90_norm'
    ],
    'FWD': [  # Forward
        'player_season_goals_90_norm',
        'player_season_np_xg_90_norm',
        'player_season_assists_90_norm',
        'player_season_shot_touch_ratio_norm',
        'player_season_obv_shot_90_norm'
    ],
    'MED': [  # Midfielder
        'player_season_assists_90_norm',
        'player_season_key_passes_90_norm',
        'player_season_obv_pass_90_norm',
        'player_season_pressures_90_norm',
        'player_season_obv_90_norm'
    ],
    'DEF': [  # Defender
        'player_season_tackles_90_norm',
        'player_season_interceptions_90_norm',
        'player_season_defensive_actions_90_norm',
        'player_season_obv_defensive_action_90_norm',
        'player_season_aerial_ratio_norm'
    ],
    'GK': [  # Goalkeeper
        'player_season_save_ratio_norm',
        'player_season_obv_90_norm'
    ]
}
