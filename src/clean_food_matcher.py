#!/usr/bin/env python3
"""
Clean food matcher using simplified database
"""

import pandas as pd
import re
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher

class CleanFoodMatcher:
    """Simple matcher using clean food database"""
    
    def __init__(self, db_path: str = 'data/nutrition_db_clean.csv'):
        self.db = pd.read_csv(db_path)
        
        # Create search index with priority
        self.search_index = {}
        self.exact_matches = {}  # For exact word matches
        
        for _, row in self.db.iterrows():
            name = row['display_name'].lower()
            self.search_index[name] = row['display_name']
            
            # Add individual words with priority for exact matches
            for word in name.split():
                if len(word) > 2:
                    # Prioritize single-word foods over multi-word foods
                    if word not in self.exact_matches or len(name.split()) == 1:
                        self.exact_matches[word] = row['display_name']
    
    def find_food(self, query: str) -> Optional[str]:
        """Find matching food with improved priority"""
        original_query = query.lower().strip()
        
        # Remove modifiers
        query = re.sub(r'\b(with|and|of|small|large|medium|boiled|fried|grilled|cooked|raw|baked|steamed)\b', ' ', original_query)
        query = re.sub(r'\s+', ' ', query).strip()
        
        # 1. Exact match (highest priority)
        if query in self.search_index:
            return self.search_index[query]
        
        # 1.5. Exact word match (prioritize single words)
        if query in self.exact_matches:
            return self.exact_matches[query]
        
        # 2. Multi-word exact matches (e.g., "whole wheat bread")
        for display_name in self.db['display_name']:
            if query == display_name.lower():
                return display_name
        
        # 3. Phrase matching (e.g., "brown rice" should match "Brown Rice" not "Rice")
        words = query.split()
        if len(words) > 1:
            for display_name in self.db['display_name']:
                display_lower = display_name.lower()
                if all(word in display_lower for word in words):
                    # Prefer exact phrase matches
                    if query in display_lower:
                        return display_name
        
        # 4. Single word matching (but prefer longer matches)
        best_match = None
        best_score = 0
        
        for word in words:
            if len(word) > 2:  # Skip short words
                for display_name in self.db['display_name']:
                    display_lower = display_name.lower()
                    if word in display_lower:
                        # Score based on word importance and position
                        score = 0.5
                        
                        # Boost if word starts the name
                        if display_lower.startswith(word):
                            score += 0.3
                        
                        # Boost for longer words
                        score += len(word) * 0.05
                        
                        # Penalize if it's just a partial match of a longer word
                        if len(display_name.split()) > 1 and len(words) == 1:
                            score -= 0.2
                        
                        if score > best_score:
                            best_score = score
                            best_match = display_name
        
        # 5. Fuzzy matching as last resort
        if best_score < 0.7:
            for display_name in self.db['display_name']:
                score = SequenceMatcher(None, query, display_name.lower()).ratio()
                if score > best_score and score >= 0.7:
                    best_score = score
                    best_match = display_name
        
        return best_match
    
    def extract_foods_with_quantities(self, text: str) -> List[Dict]:
        """Extract foods with quantities"""
        text = text.lower().strip()
        
        # Split by meal types and connectors
        text = re.sub(r'\b(breakfast|lunch|dinner|snack|morning|afternoon|evening):\s*', '\n', text)
        text = re.sub(r'\b(with|and)\b', ',', text)
        
        segments = re.split(r'[\n,.]', text)
        foods = []
        seen = set()
        
        for segment in segments:
            segment = segment.strip()
            if not segment or len(segment) < 3:
                continue
            
            # Quantity patterns - more specific matching
            patterns = [
                (r'(\d+(?:\.\d+)?)\s*(cups?)\s+(.+)', 'cup'),
                (r'(\d+(?:\.\d+)?)\s*(slices?)\s+(.+)', 'slice'),
                (r'(\d+(?:\.\d+)?)\s*(bowls?)\s+(.+)', 'bowl'),
                (r'(\d+(?:\.\d+)?)\s*(tbsp|tablespoons?)\s+(.+)', 'tbsp'),
                (r'(\d+(?:\.\d+)?)\s+(.+)', 'count'),
            ]
            
            matched = False
            for pattern, unit in patterns:
                match = re.search(pattern, segment)
                if match:
                    if unit == 'count':
                        qty = float(match.group(1))
                        food_text = match.group(2)
                    else:
                        qty = float(match.group(1))
                        food_text = match.group(3)
                    
                    food_name = self.find_food(food_text)
                    if food_name:
                        # Check for duplicates more carefully
                        duplicate = False
                        for existing in foods:
                            if food_name == existing['food']:
                                duplicate = True
                                break
                        
                        if not duplicate:
                            foods.append({
                                'food': food_name,
                                'quantity': qty,
                                'unit': unit,
                                'original_text': food_text.strip()
                            })
                        matched = True
                        break
            
            if not matched:
                food_name = self.find_food(segment)
                if food_name:
                    # Check for duplicates
                    duplicate = False
                    for existing in foods:
                        if food_name == existing['food']:
                            duplicate = True
                            break
                    
                    if not duplicate:
                        foods.append({
                            'food': food_name,
                            'quantity': 1.0,  # Default portion
                            'unit': 'serving',
                            'original_text': segment.strip()
                        })
        
        return foods
    
    def get_nutrition_data(self, foods: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """Get nutrition data"""
        nutrition_data = []
        unknown_foods = []
        
        for food_item in foods:
            food_name = food_item['food']
            match = self.db[self.db['display_name'] == food_name]
            
            if not match.empty:
                row = match.iloc[0]
                
                # Calculate multiplier
                multiplier = food_item['quantity']
                unit = food_item['unit']
                
                if unit == 'cup':
                    multiplier *= 1.5
                elif unit == 'slice':
                    multiplier *= 0.3
                elif unit == 'bowl':
                    multiplier *= 2.0
                elif unit == 'tbsp':
                    multiplier *= 0.15
                elif unit == 'serving':
                    multiplier *= 1.0  # Full serving for unspecified items
                else:  # count
                    multiplier *= 1.0  # Full portion for counted items
                
                nutrition_data.append({
                    'food': food_name,
                    'quantity': f"{food_item['quantity']} {food_item['unit']}",
                    'calories': round(row['calories_per_100g'] * multiplier, 1),
                    'protein': round(row['protein_g'] * multiplier, 1),
                    'carbs': round(row['carbs_g'] * multiplier, 1),
                    'fat': round(row['fat_g'] * multiplier, 1)
                })
            else:
                unknown_foods.append(food_item['original_text'])
        
        return nutrition_data, unknown_foods