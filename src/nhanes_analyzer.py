import pandas as pd
from typing import Dict, List, Tuple

class NHANESAnalyzer:
    def __init__(self, nhanes_data_path: str = "data/nhanes_demographics.csv"):
        self.nhanes_data = pd.read_csv(nhanes_data_path)
        
    def get_demographic_comparison(self, totals: Dict, age: int, gender: str) -> Dict:
        """Compare user's intake to NHANES population data"""
        
        # Determine age group
        if age < 31:
            age_group = "18-30"
        elif age < 51:
            age_group = "31-50"
        elif age < 66:
            age_group = "51-65"
        else:
            age_group = "65+"
        
        # Get matching demographic data
        demo_data = self.nhanes_data[
            (self.nhanes_data['age_group'] == age_group) & 
            (self.nhanes_data['gender'] == gender)
        ]
        
        if demo_data.empty:
            return {"error": "No demographic data available"}
        
        demo = demo_data.iloc[0]
        
        # Calculate percentiles for user's intake
        comparisons = {}
        
        for nutrient in ['calories', 'protein', 'carbs', 'fat']:
            user_value = totals[nutrient]
            p50 = demo[f'{nutrient}_p50']
            p75 = demo[f'{nutrient}_p75']
            
            if user_value < p50:
                percentile = "below 50th percentile"
                status = "low"
            elif user_value < p75:
                percentile = "50th-75th percentile"
                status = "average"
            else:
                percentile = "above 75th percentile"
                status = "high"
            
            comparisons[nutrient] = {
                'user_value': user_value,
                'p50': p50,
                'p75': p75,
                'percentile': percentile,
                'status': status
            }
        
        return {
            'age_group': age_group,
            'gender': gender,
            'sample_size': demo['sample_size'],
            'comparisons': comparisons
        }
    
    def generate_population_insights(self, comparison: Dict) -> List[str]:
        """Generate insights based on population comparison"""
        if "error" in comparison:
            return ["Population comparison not available"]
        
        insights = []
        comparisons = comparison['comparisons']
        
        # Calorie insights
        cal_status = comparisons['calories']['status']
        if cal_status == "low":
            insights.append(f"📊 Your calorie intake is below average for {comparison['gender'].lower()}s aged {comparison['age_group']}")
        elif cal_status == "high":
            insights.append(f"📊 Your calorie intake is above 75% of {comparison['gender'].lower()}s in your age group")
        
        # Protein insights
        protein_status = comparisons['protein']['status']
        if protein_status == "high":
            insights.append(f"💪 Excellent protein intake - higher than 75% of your demographic")
        elif protein_status == "low":
            insights.append(f"💪 Your protein intake is below average for your age group")
        
        # Risk factor insights
        high_nutrients = [k for k, v in comparisons.items() if v['status'] == 'high']
        if len(high_nutrients) >= 2:
            insights.append(f"⚠️ Multiple nutrients above 75th percentile - monitor portion sizes")
        
        low_nutrients = [k for k, v in comparisons.items() if v['status'] == 'low']
        if len(low_nutrients) >= 2:
            insights.append(f"📈 Multiple nutrients below average - consider increasing intake")
        
        # Sample size context
        insights.append(f"📋 Based on {comparison['sample_size']:,} individuals in NHANES survey")
        
        return insights
    
    def get_risk_assessment(self, comparison: Dict, totals: Dict) -> Dict:
        """Assess health risks based on population data"""
        if "error" in comparison:
            return {"risk_level": "unknown", "factors": []}
        
        risk_factors = []
        risk_score = 0
        
        # High calorie risk
        if comparison['comparisons']['calories']['status'] == 'high':
            if totals['calories'] > 2800:
                risk_factors.append("Very high calorie intake (>2800)")
                risk_score += 2
            else:
                risk_factors.append("Above-average calorie intake")
                risk_score += 1
        
        # Low protein risk
        if comparison['comparisons']['protein']['status'] == 'low':
            protein_pct = (totals['protein'] * 4) / totals['calories'] * 100 if totals['calories'] > 0 else 0
            if protein_pct < 10:
                risk_factors.append("Very low protein intake (<10% calories)")
                risk_score += 2
            else:
                risk_factors.append("Below-average protein intake")
                risk_score += 1
        
        # High carb risk
        if comparison['comparisons']['carbs']['status'] == 'high':
            carb_pct = (totals['carbs'] * 4) / totals['calories'] * 100 if totals['calories'] > 0 else 0
            if carb_pct > 70:
                risk_factors.append("Very high carbohydrate intake (>70% calories)")
                risk_score += 2
        
        # Determine overall risk level
        if risk_score >= 4:
            risk_level = "high"
        elif risk_score >= 2:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "factors": risk_factors
        }