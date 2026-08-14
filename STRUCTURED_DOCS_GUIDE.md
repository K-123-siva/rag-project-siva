# Structured Documents Extraction Guide

## Problem: Why Some PDFs Don't Extract Well

Your EAPCET Allotment PDF (and similar documents) contain:
- **Tables and forms** with structured layouts
- **Multiple columns** 
- **Headers and footers**
- **Form fields** with labels and values

Standard PDF text extraction often fails because:
1. Text order gets scrambled in multi-column layouts
2. Table structures are lost
3. Form fields are separated from their labels
4. Whitespace and positioning info is ignored

## Solution: Enhanced Extraction

We now use **3-tier extraction**:

### Method 1: PDFPlumber (BEST)
- ✅ Handles tables correctly
- ✅ Preserves structure
- ✅ Extracts form fields with positioning
- ✅ Maintains relationships between labels and values

### Method 2: pypdf (Fallback)
- ✅ Good for text-heavy documents
- ⚠️ May lose structure

### Method 3: PyPDFLoader (Last Resort)
- ✅ Basic text extraction
- ⚠️ Often loses structure

## Testing Your EAPCET PDF

Your allotment document contains:

```
Hall Ticket No: 260869010051
Candidate Name: KOMTHREDDY LASYA REDDY
Father's Name: KOMTHREDDY RAVI SEKHAR REDDY
Rank: 5929
Gender/Caste: FEMALE/OC
Fee-Reimb/Region: YES/SVU

College: ANNAMACHARYA UNIVERSITY (AITSPU), RAJAMPETA, KADAPA
Course: CSE (ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING) (CSM)
Category: OC_GIRLS_UR
Tuition Fee: Rs. 60000/-
```

### Test Questions:

1. **Specific field extraction:**
   - "What is the hall ticket number?"
   - "What is the candidate name?"
   - "What rank did the candidate get?"
   - "Which college was allotted?"

2. **Course information:**
   - "What course was allotted?"
   - "What is the tuition fee?"
   - "What category was the seat allotted under?"

3. **Instructions extraction:**
   - "What are the instructions for reporting?"
   - "What is the deadline for reporting?"
   - "What documents are required?"

## Installation

Install the enhanced extraction library:

```bash
pip install pdfplumber>=0.10.0
```

Or update from requirements.txt:

```bash
pip install -r requirements.txt
```

## Debugging Tips

### Check Extraction Logs

Look for these log messages:

```
✅ pdfplumber extracted 1 pages
📊 TOTAL: 1 document pages extracted  
📄 Created X text chunks from 1 document pages
```

### If Extraction Fails:

1. **Check PDF type:**
   - Is it a scanned image? → OCR required (not supported yet)
   - Is it password protected? → Remove password first
   - Is it a form PDF? → Should work with pdfplumber

2. **Try manual extraction test:**
   ```python
   import pdfplumber
   with pdfplumber.open("your_file.pdf") as pdf:
       page = pdf.pages[0]
       print(page.extract_text())
   ```

3. **Check logs:**
   - Look at `logs/app.log` for detailed extraction info
   - Search for "Page 1 preview:" to see what was extracted

## Expected Behavior

### Good Extraction:
```
Page 1 preview: Hall Ticket No: 260869010051 | Rank: 5929 
Candidate Name: KOMTHREDDY LASYA REDDY | Gender / Caste: FEMALE / OC
...
```

### Poor Extraction:
```
Page 1 preview: 260869010051 KOMTHREDDY LASYA REDDY 5929
```

## Troubleshooting

### Issue: "Information not available in document"

**Cause:** Text was extracted but chunking split related info

**Solution:** 
- Reduce chunk size in `config.py`
- Increase chunk overlap
- Use MMR retrieval (already enabled)

### Issue: Scrambled text order

**Cause:** PyPDFLoader used instead of pdfplumber

**Solution:**
- Ensure `pdfplumber` is installed
- Check logs for "Trying pdfplumber extraction"
- If missing, install: `pip install pdfplumber`

### Issue: Table data missing

**Cause:** Text-only extraction, tables not detected

**Solution:**
- pdfplumber automatically extracts tables
- Check logs for "TABLES:" section in extracted content

## Advanced: Chunk Size Configuration

Edit `src/config.py`:

```python
# For structured documents like forms/allotments
CHUNK_SIZE = 800  # Smaller chunks keep fields together
CHUNK_OVERLAP = 150  # More overlap preserves relationships

# For long documents like research papers
CHUNK_SIZE = 1500  # Larger chunks for context
CHUNK_OVERLAP = 200
```

## Next Steps

1. ✅ Install pdfplumber
2. ✅ Update code (already done)
3. 🧪 Test with your EAPCET PDF
4. 📊 Check logs for extraction quality
5. 🎯 Adjust chunk size if needed

## Questions to Test With Your PDF

Try these after uploading your EAPCET allotment:

1. "What is my hall ticket number?"
2. "Which college am I allotted to?"
3. "What is the course name?"
4. "What is my rank?"
5. "How much is the tuition fee?"
6. "What are the reporting instructions?"
7. "What is the deadline for reporting?"
8. "What category is my seat under?"
9. "List all the personal details in the document"
10. "Summarize the allotment details"
