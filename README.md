# 🥗 Daily Nutrition Analyzer

A comprehensive web application that analyzes daily food intake and provides personalized nutrition insights using AI-powered recommendations and population health data.

## 🌟 Features

### Core Functionality
- **Natural Language Input**: Enter meals in free text (e.g., "2 slices toast with butter")
- **Smart Food Recognition**: Advanced text parsing with 96.6% F1 score accuracy
- **Comprehensive Nutrition Analysis**: Calories, protein, carbs, fat breakdown
- **AI-Powered Insights**: Evidence-based recommendations using RAG (Retrieval Augmented Generation)

### Advanced Analytics
- **Population Health Comparison**: Compare your intake with NHANES demographic data
- **Personalized Meal Recommendations**: Get specific food suggestions based on nutrition gaps
- **Clinical Notes Integration**: Analyze medical nutrition recommendations
- **AI Provider Comparison**: Compare Gemini vs Ollama performance for research analysis

## 🏗️ Architecture

```
nutrition-analyzer/
├── app.py                          # Main Streamlit application
├── src/                           # Core application modules
│   ├── clean_food_matcher.py      # Primary food recognition engine
│   ├── llm_summarizer.py          # AI summary generation with RAG
│   ├── meal_recommender.py        # Personalized meal suggestions
│   ├── nhanes_analyzer.py         # Population health analysis
│   ├── clinical_parser.py         # Medical notes processing
│   └── rag_system.py              # RAG implementation
├── data/                          # Databases and guidelines
│   ├── nutrition_db_clean.csv     # Curated 68-food database
│   ├── nhanes_demographics.csv    # Population health data
│   └── nutrition_guidelines.txt   # Evidence base for RAG
├── evaluation/                    # Academic evaluation scripts
│   ├── training_script.py         # USDA database training
│   ├── comprehensive_evaluation.py # System performance testing
│   ├── visualization_script.py    # LLM comparison visualizations
│   └── overfitting_test.py        # System validation
└── requirements.txt               # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Gemini API key (optional, has Ollama fallback)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd nutrition-analyzer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key for enhanced AI features
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

### Usage Example

**Input**:
```
Breakfast: 2 slices whole wheat toast with butter and scrambled eggs
Lunch: Grilled chicken breast with brown rice and steamed broccoli  
Snack: 1 apple with peanut butter
Dinner: Baked salmon with sweet potato and romaine lettuce salad
```

**Output**:
- Daily nutrition totals with target comparison
- Per-food breakdown table
- AI-generated evidence-based summary
- Personalized meal recommendations
- Population health comparison

## 🔬 Technical Details

### Food Recognition System
- **Database**: 68 carefully curated foods with complete nutrition profiles
- **Matching Algorithm**: Multi-stage text processing with exact match priority
- **Performance**: 96.6% F1 score on comprehensive test suite
- **Supported Foods**: Common American/Western foods (bread, chicken, salmon, etc.)

### AI & Machine Learning
- **RAG System**: FAISS vector database with SentenceTransformer embeddings
- **LLM Integration**: Gemini API with Ollama fallback
- **Evidence Base**: WHO, USDA guidelines, clinical nutrition research
- **Provider Comparison**: Gemini vs Ollama performance analysis

### Population Health Analytics
- **Data Source**: NHANES (National Health and Nutrition Examination Survey)
- **Demographics**: Age and gender-specific comparisons
- **Sample Sizes**: 1,000-1,500 people per demographic group

## 📊 Performance Metrics

### System Performance
- **Food Detection F1 Score**: 96.6%
- **Calorie Estimation Accuracy**: 60%
- **Processing Time**: 0.12s (single food) to 0.67s (complex meals)
- **Database Coverage**: 68 foods across 5 major categories

### AI Provider Comparison
- **Gemini**: 72.2/100 quality score, 6.29s response time
- **Ollama**: 66.0/100 quality score, 4.09s response time
- **Both**: 100% success rate, evidence-based responses

## 🛠️ Development

### Running Academic Evaluation Scripts
```bash
# Train USDA nutrition database system
python evaluation/training_script.py

# Comprehensive system evaluation
python evaluation/comprehensive_evaluation.py

# AI provider comparison with visualizations
export PYTHONPATH=/path/to/nutrition-analyzer && python evaluation/visualization_script.py

# System validation and overfitting analysis
python evaluation/overfitting_test.py
```

### Adding New Foods
1. Add entries to `data/nutrition_db_clean.csv`
2. Follow the format: `display_name,usda_name,calories_per_100g,protein_g,carbs_g,fat_g,serving_size_g,serving_description`
3. Restart the application to reload the database

## 🔧 Configuration

### Environment Variables
```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key_here  # Optional
STREAMLIT_SERVER_PORT=8501               # Default port
```

### Customization Options
- **Target Calories**: Adjustable in sidebar (1200-3000)
- **Demographics**: Age and gender for population comparison
- **Clinical Integration**: Paste medical nutrition notes
- **AI Provider**: Automatic Gemini → Ollama → Rule-based fallback

## 📈 Research Applications

This system is designed for academic research in:
- **Nutrition Informatics**: Automated dietary assessment
- **Population Health**: Demographic nutrition analysis  
- **Clinical Decision Support**: Medical nutrition therapy
- **AI Comparison Studies**: LLM provider performance analysis
- **Human-Computer Interaction**: Natural language nutrition interfaces

## 📝 Academic Compliance

### Training Script (2%)
- **File**: `evaluation/training_script.py`
- **Function**: Trains USDA nutrition database system with TF-IDF matching
- **Output**: Trained model with 92.6% nutrition accuracy on 68 foods

### Testing Script (2%)
- **File**: `evaluation/comprehensive_evaluation.py`
- **Function**: Tests CleanFoodMatcher system used in production
- **Output**: 96.6% F1 score, performance metrics, accuracy analysis

### Visualization Script (1%)
- **File**: `evaluation/visualization_script.py`
- **Function**: Compares Gemini vs Ollama AI providers with charts
- **Output**: Quality scores, response times, comparative visualizations

## Troubleshooting

### Common Issues

**"No recognizable foods found"**
- Use simpler food names (e.g., "chicken" instead of "grilled chicken breast")
- Check spelling of food items
- Refer to supported foods list in the app

**"ModuleNotFoundError"**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility (3.8+)

**Slow AI responses**
- Check internet connection for Gemini API
- System automatically falls back to Ollama then rule-based responses

### Support
- Create issues for bugs or feature requests
- All evaluation scripts include detailed logging for debugging

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.