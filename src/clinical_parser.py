import re
from typing import Dict, List, Tuple

class ClinicalNotesParser:
    def __init__(self):
        # Clinical nutrition keywords and patterns
        self.nutrition_patterns = {
            'calories': [
                r'(\d+)\s*(?:kcal|calories?|cal)\s*(?:per\s*day|daily|\/day)?',
                r'caloric?\s*intake\s*(?:of\s*)?(\d+)',
                r'energy\s*(?:needs?|requirements?)\s*(?:of\s*)?(\d+)'
            ],
            'protein': [
                r'(\d+(?:\.\d+)?)\s*g(?:rams?)?\s*protein',
                r'protein\s*(?:intake|requirement)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*g',
                r'(\d+(?:\.\d+)?)\s*g\s*pro(?:tein)?'
            ],
            'carbs': [
                r'(\d+(?:\.\d+)?)\s*g(?:rams?)?\s*carb(?:ohydrate)?s?',
                r'carb(?:ohydrate)?\s*(?:intake|limit)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*g'
            ],
            'fat': [
                r'(\d+(?:\.\d+)?)\s*g(?:rams?)?\s*fat',
                r'fat\s*(?:intake|limit)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*g'
            ],
            'sodium': [
                r'(\d+)\s*mg\s*sodium',
                r'sodium\s*(?:limit|restriction)\s*(?:of\s*)?(\d+)\s*mg'
            ]
        }
        
        # Dietary restrictions patterns
        self.restriction_patterns = {
            'diabetic': [
                r'diabetic\s*diet', r'diabetes\s*management', r'glucose\s*control',
                r'carb(?:ohydrate)?\s*counting', r'low\s*glycemic'
            ],
            'cardiac': [
                r'cardiac\s*diet', r'heart\s*healthy', r'low\s*sodium',
                r'dash\s*diet', r'cholesterol\s*management'
            ],
            'renal': [
                r'renal\s*diet', r'kidney\s*diet', r'low\s*protein',
                r'phosphorus\s*restriction', r'potassium\s*limit'
            ],
            'weight_loss': [
                r'weight\s*(?:loss|reduction)', r'caloric?\s*restriction',
                r'low\s*calorie', r'bariatric'
            ]
        }
        
        # Meal timing patterns
        self.timing_patterns = [
            r'(\d+)\s*meals?\s*per\s*day',
            r'eat\s*every\s*(\d+)\s*hours?',
            r'frequent\s*small\s*meals?',
            r'intermittent\s*fasting'
        ]
    
    def parse_clinical_notes(self, notes_text: str) -> Dict:
        """Parse clinical notes for nutrition information"""
        notes_text = notes_text.lower().strip()
        
        parsed_data = {
            'nutrition_targets': {},
            'dietary_restrictions': [],
            'meal_timing': [],
            'clinical_conditions': [],
            'recommendations': []
        }
        
        # Extract nutrition targets
        for nutrient, patterns in self.nutrition_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, notes_text)
                if matches:
                    # Take the first numeric match
                    value = float(matches[0]) if matches[0] else None
                    if value:
                        parsed_data['nutrition_targets'][nutrient] = value
                    break
        
        # Extract dietary restrictions
        for restriction, patterns in self.restriction_patterns.items():
            for pattern in patterns:
                if re.search(pattern, notes_text):
                    parsed_data['dietary_restrictions'].append(restriction)
                    break
        
        # Extract meal timing
        for pattern in self.timing_patterns:
            matches = re.findall(pattern, notes_text)
            if matches:
                parsed_data['meal_timing'].extend(matches)
        
        # Extract specific recommendations
        recommendation_sentences = self._extract_recommendations(notes_text)
        parsed_data['recommendations'] = recommendation_sentences
        
        return parsed_data
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendation sentences from clinical notes"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        recommendation_keywords = [
            'recommend', 'suggest', 'advise', 'should', 'must',
            'increase', 'decrease', 'limit', 'avoid', 'include'
        ]
        
        recommendations = []
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence for keyword in recommendation_keywords):
                if len(sentence) > 10:  # Filter out very short sentences
                    recommendations.append(sentence.capitalize())
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def generate_clinical_summary(self, parsed_data: Dict, user_totals: Dict) -> str:
        """Generate summary comparing user intake to clinical targets"""
        if not parsed_data['nutrition_targets'] and not parsed_data['dietary_restrictions']:
            return "No specific clinical nutrition targets found in notes."
        
        summary_parts = []
        
        # Compare to clinical targets
        if parsed_data['nutrition_targets']:
            summary_parts.append("**Clinical Target Comparison:**")
            
            for nutrient, target in parsed_data['nutrition_targets'].items():
                if nutrient in user_totals:
                    user_value = user_totals[nutrient]
                    diff = user_value - target
                    
                    if abs(diff) < (target * 0.1):  # Within 10%
                        status = "✅ On target"
                    elif diff > 0:
                        status = f"⚠️ {diff:.0f} over target"
                    else:
                        status = f"📉 {abs(diff):.0f} under target"
                    
                    summary_parts.append(f"• {nutrient.title()}: {user_value:.0f} vs {target:.0f} target ({status})")
        
        # Dietary restrictions compliance
        if parsed_data['dietary_restrictions']:
            summary_parts.append(f"\\n**Dietary Restrictions:** {', '.join(parsed_data['dietary_restrictions']).title()}")
        
        # Clinical recommendations
        if parsed_data['recommendations']:
            summary_parts.append("\\n**Clinical Recommendations:**")
            for rec in parsed_data['recommendations'][:3]:
                summary_parts.append(f"• {rec}")
        
        return "\\n".join(summary_parts) if summary_parts else "No clinical nutrition guidance found."