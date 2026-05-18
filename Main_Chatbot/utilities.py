# =========================================================
# UTILITIES & CONFIGURATION
# =========================================================

import requests
import streamlit as st

# API Configuration
PRIMARY_API_KEY = st.secrets["PRIMARY_API_KEY"]
BACKUP_API_KEY = st.secrets["BACKUP_API_KEY"]

MODEL_NAME = "openai/gpt-oss-120b:free"

# LLM Request Payload
def create_llm_payload(prompt):
    """Create payload for LLM API request"""
    return {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": """
                Kamu adalah AI Data Assistant yang ramah dan profesional.
                Tugasmu membantu user membaca, mencari, mengedit, dan menganalisis data.
                Berikan respon yang jelas, ringkas, dan membantu.
                """
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

# Build full prompt with data context
def build_prompt_with_context(user_input, df=None):
    """Build full prompt with dataframe context if available"""
    if df is not None:
        df_preview = df.head(50).to_string()
        full_prompt = f"""
DATASET PREVIEW:
{df_preview}

PERTANYAAN USER:
{user_input}

Silakan analisis data dan berikan jawaban yang jelas dan berguna.
"""
    else:
        full_prompt = f"""
CATATAN: User belum upload data apapun.

PERTANYAAN USER:
{user_input}

Berikan respon yang membantu. Jika pertanyaan terkait data, ingatkan user untuk upload data terlebih dahulu.
"""
    return full_prompt
