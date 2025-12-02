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

# Run setup script
python setup.py

# Start application
streamlit run app.py
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env to add OpenAI API key (optional)

# Test installation
python test_installation.py

# Run application
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
   OPENAI_API_KEY = "your_api_key_here"
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
   heroku config:set OPENAI_API_KEY=your_api_key_here
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

### AWS EC2 Deployment

1. **Launch EC2 instance** (Ubuntu 20.04 LTS)

2. **Connect and setup**:
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and Git
   sudo apt install python3 python3-pip git -y
   
   # Clone repository
   git clone <repository-url>
   cd nutrition-analyzer
   
   # Install dependencies
   pip3 install -r requirements.txt
   ```

3. **Setup systemd service**:
   ```bash
   sudo nano /etc/systemd/system/nutrition-analyzer.service
   ```
   
   ```ini
   [Unit]
   Description=Daily Nutrition Analyzer
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/nutrition-analyzer
   ExecStart=/usr/bin/python3 -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable nutrition-analyzer
   sudo systemctl start nutrition-analyzer
   ```

5. **Setup nginx reverse proxy** (optional):
   ```bash
   sudo apt install nginx -y
   sudo nano /etc/nginx/sites-available/nutrition-analyzer
   ```
   
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for enhanced AI features | No |
| `STREAMLIT_SERVER_PORT` | Port for Streamlit server | No (default: 8501) |
| `DEBUG_MODE` | Enable debug logging | No (default: false) |

### Performance Optimization

1. **Enable caching**:
   ```python
   # Already implemented with @st.cache_resource
   ```

2. **Optimize database loading**:
   ```python
   # Use smaller database for faster loading
   # Current: 68 foods (optimized)
   ```

3. **Configure memory limits**:
   ```bash
   # For Docker
   docker run -m 512m nutrition-analyzer
   ```

## 🔒 Security Considerations

### API Keys
- Never commit API keys to version control
- Use environment variables or secrets management
- Rotate keys regularly

### Data Privacy
- No user data is stored permanently
- Session data is cleared on browser close
- NHANES data is anonymized population statistics

### Network Security
- Use HTTPS in production
- Configure firewall rules
- Regular security updates

## 📊 Monitoring

### Health Checks
```bash
# Check if app is running
curl http://localhost:8501/_stcore/health

# Check specific functionality
python test_installation.py
```

### Logging
```python
# Enable debug logging in .env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

### Performance Metrics
- Response time: < 2 seconds for typical queries
- Memory usage: ~200MB baseline
- CPU usage: Low (mostly I/O bound)

## 🚨 Troubleshooting

### Common Issues

**Port already in use**:
```bash
# Kill existing Streamlit processes
pkill -f streamlit
# Or use different port
streamlit run app.py --server.port=8502
```

**Module not found**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Database errors**:
```bash
# Verify data files exist
ls -la data/
# Re-download if necessary
```

**Memory issues**:
```bash
# Clear Streamlit cache
streamlit cache clear
```

### Performance Issues

**Slow food matching**:
- Check database size (should be ~68 foods)
- Verify text preprocessing efficiency
- Monitor regex performance

**AI timeouts**:
- Check OpenAI API key validity
- Verify internet connection
- Use fallback mode if needed

## 📈 Scaling

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use session affinity for user state
- Consider Redis for shared caching

### Database Optimization
- Current database is optimized for speed
- Consider PostgreSQL for larger datasets
- Implement database connection pooling

### CDN Integration
- Serve static assets via CDN
- Cache nutrition guidelines
- Optimize image delivery

---

**Need help?** Check the main README.md or create an issue in the repository.