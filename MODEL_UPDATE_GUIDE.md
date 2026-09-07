# Groq Model Update Guide

## ⚠️ Important: Model Deprecation Notice

**Date:** June 17, 2026  
**Affected Models:**
- `llama-3.3-70b-versatile` → Moved to **Enterprise tier only**
- `llama-3.1-8b-instant` → **Deprecated**

## What Changed?

As of **June 17, 2026**, Groq has updated their model lineup:

### ❌ No Longer Available (Free/Developer Tier)
- `llama-3.3-70b-versatile` - Now requires Enterprise plan
- `llama-3.1-8b-instant` - Fully deprecated

### ✅ Current Production Models (Developer Tier)

| Model ID | Speed | Price (per 1M tokens) | Context | Best For |
|----------|-------|----------------------|---------|----------|
| `openai/gpt-oss-120b` | 500 t/s | $0.15 in / $0.60 out | 131K | Balanced performance |
| `openai/gpt-oss-20b` | 1000 t/s | $0.075 in / $0.30 out | 131K | Speed & cost efficiency |

## How This Project Was Updated

### 1. Updated `src/llm_chain.py`
- Changed default model from `llama-3.3-70b-versatile` to `openai/gpt-oss-120b`
- Added `MODEL_INFO` dictionary to track model availability
- Added `check_model_availability()` function to validate models before use
- Added fallback to `openai/gpt-oss-20b` if primary model fails
- Enhanced error messages with deprecation warnings

### 2. Updated `streamlit_app.py`
- Added "Model Status" expander in sidebar showing current and deprecated models
- Added specific error handling for model deprecation errors
- Improved user-facing error messages

### 3. Created Utilities
- `check_groq_models.py` - Script to check which models are available for your API key
- This documentation file

## How to Check Your Model Availability

Run the model checker script:

```bash
python check_groq_models.py
```

This will:
- List all models available with your API key
- Identify deprecated models
- Show recommended models for RAG applications

## If You See "Model Not Available" Errors

### Symptom
```
Error: Model 'llama-3.3-70b-versatile' is not available
```

### Solution
1. Pull the latest code updates (this has been fixed)
2. Or manually update `src/llm_chain.py`:
   ```python
   model="openai/gpt-oss-120b"  # or "openai/gpt-oss-20b"
   ```

## Model Selection Guide

### For Most Users → `openai/gpt-oss-120b`
- **Best choice** for balanced performance
- 120B parameters for better accuracy
- 500 tokens/sec is plenty fast
- Reasonable pricing

### For High Volume → `openai/gpt-oss-20b`
- **Fastest** option (1000 t/s)
- **Cheapest** option (half the price)
- Still very capable for RAG tasks
- Great for demos and high-traffic apps

## Code Changes Made

### Before (deprecated):
```python
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # ❌ No longer available
    temperature=0.1,
    max_tokens=600,
    groq_api_key=os.getenv("GROQ_API_KEY")
)
```

### After (current):
```python
llm = ChatGroq(
    model="openai/gpt-oss-120b",  # ✅ Current production model
    temperature=0.1,
    max_tokens=600,
    groq_api_key=os.getenv("GROQ_API_KEY")
)
```

## Testing Your Setup

1. **Check your API key is valid:**
   ```bash
   python check_groq_models.py
   ```

2. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Look for the model status in sidebar:**
   - Expand "🤖 Model Status" in the sidebar
   - Should show: `GPT OSS 120B - Status: ✓ Active`

4. **Upload a PDF and ask a question:**
   - If it works → ✅ Successfully using current model
   - If error → Check logs in `logs/app.log`

## Where to Get Latest Model Info

- **Official Docs:** https://console.groq.com/docs/models
- **Deprecation Policy:** https://console.groq.com/docs/models (see "Deprecated models" section)
- **API Endpoint:** `https://api.groq.com/openai/v1/models`

## Enterprise Users

If you have an Enterprise contract with Groq:
- You can still use `llama-3.3-70b-versatile`
- You can still use `llama-3.1-8b-instant`
- Contact Groq support for Enterprise-specific model access

To use Enterprise models, update `src/llm_chain.py`:
```python
model="llama-3.3-70b-versatile"  # Only works with Enterprise API keys
```

## Monitoring Future Deprecations

The updated `llm_chain.py` includes a `MODEL_INFO` dictionary that tracks:
- Model availability status
- Deprecation dates
- Replacement recommendations

Update this dictionary when Groq announces new deprecations.

## Questions?

- **Check logs:** `logs/app.log` for detailed error messages
- **Run checker:** `python check_groq_models.py`
- **Groq Console:** https://console.groq.com/
- **Groq Docs:** https://console.groq.com/docs/models

## Summary

✅ **What was done:**
- Updated to current production model (`openai/gpt-oss-120b`)
- Added model availability tracking
- Added deprecation warnings
- Created utilities to check model status
- Improved error messages

🚀 **Result:**
- App now uses currently available models
- Users see clear warnings about deprecated models
- Easy to update when future models change
- Better monitoring and debugging

---

**Last Updated:** September 5, 2026  
**Current Model:** openai/gpt-oss-120b  
**Status:** ✅ Active and tested
