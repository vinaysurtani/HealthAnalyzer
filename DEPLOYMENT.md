# 🚀 Deployment Guide

This guide covers different ways to deploy the Daily Nutrition Analyzer application.

## 📋 Prerequisites

- Python 3.8+
- Git
- Internet connection for AI features

## 🖥️ Local Development

### Quick Setup
```bash
# Clone repository
git clone <repository-url>
cd nutrition-analyzer

# Install dependencies
pip install -r requirements.txt

# Copy environment file (optional)
cp .env.example .env
# Edit .env to add Gemini API key for enhanced AI features

# Start application
streamlit run app.py
```

## ☁️ Cloud Deployment

### Streamlit Cloud (Recommended)

1. **Fork the repository** to your GitHub account

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Deploy new app**:
   - Repository: `your-username/nutrition-analyzer`
   - Branch: `main`
   - Main file path: `app.py`

4. **Add secrets** (optional):
   ```toml
   # In Streamlit Cloud secrets
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```

5. **Deploy** - Your app will be available at `https://your-app-name.streamlit.app`

### Heroku Deployment

1. **Create Heroku app**:
   ```bash
   heroku create your-nutrition-analyzer
   ```

2. **Add buildpack**:
   ```bash
   heroku buildpacks:set heroku/python
   ```

3. **Create Procfile**:
   ```bash
   echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
   ```

4. **Set environment variables**:
   ```bash
   heroku config:set GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Docker Deployment

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
   
   ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and run**:
   ```bash
   docker build -t nutrition-analyzer .
   docker run -p 8501:8501 nutrition-analyzer
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Gemini API key for enhanced AI features | No |
| `STREAMLIT_SERVER_PORT` | Port for Streamlit server | No (default: 8501) |

### AI Provider Fallback Chain
1. **Gemini API** (if key provided) - Cloud AI with high quality
2. **Ollama** (if running locally) - Local AI processing
3. **Rule-based** - Deterministic fallback using WHO guidelines

## 🛠️ Academic Evaluation

### Running Evaluation Scripts
```bash
# Train USDA nutrition database system
python evaluation/training_script.py

# Test system performance
python evaluation/comprehensive_evaluation.py

# Generate AI comparison visualizations
export PYTHONPATH=$(pwd) && python evaluation/visualization_script.py

# Validate system robustness
python evaluation/overfitting_test.py
```

## 🔒 Security Considerations

### API Keys
- Never commit API keys to version control
- Use environment variables or secrets management
- Gemini API has generous free tier limits

### Data Privacy
- No user data is stored permanently
- Session data is cleared on browser close
- NHANES data is anonymized population statistics

## 📊 Performance Metrics

### System Performance
- **Food Detection**: 96.6% F1 score
- **Response Time**: 0.12s - 6.29s depending on AI provider
- **Database**: 68 curated foods for optimal speed
- **Memory Usage**: ~200MB baseline

### AI Provider Performance
- **Gemini**: 72.2/100 quality, 6.29s avg response time
- **Ollama**: 66.0/100 quality, 4.09s avg response time
- **Rule-based**: Instant response, WHO guideline-based

## 🚨 Troubleshooting

### Common Issues

**"No recognizable foods found"**:
- Use simpler food names (e.g., "chicken" vs "grilled chicken breast")
- Check spelling of food items
- System supports 68 common foods

**Module not found**:
```bash
pip install -r requirements.txt --force-reinstall
```

**AI timeouts**:
- Check internet connection for Gemini API
- System automatically falls back to Ollama then rule-based
- No API key required for basic functionality

**Port already in use**:
```bash
streamlit run app.py --server.port=8502
```

## 📈 Academic Applications

This deployment supports research in:
- **Nutrition Informatics**: Automated dietary assessment
- **AI Comparison Studies**: Multi-provider LLM analysis
- **Population Health**: NHANES demographic analysis
- **Clinical Decision Support**: Medical nutrition integration

---

**Need help?** Check the main README.md or create an issue in the repository.