#!/usr/bin/env python3
"""
LLM Provider Comparison: Gemini vs Ollama + RAG
Evaluates response quality, speed, and accuracy for academic analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import json
from typing import Dict, List, Tuple
from src.llm_summarizer import NutritionSummarizer
import matplotlib.pyplot as plt
import pandas as pd

class LLMComparison:
    def __init__(self):
        self.summarizer = NutritionSummarizer()
        self.test_cases = [
            {
                "name": "Balanced Diet",
                "nutrition_data": [
                    {"food": "Chicken Breast", "quantity": "1 serving"},
                    {"food": "Brown Rice", "quantity": "1 serving"},
                    {"food": "Broccoli", "quantity": "1 serving"}
                ],
                "totals": {"calories": 450, "protein": 35, "carbs": 45, "fat": 8}
            },
            {
                "name": "High Protein",
                "nutrition_data": [
                    {"food": "Salmon", "quantity": "1 serving"},
                    {"food": "Greek Yogurt", "quantity": "1 serving"},
                    {"food": "Almonds", "quantity": "1 serving"}
                ],
                "totals": {"calories": 520, "protein": 45, "carbs": 15, "fat": 28}
            },
            {
                "name": "Low Calorie",
                "nutrition_data": [
                    {"food": "Spinach Salad", "quantity": "1 serving"},
                    {"food": "Apple", "quantity": "1 serving"}
                ],
                "totals": {"calories": 180, "protein": 8, "carbs": 35, "fat": 2}
            },
            {
                "name": "High Calorie",
                "nutrition_data": [
                    {"food": "Pizza", "quantity": "2 slices"},
                    {"food": "Ice Cream", "quantity": "1 serving"},
                    {"food": "Soda", "quantity": "1 serving"}
                ],
                "totals": {"calories": 850, "protein": 25, "carbs": 95, "fat": 35}
            }
        ]
    
    def get_both_responses(self, nutrition_data: List[Dict], totals: Dict) -> Tuple[Dict, Dict]:
        """Get responses from both Gemini and Ollama for comparison"""
        
        # Get Gemini response
        gemini_start = time.time()
        try:
            gemini_response, provider, sources = self.summarizer.generate_summary(nutrition_data, totals)
            gemini_time = time.time() - gemini_start
            gemini_result = {
                "response": gemini_response,
                "provider": provider,
                "response_time": gemini_time,
                "success": True,
                "word_count": len(gemini_response.split()),
                "char_count": len(gemini_response)
            }
        except Exception as e:
            gemini_result = {
                "response": f"Error: {e}",
                "provider": "Gemini + RAG",
                "response_time": time.time() - gemini_start,
                "success": False,
                "word_count": 0,
                "char_count": 0
            }
        
        # Force Ollama response by temporarily removing Gemini key
        import os
        original_key = os.environ.get('GEMINI_API_KEY')
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        ollama_start = time.time()
        try:
            # Create new summarizer without Gemini key
            temp_summarizer = NutritionSummarizer()
            ollama_response, provider, sources = temp_summarizer.generate_summary(nutrition_data, totals)
            ollama_time = time.time() - ollama_start
            ollama_result = {
                "response": ollama_response,
                "provider": provider,
                "response_time": ollama_time,
                "success": True,
                "word_count": len(ollama_response.split()),
                "char_count": len(ollama_response)
            }
        except Exception as e:
            ollama_result = {
                "response": f"Error: {e}",
                "provider": "Ollama + RAG",
                "response_time": time.time() - ollama_start,
                "success": False,
                "word_count": 0,
                "char_count": 0
            }
        
        # Restore Gemini key
        if original_key:
            os.environ['GEMINI_API_KEY'] = original_key
        
        return gemini_result, ollama_result
    
    def score_response_quality(self, response: str, totals: Dict) -> Dict:
        """Score response quality based on content analysis"""
        score = {"total": 0, "breakdown": {}}
        
        # Check for key nutrition mentions (0-30 points)
        nutrition_terms = ["calories", "protein", "carbs", "fat", "WHO", "guidelines"]
        mentioned_terms = sum(1 for term in nutrition_terms if term.lower() in response.lower())
        score["breakdown"]["nutrition_coverage"] = (mentioned_terms / len(nutrition_terms)) * 30
        
        # Check for specific recommendations (0-25 points)
        recommendation_indicators = ["recommend", "suggest", "try", "add", "increase", "decrease", "consider"]
        has_recommendation = any(indicator in response.lower() for indicator in recommendation_indicators)
        score["breakdown"]["actionable_advice"] = 25 if has_recommendation else 0
        
        # Check response length appropriateness (0-20 points)
        word_count = len(response.split())
        if 20 <= word_count <= 80:
            score["breakdown"]["appropriate_length"] = 20
        elif 10 <= word_count <= 100:
            score["breakdown"]["appropriate_length"] = 15
        else:
            score["breakdown"]["appropriate_length"] = 5
        
        # Check for evidence-based language (0-15 points)
        evidence_terms = ["WHO", "guidelines", "recommended", "studies", "research"]
        evidence_mentions = sum(1 for term in evidence_terms if term.lower() in response.lower())
        score["breakdown"]["evidence_based"] = min(evidence_mentions * 5, 15)
        
        # Check for personalization (0-10 points)
        personal_terms = ["your", "you", "daily", "intake"]
        personal_mentions = sum(1 for term in personal_terms if term.lower() in response.lower())
        score["breakdown"]["personalization"] = min(personal_mentions * 3, 10)
        
        score["total"] = sum(score["breakdown"].values())
        return score
    
    def run_comparison(self) -> Dict:
        """Run comprehensive comparison between Gemini and Ollama"""
        results = {
            "test_cases": [],
            "summary": {
                "gemini": {"avg_score": 0, "avg_time": 0, "success_rate": 0},
                "ollama": {"avg_score": 0, "avg_time": 0, "success_rate": 0}
            }
        }
        
        print("🔬 Running LLM Provider Comparison...")
        print("=" * 50)
        
        for i, test_case in enumerate(self.test_cases):
            print(f"\n📊 Test Case {i+1}: {test_case['name']}")
            print(f"Nutrition: {test_case['totals']}")
            
            # Get responses from both providers
            gemini_result, ollama_result = self.get_both_responses(
                test_case['nutrition_data'], 
                test_case['totals']
            )
            
            # Score both responses
            if gemini_result['success']:
                gemini_score = self.score_response_quality(gemini_result['response'], test_case['totals'])
                gemini_result['quality_score'] = gemini_score
            else:
                gemini_result['quality_score'] = {"total": 0, "breakdown": {}}
            
            if ollama_result['success']:
                ollama_score = self.score_response_quality(ollama_result['response'], test_case['totals'])
                ollama_result['quality_score'] = ollama_score
            else:
                ollama_result['quality_score'] = {"total": 0, "breakdown": {}}
            
            # Store results
            case_result = {
                "name": test_case['name'],
                "nutrition": test_case['totals'],
                "gemini": gemini_result,
                "ollama": ollama_result
            }
            results['test_cases'].append(case_result)
            
            # Print comparison
            print(f"  Gemini: {gemini_result['quality_score']['total']:.1f}/100 ({gemini_result['response_time']:.2f}s)")
            print(f"  Ollama: {ollama_result['quality_score']['total']:.1f}/100 ({ollama_result['response_time']:.2f}s)")
        
        # Calculate summary statistics
        gemini_scores = [case['gemini']['quality_score']['total'] for case in results['test_cases'] if case['gemini']['success']]
        ollama_scores = [case['ollama']['quality_score']['total'] for case in results['test_cases'] if case['ollama']['success']]
        
        gemini_times = [case['gemini']['response_time'] for case in results['test_cases'] if case['gemini']['success']]
        ollama_times = [case['ollama']['response_time'] for case in results['test_cases'] if case['ollama']['success']]
        
        results['summary']['gemini'] = {
            "avg_score": sum(gemini_scores) / len(gemini_scores) if gemini_scores else 0,
            "avg_time": sum(gemini_times) / len(gemini_times) if gemini_times else 0,
            "success_rate": len(gemini_scores) / len(self.test_cases) * 100
        }
        
        results['summary']['ollama'] = {
            "avg_score": sum(ollama_scores) / len(ollama_scores) if ollama_scores else 0,
            "avg_time": sum(ollama_times) / len(ollama_times) if ollama_times else 0,
            "success_rate": len(ollama_scores) / len(self.test_cases) * 100
        }
        
        return results
    
    def create_visualizations(self, results: Dict):
        """Create comparison visualizations"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Quality Score Comparison
        test_names = [case['name'] for case in results['test_cases']]
        gemini_scores = [case['gemini']['quality_score']['total'] for case in results['test_cases']]
        ollama_scores = [case['ollama']['quality_score']['total'] for case in results['test_cases']]
        
        x = range(len(test_names))
        width = 0.35
        
        ax1.bar([i - width/2 for i in x], gemini_scores, width, label='Gemini + RAG', color='#4285f4')
        ax1.bar([i + width/2 for i in x], ollama_scores, width, label='Ollama + RAG', color='#ff6b35')
        ax1.set_xlabel('Test Cases')
        ax1.set_ylabel('Quality Score (0-100)')
        ax1.set_title('Response Quality Comparison')
        ax1.set_xticks(x)
        ax1.set_xticklabels(test_names, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Response Time Comparison
        gemini_times = [case['gemini']['response_time'] for case in results['test_cases']]
        ollama_times = [case['ollama']['response_time'] for case in results['test_cases']]
        
        ax2.bar([i - width/2 for i in x], gemini_times, width, label='Gemini + RAG', color='#4285f4')
        ax2.bar([i + width/2 for i in x], ollama_times, width, label='Ollama + RAG', color='#ff6b35')
        ax2.set_xlabel('Test Cases')
        ax2.set_ylabel('Response Time (seconds)')
        ax2.set_title('Response Speed Comparison')
        ax2.set_xticks(x)
        ax2.set_xticklabels(test_names, rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Overall Performance Radar
        categories = ['Avg Quality', 'Speed (inverted)', 'Success Rate']
        gemini_values = [
            results['summary']['gemini']['avg_score'],
            100 - (results['summary']['gemini']['avg_time'] * 10),  # Invert time (faster = better)
            results['summary']['gemini']['success_rate']
        ]
        ollama_values = [
            results['summary']['ollama']['avg_score'],
            100 - (results['summary']['ollama']['avg_time'] * 10),
            results['summary']['ollama']['success_rate']
        ]
        
        ax3.bar(categories, gemini_values, alpha=0.7, label='Gemini + RAG', color='#4285f4')
        ax3.bar(categories, ollama_values, alpha=0.7, label='Ollama + RAG', color='#ff6b35')
        ax3.set_ylabel('Score')
        ax3.set_title('Overall Performance Comparison')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Quality Score Breakdown
        quality_categories = ['Nutrition Coverage', 'Actionable Advice', 'Appropriate Length', 'Evidence Based', 'Personalization']
        
        # Average breakdown scores across all test cases
        gemini_breakdown = {cat: 0 for cat in quality_categories}
        ollama_breakdown = {cat: 0 for cat in quality_categories}
        
        for case in results['test_cases']:
            if case['gemini']['success']:
                breakdown = case['gemini']['quality_score']['breakdown']
                gemini_breakdown['Nutrition Coverage'] += breakdown.get('nutrition_coverage', 0)
                gemini_breakdown['Actionable Advice'] += breakdown.get('actionable_advice', 0)
                gemini_breakdown['Appropriate Length'] += breakdown.get('appropriate_length', 0)
                gemini_breakdown['Evidence Based'] += breakdown.get('evidence_based', 0)
                gemini_breakdown['Personalization'] += breakdown.get('personalization', 0)
            
            if case['ollama']['success']:
                breakdown = case['ollama']['quality_score']['breakdown']
                ollama_breakdown['Nutrition Coverage'] += breakdown.get('nutrition_coverage', 0)
                ollama_breakdown['Actionable Advice'] += breakdown.get('actionable_advice', 0)
                ollama_breakdown['Appropriate Length'] += breakdown.get('appropriate_length', 0)
                ollama_breakdown['Evidence Based'] += breakdown.get('evidence_based', 0)
                ollama_breakdown['Personalization'] += breakdown.get('personalization', 0)
        
        # Average the scores
        num_cases = len(results['test_cases'])
        gemini_avg_breakdown = [gemini_breakdown[cat] / num_cases for cat in quality_categories]
        ollama_avg_breakdown = [ollama_breakdown[cat] / num_cases for cat in quality_categories]
        
        x_breakdown = range(len(quality_categories))
        ax4.bar([i - width/2 for i in x_breakdown], gemini_avg_breakdown, width, label='Gemini + RAG', color='#4285f4')
        ax4.bar([i + width/2 for i in x_breakdown], ollama_avg_breakdown, width, label='Ollama + RAG', color='#ff6b35')
        ax4.set_xlabel('Quality Metrics')
        ax4.set_ylabel('Average Score')
        ax4.set_title('Quality Score Breakdown')
        ax4.set_xticks(x_breakdown)
        ax4.set_xticklabels(quality_categories, rotation=45)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('llm_comparison_results.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig

def main():
    comparison = LLMComparison()
    results = comparison.run_comparison()
    
    # Print summary
    print("\n" + "="*50)
    print("📊 COMPARISON SUMMARY")
    print("="*50)
    
    print(f"\n🤖 Gemini + RAG:")
    print(f"  Average Quality Score: {results['summary']['gemini']['avg_score']:.1f}/100")
    print(f"  Average Response Time: {results['summary']['gemini']['avg_time']:.2f}s")
    print(f"  Success Rate: {results['summary']['gemini']['success_rate']:.1f}%")
    
    print(f"\n🦙 Ollama + RAG:")
    print(f"  Average Quality Score: {results['summary']['ollama']['avg_score']:.1f}/100")
    print(f"  Average Response Time: {results['summary']['ollama']['avg_time']:.2f}s")
    print(f"  Success Rate: {results['summary']['ollama']['success_rate']:.1f}%")
    
    # Save results
    with open('llm_comparison_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create visualizations
    comparison.create_visualizations(results)
    
    print(f"\n💾 Results saved to 'llm_comparison_results.json'")
    print(f"📊 Visualizations saved to 'llm_comparison_results.png'")

if __name__ == "__main__":
    main()