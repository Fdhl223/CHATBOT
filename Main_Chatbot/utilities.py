# =========================================================
# UTILITIES & CONFIGURATION
# =========================================================

import requests

# API Configuration
PRIMARY_API_KEY = "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"
BACKUP_API_KEY = "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"
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
