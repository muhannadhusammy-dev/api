# Start the new Python + LLM dashboard

The new `llm_streamlit/` folder adds a lightweight Streamlit/ML/LLM decision-support app to the supplied TajerOS project. It can be run independently without .NET or Node.

```powershell
cd llm_streamlit
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
# Edit .env and set your real OPENAI_API_KEY
python -m streamlit run app.py
```

The original .NET/React/FastAPI project has NOT been replaced and retains its original instructions in `README.md`.

See `llm_streamlit/README.md` for data requirements, validation methodology, privacy notes and current limitations.
