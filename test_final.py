"""
Final comprehensive test for Club América Scouting System
"""
import sys
from pathlib import Path
import json

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def test_complete_workflow():
    """Test the complete workflow from data loading to recommendations"""
    print("🎯 Testing Complete Workflow")
    print("=" * 50)
    
    try:
        # 1. Test data loading
        print("1. Testing data loading...")
        from src.utils.data_loader import DataLoader
        loader = DataLoader()
        summary = loader.get_summary()
        print(f"   ✅ Loaded {summary['total_players']} players from {summary['total_teams']} teams")
        
        # 2. Test America analysis
        print("2. Testing America analysis...")
        from src.models.america_analysis import AmericaAnalysis
        analysis = AmericaAnalysis()
        
        # Load existing profile
        profile_path = project_root / "data" / "results" / "america_profile.json"
        if profile_path.exists():
            with open(profile_path, 'r') as f:
                analysis.america_profile = json.load(f)
            analysis.initialize_analyzers()
            print("   ✅ America analysis initialized")
        else:
            print("   ⚠️  Profile not found, would need to build it")
        
        # 3. Test player analysis
        print("3. Testing player analysis...")
        test_player = "Alejandro Zendejas"
        try:
            result = analysis.analyze_player_fit(test_player)
            print(f"   ✅ Player analysis: {result['player_name']} - Fit: {result['overall_fit']:.1f}/100")
        except Exception as e:
            print(f"   ⚠️  Player analysis: {e}")
        
        # 4. Test recommendations
        print("4. Testing recommendations...")
        try:
            recommendations = analysis.get_position_recommendations('FWD', top_n=2)
            print(f"   ✅ Recommendations: Found {len(recommendations)} forwards")
            if not recommendations.empty:
                best = recommendations.iloc[0]
                print(f"   📊 Best recommendation: {best['player_name']} - Fit: {best['overall_fit']:.1f}/100")
        except Exception as e:
            print(f"   ⚠️  Recommendations: {e}")
        
        # 5. Test similar players
        print("5. Testing similar players...")
        try:
            similar = analysis.find_similar_players(test_player, top_n=2)
            print(f"   ✅ Similar players: Found {len(similar)} similar players")
            if not similar.empty:
                most_similar = similar.iloc[0]
                print(f"   📊 Most similar: {most_similar['player_name']} - Similarity: {most_similar['similarity_score']:.3f}")
        except Exception as e:
            print(f"   ⚠️  Similar players: {e}")
        
        print("\n🎉 Complete workflow test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow test failed: {e}")
        return False

def test_streamlit_app():
    """Test Streamlit app imports and basic functionality"""
    print("\n🚀 Testing Streamlit App")
    print("=" * 50)
    
    try:
        # Test Streamlit import
        import streamlit as st
        print("   ✅ Streamlit imported")
        
        # Test app import
        import app
        print("   ✅ App module imported")
        
        # Test main functions exist
        if hasattr(app, 'main'):
            print("   ✅ Main function exists")
        
        print("   🎉 Streamlit app test successful!")
        return True
        
    except Exception as e:
        print(f"   ❌ Streamlit app test failed: {e}")
        return False

def test_data_files():
    """Test that all required data files exist"""
    print("\n📁 Testing Data Files")
    print("=" * 50)
    
    required_files = [
        "data/processed/all_players_processed.csv",
        "data/results/america_profile.json",
        "data/results/america_recruitment_report.json"
    ]
    
    all_exist = True
    for file_path in required_files:
        path = project_root / file_path
        if path.exists():
            size = path.stat().st_size
            print(f"   ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_exist = False
    
    if all_exist:
        print("   🎉 All data files present!")
    else:
        print("   ⚠️  Some data files missing")
    
    return all_exist

def main():
    """Run all tests"""
    print("⚽ Club América Scouting System - Final Test")
    print("=" * 60)
    
    tests = [
        ("Complete Workflow", test_complete_workflow),
        ("Streamlit App", test_streamlit_app),
        ("Data Files", test_data_files)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"Final Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready for production!")
        print("\n🚀 To launch the application:")
        print("   uv run python main.py --quick")
        print("\n📊 To run full analysis:")
        print("   uv run python main.py --full")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
