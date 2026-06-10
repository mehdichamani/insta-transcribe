FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install CPU-only PyTorch to keep image size minimal
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install application dependencies (Added deep-translator)
RUN pip install --no-cache-dir yt-dlp deep-translator git+https://github.com/openai/whisper.git

WORKDIR /app

COPY transcribe_reel.py .

ENTRYPOINT ["python", "transcribe_reel.py"]