"""Download speech editing audio samples from voicecraft-x.github.io"""
import os
import urllib.request

BASE_URL = "https://voicecraft-x.github.io/audios/editing"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "voicecraft-x")

# Files to download based on the HTML source
FILES = [
    # English - Original (prompt)
    "EN/prompt/1.wav",
    "EN/prompt/2.wav",
    "EN/prompt/12.wav",
    "EN/prompt/7.wav",
    "EN/prompt/6.wav",
    # English - Edited (voicecraftx)
    "EN/voicecraftx/1.wav",
    "EN/voicecraftx/2.wav",
    "EN/voicecraftx/12.wav",
    "EN/voicecraftx/7.wav",
    "EN/voicecraftx/6.wav",
    # Chinese - Original (prompt)
    "ZH/prompt/1.wav",
    "ZH/prompt/11.wav",
    "ZH/prompt/3.wav",
    "ZH/prompt/9.wav",
    "ZH/prompt/10.wav",
    # Chinese - Edited (voicecraftx)
    "ZH/voicecraftx/1.wav",
    "ZH/voicecraftx/11.wav",
    "ZH/voicecraftx/3.wav",
    "ZH/voicecraftx/9.wav",
    "ZH/voicecraftx/10.wav",
]

def download_file(relative_path):
    url = f"{BASE_URL}/{relative_path}"
    # Keep directory structure: EN/prompt/1.wav -> EN_prompt_1.wav
    local_name = relative_path.replace("/", "_")
    local_path = os.path.join(OUTPUT_DIR, local_name)
    
    if os.path.exists(local_path):
        print(f"  Skip (exists): {local_name}")
        return True
    
    print(f"  Downloading: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            with open(local_path, "wb") as f:
                f.write(data)
        print(f"    -> Saved: {local_name} ({len(data)//1024} KB)")
        return True
    except Exception as e:
        print(f"    -> FAILED: {e}")
        return False

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Downloading {len(FILES)} files...\n")
    
    success = 0
    for f in FILES:
        if download_file(f):
            success += 1
    
    print(f"\nDone. {success}/{len(FILES)} files downloaded.")
