FROM python:3.12-slim

# Install system dependencies needed for audio/video muxing and git
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

# 3. Copy only the bot script
COPY telegram_bot.py .

CMD ["python", "telegram_bot.py"]