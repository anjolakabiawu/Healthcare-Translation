FROM python:3.11-slim

# System deps for audio handling (faster-whisper / libsndfile).
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Run as a non-root user. Hugging Face Spaces runs containers as UID 1000,
# so model/cache writes must target a directory this user owns.
RUN useradd -m -u 1000 appuser
ENV HOME=/home/appuser \
    HF_HOME=/home/appuser/.cache/huggingface \
    PATH=/home/appuser/.local/bin:$PATH

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R appuser:appuser /app
USER appuser

# Hugging Face Spaces expects the app on port 7860; $PORT is honoured
# everywhere else (Render/Railway inject their own). Falls back to 7860.
ENV PORT=7860
EXPOSE 7860

# One worker: each worker loads its own copy of the ML models into RAM.
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 180 run:app
