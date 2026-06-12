Insta-Transcribe (Bot & CLI)

A unified Docker Compose setup that runs a 24/7 Telegram bot AND a local CLI tool to extract and translate Instagram Reels to Persian.

The heavy AI models are downloaded once and shared between both tools using a persistent Docker volume.

Quick Start (Linux / Windows 11)

Create a .env file in the same directory by renaming .env.example.

Open it in nvim or VSCode and paste your Telegram Bot token inside:

TELEGRAM_BOT_TOKEN=123456789:ABCDEF...


To Run the 24/7 Telegram Bot

Open PowerShell (WorkPC) or your terminal (HomePC) and run:

docker compose up -d


The bot will build itself and run silently in the background. Send it an Instagram link on Telegram!

To Run the CLI Tool Locally

You don't need to stop the bot! Run this command to process a link directly on your PC:

docker compose run --rm cli "[https://www.instagram.com/reel/YOUR_LINK/](https://www.instagram.com/reel/YOUR_LINK/)"


The video and .srt files will automatically appear in an output/ folder inside your current directory.