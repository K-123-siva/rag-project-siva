# 🚀 Quick Start Guide

## Prerequisites

1. **Python 3.10+** installed
2. **Ollama** installed and running with llama3.2:3b model
3. Your **PDF files** ready to upload

## Step 1: Verify Ollama Setup

```bash
# Check if Ollama is installed
ollama --version

# Check installed models
ollama list

# If llama3.2:3b is not installed:
ollama pull llama3.2:3b

# Start Ollama (if not running)
ollama serve
```

## Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

## Step 3: Test Your PDF (Optional but Recommended)

Before running the app, test if your PDF can be properly extracted:

```bash
python test_extraction.py path/to/your.pdf
```

**Expected output:**
```
✅ Loaded X pages
📄 Page 1:
   - Characters: 1234
   - Preview: <actual text from your PDF>
...
✅ SUCCESS: All pages have text content!
```

**If you see:**
```
❌ FAILED: No text content found!
```
Your PDF is likely scanned/image-based and won't work without OCR.

## Step 4: Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Step 5: Upload and Process PDF

1. Click **"Browse files"** in the sidebar
2. Select your PDF (up to 3 files, 300 pages each)
3. Click **"Process PDFs"**
4. Wait for **"✅ PDFs processed successfully!"**

## Step 6: Ask Questions

Try these test questions based on your PDF type:

### For Linux Commands PDF:
```
1. What are the top 10 Linux commands?
2. List all the commands mentioned in the document
3. What does the cd command do?
4. Explain the grep command
```

### For Any PDF:
```
1. Summarize this document
2. List the main topics covered
3. What are the key points?
4. Extract all important information
```

## 🔍 How to Check If It's Working

### ✅ Good Signs:
- Logs show: `"Page 1 content preview: <actual text>"`
- Logs show: `"Successfully extracted X valid pages"`
- Answers contain specific info from YOUR PDF
- Lists match what's actually in the document

### ❌ Bad Signs:
- Logs show: `"No text content found"`
- Logs show: `"Creating fallback content"`
- Answers are generic (not from your PDF)
- System gives allotment info for non-allotment PDFs

## 🐛 Troubleshooting

### Problem: "No text content found"
**Solution**: Your PDF is likely scanned/image-based. Try:
1. Use a different PDF with selectable text
2. Use OCR tools to convert the PDF first
3. Test with `test_extraction.py` to verify

### Problem: Ollama errors
**Solution**: 
```bash
# Check if Ollama is running
ollama list

# If not, start it
ollama serve

# Make sure you have the model
ollama pull llama3.2:3b
```

### Problem: Import errors
**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Problem: Wrong/generic answers
**Check**:
1. Terminal logs - is actual content being extracted?
2. Look for "Content preview" in logs
3. Verify Ollama is responding: `ollama run llama3.2:3b "test"`

## 📋 Terminal Output to Expect

### During Upload:
```
INFO - Processing PDF: /path/to/file.pdf
INFO - Loaded 5 pages from PDF
INFO - Page 1 content preview: Top 10 Linux Commands...
INFO - ✅ Successfully extracted 5 valid pages
INFO - Created 12 text chunks
INFO - Sample chunk preview: Top 10 Linux Commands...
INFO - ✅ Vectorstore created successfully!
```

### During Question:
```
INFO - 🔍 Processing question: What are the top 10 Linux commands?
INFO - Retrieved 8 document chunks for context
INFO - Context preview: [Source 1 - Page 0]...
INFO - ✅ Generated answer (length: 450 chars)
INFO - Answer preview: Based on the document, here are...
```

## 💡 Pro Tips

1. **Always check terminal output** - It shows exactly what's happening
2. **Test PDFs first** - Use `test_extraction.py` to verify PDFs work
3. **Start simple** - Ask "Summarize this document" first
4. **Be specific** - "List all commands" works better than "tell me about it"
5. **Watch the logs** - They reveal where issues occur

## 📚 Additional Resources

- `TESTING_GUIDE.md` - Comprehensive testing instructions
- `IMPROVEMENTS.md` - Technical details of what was improved
- `deploy_guide.md` - Deployment instructions for Streamlit Cloud

## 🎯 Success Criteria

Your system is working correctly when:
- ✅ PDFs extract actual text (visible in logs)
- ✅ Questions get answered from YOUR PDF content
- ✅ Lists are extracted accurately
- ✅ Specific information is cited/quoted
- ✅ System says "not available" when info isn't in the PDF

## 🔄 Reset System

If you need to start fresh:
1. Click **"🗑️ Clear All Context"** in the sidebar
2. Or restart the Streamlit app: `Ctrl+C` then `streamlit run app.py`

## ❓ Need Help?

If you're still having issues:
1. Check the terminal logs during upload and question
2. Run `test_extraction.py` on your PDF
3. Verify Ollama is running: `ollama list`
4. Check `TESTING_GUIDE.md` for detailed debugging steps

---

**Ready to go!** 🚀 Just run `streamlit run app.py` and start asking questions about your PDFs!
