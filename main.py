"""
Main runner script for Club América Scouting System
Sistema de Scouting Inteligente - Club América
"""
import sys
import argparse
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.utils.data_processor import run_full_data_processing
from src.models.pca_analyzer import run_pca_analysis
from src.models.america_analysis import run_complete_america_analysis


def setup_environment():
    """Setup environment and check dependencies"""
    print("🔧 Configurando entorno...")
    
    # Check if .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  Archivo .env no encontrado")
        print("   Copia .env.example a .env y configura tus credenciales de StatsBomb")
        return False
    
    # Check if data directory exists
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    processed_dir = data_dir / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    results_dir = data_dir / "results"
    results_dir.mkdir(exist_ok=True)
    
    print("✅ Entorno configurado correctamente")
    return True


def run_data_pipeline():
    """Run the complete data processing pipeline"""
    print("\n" + "="*60)
    print("📊 EJECUTANDO PIPELINE DE PROCESAMIENTO DE DATOS")
    print("="*60)
    
    try:
        processor, files = run_full_data_processing()
        if processor and files:
            print("✅ Pipeline de datos completado exitosamente")
            return True
        else:
            print("❌ Error en el pipeline de datos")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando pipeline de datos: {e}")
        return False


def run_pca_pipeline():
    """Run PCA analysis pipeline"""
    print("\n" + "="*60)
    print("🔍 EJECUTANDO ANÁLISIS PCA")
    print("="*60)
    
    try:
        analyzer, files = run_pca_analysis()
        if analyzer and files:
            print("✅ Análisis PCA completado exitosamente")
            return True
        else:
            print("❌ Error en el análisis PCA")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando análisis PCA: {e}")
        return False


def run_america_analysis():
    """Run complete America analysis"""
    print("\n" + "="*60)
    print("🏆 EJECUTANDO ANÁLISIS COMPLETO DEL AMÉRICA")
    print("="*60)
    
    try:
        analysis, files = run_complete_america_analysis()
        if analysis and files:
            print("✅ Análisis del América completado exitosamente")
            return True
        else:
            print("❌ Error en el análisis del América")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando análisis del América: {e}")
        return False


def launch_streamlit():
    """Launch Streamlit application"""
    print("\n" + "="*60)
    print("🚀 LANZANDO APLICACIÓN STREAMLIT")
    print("="*60)
    
    import subprocess
    import os
    
    app_path = project_root / "app.py"
    
    if not app_path.exists():
        print("❌ Archivo app.py no encontrado")
        return False
    
    try:
        # Launch Streamlit
        cmd = ["streamlit", "run", str(app_path), "--server.port", "8501", "--server.address", "0.0.0.0"]
        print(f"Ejecutando: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error lanzando Streamlit: {e}")
        return False
    except FileNotFoundError:
        print("❌ Streamlit no está instalado. Instálalo con: pip install streamlit")
        return False


def check_data_availability():
    """Check if processed data is available"""
    processed_dir = project_root / "data" / "processed"
    main_data_file = processed_dir / "all_players_processed.csv"
    
    if main_data_file.exists():
        print("✅ Datos procesados encontrados")
        return True
    else:
        print("⚠️  Datos procesados no encontrados")
        return False


def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(
        description="Club América Scouting System - Sistema de Scouting Inteligente",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py --setup                    # Solo configurar entorno
  python main.py --data                     # Solo procesar datos
  python main.py --pca                      # Solo análisis PCA
  python main.py --america                  # Solo análisis del América
  python main.py --streamlit                # Solo lanzar Streamlit
  python main.py --full                     # Pipeline completo
  python main.py --quick                    # Solo lanzar Streamlit (datos existentes)
        """
    )
    
    parser.add_argument('--setup', action='store_true', 
                       help='Configurar entorno y verificar dependencias')
    parser.add_argument('--data', action='store_true', 
                       help='Ejecutar pipeline de procesamiento de datos')
    parser.add_argument('--pca', action='store_true', 
                       help='Ejecutar análisis PCA')
    parser.add_argument('--america', action='store_true', 
                       help='Ejecutar análisis completo del América')
    parser.add_argument('--streamlit', action='store_true', 
                       help='Lanzar aplicación Streamlit')
    parser.add_argument('--full', action='store_true', 
                       help='Ejecutar pipeline completo (datos + PCA + América + Streamlit)')
    parser.add_argument('--quick', action='store_true', 
                       help='Lanzar Streamlit rápidamente (asume datos existentes)')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("⚽ Club América Scouting System")
    print("Sistema de Scouting Inteligente")
    print("="*60)
    
    # Setup environment
    if args.setup or args.full:
        if not setup_environment():
            print("❌ Error en configuración del entorno")
            return
    
    # Quick launch (just Streamlit)
    if args.quick:
        if check_data_availability():
            launch_streamlit()
        else:
            print("❌ No hay datos disponibles. Ejecuta --full primero")
        return
    
    # Data processing
    if args.data or args.full:
        if not run_data_pipeline():
            print("❌ Pipeline de datos falló")
            return
    
    # PCA analysis
    if args.pca or args.full:
        if not run_pca_pipeline():
            print("❌ Análisis PCA falló")
            return
    
    # America analysis
    if args.america or args.full:
        if not run_america_analysis():
            print("❌ Análisis del América falló")
            return
    
    # Launch Streamlit
    if args.streamlit or args.full:
        launch_streamlit()


if __name__ == "__main__":
    main()
