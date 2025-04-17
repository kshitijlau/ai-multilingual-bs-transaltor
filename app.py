import streamlit as st
import pandas as pd
import openai
from io import BytesIO
import time

# Streamlit config
st.set_page_config(page_title="Multilingual Translator", layout="wide")
st.title("🌍 AI-Powered Multilingual Simulation Translator")

# Azure OpenAI credentials via Streamlit secrets
openai.api_type = "azure"
openai.api_key = st.secrets["AZURE_OPENAI_API_KEY"]
openai.api_base = st.secrets["AZURE_OPENAI_ENDPOINT"]
openai.api_version = "2024-08-01-preview"

DEPLOYMENT_NAME = st.secrets["AZURE_DEPLOYMENT_NAME"]

# Upload Excel
uploaded_file = st.file_uploader("Upload the latest Excel file with language-specific prompts", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Show preview
    st.subheader("📄 File Preview")
    st.dataframe(df.head(10))

    # Ask which languages to generate
    st.subheader("🌐 Choose languages to translate")
    langs = ["Italian", "German", "French"]
    selected_langs = st.multiselect("Select target languages", langs, default=langs)

    if st.button("⚙️ Run Translations"):
        with st.spinner("Running translations, please wait..."):
            for lang in selected_langs:
                col_name = f"Prompt - English to {lang}"
                result_col = f"Translation - {lang}"
                df[result_col] = ""

                for i, row in df.iterrows():
                    prompt = row[col_name]
                    if pd.notna(prompt):
                        try:
                            response = openai.chat.completions.create(
                                model=DEPLOYMENT_NAME,
                                messages=[
                                    {"role": "system", "content": "You are a culturally-aware professional business content translator."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.5,
                                max_tokens=1000
                            )
                            df.at[i, result_col] = response.choices[0].message.content.strip()
                            time.sleep(1.5)  # prevent rate limits
                        except Exception as e:
                            df.at[i, result_col] = f"[ERROR] {str(e)}"

            st.success("✅ Translations completed!")
            st.dataframe(df.head(10))

            # Download
            buffer = BytesIO()
            df.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)

            st.download_button(
                label="📥 Download Translated Excel",
                data=buffer,
                file_name="translated_simulation.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
