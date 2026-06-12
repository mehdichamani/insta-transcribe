import os
import sys
import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
import whisper
from whisper.utils import get_writer
from deep_translator import GoogleTranslator

# Retrieve Token from environment variables for security
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
    sys.exit(1)

print("Pre-loading Whisper model (base) into memory...")
whisper_model = whisper.load_model("base")
print("Model loaded successfully!")

def extract_reel_id(url):
    match = re.search(r'/(?:reel|p)/([A-Za-z0-9_-]+)', url)
    return match.group(1) if match else "clip"

def translate_srt_to_persian(en_srt_path, fa_srt_path):
    # Changed source to 'auto' so it can translate from ANY language Whisper detected
    translator = GoogleTranslator(source='auto', target='fa')
    with open(en_srt_path, 'r', encoding='utf-8') as f_in, open(fa_srt_path, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            clean_line = line.strip()
            if not clean_line or clean_line.isdigit() or "-->" in clean_line:
                f_out.write(line)
            else:
                try:
                    translated_text = translator.translate(clean_line)
                    f_out.write(f"{translated_text}\n")
                except Exception:
                    f_out.write(line)

def download_clip_sync(url, base_path):
    # Download the best video and audio merged as an mp4
    out_path = f"{base_path}_video.mp4"
    ydl_opts_video = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': out_path,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
        ydl.download([url])
    return out_path

def embed_subtitle_sync(video_path, srt_path, output_mkv):
    import subprocess
    # Use ffmpeg to mux the video and the translated srt into an mkv container
    cmd = [
        'ffmpeg', '-y', 
        '-i', video_path, 
        '-i', srt_path,
        '-c', 'copy',                  # Copy video and audio without quality loss
        '-c:s', 'srt',                 # Subtitle codec
        '-metadata:s:s:0', 'language=per',
        '-metadata:s:s:0', 'title=Persian',
        '-disposition:s:0', 'default', # Make it the default track
        output_mkv
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! Send me any Instagram Reel link. I will auto-detect the language, "
        "translate it to Persian, and send you an MKV video with embedded subtitles!"
    )

async def process_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "instagram.com" not in url:
        await update.message.reply_text("Please send a valid Instagram link.")
        return

    clip_id = extract_reel_id(url)
    work_dir = "/tmp"
    base_path = os.path.join(work_dir, clip_id)
    
    src_srt_path = f"{base_path}.srt"
    fa_srt_path = f"{base_path}.fa.srt"
    final_mkv_path = f"{base_path}_final.mkv"

    status_msg = await update.message.reply_text("⏳ Downloading best quality video...")

    try:
        loop = asyncio.get_event_loop()
        
        # 1. Download Video
        video_path = await loop.run_in_executor(None, download_clip_sync, url, base_path)
        
        # 2. Transcribe (Whisper reads mp4 directly and we removed language="en" so it auto-detects)
        await status_msg.edit_text("🧠 Analyzing audio and auto-detecting language...")
        result = await loop.run_in_executor(
            None, lambda: whisper_model.transcribe(video_path, task="transcribe")
        )
        
        writer = get_writer("srt", work_dir)
        writer(result, clip_id, {})

        # 3. Translate the auto-detected language to Persian
        await status_msg.edit_text("✍️ Translating subtitles to Persian (فارسی)...")
        await loop.run_in_executor(None, translate_srt_to_persian, src_srt_path, fa_srt_path)

        # 4. Embed into MKV
        await status_msg.edit_text("🎬 Embedding Persian subtitles into an MKV container...")
        await loop.run_in_executor(None, embed_subtitle_sync, video_path, fa_srt_path, final_mkv_path)

        # 5. Ship the MKV back to User as a Document
        await status_msg.edit_text("🚀 Uploading uncompressed MKV to Telegram...")
        
        if os.path.exists(final_mkv_path):
            with open(final_mkv_path, "rb") as doc:
                await update.message.reply_document(
                    document=doc, 
                    filename=f"{clip_id}_Persian.mkv", 
                    caption="Here is your clip with embedded Persian subtitles! 🎬"
                )

        # Cleanup all working files
        for p in [video_path, src_srt_path, fa_srt_path, final_mkv_path]:
            if os.path.exists(p):
                os.remove(p)
                
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Failed to process clip: {str(e)}")
        # Try to clean up leftover files on failure
        for p in [f"{base_path}_video.mp4", src_srt_path, fa_srt_path, final_mkv_path]:
            if os.path.exists(p):
                os.remove(p)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_reel))
    
    print("Bot loop started. Waiting for messages...")
    app.run_polling()

if __name__ == "__main__":
    main()
