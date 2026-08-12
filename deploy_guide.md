# 🚀 Deployment Guide for NeuroQuery RAG

## 📋 Deployment Options

### Option 1: Streamlit Cloud (Free & Easy)

#### 1. Prepare for Cloud Deployment
```bash
# Set deployment mode for cloud
echo "DEPLOYMENT_MODE=cloud" > .env
```

#### 2. Push to GitHub
```bash
git init
git add .
git commit -m "Initial RAG project setup"
git branch -M main
git remote add origin https://github.com/yourusername/neuroquery-rag.git
git push -u origin main
```

#### 3. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file: `streamlit_app.py`
6. Click "Deploy"

#### 4. Environment Variables (if needed)
- Add `DEPLOYMENT_MODE=cloud` in Streamlit Cloud settings

---

### Option 2: Heroku Deployment

#### 1. Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

#### 2. Create Heroku App
```bash
heroku create your-rag-app-name
heroku config:set DEPLOYMENT_MODE=cloud
```

#### 3. Create Procfile
```bash
echo "web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile
```

#### 4. Deploy
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

---

### Option 3: Railway Deployment

#### 1. Connect to Railway
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"

#### 2. Environment Variables
Set in Railway dashboard:
- `DEPLOYMENT_MODE=cloud`

#### 3. Railway will auto-deploy from your GitHub repo

---

### Option 4: Docker Deployment (VPS/Cloud)

#### 1. Build Docker Image
```bash
docker build -t neuroquery-rag .
```

#### 2. Run Container
```bash
docker run -p 8501:8501 -e DEPLOYMENT_MODE=cloud neuroquery-rag
```

#### 3. For Production (with Docker Compose)
```yaml
version: '3.8'
services:
  rag-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DEPLOYMENT_MODE=cloud
    volumes:
      - ./db:/app/db
      - ./logs:/app/logs
```

---

## 🔧 Configuration for Different Environments

### Local Development (with Ollama)
```bash
echo "DEPLOYMENT_MODE=local" > .env
streamlit run streamlit_app.py
```

### Cloud Deployment (HuggingFace models)
```bash
echo "DEPLOYMENT_MODE=cloud" > .env
streamlit run streamlit_app.py
```

---

## 🎯 Quick Start - Streamlit Cloud (Recommended)

1. **Fork/Clone this repo**
2. **Set cloud mode**: `echo "DEPLOYMENT_MODE=cloud" > .env`
3. **Push to your GitHub**
4. **Deploy on Streamlit Cloud** using your GitHub repo
5. **Test with the example PDF**

Your app will be live at: `https://your-app-name.streamlit.app`

---

## 📝 Testing Your Deployment

Once deployed, test with this question:
**"What are the key statistical concepts explained in this document? Please provide definitions and examples for each concept mentioned."**

---

## 🐛 Troubleshooting

### Common Issues:
1. **Memory errors**: Reduce `MAX_TOKENS` in config.py
2. **Model loading fails**: App will fallback to GPT-2
3. **Slow responses**: Normal for free cloud models

### Performance Tips:
- Use smaller PDFs for demo
- Keep questions focused and specific
- Cloud models are slower but work without API keys

---

## 🎉 Success! 
Your RAG application is now live and accessible to anyone with the URL!