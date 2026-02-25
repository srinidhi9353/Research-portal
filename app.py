
import streamlit as st
import pdfplumber
import pandas as pd
import re
import requests
import os
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Research Portal - Financial Extraction",
    layout="wide",
    page_icon="📊"
)

st.markdown("""
<style>
.main { padding: 2rem; }
.stButton>button {
    width: 100%;
    border-radius: 8px;
    height: 3em;
    font-size: 16px;
}
.upload-box {
    border: 2px dashed #4CAF50;
    padding: 2rem;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 AI Research Tool – Financial Statement Extraction")
st.markdown("Upload an annual report PDF to extract structured Income Statement data.")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.warning("⚠️ Add OPENROUTER_API_KEY in Streamlit secrets or environment variables.")
    st.stop()

st.markdown('<div class="upload-box">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Drag & Drop or Select PDF File", type=["pdf"])
st.markdown('</div>', unsafe_allow_html=True)

def call_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a financial analyst extracting income statement rows. Only return rows present in text."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

def extract_currency_units(text):
    currency_match = re.search(r"(USD|INR|\$|₹|EUR)", text)
    unit_match = re.search(r"(millions|thousands|crores|lakhs)", text, re.IGNORECASE)
    return (
        currency_match.group() if currency_match else "Unknown",
        unit_match.group() if unit_match else "Unknown"
    )

def extract_numbers(line):
    pattern = r"\(?\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?\)?"
    return re.findall(pattern, line)

if uploaded_file:
    with st.spinner("Processing document..."):
        with pdfplumber.open(uploaded_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

        currency, units = extract_currency_units(full_text)

        prompt = f"""
        Extract Income Statement line items exactly as written below.
        Do not fabricate numbers.
        Text:
        {full_text[:12000]}
        """

        llm_output = call_openrouter(prompt)

        lines = llm_output.split("\n")
        data = {}

        for line in lines:
            nums = extract_numbers(line)
            if nums:
                name = re.sub(r"[0-9,$()]", "", line).strip()
                data[name] = nums

        df = pd.DataFrame.from_dict(data, orient="index")
        df.reset_index(inplace=True)
        df.rename(columns={"index": "Line Item"}, inplace=True)

    if not df.empty:
        st.success("✅ Extraction Completed")
        st.dataframe(df, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Income Statement", index=False)
            metadata = pd.DataFrame({
                "Field": ["Currency", "Units", "Source File"],
                "Value": [currency, units, uploaded_file.name]
            })
            metadata.to_excel(writer, sheet_name="Metadata", index=False)

        st.download_button(
            label="⬇ Download Excel File",
            data=output.getvalue(),
            file_name="extracted_income_statement.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("No structured income statement data detected.")
