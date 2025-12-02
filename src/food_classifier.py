#!/usr/bin/env python3
"""
ML-based food classification model for nutrition analysis
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import re

class FoodClassificationModel:
    """ML model for food classification and nutrition prediction"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.nutrition_predictor = RandomForestClassifier(n_estimators=50, random_state=42)
        self.is_trained = False
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess food text for classification"""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', '', text)  # Remove numbers
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def create_training_data(self) -> tuple:
        """Create training data from clean food database"""
        # Load clean database
        db = pd.read_csv('data/nutrition_db_clean.csv')
        
        # Create synthetic training examples
        training_data = []
        labels = []
        nutrition_targets = []
        
        for _, row in db.iterrows():
            food_name = row['display_name']
            
            # Create variations of food names
            variations = [
                food_name.lower(),
                f"grilled {food_name.lower()}",
                f"baked {food_name.lower()}",
                f"fresh {food_name.lower()}",
                f"cooked {food_name.lower()}",
                f"raw {food_name.lower()}"
            ]
            
            for variation in variations:
                processed_text = self.preprocess_text(variation)
                training_data.append(processed_text)
                labels.append(food_name)
                
                # Nutrition target (calories per 100g category)
                calories = row['calories_per_100g']
                if calories < 100:
                    nutrition_targets.append(0)  # Low calorie
                elif calories < 300:
                    nutrition_targets.append(1)  # Medium calorie
                else:
                    nutrition_targets.append(2)  # High calorie
        
        return training_data, labels, nutrition_targets
    
    def train(self) -> dict:
        """Train the food classification model"""
        print("Creating training data...")
        texts, food_labels, nutrition_labels = self.create_training_data()
        
        # Split data
        X_train, X_test, y_food_train, y_food_test, y_nutr_train, y_nutr_test = train_test_split(
            texts, food_labels, nutrition_labels, test_size=0.2, random_state=42
        )
        
        # Vectorize text
        print("Vectorizing text...")
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Train food classifier
        print("Training food classifier...")
        self.classifier.fit(X_train_vec, y_food_train)
        food_pred = self.classifier.predict(X_test_vec)
        food_accuracy = accuracy_score(y_food_test, food_pred)
        
        # Train nutrition predictor
        print("Training nutrition predictor...")
        self.nutrition_predictor.fit(X_train_vec, y_nutr_train)
        nutr_pred = self.nutrition_predictor.predict(X_test_vec)
        nutr_accuracy = accuracy_score(y_nutr_test, nutr_pred)
        
        self.is_trained = True
        
        results = {
            'food_classification_accuracy': food_accuracy,
            'nutrition_prediction_accuracy': nutr_accuracy,
            'training_samples': len(texts),
            'test_samples': len(X_test)
        }
        
        print(f"Food Classification Accuracy: {food_accuracy:.3f}")
        print(f"Nutrition Prediction Accuracy: {nutr_accuracy:.3f}")
        
        return results
    
    def predict_food(self, text: str) -> tuple:
        """Predict food type and nutrition category"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        processed_text = self.preprocess_text(text)
        text_vec = self.vectorizer.transform([processed_text])
        
        food_pred = self.classifier.predict(text_vec)[0]
        food_prob = max(self.classifier.predict_proba(text_vec)[0])
        
        nutr_pred = self.nutrition_predictor.predict(text_vec)[0]
        nutr_categories = ['Low Calorie (<100)', 'Medium Calorie (100-300)', 'High Calorie (>300)']
        
        return {
            'predicted_food': food_pred,
            'confidence': food_prob,
            'nutrition_category': nutr_categories[nutr_pred],
            'nutrition_level': nutr_pred
        }
    
    def save_model(self, path: str = 'models/food_classifier.pkl'):
        """Save trained model"""
        import os
        os.makedirs('models', exist_ok=True)
        
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'nutrition_predictor': self.nutrition_predictor,
            'is_trained': self.is_trained
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {path}")
    
    def load_model(self, path: str = 'models/food_classifier.pkl'):
        """Load trained model"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.classifier = model_data['classifier']
        self.nutrition_predictor = model_data['nutrition_predictor']
        self.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {path}")

def train_and_evaluate():
    """Train and evaluate the food classification model"""
    model = FoodClassificationModel()
    
    # Train model
    results = model.train()
    
    # Save model
    model.save_model()
    
    # Test predictions
    test_inputs = [
        "grilled chicken breast",
        "whole wheat bread",
        "greek yogurt",
        "brown rice"
    ]
    
    print("\n=== Test Predictions ===")
    for text in test_inputs:
        prediction = model.predict_food(text)
        print(f"Input: '{text}'")
        print(f"Predicted: {prediction['predicted_food']} (confidence: {prediction['confidence']:.3f})")
        print(f"Nutrition: {prediction['nutrition_category']}")
        print()
    
    return results

if __name__ == "__main__":
    train_and_evaluate()