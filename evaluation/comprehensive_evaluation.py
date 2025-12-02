#!/usr/bin/env python3
"""
Comprehensive evaluation of nutrition analysis system
"""

import sys
sys.path.append('..')
from src.clean_food_matcher import CleanFoodMatcher
import pandas as pd

class NutritionSystemEvaluator:
    """Evaluate the complete nutrition analysis system"""
    
    def __init__(self):
        self.matcher = CleanFoodMatcher('../data/nutrition_db_clean.csv')
        self.test_cases = self._create_comprehensive_test_cases()
    
    def _create_comprehensive_test_cases(self):
        """Create comprehensive test cases with expected results"""
        return [
            {
                "name": "Simple breakfast",
                "input": "2 slices whole wheat toast with butter and scrambled eggs",
                "expected_foods": ["toast", "butter", "eggs"],
                "expected_count": 3,
                "difficulty": "easy"
            },
            {
                "name": "Complex lunch",
                "input": "Grilled chicken breast with brown rice, steamed broccoli, and olive oil dressing",
                "expected_foods": ["chicken", "rice", "broccoli"],
                "expected_count": 3,
                "difficulty": "medium"
            },
            {
                "name": "Snack with quantities",
                "input": "1 cup greek yogurt with 1/4 cup blueberries and 2 tbsp almonds",
                "expected_foods": ["yogurt", "blueberries", "almonds"],
                "expected_count": 3,
                "difficulty": "medium"
            },
            {
                "name": "Dinner with cooking methods",
                "input": "Baked salmon with roasted sweet potato and spinach salad",
                "expected_foods": ["salmon", "sweet potato", "salad"],
                "expected_count": 3,
                "difficulty": "medium"
            },
            {
                "name": "Full day meal log",
                "input": "Breakfast: oatmeal with banana. Lunch: chicken sandwich with lettuce. Dinner: pasta with cheese. Snack: apple and peanut butter",
                "expected_foods": ["oatmeal", "banana", "chicken", "sandwich", "lettuce", "pasta", "cheese", "apple", "peanut butter"],
                "expected_count": 9,
                "difficulty": "hard"
            },
            {
                "name": "Ambiguous foods",
                "input": "rice bowl with mixed vegetables and protein",
                "expected_foods": ["rice"],
                "expected_count": 1,
                "difficulty": "hard"
            }
        ]
    
    def evaluate_food_detection(self):
        """Evaluate food detection accuracy"""
        results = []
        
        for test_case in self.test_cases:
            print(f"\n--- Testing: {test_case['name']} ---")
            print(f"Input: {test_case['input']}")
            
            # Extract foods
            foods = self.matcher.extract_foods_with_quantities(test_case['input'])
            nutrition_data, unknown = self.matcher.get_nutrition_data(foods)
            
            detected_foods = [item['food'].lower() for item in nutrition_data]
            expected_foods = test_case['expected_foods']
            
            print(f"Expected: {expected_foods}")
            print(f"Detected: {detected_foods}")
            
            # Calculate metrics
            true_positives = 0
            for expected in expected_foods:
                if any(expected in detected for detected in detected_foods):
                    true_positives += 1
            
            precision = true_positives / len(detected_foods) if detected_foods else 0
            recall = true_positives / len(expected_foods) if expected_foods else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            result = {
                'test_case': test_case['name'],
                'difficulty': test_case['difficulty'],
                'expected_count': len(expected_foods),
                'detected_count': len(detected_foods),
                'true_positives': true_positives,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'unknown_foods': unknown
            }
            
            results.append(result)
            
            print(f"Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
            if unknown:
                print(f"Unknown foods: {unknown}")
        
        return results
    
    def evaluate_calorie_estimation(self):
        """Evaluate calorie estimation reasonableness"""
        calorie_tests = [
            {"input": "1 slice bread", "expected_range": (60, 120)},
            {"input": "1 cup rice", "expected_range": (200, 300)},
            {"input": "1 chicken breast", "expected_range": (150, 250)},
            {"input": "1 tbsp butter", "expected_range": (80, 120)},
            {"input": "1 apple", "expected_range": (60, 100)}
        ]
        
        print(f"\n=== CALORIE ESTIMATION EVALUATION ===")
        accurate_estimates = 0
        
        for test in calorie_tests:
            foods = self.matcher.extract_foods_with_quantities(test['input'])
            nutrition_data, _ = self.matcher.get_nutrition_data(foods)
            
            if nutrition_data:
                calories = nutrition_data[0]['calories']
                min_cal, max_cal = test['expected_range']
                is_accurate = min_cal <= calories <= max_cal
                
                print(f"{test['input']}: {calories} cal (expected {min_cal}-{max_cal}) {'✅' if is_accurate else '❌'}")
                
                if is_accurate:
                    accurate_estimates += 1
            else:
                print(f"{test['input']}: No food detected ❌")
        
        accuracy = accurate_estimates / len(calorie_tests)
        print(f"\nCalorie Estimation Accuracy: {accuracy:.1%}")
        return accuracy
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("=" * 60)
        print("COMPREHENSIVE NUTRITION SYSTEM EVALUATION")
        print("=" * 60)
        
        # Food detection evaluation
        detection_results = self.evaluate_food_detection()
        
        # Calculate overall metrics
        total_precision = sum(r['precision'] for r in detection_results) / len(detection_results)
        total_recall = sum(r['recall'] for r in detection_results) / len(detection_results)
        total_f1 = sum(r['f1_score'] for r in detection_results) / len(detection_results)
        
        # Calorie estimation evaluation
        calorie_accuracy = self.evaluate_calorie_estimation()
        
        # Performance by difficulty
        print(f"\n=== PERFORMANCE BY DIFFICULTY ===")
        for difficulty in ['easy', 'medium', 'hard']:
            diff_results = [r for r in detection_results if r['difficulty'] == difficulty]
            if diff_results:
                avg_f1 = sum(r['f1_score'] for r in diff_results) / len(diff_results)
                print(f"{difficulty.capitalize()}: {avg_f1:.3f} F1 score")
        
        # Overall summary
        print(f"\n=== OVERALL PERFORMANCE SUMMARY ===")
        print(f"Food Detection F1 Score: {total_f1:.3f}")
        print(f"Food Detection Precision: {total_precision:.3f}")
        print(f"Food Detection Recall: {total_recall:.3f}")
        print(f"Calorie Estimation Accuracy: {calorie_accuracy:.1%}")
        
        # Performance interpretation
        overall_score = (total_f1 + calorie_accuracy) / 2
        print(f"Overall System Score: {overall_score:.3f}")
        
        if overall_score >= 0.8:
            print("🎉 EXCELLENT: System is working very well!")
        elif overall_score >= 0.6:
            print("✅ GOOD: System is working well with room for improvement")
        elif overall_score >= 0.4:
            print("⚠️ FAIR: System needs significant improvement")
        else:
            print("❌ POOR: System needs major fixes")
        
        return {
            'food_detection_f1': total_f1,
            'calorie_accuracy': calorie_accuracy,
            'overall_score': overall_score,
            'detailed_results': detection_results
        }

def run_evaluation():
    """Run the complete evaluation"""
    evaluator = NutritionSystemEvaluator()
    results = evaluator.generate_performance_report()
    return results

if __name__ == "__main__":
    run_evaluation()