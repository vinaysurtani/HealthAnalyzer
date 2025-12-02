#!/usr/bin/env python3
"""
Test for overfitting in the nutrition analysis system
"""

import sys
sys.path.append('..')
from src.clean_food_matcher import CleanFoodMatcher
from src.food_classifier import FoodClassificationModel

def test_overfitting():
    """Test system with completely unseen foods and edge cases"""
    
    matcher = CleanFoodMatcher('../data/nutrition_db_clean.csv')
    
    # Test 1: Foods NOT in database (should fail gracefully)
    unseen_foods = [
        "quinoa with kale and tahini",  # Exotic combinations
        "dragon fruit smoothie",       # Rare fruits
        "tempeh stir fry",            # Uncommon proteins
        "nutritional yeast flakes",    # Specialty items
        "jackfruit tacos",            # Very uncommon
    ]
    
    print("=== OVERFITTING TEST: UNSEEN FOODS ===")
    total_unseen = len(unseen_foods)
    detected_unseen = 0
    
    for food in unseen_foods:
        foods = matcher.extract_foods_with_quantities(food)
        nutrition_data, unknown = matcher.get_nutrition_data(foods)
        
        if nutrition_data:
            detected_unseen += 1
            print(f"❌ OVERFITTING RISK: '{food}' → {[item['food'] for item in nutrition_data]}")
        else:
            print(f"✅ GOOD: '{food}' → Not detected (expected)")
    
    overfitting_rate = detected_unseen / total_unseen
    print(f"\nOverfitting Risk Score: {overfitting_rate:.1%}")
    
    # Test 2: Misspellings and variations
    print(f"\n=== ROBUSTNESS TEST: MISSPELLINGS ===")
    misspelling_tests = [
        ("chiken breast", "chicken"),      # Common misspelling
        ("tomatoe", "tomato"),            # Extra letter
        ("brocoli", "broccoli"),          # Missing letter
        ("yoghurt", "yogurt"),            # Alternative spelling
        ("bred", "bread"),                # Phonetic error
    ]
    
    robust_matches = 0
    for misspelled, expected in misspelling_tests:
        result = matcher.find_food(misspelled)
        if result and expected.lower() in result.lower():
            robust_matches += 1
            print(f"✅ ROBUST: '{misspelled}' → '{result}'")
        else:
            print(f"❌ BRITTLE: '{misspelled}' → '{result}' (expected {expected})")
    
    robustness_score = robust_matches / len(misspelling_tests)
    print(f"\nRobustness Score: {robustness_score:.1%}")
    
    # Test 3: Cross-validation with ML model
    print(f"\n=== ML MODEL CROSS-VALIDATION ===")
    try:
        # Fix path for ML model when running from evaluation directory
        import os
        original_cwd = os.getcwd()
        os.chdir('..')  # Go to parent directory
        
        model = FoodClassificationModel()
        training_results = model.train()
        
        os.chdir(original_cwd)  # Return to original directory
        
        print(f"Food Classification Accuracy: {training_results['food_classification_accuracy']:.3f}")
        print(f"Training Samples: {training_results['training_samples']}")
        
        # High accuracy with small dataset is suspicious
        if training_results['food_classification_accuracy'] > 0.95 and training_results['training_samples'] < 500:
            print("⚠️ WARNING: High accuracy + small dataset = potential overfitting")
        else:
            print("✅ GOOD: Reasonable accuracy for dataset size")
            
    except Exception as e:
        print(f"ML test failed: {e}")
    
    # Overall assessment
    print(f"\n=== OVERFITTING ASSESSMENT ===")
    
    if overfitting_rate > 0.3:
        print("🚨 HIGH OVERFITTING RISK: System matches too many unseen foods")
    elif robustness_score < 0.4:
        print("⚠️ MODERATE RISK: System is brittle to variations")
    else:
        print("✅ LOW OVERFITTING RISK: System shows good generalization")
    
    return {
        'overfitting_rate': overfitting_rate,
        'robustness_score': robustness_score,
        'overall_risk': 'HIGH' if overfitting_rate > 0.3 else 'MODERATE' if robustness_score < 0.4 else 'LOW'
    }

if __name__ == "__main__":
    test_overfitting()