import openai
import requests
from typing import List, Dict
import os
from dotenv import load_dotenv
from .rag_system import NutritionRAG

load_dotenv()

class NutritionSummarizer:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.rag = NutritionRAG()
        
    def generate_summary(self, nutrition_data: List[Dict], totals: Dict, age: int = 30, gender: str = "Male") -> tuple[str, str, List[Dict]]:
        """Generate evidence-based nutrition summary using RAG + LLM"""
        
        # Get relevant guidelines from RAG system
        evidence_context = self.rag.get_evidence_based_context(nutrition_data, totals)
        
        # Get evidence sources for display
        evidence_sources = self._get_evidence_sources(nutrition_data, totals)
        
        # Prepare context for LLM
        foods_text = ", ".join([f"{item['food']} ({item['quantity']} serving)" for item in nutrition_data])
        
        prompt = f"""Based on the following evidence-based nutrition guidelines, analyze this daily nutrition intake:

**EVIDENCE-BASED GUIDELINES:**
{evidence_context}

**USER'S DAILY INTAKE:**
Foods consumed: {foods_text}

Daily totals:
- Calories: {totals['calories']}
- Protein: {totals['protein']}g
- Carbohydrates: {totals['carbs']}g  
- Fat: {totals['fat']}g

Provide a 2-3 sentence summary that:
1. Compares their intake to evidence-based guidelines
2. Gives one specific, actionable recommendation
3. Uses friendly, non-technical language
4. Mentions the guideline source when relevant

Keep it encouraging and practical."""
        
        # Try Ollama first (free local LLM)
        try:
            response = requests.post('http://localhost:11434/api/generate',
                json={
                    'model': 'llama3.2:1b',
                    'prompt': prompt,
                    'stream': False
                },
                timeout=10
            )
            if response.status_code == 200:
                return response.json()['response'].strip(), "Ollama + RAG", evidence_sources
        except:
            pass
        
        # Try OpenAI if Ollama fails
        try:
            if os.getenv('OPENAI_API_KEY'):
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a friendly nutrition assistant who explains nutrition in simple terms."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip(), "OpenAI + RAG", evidence_sources
        except:
            pass
            
        # Fallback summary if both LLMs fail
        return self._generate_fallback_summary(totals, evidence_context, age, gender), "Rule-based + RAG", evidence_sources
    
    def _generate_fallback_summary(self, totals: Dict, evidence_context: str = "", age: int = 30, gender: str = "Male") -> str:
        """Enhanced rule-based summary as fallback"""
        cal = totals['calories']
        protein = totals['protein']
        carbs = totals['carbs']
        fat = totals['fat']
        
        # Enhanced assessment with evidence context
        protein_pct = (protein * 4) / cal * 100 if cal > 0 else 0
        carb_pct = (carbs * 4) / cal * 100 if cal > 0 else 0
        
        # Calorie assessment with WHO guidelines based on gender
        target_range = "2200-2500" if gender.lower() == "male" else "1800-2000"
        min_cal = 2200 if gender.lower() == "male" else 1800
        max_cal = 2500 if gender.lower() == "male" else 2000
        
        if cal < min_cal:
            cal_msg = f"Your {cal:.0f} calories are below WHO recommendations ({target_range} for {gender.lower()}s). Consider adding nutrient-dense snacks."
        elif cal > max_cal:
            cal_msg = f"Your {cal:.0f} calories exceed WHO guidelines ({target_range} for {gender.lower()}s). Focus on portion control."
        else:
            cal_msg = f"Your {cal:.0f} calories align well with WHO recommendations for {gender.lower()}s ({target_range})."
        
        # Macro assessment with evidence
        if protein_pct < 10:
            macro_msg = f" Protein is {protein_pct:.1f}% of calories - WHO recommends 10-35%. Add lean proteins like fish, legumes, or eggs."
        elif carb_pct > 65:
            macro_msg = f" Carbs are {carb_pct:.1f}% of calories - WHO recommends 45-65%. Balance with more protein and healthy fats."
        elif protein_pct > 35:
            macro_msg = f" High protein at {protein_pct:.1f}% - ensure adequate hydration and kidney health."
        else:
            macro_msg = f" Macronutrient balance looks good per WHO guidelines (protein: {protein_pct:.1f}%, carbs: {carb_pct:.1f}%)."
        
        return cal_msg + macro_msg
    
    def _get_evidence_sources(self, nutrition_data: List[Dict], totals: Dict) -> List[Dict]:
        """Get evidence sources that were used for recommendations"""
        cal = totals['calories']
        protein = totals['protein']
        carbs = totals['carbs']
        
        # Determine what to look up based on the nutrition profile
        queries = []
        
        if cal < 1200:
            queries.append("low calorie intake daily requirements")
        elif cal > 2500:
            queries.append("high calorie intake recommendations")
        
        protein_pct = (protein * 4) / cal * 100 if cal > 0 else 0
        if protein_pct < 15:
            queries.append("protein requirements daily intake")
        elif protein_pct > 25:
            queries.append("high protein diet recommendations")
        
        # Always include general guidelines
        queries.append("daily nutrition recommendations adults")
        
        # Retrieve context for all queries
        all_sources = []
        for query in queries:
            sources = self.rag.retrieve_context(query, n_results=2)
            all_sources.extend(sources)
        
        # Remove duplicates
        seen_titles = set()
        unique_sources = []
        for source in all_sources:
            if source['title'] not in seen_titles:
                unique_sources.append(source)
                seen_titles.add(source['title'])
        
        return unique_sources[:3]  # Return top 3 most relevant