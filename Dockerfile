FROM python:3.12-slim

# Install necessary system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Install PyTorch (CPU ONLY) first to save massive amounts of image size
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 2. Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy application files
COPY telegram_bot.py .
COPY transcribe_reel.py .

# Create the output directory for the CLI tool
RUN mkdir -p /app/output

# Default to running the bot. The docker-compose 'cli' service overrides this.
CMD ["python", "telegram_bot.py"]
