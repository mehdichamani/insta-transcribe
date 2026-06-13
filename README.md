# Insta-Transcribe Bot

A Docker Compose setup that runs a 24/7 Telegram bot to extract and translate Instagram Reels to Persian.

The heavy Whisper AI model is downloaded once and cached via a persistent Docker volume.

## Quick Start

1. Create a `.env` file by copying `.env.example` and paste your Telegram Bot token inside:

```
TELEGRAM_BOT_TOKEN=123456789:ABCDEF...
```

2. Run the bot:

```bash
docker compose up -d
```

The bot will build itself and run silently in the background. Send it an Instagram link on Telegram!