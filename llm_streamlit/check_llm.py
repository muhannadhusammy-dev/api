import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

base = Path(__file__).resolve().parent
load_dotenv(base / ".env")
key = os.getenv("OPENAI_API_KEY", "").strip()
model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()

if not key:
    print("OPENAI_API_KEY is missing. Create a .env file with your API key.")
else:
    try:
        client = OpenAI(api_key=key, timeout=30, max_retries=1)
        result = client.responses.create(
            model=model,
            input="Reply with: TajerOS LLM connection is working.",
            max_output_tokens=100,
            store=False,
        )
        print(result.output_text)
    except Exception as error:
        print("Connection failed:", type(error).__name__, str(error)[:250])
