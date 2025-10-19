"""
Simple integration test for the Club América Scouting System
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        from src.utils.data_loader import DataLoader
        print("✅ DataLoader imported successfully")
    except Exception as e:
        print(f"❌ DataLoader import failed: {e}")
        return False
    
    try:
        from src.models.team_fit_analyzer import TeamFitAnalyzer
        print("✅ TeamFitAnalyzer imported successfully")
    except Exception as e:
        print(f"❌ TeamFitAnalyzer import failed: {e}")
        return False
    
    try:
        from src.models.recommender import PlayerRecommender
        print("✅ PlayerRecommender imported successfully")
    except Exception as e:
        print(f"❌ PlayerRecommender import failed: {e}")
        return False
    
    try:
        from src.models.america_analysis import AmericaAnalysis
        print("✅ AmericaAnalysis imported successfully")
    except Exception as e:
        print(f"❌ AmericaAnalysis import failed: {e}")
        return False
    
    try:
        from src.utils.data_processor import DataProcessor
        print("✅ DataProcessor imported successfully")
    except Exception as e:
        print(f"❌ DataProcessor import failed: {e}")
        return False
    
    try:
        from src.models.pca_analyzer import PCAAnalyzer
        print("✅ PCAAnalyzer imported successfully")
    except Exception as e:
        print(f"❌ PCAAnalyzer import failed: {e}")
        return False
    
    return True

def test_data_availability():
    """Test if processed data is available"""
    print("\n🔍 Testing data availability...")
    
    data_file = project_root / "data" / "processed" / "all_players_processed.csv"
    
    if data_file.exists():
        print("✅ Processed data file found")
        return True
    else:
        print("⚠️  Processed data file not found")
        print("   Run 'python main.py --data' to generate data")
        return False

def test_config():
    """Test configuration"""
    print("\n🔍 Testing configuration...")
    
    try:
        from src.config import NORMALIZED_FEATURES, POSITION_FEATURES
        print(f"✅ Configuration loaded: {len(NORMALIZED_FEATURES)} normalized features")
        print(f"✅ Position features: {len(POSITION_FEATURES)} position categories")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("⚽ Club América Scouting System - Integration Test")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test imports
    if test_imports():
        tests_passed += 1
    
    # Test data availability
    if test_data_availability():
        tests_passed += 1
    
    # Test configuration
    if test_config():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"Integration Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python main.py --data' to process data")
        print("2. Run 'python main.py --america' to analyze Club América")
        print("3. Run 'python main.py --streamlit' to launch the UI")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
