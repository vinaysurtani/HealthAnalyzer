import pandas as pd
from typing import List, Dict, Tuple
from .rag_system import NutritionRAG

class MealRecommender:
    def __init__(self, nutrition_db_path: str = "data/nutrition_db_clean.csv"):
        self.nutrition_db = pd.read_csv(nutrition_db_path)
        self.rag = NutritionRAG()
        
        # Define target ranges (WHO guidelines)
        self.targets = {
            'calories': {'min': 1800, 'max': 2500},  # Adult range
            'protein_pct': {'min': 15, 'max': 35},   # % of calories
            'carbs_pct': {'min': 45, 'max': 65},     # % of calories
            'fat_pct': {'min': 20, 'max': 35}        # % of calories
        }
        
        # High-value foods for recommendations
        self.recommendation_foods = {
            'protein': ['chicken breast', 'egg', 'greek yogurt', 'salmon', 'tofu', 'lentils'],
            'healthy_carbs': ['oatmeal', 'quinoa', 'sweet potato', 'brown rice'],
            'healthy_fats': ['avocado', 'almonds', 'olive oil', 'salmon'],
            'low_calorie': ['broccoli', 'spinach', 'cucumber', 'apple', 'berries']
        }
    
    def analyze_gaps(self, totals: Dict, target_calories: int = 2000) -> Dict:
        """Analyze nutritional gaps and deficiencies"""
        gaps = {}
        
        # Calorie gap
        cal_gap = target_calories - totals['calories']
        gaps['calories'] = cal_gap
        
        # Macro percentages
        if totals['calories'] > 0:
            protein_pct = (totals['protein'] * 4) / totals['calories'] * 100
            carbs_pct = (totals['carbs'] * 4) / totals['calories'] * 100
            fat_pct = (totals['fat'] * 9) / totals['calories'] * 100
        else:
            protein_pct = carbs_pct = fat_pct = 0
        
        # Calculate target grams for balanced diet
        target_protein_g = (target_calories * 0.20) / 4  # 20% of calories from protein
        target_carbs_g = (target_calories * 0.55) / 4    # 55% of calories from carbs
        target_fat_g = (target_calories * 0.25) / 9      # 25% of calories from fat
        
        gaps['protein'] = max(0, target_protein_g - totals['protein'])
        gaps['carbs'] = max(0, target_carbs_g - totals['carbs'])
        gaps['fat'] = max(0, target_fat_g - totals['fat'])
        
        # Priority assessment
        gaps['priorities'] = []
        if protein_pct < 15:
            gaps['priorities'].append('protein')
        if cal_gap > 300:
            gaps['priorities'].append('calories')
        if carbs_pct > 65:
            gaps['priorities'].append('reduce_carbs')
        if fat_pct < 20:
            gaps['priorities'].append('healthy_fats')
        
        return gaps
    
    def get_food_recommendations(self, gaps: Dict) -> List[Dict]:
        """Generate specific food recommendations with quantities"""
        recommendations = []
        
        # Protein recommendations
        if gaps['protein'] > 10:
            protein_foods = self._get_available_foods(self.recommendation_foods['protein'])
            for food in protein_foods[:2]:  # Top 2 protein sources
                serving_size = self._calculate_serving_for_nutrient(food, 'protein', gaps['protein'] / 2)
                if serving_size:
                    recommendations.append({
                        'food': food,
                        'quantity': serving_size['quantity'],
                        'unit': serving_size['unit'],
                        'reason': f"Add {gaps['protein']:.0f}g protein",
                        'nutrition': serving_size['nutrition'],
                        'priority': 'high' if gaps['protein'] > 20 else 'medium'
                    })
        
        # Calorie recommendations (if under-eating)
        if gaps['calories'] > 200:
            if 'protein' in gaps['priorities']:
                # Protein-rich calorie additions
                foods = self._get_available_foods(['greek yogurt', 'almonds', 'chicken breast'])
            else:
                # Balanced calorie additions
                foods = self._get_available_foods(['banana', 'oatmeal', 'avocado'])
            
            for food in foods[:1]:  # One main calorie addition
                serving_size = self._calculate_serving_for_nutrient(food, 'calories', min(gaps['calories'], 300))
                if serving_size:
                    recommendations.append({
                        'food': food,
                        'quantity': serving_size['quantity'],
                        'unit': serving_size['unit'],
                        'reason': f"Add {gaps['calories']:.0f} calories",
                        'nutrition': serving_size['nutrition'],
                        'priority': 'medium'
                    })
        
        # Healthy fat recommendations
        if gaps['fat'] > 5 and 'healthy_fats' in gaps['priorities']:
            fat_foods = self._get_available_foods(self.recommendation_foods['healthy_fats'])
            for food in fat_foods[:1]:
                serving_size = self._calculate_serving_for_nutrient(food, 'fat', gaps['fat'])
                if serving_size:
                    recommendations.append({
                        'food': food,
                        'quantity': serving_size['quantity'],
                        'unit': serving_size['unit'],
                        'reason': f"Add {gaps['fat']:.0f}g healthy fats",
                        'nutrition': serving_size['nutrition'],
                        'priority': 'medium'
                    })
        
        return recommendations[:4]  # Limit to top 4 recommendations
    
    def _get_available_foods(self, food_list: List[str]) -> List[str]:
        """Filter foods that exist in our database"""
        available = []
        for food in food_list:
            if any(food.lower() in db_food.lower() for db_food in self.nutrition_db['display_name']):
                available.append(food)
        return available
    
    def _calculate_serving_for_nutrient(self, food_name: str, nutrient: str, target_amount: float) -> Dict:
        """Calculate serving size to meet target nutrient amount"""
        # Find food in database
        food_match = None
        for _, row in self.nutrition_db.iterrows():
            if food_name.lower() in row['display_name'].lower():
                food_match = row
                break
        
        if food_match is None:
            return None
        
        # Calculate serving size
        nutrient_per_100g = {
            'calories': food_match['calories_per_100g'],
            'protein': food_match['protein_g'],
            'carbs': food_match['carbs_g'],
            'fat': food_match['fat_g']
        }
        
        if nutrient_per_100g[nutrient] <= 0:
            return None
        
        # Calculate grams needed
        grams_needed = (target_amount / nutrient_per_100g[nutrient]) * 100
        
        # Convert to reasonable serving units
        if grams_needed < 30:
            quantity = round(grams_needed, 0)
            unit = "g"
        elif grams_needed < 100:
            quantity = round(grams_needed / 15) * 15  # Round to nearest 15g
            unit = "g"
        elif grams_needed < 250:
            if food_name in ['rice', 'oatmeal', 'yogurt', 'milk']:
                quantity = round(grams_needed / 100, 1)
                unit = "cup"
            else:
                quantity = round(grams_needed, 0)
                unit = "g"
        else:
            quantity = round(grams_needed / 100, 1)
            unit = "serving"
        
        # Calculate actual nutrition for this serving
        multiplier = grams_needed / 100
        nutrition = {
            'calories': round(nutrient_per_100g['calories'] * multiplier, 0),
            'protein': round(nutrient_per_100g['protein'] * multiplier, 1),
            'carbs': round(nutrient_per_100g['carbs'] * multiplier, 1),
            'fat': round(nutrient_per_100g['fat'] * multiplier, 1)
        }
        
        return {
            'quantity': quantity,
            'unit': unit,
            'nutrition': nutrition
        }
    
    def generate_meal_plan_suggestions(self, gaps: Dict, recommendations: List[Dict]) -> str:
        """Generate meal timing suggestions"""
        if not recommendations:
            return "Your nutrition looks well balanced! Keep up the good work."
        
        suggestions = []
        
        # Group by meal timing
        high_priority = [r for r in recommendations if r['priority'] == 'high']
        medium_priority = [r for r in recommendations if r['priority'] == 'medium']
        
        if high_priority:
            suggestions.append("**Priority additions:**")
            for rec in high_priority:
                suggestions.append(f"• {rec['quantity']} {rec['unit']} {rec['food']} ({rec['reason']}) - adds {rec['nutrition']['calories']:.0f} cal, {rec['nutrition']['protein']:.1f}g protein")
        
        if medium_priority:
            suggestions.append("**Additional suggestions:**")
            for rec in medium_priority:
                suggestions.append(f"• {rec['quantity']} {rec['unit']} {rec['food']} ({rec['reason']}) - adds {rec['nutrition']['calories']:.0f} cal")
        
        # Meal timing advice
        if gaps['calories'] > 300:
            suggestions.append("\n**Timing tip:** Spread these additions across meals or add as healthy snacks.")
        
        return "\n".join(suggestions)