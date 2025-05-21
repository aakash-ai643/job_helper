import os
import uuid
import tempfile
import subprocess
from pathlib import Path
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from pydantic import BaseModel
from gtts import gTTS
import typer
import tkinter as tk
from tkinter import simpledialog, messagebox
from transformers import pipeline
from fastapi import APIRouter

router = APIRouter()

@router.get("/tts-example")
def test_tts():
    return {"message": "🎙️ TTS route is working!"}

app = FastAPI(title="🎙️ Smart TTS AI")
cli = typer.Typer()
TEMP_DIR = Path(tempfile.gettempdir())

# ✅ Supported languages
SUPPORTED_LANGUAGES = {
    "hindi": "hi",
    "english": "en",
    "french": "fr",
    "german": "de",
    "japanese": "ja",
    "korean": "ko",
    "spanish": "es",
    "russian": "ru",
    "chinese": "zh-CN",
    "arabic": "ar",
    "italian": "it",
    "portuguese": "pt"
}

# ✅ Bark-style (Optional)
try:
    bark_tts = pipeline("text-to-speech", model="suno/bark-small")
except:
    bark_tts = None

# ✅ Generate TTS with overwrite support
def generate_audio_file(text: str, language: str = "english", engine: str = "gtts", file_name: str = "") -> Path:
    lang_code = SUPPORTED_LANGUAGES.get(language.lower(), "en")
    file_name_base = file_name.strip().replace(" ", "_") if file_name else f"voice_{uuid.uuid4()}"
    file_path = TEMP_DIR / f"{file_name_base}.mp3"

    if file_path.exists() and not file_name:
        file_path = TEMP_DIR / f"{file_name_base}_{uuid.uuid4().hex[:4]}.mp3"

    if engine == "bark" and bark_tts:
        audio = bark_tts(text)[0]["audio"]
        with open(file_path, "wb") as f:
            f.write(audio)
    else:
        tts = gTTS(text=text, lang=lang_code)
        tts.save(file_path)

    return file_path

def play_audio(file_path: Path):
    try:
        if os.name == 'nt':
            os.startfile(str(file_path))
        elif os.uname().sysname == "Darwin":
            subprocess.run(["open", str(file_path)])
        else:
            subprocess.run(["xdg-open", str(file_path)])
    except Exception as e:
        print(f"⚠️ Could not auto-play: {e}")

# ✅ API Schema
class TTSRequest(BaseModel):
    text: str
    language: str = "english"
    engine: str = "gtts"
    file_name: str = ""

# ✅ FastAPI Routes
@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>🎙️ Shinchan TTS Generator</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                background: linear-gradient(to right, #f8f9fa, #e0f7fa);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 40px 10px;
            }
            .card {
                background: #ffffff;
                max-width: 520px;
                margin: auto;
                padding: 30px 40px;
                border-radius: 16px;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
            }
            h2 {
                text-align: center;
                color: #1e88e5;
                margin-bottom: 25px;
            }
            label {
                font-weight: 600;
                margin-bottom: 8px;
                display: block;
            }
            textarea, input[type="text"], select {
                width: 100%;
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 14px;
                margin-bottom: 20px;
                transition: border-color 0.3s ease;
            }
            textarea:focus, input:focus, select:focus {
                outline: none;
                border-color: #1e88e5;
            }
            input[type="submit"] {
                background: #1e88e5;
                color: white;
                border: none;
                padding: 14px;
                border-radius: 8px;
                width: 100%;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            input[type="submit"]:hover {
                background-color: #1565c0;
            }
            @media (max-width: 600px) {
                .card {
                    padding: 20px;
                }
                input[type="submit"] {
                    font-size: 15px;
                }
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🗣️ Shinchan Style TTS Generator</h2>
            <form action="/tts/generate" method="post">
                <label for="text">Text to Speak:</label>
                <textarea id="text" name="text" rows="4" placeholder="Enter something funny like 'Mummy mujhe chocolate chahiye!'"></textarea>

                <label for="language">Language:</label>
                <input type="text" id="language" name="language" value="english">

                <label for="engine">Voice Engine:</label>
                <select id="engine" name="engine">
                    <option value="gtts">gTTS (Google)</option>
                    <option value="bark">Bark (Offline)</option>
                </select>

                <label for="file_name">Optional File Name:</label>
                <input type="text" id="file_name" name="file_name" placeholder="e.g. shinchan_intro">

                <input type="submit" value="🎤 Speak Like Shinchan">
            </form>
        </div>
    </body>
    </html>
    """)

@app.post("/tts/generate")
def generate_tts(text: str = Form(...), language: str = Form("english"), engine: str = Form("gtts"), file_name: str = Form("")):
    try:
        path = generate_audio_file(text, language, engine, file_name)
        return FileResponse(path, media_type="audio/mpeg", filename=path.name)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ✅ CLI Mode
@cli.command()
def speak(
    text: str = typer.Argument(...),
    language: str = typer.Option("english", help="Language"),
    engine: str = typer.Option("gtts", help="Engine: gtts or bark"),
    file_name: str = typer.Option("", help="Optional file name"),
    play: bool = typer.Option(True, "--play/--no-play", help="Play audio")
):
    try:
        path = generate_audio_file(text, language, engine, file_name)
        print(f"✅ Audio saved: {path}")
        if play:
            play_audio(path)
    except Exception as e:
        print(f"❌ Error: {e}")

# ✅ GUI Mode
def start_gui():
    root = tk.Tk()
    root.title("Shinchan TTS Generator")

    def run():
        text = simpledialog.askstring("Text", "Shinchan kya bole?")
        lang = simpledialog.askstring("Language", "Language (hindi/english/...)", initialvalue="hindi")
        engine = simpledialog.askstring("Engine", "gtts / bark", initialvalue="gtts")
        file_name = simpledialog.askstring("File Name", "Save as (optional)")
        if not text:
            return
        path = generate_audio_file(text, lang, engine, file_name)
        messagebox.showinfo("🎉 Done", f"Saved: {path}")
        play_audio(path)

    tk.Button(root, text="🎤 Speak Like Shinchan", command=run, height=2, width=30).pack(pady=20)
    root.mainloop()

# ✅ Main Entry
if __name__ == "__main__":
    import sys
    if "--gui" in sys.argv:
        start_gui()
    elif "--cli" in sys.argv:
        cli()
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
