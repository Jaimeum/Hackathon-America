# 🚀 Guía de Despliegue en Streamlit Cloud

## Configuración para Streamlit Cloud

### 1. Archivos Necesarios ✅
- ✅ `requirements.txt` - Dependencias de Python
- ✅ `.streamlit/config.toml` - Configuración de Streamlit
- ✅ `streamlit_app.py` - Punto de entrada simplificado
- ✅ `app.py` - Aplicación principal

### 2. Configuración de Secrets en Streamlit Cloud

1. Ve a tu app en [share.streamlit.io](https://share.streamlit.io)
2. Haz clic en **Settings** (⚙️)
3. Ve a la sección **Secrets**
4. Agrega las siguientes variables:

```
STATSBOMB_USERNAME=tu_usuario_statsbomb
STATSBOMB_PASSWORD=tu_contraseña_statsbomb
```

### 3. Configuración del Repositorio

- **Branch**: `main`
- **Main file**: `streamlit_app.py` (en lugar de `main.py`)
- **Python version**: 3.9+ (recomendado 3.11)

### 4. Datos Requeridos

Para que la aplicación funcione completamente, necesitas:

1. **Datos procesados** en la carpeta `data/processed/`:
   - `all_players_processed.csv`
   - `all_players_processed.parquet`

2. **Resultados de análisis** en la carpeta `data/results/`:
   - `america_profile.json`
   - `pca_feature_importance.json`

### 5. Solución de Problemas

#### App en Blanco
- ✅ Verifica que `streamlit_app.py` sea el archivo principal
- ✅ Revisa los logs en Streamlit Cloud
- ✅ Asegúrate de que las credenciales estén configuradas

#### Error de Dependencias
- ✅ Verifica que `requirements.txt` tenga todas las dependencias
- ✅ Asegúrate de que las versiones sean compatibles

#### Error de Datos
- ✅ La app funcionará con datos limitados si no están disponibles
- ✅ Se mostrarán mensajes informativos en lugar de errores

### 6. Estructura de Archivos

```
Hackathon-America/
├── streamlit_app.py          # ← Punto de entrada para Streamlit Cloud
├── app.py                    # Aplicación principal
├── requirements.txt          # Dependencias
├── .streamlit/
│   └── config.toml          # Configuración
├── data/
│   ├── processed/           # Datos procesados
│   └── results/            # Resultados de análisis
└── src/                    # Código fuente
```

### 7. Comandos Útiles

```bash
# Instalar dependencias localmente
pip install -r requirements.txt

# Ejecutar localmente
streamlit run streamlit_app.py

# Ejecutar con datos completos
python main.py --quick
```

### 8. Notas Importantes

- La aplicación está diseñada para funcionar incluso sin datos completos
- Los errores se manejan graciosamente con mensajes informativos
- Las credenciales de StatsBomb son necesarias para funcionalidad completa
- El modo "datos limitados" permite ver la interfaz sin análisis completos
