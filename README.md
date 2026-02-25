
# AI Research Portal – Financial Statement Extraction Tool

## Overview
Structured AI-powered research assistant for extracting Income Statement data from annual reports.

---

## Architecture

### 1. UI Layer (Streamlit)
- Responsive Python-based GUI
- Drag-and-drop PDF upload
- Interactive data preview
- Excel export button

### 2. Document Processing Layer
- Text extraction via pdfplumber
- Currency and unit detection using regex
- Deterministic numeric extraction (prevents hallucination)

### 3. AI Layer (OpenRouter)
- Model: mistralai/mistral-7b-instruct
- LLM used only for identifying income statement rows
- Temperature = 0 for deterministic output

### 4. Output Layer
- Structured Pandas DataFrame
- Excel generation (Income Statement + Metadata sheets)

---

## Key Design Decisions
- LLM never generates financial numbers
- Regex ensures reliable numeric extraction
- 12,000 character token safety limit
- Missing data remains blank (analyst-visible)

---

## 🚀 How to Run Locally

### 1. Pre-requisites
Ensure you have Python installed (3.8+ recommended).

### 2. Setup (First time only)
Open your terminal in the project folder and run:
```bash
pip install -r requirements.txt
```

### 3. API Key Configuration
Create a file named `.env` in the root directory and add your key:
```text
OPENROUTER_API_KEY=your_actual_key_here
```
*(I have already created this file for you with your provided key!)*

### 4. Launch the App
Run the following command:
```bash
streamlit run app.py
```
The app will automatically open in your browser at `http://localhost:8501`.

---

## 💡 Limitations
- No OCR for scanned PDFs (text-based PDFs only).
- Token limit: 12,000 characters from the document are sent to the AI.
