import json
import pandas as pd
from typing import Dict, List, Tuple
from rouge_score import rouge_scorer
from sacrebleu.metrics import BLEU
from bert_score import score as bert_score
import datetime
import os

class NutritionEvaluator:
    def __init__(self):
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        self.bleu_scorer = BLEU()
        self.evaluation_log = []
        
    def evaluate_summary_quality(self, generated_summary: str, reference_summary: str) -> Dict:
        """Evaluate generated nutrition summary against reference using multiple metrics"""
        
        # ROUGE scores
        rouge_scores = self.rouge_scorer.score(reference_summary, generated_summary)
        
        # BLEU score
        bleu_score = self.bleu_scorer.sentence_score(generated_summary, [reference_summary])
        
        # BERTScore
        P, R, F1 = bert_score([generated_summary], [reference_summary], lang="en", verbose=False)
        
        metrics = {
            'rouge1_f1': rouge_scores['rouge1'].fmeasure,
            'rouge2_f1': rouge_scores['rouge2'].fmeasure,
            'rougeL_f1': rouge_scores['rougeL'].fmeasure,
            'bleu_score': bleu_score.score / 100,  # Normalize to 0-1
            'bert_precision': P.item(),
            'bert_recall': R.item(),
            'bert_f1': F1.item(),
            'overall_score': self._calculate_overall_score(rouge_scores, bleu_score.score / 100, F1.item())
        }
        
        return metrics
    
    def _calculate_overall_score(self, rouge_scores: Dict, bleu_score: float, bert_f1: float) -> float:
        """Calculate weighted overall quality score"""
        weights = {
            'rouge1': 0.2,
            'rouge2': 0.2,
            'rougeL': 0.2,
            'bleu': 0.2,
            'bert': 0.2
        }
        
        overall = (
            rouge_scores['rouge1'].fmeasure * weights['rouge1'] +
            rouge_scores['rouge2'].fmeasure * weights['rouge2'] +
            rouge_scores['rougeL'].fmeasure * weights['rougeL'] +
            bleu_score * weights['bleu'] +
            bert_f1 * weights['bert']
        )
        
        return overall
    
    def evaluate_retrieval_grounding(self, generated_summary: str, evidence_sources: List[Dict]) -> Dict:
        """Evaluate how well the summary is grounded in retrieved evidence"""
        
        if not evidence_sources:
            return {'grounding_score': 0.0, 'cited_sources': 0, 'total_sources': 0}
        
        # Check for evidence citations in summary
        cited_sources = 0
        total_sources = len(evidence_sources)
        
        summary_lower = generated_summary.lower()
        
        for source in evidence_sources:
            # Check if key terms from source appear in summary
            source_title = source['title'].lower()
            source_content = source['content'].lower()
            
            # Extract key terms (simple approach)
            key_terms = self._extract_key_terms(source_title + " " + source_content)
            
            # Check if any key terms appear in summary
            if any(term in summary_lower for term in key_terms):
                cited_sources += 1
        
        grounding_score = cited_sources / total_sources if total_sources > 0 else 0
        
        return {
            'grounding_score': grounding_score,
            'cited_sources': cited_sources,
            'total_sources': total_sources
        }
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key nutrition terms from text"""
        nutrition_terms = [
            'who', 'calories', 'protein', 'carbohydrate', 'fat', 'fiber',
            'vitamin', 'mineral', 'daily', 'intake', 'recommendation',
            'guideline', 'nutrition', 'diet', 'health'
        ]
        
        words = text.split()
        key_terms = [word for word in words if word in nutrition_terms]
        return list(set(key_terms))  # Remove duplicates
    
    def evaluate_recommendation_accuracy(self, recommendations: List[Dict], user_gaps: Dict) -> Dict:
        """Evaluate accuracy of meal recommendations"""
        
        if not recommendations:
            return {'accuracy_score': 0.0, 'relevant_recommendations': 0}
        
        relevant_count = 0
        
        for rec in recommendations:
            # Check if recommendation addresses actual nutritional gaps
            reason = rec.get('reason', '').lower()
            
            # Check if recommendation targets identified gaps
            if 'protein' in reason and user_gaps.get('protein', 0) > 10:
                relevant_count += 1
            elif 'calorie' in reason and user_gaps.get('calories', 0) > 200:
                relevant_count += 1
            elif 'fat' in reason and user_gaps.get('fat', 0) > 5:
                relevant_count += 1
        
        accuracy_score = relevant_count / len(recommendations) if recommendations else 0
        
        return {
            'accuracy_score': accuracy_score,
            'relevant_recommendations': relevant_count,
            'total_recommendations': len(recommendations)
        }
    
    def log_evaluation(self, evaluation_data: Dict):
        """Log evaluation results for analysis"""
        
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'evaluation_id': len(self.evaluation_log) + 1,
            **evaluation_data
        }
        
        self.evaluation_log.append(log_entry)
        
        # Save to file
        os.makedirs('evaluation_logs', exist_ok=True)
        with open('evaluation_logs/evaluation_log.json', 'w') as f:
            json.dump(self.evaluation_log, f, indent=2)
    
    def generate_evaluation_report(self) -> Dict:
        """Generate comprehensive evaluation report"""
        
        if not self.evaluation_log:
            return {'error': 'No evaluation data available'}
        
        # Calculate aggregate metrics
        df = pd.DataFrame(self.evaluation_log)
        
        summary_metrics = {}
        if 'summary_quality' in df.columns:
            quality_data = [entry for entry in df['summary_quality'] if entry]
            if quality_data:
                summary_metrics = {
                    'avg_rouge1_f1': sum(q['rouge1_f1'] for q in quality_data) / len(quality_data),
                    'avg_rouge2_f1': sum(q['rouge2_f1'] for q in quality_data) / len(quality_data),
                    'avg_bleu_score': sum(q['bleu_score'] for q in quality_data) / len(quality_data),
                    'avg_bert_f1': sum(q['bert_f1'] for q in quality_data) / len(quality_data),
                    'avg_overall_score': sum(q['overall_score'] for q in quality_data) / len(quality_data)
                }
        
        grounding_metrics = {}
        if 'grounding_quality' in df.columns:
            grounding_data = [entry for entry in df['grounding_quality'] if entry]
            if grounding_data:
                grounding_metrics = {
                    'avg_grounding_score': sum(g['grounding_score'] for g in grounding_data) / len(grounding_data),
                    'total_evaluations': len(grounding_data)
                }
        
        recommendation_metrics = {}
        if 'recommendation_accuracy' in df.columns:
            rec_data = [entry for entry in df['recommendation_accuracy'] if entry]
            if rec_data:
                recommendation_metrics = {
                    'avg_accuracy_score': sum(r['accuracy_score'] for r in rec_data) / len(rec_data),
                    'total_recommendations_evaluated': sum(r['total_recommendations'] for r in rec_data)
                }
        
        return {
            'evaluation_period': {
                'start': df['timestamp'].min() if not df.empty else None,
                'end': df['timestamp'].max() if not df.empty else None,
                'total_evaluations': len(df)
            },
            'summary_quality_metrics': summary_metrics,
            'grounding_metrics': grounding_metrics,
            'recommendation_metrics': recommendation_metrics
        }

class ExpertValidationInterface:
    def __init__(self):
        self.validation_data = []
    
    def create_validation_task(self, generated_summary: str, recommendations: List[Dict], 
                             nutrition_data: List[Dict], totals: Dict) -> Dict:
        """Create a validation task for expert review"""
        
        task = {
            'task_id': len(self.validation_data) + 1,
            'timestamp': datetime.datetime.now().isoformat(),
            'generated_summary': generated_summary,
            'recommendations': recommendations,
            'nutrition_data': nutrition_data,
            'totals': totals,
            'validation_status': 'pending',
            'expert_feedback': {}
        }
        
        self.validation_data.append(task)
        return task
    
    def submit_expert_feedback(self, task_id: int, feedback: Dict) -> bool:
        """Submit expert validation feedback"""
        
        for task in self.validation_data:
            if task['task_id'] == task_id:
                task['expert_feedback'] = feedback
                task['validation_status'] = 'completed'
                task['validation_timestamp'] = datetime.datetime.now().isoformat()
                
                # Save to file
                os.makedirs('expert_validation', exist_ok=True)
                with open('expert_validation/validation_data.json', 'w') as f:
                    json.dump(self.validation_data, f, indent=2)
                
                return True
        
        return False
    
    def get_validation_statistics(self) -> Dict:
        """Get expert validation statistics"""
        
        if not self.validation_data:
            return {'total_tasks': 0}
        
        completed_tasks = [task for task in self.validation_data if task['validation_status'] == 'completed']
        
        if not completed_tasks:
            return {'total_tasks': len(self.validation_data), 'completed_tasks': 0}
        
        # Calculate agreement metrics
        accuracy_scores = []
        safety_scores = []
        
        for task in completed_tasks:
            feedback = task['expert_feedback']
            if 'accuracy_rating' in feedback:
                accuracy_scores.append(feedback['accuracy_rating'])
            if 'safety_rating' in feedback:
                safety_scores.append(feedback['safety_rating'])
        
        return {
            'total_tasks': len(self.validation_data),
            'completed_tasks': len(completed_tasks),
            'completion_rate': len(completed_tasks) / len(self.validation_data),
            'avg_accuracy_rating': sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0,
            'avg_safety_rating': sum(safety_scores) / len(safety_scores) if safety_scores else 0
        }