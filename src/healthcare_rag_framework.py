#!/usr/bin/env python3
"""
Reusable Healthcare RAG Framework
Extends nutrition RAG for other healthcare text analysis tasks
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .rag_system import NutritionRAG

class HealthcareRAGFramework(ABC):
    """Abstract base class for healthcare text analysis using RAG"""
    
    def __init__(self, knowledge_base_path: str, domain: str):
        self.domain = domain
        self.rag_system = self._initialize_rag(knowledge_base_path)
    
    @abstractmethod
    def _initialize_rag(self, knowledge_base_path: str):
        """Initialize domain-specific RAG system"""
        pass
    
    @abstractmethod
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract domain-specific entities from text"""
        pass
    
    @abstractmethod
    def analyze_content(self, entities: List[Dict]) -> Dict:
        """Analyze extracted entities"""
        pass
    
    @abstractmethod
    def generate_insights(self, analysis: Dict) -> str:
        """Generate evidence-based insights using RAG"""
        pass
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """Complete pipeline for healthcare text analysis"""
        entities = self.extract_entities(text)
        analysis = self.analyze_content(entities)
        insights = self.generate_insights(analysis)
        
        return {
            'entities': entities,
            'analysis': analysis,
            'insights': insights,
            'domain': self.domain
        }

class NutritionAnalysisFramework(HealthcareRAGFramework):
    """Nutrition-specific implementation of healthcare RAG framework"""
    
    def _initialize_rag(self, knowledge_base_path: str):
        return NutritionRAG(knowledge_base_path)
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract food items and quantities"""
        # Use existing food matcher
        from .clean_food_matcher import CleanFoodMatcher
        matcher = CleanFoodMatcher()
        return matcher.extract_foods_with_quantities(text)
    
    def analyze_content(self, entities: List[Dict]) -> Dict:
        """Analyze nutritional content"""
        from .clean_food_matcher import CleanFoodMatcher
        matcher = CleanFoodMatcher()
        nutrition_data, unknown = matcher.get_nutrition_data(entities)
        
        totals = {
            'calories': sum(item['calories'] for item in nutrition_data),
            'protein': sum(item['protein'] for item in nutrition_data),
            'carbs': sum(item['carbs'] for item in nutrition_data),
            'fat': sum(item['fat'] for item in nutrition_data)
        }
        
        return {
            'nutrition_data': nutrition_data,
            'totals': totals,
            'unknown_foods': unknown
        }
    
    def generate_insights(self, analysis: Dict) -> str:
        """Generate nutrition insights using RAG"""
        context = self.rag_system.get_evidence_based_context(
            analysis['nutrition_data'], 
            analysis['totals']
        )
        
        # Use existing summarizer logic
        from .llm_summarizer import NutritionSummarizer
        summarizer = NutritionSummarizer()
        summary, method, sources = summarizer.generate_summary(
            analysis['nutrition_data'], 
            analysis['totals']
        )
        
        return summary

# Example extensions for other healthcare domains
class MedicationAnalysisFramework(HealthcareRAGFramework):
    """Framework for medication text analysis"""
    
    def _initialize_rag(self, knowledge_base_path: str):
        # Would use medication guidelines database
        return NutritionRAG(knowledge_base_path)  # Placeholder
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract medications, dosages, frequencies"""
        # Implementation for medication extraction
        pass
    
    def analyze_content(self, entities: List[Dict]) -> Dict:
        """Analyze drug interactions, dosages"""
        # Implementation for medication analysis
        pass
    
    def generate_insights(self, analysis: Dict) -> str:
        """Generate medication insights using RAG"""
        # Implementation for medication insights
        pass

class SymptomAnalysisFramework(HealthcareRAGFramework):
    """Framework for symptom text analysis"""
    
    def _initialize_rag(self, knowledge_base_path: str):
        # Would use medical symptom guidelines
        return NutritionRAG(knowledge_base_path)  # Placeholder
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract symptoms, severity, duration"""
        # Implementation for symptom extraction
        pass
    
    def analyze_content(self, entities: List[Dict]) -> Dict:
        """Analyze symptom patterns"""
        # Implementation for symptom analysis
        pass
    
    def generate_insights(self, analysis: Dict) -> str:
        """Generate symptom insights using RAG"""
        # Implementation for symptom insights
        pass