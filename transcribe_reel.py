import os
import sys
import re
import yt_dlp
import whisper
from whisper.utils import get_writer
from deep_translator import GoogleTranslator

def extract_reel_id(url):
    match = re.search(r'/(?:reel|p)/([A-Za-z0-9_-]+)', url)
    return match.group(1) if match else "insta_clip"

def translate_srt_to_persian(en_srt_path, fa_srt_path):
    print("Translating subtitles to Persian (فارسی)...")
    translator = GoogleTranslator(source='en', target='fa')
    
    with open(en_srt_path, 'r', encoding='utf-8') as f_in, open(fa_srt_path, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            clean_line = line.strip()
            
            if not clean_line or clean_line.isdigit() or "-->" in clean_line:
                f_out.write(line)
            else:
                try:
                    translated_text = translator.translate(clean_line)
                    f_out.write(f"{translated_text}\n")
                except Exception as e:
                    print(f"Warning: Line translation failed: {e}")
                    f_out.write(line)

def download_and_transcribe(url, output_dir="/app/output"):
    clip_id = extract_reel_id(url)
    base_path = os.path.join(output_dir, clip_id)
    
    video_path = f"{base_path}.mp4"
    audio_path = f"{base_path}_audio.mp3"
    en_srt_path = f"{base_path}.srt"
    fa_srt_path = f"{base_path}.fa.srt"
    
    ydl_opts_video = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': base_path, 
        'quiet': True,
        'no_warnings': True
    }
    
    ydl_opts_audio = {
        'format': 'bestaudio/best',
        'outtmpl': f"{base_path}_audio.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True
    }
    
    print(f"Downloading clip to: {video_path}")
    with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
        ydl.download([url])
        
    print("Extracting audio stream for Whisper engine...")
    with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
        ydl.download([url])
        
    print("Loading Whisper AI model (base)...")
    model = whisper.load_model("base")
    
    print("Transcribing core tracks...")
    result = model.transcribe(audio_path, task="transcribe", language="en")
    
    print(f"Writing base English track: {clip_id}.srt")
    writer = get_writer("srt", output_dir)
    writer(result, clip_id, {})
    
    translate_srt_to_persian(en_srt_path, fa_srt_path)
    print(f"Writing Persian track: {clip_id}.fa.srt")
    
    if os.path.exists(audio_path):
        os.remove(audio_path)
    print("Process Complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_reel.py <video_url>")
        sys.exit(1)
        
    video_url = sys.argv[1]
    
    try:
        download_and_transcribe(video_url)
    except Exception as e:
        print(f"\nAn error occurred: {e}")