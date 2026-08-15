# 🚀 Deployment Guide - Groq-Powered RAG System

## ✅ **System Now Uses Groq API** (Cloud-Ready!)

Your RAG system now uses **Groq API** which works perfectly on Streamlit Cloud!

---

## 📋 **Prerequisites**

1. **Groq API Key** (FREE!)
   - Go to: https://console.groq.com/keys
   - Create a free account
   - Generate your API key

---

## 🏠 **Local Testing**

### Step 1: Set up your API key

Edit `.env` file:
```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run locally
```bash
streamlit run app.py
```

---

## ☁️ **Deploy to Streamlit Cloud**

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment with Groq"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your repository
4. Set main file: `app.py`
5. **IMPORTANT:** Add your secrets:
   - Click "Advanced settings"
   - In "Secrets" section, add:
   ```toml
   GROQ_API_KEY = "your_actual_groq_api_key_here"
   ```
6. Click "Deploy"!

---

## ✅ **Why Groq Works for Deployment**

| Feature | Ollama (Old) | Groq (New) |
|---------|-------------|------------|
| **Cloud Deploy** | ❌ Requires local server | ✅ Works everywhere |
| **Speed** | ~30 tokens/sec | ⚡ 500+ tokens/sec |
| **Cost** | Free but local only | Free tier + fast |
| **Setup** | Complex installation | API key only |

---

## 🎯 **Testing Your Deployment**

After deployment, test with these questions:

1. Upload the Linux PDF
2. Ask: "What are the top 10 Linux commands?"
3. Ask: "Explain the Linux directory system"

Expected behavior:
- ✅ Fast responses (1-2 seconds)
- ✅ Accurate extraction from your PDF
- ✅ Proper context retrieval

---

## 🐛 **Troubleshooting**

### Error: "GROQ_API_KEY not found"
**Solution:** Make sure you added the secret in Streamlit Cloud settings

### Error: "Rate limit exceeded"
**Solution:** Groq free tier has limits. Wait or upgrade to paid tier.

### Slow responses
**Solution:** Groq is very fast. If slow, check your embeddings processing.

---

## 📊 **Performance**

With Groq API:
- **Processing Speed:** ⚡ 500+ tokens/second
- **Response Time:** 1-3 seconds
- **Context Window:** Up to 8K tokens
- **Cost:** FREE tier available, then $0.10 per 1M tokens

---

## 🎉 **You're Ready!**

Your app is now **100% cloud-ready** and will work perfectly on Streamlit Cloud!
