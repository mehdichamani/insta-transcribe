# Instagram Subtitle Extractor (Cross-Platform via Docker)

A lightweight, localized AI tool using Python, `yt-dlp`, and OpenAI's Whisper `base` model to automatically download Instagram reels and extract matching `.srt` subtitles. Everything runs isolated in Docker to prevent host dependency bloat.

---

## 📂 Project Structure

Ensure your project folder contains the following core files:
* `Dockerfile` (Environment configuration)
* `transcribe_reel.py` (The extraction engine script)
* `README.md` (This guide)

---

## 🛠️ Initial Installation (Build Once)

Open your terminal or PowerShell inside the project directory and run the following command to build the isolated Docker image on either machine:

```bash
docker build -t insta-transcribe .

```

*Note: The initial setup might take a few minutes to fetch the base image, lightweight CPU PyTorch, and Whisper layers. Once cached, runs are near-instantaneous.*

---

## 🚀 Environment Setup & Integration

### 🐟 1. HomePC Setup (ZorinOS + Fish Shell)

To make the execution a seamless single-word command, add this function to your Fish environment configuration.

Run this directly in your Fish shell:

```fish
function transcribe
    if test (count $argv) -lt 1
        echo "Usage: transcribe <instagram_url> [optional_output_path]"
        return 1
    end

    set url $argv[1]
    set out_dir (pwd)
    if test (count $argv) -ge 2
        set out_dir $argv[2]
    end

    # Added a mount point for the root cache directory
    docker run --rm \
      -v "$out_dir:/app/output" \
      -v "$HOME/.cache/whisper:/root/.cache/whisper" \
      insta-transcribe "$url"
end

funcsave transcribe

```

### ⚡ 2. WorkPC Setup (Windows 11 + PowerShell)

To link the command inside your Windows environment, register this function alias inside your PowerShell profile.

1. Open your profile in editor: `notepad $PROFILE` (or create it if prompted).
2. Paste the following block at the bottom and save:

```powershell
function Transcribe-Reel {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Url,
        [Parameter(Mandatory=$false)]
        [string]$OutDir = (Get-Location).Path
    )

    # Ensures a local directory exists for storing the weights file permanently
    $CacheDir = "$env:USERPROFILE\.cache\whisper"
    if (!(Test-Path $CacheDir)) { New-Item -ItemType Directory -Force -Path $CacheDir | Out-Null }

    docker run --rm `
      -v "${OutDir}:/app/output" `
      -v "${CacheDir}:/root/.cache/whisper" `
      insta-transcribe "$Url"

```

3. Reload your shell profile: `. $PROFILE`

---

## 🎮 How to Use

The command works identically across both platforms. Navigate to any folder where you want to store your media and fire away.

### Option A: Save directly to your current working directory

```bash
transcribe "[https://www.instagram.com/reel/DZKlCXtBb0d/](https://www.instagram.com/reel/DZKlCXtBb0d/)"

```

### Option B: Save to a specific custom directory

```bash
# Example for Linux/ZorinOS
transcribe "[https://www.instagram.com/reel/DZKlCXtBb0d/](https://www.instagram.com/reel/DZKlCXtBb0d/)" "/home/mehdi/Downloads"

# Example for Windows PowerShell
transcribe "[https://www.instagram.com/reel/DZKlCXtBb0d/](https://www.instagram.com/reel/DZKlCXtBb0d/)" "D:\Media\Clips"

```

### 📦 Output Behavior

The engine automatically parses the unique shortcode ID from the URL string. If processing multiple files, they will save cleanly side-by-side without overwriting conflicts:

* 🎥 `DZKlCXtBb0d.mp4` *(The local high-quality clip)*
* 📄 `DZKlCXtBb0d.srt` *(The matching English time-stamped text subtitle track)*

*Tip: Standard players like VLC will pick up the subtitle track instantly if the video and subtitle files share the same filename in the same directory.*# insta-transcribe
