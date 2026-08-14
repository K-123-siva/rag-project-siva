# How to Configure Streamlit Cloud to Use app.py

## The Problem

Streamlit Cloud by default looks for `streamlit_app.py` as the main entry point.
Your app uses `app.py` instead, causing the error:
```
❗️ The main module file does not exist: /mount/src/rag-project-siva/streamlit_app.py
```

## Solution: Configure Main File Path

Follow these steps to tell Streamlit Cloud to use `app.py`:

### Step 1: Go to Streamlit Cloud Dashboard
1. Visit: **https://share.streamlit.io/**
2. Log in with your GitHub account

### Step 2: Find Your App
1. Look for your app: **rag-project-siva** or **neuroquery-rag**
2. Click on it

### Step 3: Open App Settings
1. Click the **3 dots menu** (⋮) on your app
2. Select **"Settings"**

### Step 4: Change Main File Path
1. In the settings panel, find **"Main file path"**
2. Change from: `streamlit_app.py`
3. Change to: `app.py`
4. Click **"Save"**

### Step 5: Reboot the App
1. Click the **3 dots menu** (⋮) again
2. Select **"Reboot app"**
3. Wait 30-60 seconds for the app to restart

## Alternative: Settings via Advanced Settings

If you don't see "Main file path" in basic settings:

1. Click **"⋮"** → **"Settings"**
2. Go to **"Advanced settings"** tab
3. Under **"Main file path"**, enter: `app.py`
4. Click **"Save"**
5. Reboot the app

## Visual Guide

```
Streamlit Cloud Dashboard
  └─ Your Apps
      └─ rag-project-siva
          └─ [⋮] Menu
              ├─ Settings
              │   └─ Main file path: app.py  ← Change here
              │   └─ [Save]
              └─ Reboot app  ← Click after saving
```

## Verify It Works

After rebooting, check the logs:

**Good logs:**
```
✅ Cloning repository
✅ Installing dependencies
✅ Starting app from app.py
✅ App is running
```

**Bad logs (if not configured):**
```
❗️ Main module does not exist
❗️ The main module file does not exist: streamlit_app.py
```

## Alternative Solution: Rename app.py

If you prefer not to change settings, you can rename the file:

```bash
# In your local repository
git mv app.py streamlit_app.py
git commit -m "Rename app.py to streamlit_app.py for Streamlit Cloud"
git push
```

But this is **NOT recommended** because:
- `app.py` is the standard Python application name
- You'd need to update documentation
- Less flexible for other deployment platforms

## Current Status

- ✅ `streamlit_app.py` deleted from repository
- ✅ Changes pushed to GitHub
- ⏳ **YOU NEED TO:** Configure Streamlit Cloud to use `app.py`

## Quick Links

- **Streamlit Cloud Dashboard:** https://share.streamlit.io/
- **Your Live App:** https://neuroquery-rag.streamlit.app/
- **GitHub Repo:** https://github.com/K-123-siva/rag-project-siva

## After Configuration

Once you configure it correctly:

1. ✅ App will start successfully
2. ✅ You can upload PDFs
3. ✅ Enhanced extraction with pdfplumber will work
4. ✅ Your EAPCET PDF will extract correctly

## Need Help?

If you still see errors after configuration:

1. Check logs in Streamlit Cloud
2. Make sure you clicked "Save" AND "Reboot"
3. Wait 1-2 minutes for full reboot
4. Clear browser cache and refresh

## Summary

**What you need to do NOW:**
1. Go to https://share.streamlit.io/
2. Click your app → Settings
3. Change "Main file path" to `app.py`
4. Save and Reboot

That's it! 🎉
