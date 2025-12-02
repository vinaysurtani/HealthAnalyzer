#!/usr/bin/env python3
"""
Test script to verify Daily Nutrition Analyzer installation
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    required_modules = [
        ('streamlit', 'Streamlit web framework'),
        ('pandas', 'Data manipulation library'),
        ('numpy', 'Numerical computing library'),
        ('sklearn', 'Machine learning library'),
        ('sentence_transformers', 'Sentence embeddings'),
        ('faiss', 'Vector similarity search'),
    ]
    
    optional_modules = [
        ('openai', 'OpenAI API client'),
        ('matplotlib', 'Plotting library'),
        ('seaborn', 'Statistical visualization'),
    ]
    
    success_count = 0
    
    # Test required modules
    for module, description in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module} - {description} (Error: {e})")
    
    # Test optional modules
    print("\n🔧 Testing optional modules...")
    for module, description in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError:
            print(f"⚠️  {module} - {description} (Optional, not installed)")
    
    return success_count == len(required_modules)

def test_file_structure():
    """Test if required files and directories exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'data/nutrition_db_clean.csv',
        'data/nhanes_demographics.csv',
        'data/nutrition_guidelines.txt',
        'src/clean_food_matcher.py',
        'src/llm_summarizer.py',
    ]
    
    required_dirs = [
        'src',
        'data',
        'evaluation',
        'models',
    ]
    
    success = True
    
    # Check files
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (Missing)")
            success = False
    
    # Check directories
    for dir_path in required_dirs:
        if Path(dir_path).is_dir():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ (Missing)")
            success = False
    
    return success

def test_food_matcher():
    """Test the core food matching functionality"""
    print("\n🍎 Testing food matcher...")
    
    try:
        from src.clean_food_matcher import CleanFoodMatcher
        
        # Initialize matcher
        matcher = CleanFoodMatcher('data/nutrition_db_clean.csv')
        print(f"✅ Food matcher initialized with {len(matcher.db)} foods")
        
        # Test food extraction
        test_input = "1 apple with peanut butter"
        foods = matcher.extract_foods_with_quantities(test_input)
        
        if foods and len(foods) >= 2:
            print(f"✅ Food extraction successful: {[f['food'] for f in foods]}")
            
            # Test nutrition data
            nutrition_data, unknown_foods = matcher.get_nutrition_data(foods)
            if nutrition_data:
                print(f"✅ Nutrition data retrieved for {len(nutrition_data)} foods")
                return True
            else:
                print("❌ Failed to retrieve nutrition data")
                return False
        else:
            print(f"❌ Food extraction failed: {foods}")
            return False
            
    except Exception as e:
        print(f"❌ Food matcher test failed: {e}")
        return False

def test_ai_components():
    """Test AI components (optional)"""
    print("\n🤖 Testing AI components...")
    
    try:
        from src.llm_summarizer import NutritionSummarizer
        
        summarizer = NutritionSummarizer()
        print("✅ LLM summarizer initialized")
        
        # Test with sample data
        sample_data = [{'food': 'Apple', 'calories': 95, 'protein': 0.5, 'carbs': 25, 'fat': 0.3}]
        sample_totals = {'calories': 95, 'protein': 0.5, 'carbs': 25, 'fat': 0.3}
        
        summary, method, sources = summarizer.generate_summary(sample_data, sample_totals, 30, 'Male')
        
        if summary and len(summary) > 50:
            print(f"✅ AI summary generated using {method}")
            return True
        else:
            print("⚠️  AI summary generation limited (likely using fallback)")
            return True  # Still considered success
            
    except Exception as e:
        print(f"⚠️  AI components test failed: {e} (This is optional)")
        return True  # AI is optional

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Daily Nutrition Analyzer - Installation Test\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("File Structure", test_file_structure),
        ("Food Matcher", test_food_matcher),
        ("AI Components", test_ai_components),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your installation is ready.")
        print("\n📋 Next steps:")
        print("1. Run: streamlit run app.py")
        print("2. Open: http://localhost:8501")
        print("3. Try entering: '2 slices toast with butter and eggs'")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the installation.")
        print("💡 Try running: python setup.py")

if __name__ == "__main__":
    run_comprehensive_test()