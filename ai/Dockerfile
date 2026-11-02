FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr ffmpeg libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY ai/requirements-runtime.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY ai/ /app/ai/
COPY results/ /app/results/
CMD ["python","-m","uvicorn","service:app","--app-dir","ai","--host","0.0.0.0","--port","8091"]
