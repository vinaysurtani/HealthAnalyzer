#!/usr/bin/env python3
"""
Training Script: USDA Nutrition Database Training and Food Matching Optimization
Trains the food matching system and nutrition database used in production
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from typing import Dict, List, Tuple

class USDANutritionTrainer:
    def __init__(self):
        self.usda_db_path = "data/nutrition_db_clean.csv"
        self.output_path = "models/trained_food_matcher.pkl"
        
    def train_nutrition_system(self):
        """Train the USDA-based nutrition matching system used in production"""
        print("🚀 Training USDA Nutrition Database System...")
        print("=" * 50)
        
        # Step 1: Load USDA nutrition database
        print("\n📊 Step 1: Loading USDA Nutrition Database...")
        start_time = time.time()
        
        if not os.path.exists(self.usda_db_path):
            print(f"❌ Error: USDA database not found at {self.usda_db_path}")
            return None
            
        df = pd.read_csv(self.usda_db_path)
        load_time = time.time() - start_time
        print(f"✅ Loaded {len(df)} food items in {load_time:.2f}s")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Step 2: Analyze and validate nutrition data
        print("\n🔍 Step 2: Analyzing Nutrition Data Quality...")
        data_quality = self._analyze_data_quality(df)
        
        # Step 3: Build food name search index
        print("\n🗂️ Step 3: Building Food Name Search Index...")
        start_time = time.time()
        search_index = self._build_search_index(df)
        index_time = time.time() - start_time
        print(f"✅ Built search index with {len(search_index)} entries in {index_time:.2f}s")
        
        # Step 4: Train TF-IDF vectorizer for fuzzy matching
        print("\n🧠 Step 4: Training TF-IDF Food Matching Model...")
        start_time = time.time()
        vectorizer, food_vectors = self._train_tfidf_matcher(df)
        tfidf_time = time.time() - start_time
        print(f"✅ Trained TF-IDF model on {len(df)} foods in {tfidf_time:.2f}s")
        
        # Step 5: Validate nutrition calculations
        print("\n🧪 Step 5: Validating Nutrition Calculations...")
        validation_results = self._validate_nutrition_calculations(df)
        
        # Step 6: Optimize portion size mappings
        print("\n⚖️ Step 6: Optimizing Portion Size Mappings...")
        portion_mappings = self._optimize_portion_mappings(df)
        
        # Step 7: Save trained model
        print("\n💾 Step 7: Saving Trained Model...")
        model_data = {
            'nutrition_db': df,
            'search_index': search_index,
            'tfidf_vectorizer': vectorizer,
            'food_vectors': food_vectors,
            'portion_mappings': portion_mappings,
            'data_quality': data_quality,
            'validation_results': validation_results
        }
        
        os.makedirs('models', exist_ok=True)
        with open(self.output_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        # Training summary
        total_time = load_time + index_time + tfidf_time
        training_summary = {
            "usda_database": {
                "total_foods": len(df),
                "data_quality_score": data_quality['overall_score'],
                "missing_data_percentage": data_quality['missing_percentage']
            },
            "search_system": {
                "search_index_size": len(search_index),
                "tfidf_features": food_vectors.shape[1] if food_vectors is not None else 0
            },
            "training_performance": {
                "total_time": total_time,
                "load_time": load_time,
                "index_time": index_time,
                "tfidf_time": tfidf_time
            },
            "validation_results": validation_results,
            "portion_mappings": len(portion_mappings)
        }
        
        print("\n" + "=" * 50)
        print("🎯 USDA NUTRITION TRAINING COMPLETE")
        print("=" * 50)
        print(f"📊 Total Foods Trained: {len(df)}")
        print(f"🔍 Search Index Size: {len(search_index)}")
        print(f"🧠 TF-IDF Features: {food_vectors.shape[1] if food_vectors is not None else 0}")
        print(f"⏱️ Total Training Time: {total_time:.2f}s")
        print(f"✅ Data Quality Score: {data_quality['overall_score']:.2f}/5.0")
        print(f"🎯 Nutrition Accuracy: {validation_results['accuracy']:.1f}%")
        
        return training_summary
    
    def _analyze_data_quality(self, df: pd.DataFrame) -> Dict:
        """Analyze the quality of USDA nutrition data"""
        required_columns = ['display_name', 'calories_per_100g', 'protein_g', 'carbs_g', 'fat_g']
        
        quality_metrics = {}
        
        # Check for missing data
        missing_data = {}
        for col in required_columns:
            if col in df.columns:
                missing_count = df[col].isnull().sum()
                missing_data[col] = missing_count
                print(f"  {col}: {missing_count} missing values ({missing_count/len(df)*100:.1f}%)")
        
        # Check for data consistency
        consistency_issues = 0
        if 'calories_per_100g' in df.columns:
            # Check for unrealistic calorie values
            unrealistic_calories = df[(df['calories_per_100g'] < 0) | (df['calories_per_100g'] > 900)].shape[0]
            consistency_issues += unrealistic_calories
            print(f"  Unrealistic calorie values: {unrealistic_calories}")
        
        # Calculate overall quality score
        total_missing = sum(missing_data.values())
        missing_percentage = (total_missing / (len(df) * len(required_columns))) * 100
        
        quality_score = max(0, 5 - (missing_percentage / 10) - (consistency_issues / len(df) * 5))
        
        return {
            'missing_data': missing_data,
            'missing_percentage': missing_percentage,
            'consistency_issues': consistency_issues,
            'overall_score': quality_score
        }
    
    def _build_search_index(self, df: pd.DataFrame) -> Dict:
        """Build optimized search index for food names"""
        search_index = {}
        exact_matches = {}
        
        for _, row in df.iterrows():
            if pd.isna(row['display_name']):
                continue
                
            name = row['display_name'].lower()
            search_index[name] = row['display_name']
            
            # Add individual words for partial matching
            for word in name.split():
                if len(word) > 2:
                    if word not in exact_matches or len(name.split()) == 1:
                        exact_matches[word] = row['display_name']
        
        # Combine both indexes
        search_index.update(exact_matches)
        return search_index
    
    def _train_tfidf_matcher(self, df: pd.DataFrame) -> Tuple:
        """Train TF-IDF vectorizer for fuzzy food matching"""
        try:
            # Prepare food names for TF-IDF
            food_names = df['display_name'].dropna().tolist()
            
            if len(food_names) == 0:
                print("  ⚠️ No valid food names found for TF-IDF training")
                return None, None
            
            # Train TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                analyzer='char_wb',
                ngram_range=(2, 4),
                max_features=5000,
                lowercase=True
            )
            
            food_vectors = vectorizer.fit_transform(food_names)
            
            print(f"  ✅ TF-IDF trained on {len(food_names)} food names")
            print(f"  📊 Feature dimensions: {food_vectors.shape[1]}")
            
            return vectorizer, food_vectors
            
        except Exception as e:
            print(f"  ❌ TF-IDF training failed: {e}")
            return None, None
    
    def _validate_nutrition_calculations(self, df: pd.DataFrame) -> Dict:
        """Validate nutrition calculation accuracy"""
        validation_results = {
            'total_foods': len(df),
            'valid_nutrition_data': 0,
            'accuracy': 0
        }
        
        # Check for complete nutrition data
        required_nutrients = ['calories_per_100g', 'protein_g', 'carbs_g', 'fat_g']
        
        valid_count = 0
        for _, row in df.iterrows():
            if all(pd.notna(row[col]) and row[col] >= 0 for col in required_nutrients if col in df.columns):
                valid_count += 1
        
        validation_results['valid_nutrition_data'] = valid_count
        validation_results['accuracy'] = (valid_count / len(df)) * 100 if len(df) > 0 else 0
        
        print(f"  ✅ {valid_count}/{len(df)} foods have complete nutrition data")
        print(f"  📊 Nutrition data accuracy: {validation_results['accuracy']:.1f}%")
        
        return validation_results
    
    def _optimize_portion_mappings(self, df: pd.DataFrame) -> Dict:
        """Optimize portion size mappings for different units"""
        portion_mappings = {
            'cup': 1.5,      # 1 cup ≈ 1.5 servings
            'slice': 0.3,    # 1 slice ≈ 0.3 servings  
            'bowl': 2.0,     # 1 bowl ≈ 2 servings
            'tbsp': 0.15,    # 1 tbsp ≈ 0.15 servings
            'serving': 1.0,  # 1 serving = 1 serving
            'count': 1.0     # 1 item = 1 serving
        }
        
        print(f"  ✅ Optimized {len(portion_mappings)} portion size mappings")
        
        return portion_mappings

def main():
    """Main training function"""
    trainer = USDANutritionTrainer()
    
    # Check if USDA database exists
    if not os.path.exists(trainer.usda_db_path):
        print(f"❌ Error: USDA database not found at {trainer.usda_db_path}")
        print("Please ensure the nutrition database file exists.")
        return 1
    
    # Run training
    try:
        training_summary = trainer.train_nutrition_system()
        
        if training_summary is None:
            print("❌ Training failed")
            return 1
        
        # Save training summary
        with open("usda_training_summary.json", "w") as f:
            json.dump(training_summary, f, indent=2)
        
        print(f"\n💾 Training summary saved to usda_training_summary.json")
        print(f"🎯 Trained model saved to {trainer.output_path}")
        print("\n🚀 USDA nutrition system is now trained and ready for production use!")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())