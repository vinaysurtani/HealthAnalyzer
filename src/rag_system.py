import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import pickle
from typing import List, Dict

class NutritionRAG:
    def __init__(self, guidelines_path: str = "data/nutrition_guidelines.txt"):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_path = "./faiss_index.pkl"
        self.docs_path = "./documents.pkl"
        
        # Load or create index
        if os.path.exists(self.index_path) and os.path.exists(self.docs_path):
            self._load_index()
        else:
            self._create_index(guidelines_path)
    
    def _create_index(self, guidelines_path: str):
        """Create FAISS index from nutrition guidelines"""
        with open(guidelines_path, 'r') as f:
            content = f.read()
        
        # Split into chunks by sections
        sections = content.split('\n\n')
        
        self.documents = []
        self.metadatas = []
        
        for i, section in enumerate(sections):
            if section.strip():
                self.documents.append(section.strip())
                # Extract section title as metadata
                title = section.split('\n')[0] if '\n' in section else f"Section {i+1}"
                self.metadatas.append({"title": title, "type": "guideline"})
        
        # Create embeddings
        embeddings = self.encoder.encode(self.documents)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        
        # Save index and documents
        self._save_index()
    
    def _save_index(self):
        """Save FAISS index and documents"""
        faiss.write_index(self.index, "faiss_index.bin")
        with open(self.docs_path, 'wb') as f:
            pickle.dump({'documents': self.documents, 'metadatas': self.metadatas}, f)
    
    def _load_index(self):
        """Load FAISS index and documents"""
        self.index = faiss.read_index("faiss_index.bin")
        with open(self.docs_path, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadatas = data['metadatas']
    
    def retrieve_context(self, query: str, n_results: int = 3) -> List[Dict]:
        """Retrieve relevant nutrition guidelines for a query"""
        # Encode query
        query_embedding = self.encoder.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), n_results)
        
        context = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):  # Valid index
                context.append({
                    'content': self.documents[idx],
                    'title': self.metadatas[idx]['title'],
                    'relevance_score': float(score)  # FAISS returns similarity scores
                })
        
        return context
    
    def get_evidence_based_context(self, nutrition_data: List[Dict], totals: Dict) -> str:
        """Get relevant guidelines based on nutrition analysis"""
        # Create query based on nutrition profile
        cal = totals['calories']
        protein = totals['protein']
        carbs = totals['carbs']
        fat = totals['fat']
        
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
        
        carb_pct = (carbs * 4) / cal * 100 if cal > 0 else 0
        if carb_pct > 60:
            queries.append("carbohydrate intake guidelines")
        
        # Always include general guidelines
        queries.append("daily nutrition recommendations adults")
        
        # Retrieve context for all queries
        all_context = []
        for query in queries:
            context = self.retrieve_context(query, n_results=2)
            all_context.extend(context)
        
        # Remove duplicates and format
        seen_titles = set()
        unique_context = []
        for ctx in all_context:
            if ctx['title'] not in seen_titles:
                unique_context.append(ctx)
                seen_titles.add(ctx['title'])
        
        # Format context for LLM
        formatted_context = "\n\n".join([
            f"**{ctx['title']}**\n{ctx['content']}" 
            for ctx in unique_context[:3]  # Limit to top 3 most relevant
        ])
        
        return formatted_context
    
    def get_document_count(self) -> int:
        """Get number of documents in the index"""
        return len(self.documents) if hasattr(self, 'documents') else 0