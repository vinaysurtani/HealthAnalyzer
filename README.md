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
- **Risk Assessment**: Health risk profiling based on population patterns

### Research & Validation
- **Machine Learning Classification**: Random Forest model with 96.3% accuracy
- **Comprehensive Evaluation System**: Performance metrics and overfitting analysis
- **Dynamic Visualizations**: Real-time performance charts and nutrition breakdowns

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
│   ├── food_classifier.py         # ML training script
│   ├── rag_system.py              # RAG implementation
│   └── healthcare_rag_framework.py # Reusable RAG framework
├── data/                          # Databases and guidelines
│   ├── nutrition_db_clean.csv     # Curated 68-food database
│   ├── nhanes_demographics.csv    # Population health data
│   └── nutrition_guidelines.txt   # Evidence base for RAG
├── evaluation/                    # Performance testing
│   ├── comprehensive_evaluation.py # System evaluation
│   ├── benchmark_system.py        # Performance benchmarks
│   └── dynamic_visualizer.py      # Real-time visualizations
├── models/                        # Trained ML models
│   └── food_classifier.pkl        # Random Forest classifier
└── requirements.txt               # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- OpenAI API key (optional, has fallback)

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
   # Edit .env and add your OpenAI API key for enhanced AI features
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
- Risk assessment

## 🔬 Technical Details

### Food Recognition System
- **Database**: 68 carefully curated foods with complete nutrition profiles
- **Matching Algorithm**: Multi-stage text processing with exact match priority
- **Performance**: 96.6% F1 score on comprehensive test suite
- **Supported Foods**: Common American/Western foods (bread, chicken, salmon, etc.)

### AI & Machine Learning
- **RAG System**: FAISS vector database with SentenceTransformer embeddings
- **Classification**: Random Forest with TF-IDF vectorization (96.3% accuracy)
- **LLM Integration**: OpenAI GPT with fallback to local processing
- **Evidence Base**: WHO, USDA guidelines, clinical nutrition research

### Population Health Analytics
- **Data Source**: NHANES (National Health and Nutrition Examination Survey)
- **Demographics**: Age and gender-specific comparisons
- **Sample Sizes**: 1,000-1,500 people per demographic group
- **Risk Modeling**: Population-based health risk assessment

## 📊 Performance Metrics

### System Performance
- **Food Detection F1 Score**: 96.6%
- **Calorie Estimation Accuracy**: 60%
- **Processing Time**: 0.12s (single food) to 0.67s (complex meals)
- **Database Coverage**: 68 foods across 5 major categories

### Academic Validation
- **Cross-validation**: 2.4% accuracy variance (low overfitting)
- **Robustness**: 100% accuracy on misspelled foods
- **False Positive Rate**: 20% on unseen foods (acceptable threshold)

## 🛠️ Development

### Running Tests
```bash
# Comprehensive system evaluation
python evaluation/comprehensive_evaluation.py

# Performance benchmarks
python evaluation/benchmark_system.py

# Generate visualizations
python evaluation/dynamic_visualizer.py

# Train ML classifier
python src/food_classifier.py
```

### Adding New Foods
1. Add entries to `data/nutrition_db_clean.csv`
2. Follow the format: `display_name,usda_name,calories_per_100g,protein_g,carbs_g,fat_g,serving_size_g,serving_description`
3. Restart the application to reload the database

### Extending RAG System
```python
from src.healthcare_rag_framework import HealthcareRAGFramework

# Create domain-specific RAG system
rag = HealthcareRAGFramework(
    domain="cardiology",
    guidelines_path="cardiology_guidelines.txt"
)
```

## 🔧 Configuration

### Environment Variables
```bash
# .env file
OPENAI_API_KEY=your_api_key_here  # Optional
STREAMLIT_SERVER_PORT=8501        # Default port
```

### Customization Options
- **Target Calories**: Adjustable in sidebar (1200-3000)
- **Dietary Preferences**: Vegetarian, vegan, low-carb, high-protein
- **Demographics**: Age and gender for population comparison
- **Clinical Integration**: Paste medical nutrition notes

## 📈 Research Applications

This system is designed for academic research in:
- **Nutrition Informatics**: Automated dietary assessment
- **Population Health**: Demographic nutrition analysis  
- **Clinical Decision Support**: Medical nutrition therapy
- **Machine Learning**: Food classification and NLP
- **Human-Computer Interaction**: Natural language nutrition interfaces

### Citation
If you use this system in research, please cite:
```
Daily Nutrition Analyzer: An AI-Powered System for Automated Dietary Assessment
with Population Health Integration and Evidence-Based Recommendations
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**"No recognizable foods found"**
- Use simpler food names (e.g., "chicken" instead of "grilled chicken breast")
- Check spelling of food items
- Refer to supported foods list in the app

**"ModuleNotFoundError"**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility (3.8+)

**Slow performance**
- Reduce input complexity
- Check internet connection for AI features
- Consider using local LLM fallback

### Support
- Check the [Issues](link-to-issues) page for known problems
- Create a new issue for bugs or feature requests
- Review the evaluation logs in `evaluation_logs/` for debugging

## 🔮 Future Roadmap

- **Photo Food Logging**: Upload meal photos for automatic recognition
- **Barcode Scanning**: Instant nutrition data for packaged foods
- **Voice Input**: "Hey app, I ate chicken and rice"
- **Mobile App**: React Native or Flutter implementation
- **Micronutrient Tracking**: Vitamins, minerals, fiber analysis
- **Integration APIs**: Fitbit, Apple Health, MyFitnessPal sync

---

**Built with ❤️ for better nutrition and health outcomes**