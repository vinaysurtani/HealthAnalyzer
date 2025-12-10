import google.generativeai as genai
import requests
from typing import List, Dict
import os
from dotenv import load_dotenv
from .rag_system import NutritionRAG

load_dotenv()

class NutritionSummarizer:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        self.rag = NutritionRAG()
        
    def generate_summary(self, nutrition_data: List[Dict], totals: Dict, age: int = 30, gender: str = "Male") -> tuple[str, str, List[Dict]]:
        """Generate evidence-based nutrition summary using RAG + LLM"""
        
        print("🔍 DEBUG: Starting generate_summary with Gemini first...")
        
        # Get relevant guidelines from RAG system
        evidence_context = self.rag.get_evidence_based_context(nutrition_data, totals)
        
        # Get evidence sources for display
        evidence_sources = self._get_evidence_sources(nutrition_data, totals)
        
        # Prepare context for LLM
        foods_text = ", ".join([f"{item['food']} ({item['quantity']} serving)" for item in nutrition_data])
        
        prompt = f"""Nutrition intake: {totals['calories']:.0f} cal, {totals['protein']:.0f}g protein, {totals['carbs']:.0f}g carbs, {totals['fat']:.0f}g fat.

Guidelines: {evidence_context}

Provide 2-3 sentences comparing this intake to the guidelines with one recommendation."""
        
        # Try Gemini first (cloud LLM)
        print("🔍 DEBUG: Trying Gemini first...")
        try:
            if os.getenv('GEMINI_API_KEY'):
                print("🔍 DEBUG: Gemini API key found, making request...")
                response = self.gemini_model.generate_content(prompt)
                print(f"✅ DEBUG: Gemini response ({len(response.text)} chars): {response.text[:50]}...")
                    
                return response.text.strip(), "Gemini + RAG", evidence_sources
            else:
                print("❌ DEBUG: No Gemini API key found")
        except Exception as e:
            print(f"❌ DEBUG: Gemini API error: {e}")
            pass
        
        # Try Ollama as fallback (local LLM)
        print("🔍 DEBUG: Trying Ollama as fallback...")
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
                print("✅ DEBUG: Ollama response received successfully!")
                return response.json()['response'].strip(), "Ollama + RAG", evidence_sources
            else:
                print(f"❌ DEBUG: Ollama failed with status: {response.status_code}")
        except Exception as e:
            print(f"❌ DEBUG: Ollama error: {e}")
            pass
            
        # Fallback summary if both LLMs fail
        print("🔍 DEBUG: Using rule-based fallback...")
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