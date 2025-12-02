#!/usr/bin/env python3
"""
Benchmark system to compare RAG+LLM vs baseline approaches
"""

import pandas as pd
from typing import List, Dict, Tuple
import time

class NutritionBenchmark:
    """Benchmark nutrition analysis approaches"""
    
    def __init__(self):
        self.test_cases = [
            {
                "input": "2 slices whole wheat bread with butter and scrambled eggs",
                "expected_foods": ["bread", "butter", "eggs"],
                "expected_calories_range": (400, 600)
            },
            {
                "input": "grilled chicken breast with brown rice and broccoli",
                "expected_foods": ["chicken", "rice", "broccoli"],
                "expected_calories_range": (350, 500)
            },
            {
                "input": "greek yogurt with blueberries and almonds",
                "expected_foods": ["yogurt", "blueberries", "almonds"],
                "expected_calories_range": (200, 350)
            }
        ]
    
    def evaluate_food_detection(self, matcher) -> Dict:
        """Evaluate food detection accuracy"""
        total_foods = 0
        detected_foods = 0
        correct_foods = 0
        
        for test_case in self.test_cases:
            foods = matcher.extract_foods_with_quantities(test_case["input"])
            nutrition_data, _ = matcher.get_nutrition_data(foods)
            
            detected_names = [item["food"].lower() for item in nutrition_data]
            expected_names = test_case["expected_foods"]
            
            total_foods += len(expected_names)
            detected_foods += len(detected_names)
            
            for expected in expected_names:
                if any(expected in detected for detected in detected_names):
                    correct_foods += 1
        
        precision = correct_foods / detected_foods if detected_foods > 0 else 0
        recall = correct_foods / total_foods if total_foods > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "correct_matches": correct_foods
        }
    
    def run_evaluation(self, matcher, approach_name: str) -> Dict:
        """Run complete evaluation"""
        food_metrics = self.evaluate_food_detection(matcher)
        
        return {
            "approach": approach_name,
            "f1_score": food_metrics["f1_score"],
            "precision": food_metrics["precision"],
            "recall": food_metrics["recall"]
        }

def run_benchmark():
    """Run benchmark comparison"""
    benchmark = NutritionBenchmark()
    
    import sys
    sys.path.append('..')
    from src.clean_food_matcher import CleanFoodMatcher
    matcher = CleanFoodMatcher('../data/nutrition_db_clean.csv')
    results = benchmark.run_evaluation(matcher, "RAG + Clean Matcher")
    
    print("=== BENCHMARK RESULTS ===")
    print(f"F1 Score: {results['f1_score']:.3f}")
    print(f"Precision: {results['precision']:.3f}")
    print(f"Recall: {results['recall']:.3f}")
    
    return results

if __name__ == "__main__":
    run_benchmark()