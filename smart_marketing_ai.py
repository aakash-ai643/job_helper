import os, uuid, requests, tempfile
from pathlib import Path
from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel
from duckduckgo_search import DDGS
from transformers import pipeline
from serpapi import GoogleSearch
from PIL import Image, ImageDraw, ImageFont
from pytrends.request import TrendReq
import typer
import tkinter as tk
from tkinter import simpledialog, messagebox
from fastapi import APIRouter

router = APIRouter()

@router.get("/marketing-example")
def test_marketing():
    return {"message": "📈 Marketing route is working!"}

# === Setup ===
app = FastAPI(title="🚀 Smart Digital Marketing AI (Real-Time + Extension + Overwrite)")
cli = typer.Typer()
TEMP_DIR = Path(tempfile.gettempdir())

# === Load LLM (with fallback)
try:
    generator = pipeline("text2text-generation", model="google/flan-t5-large")
except:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
    def generator(prompt, max_length=128):
        tokens = tokenizer(prompt, return_tensors="pt")
        output = model.generate(**tokens, max_length=max_length)
        return [{"generated_text": tokenizer.decode(output[0], skip_special_tokens=True)}]

SERP_API_KEY = os.getenv("SERP_API_KEY")

# === AI Features ===
def get_keywords(keyword: str):
    if not SERP_API_KEY:
        return ["Error: SERP_API_KEY not set"]
    params = {"engine": "google_autocomplete", "q": keyword, "api_key": SERP_API_KEY}
    search = GoogleSearch(params)
    result = search.get_dict()
    return result.get("suggestions", [])

def competitor_overview(domain: str):
    with DDGS() as ddgs:
        results = ddgs.text(domain, max_results=1)
        return results[0] if results else {}

def generate_blog(keyword: str):
    prompt = f"Write a detailed, SEO-friendly blog about: {keyword}"
    return generator(prompt, max_length=1024)[0]["generated_text"]

def generate_seo_title(desc: str):
    prompt = f"Create an SEO-friendly title for product: {desc}"
    return generator(prompt, max_length=60)[0]["generated_text"]

def generate_meta_description(desc: str):
    prompt = f"Write a 150 character SEO meta description for: {desc}"
    return generator(prompt, max_length=80)[0]["generated_text"]

def generate_product_features(desc: str):
    prompt = f"List 5 bullet point features for: {desc}"
    text = generator(prompt, max_length=120)[0]["generated_text"]
    return text.strip().split("\n")

def generate_hashtags(keyword: str):
    prompt = f"Generate 10 trending hashtags for: {keyword}"
    text = generator(prompt, max_length=80)[0]["generated_text"]
    return text.strip().split("#")[1:]

def generate_voice_script(desc: str):
    prompt = f"Write a 2-line funny Hinglish voiceover for product: {desc}"
    return generator(prompt, max_length=80)[0]["generated_text"]

def get_google_trends(keyword: str):
    pytrends = TrendReq(hl='en-US', tz=330)
    pytrends.build_payload([keyword], cat=0, timeframe='now 1-H', geo='', gprop='')
    return pytrends.interest_over_time().to_dict()

def get_serp_rank(keyword, domain):
    params = {"engine": "google", "q": keyword, "api_key": SERP_API_KEY, "num": 10}
    search = GoogleSearch(params)
    results = search.get_dict()
    for i, res in enumerate(results.get("organic_results", [])):
        if domain in res.get("link", ""):
            return i + 1
    return "Not in top 10"

def generate_poster(title: str, tagline: str, filename: str = "") -> Path:
    img = Image.new("RGB", (800, 400), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((50, 100), title, font=font, fill=(0, 0, 0))
    draw.text((50, 200), tagline, font=font, fill=(80, 80, 80))
    file_path = TEMP_DIR / f"{filename.strip().replace(' ', '_')}.png" if filename else TEMP_DIR / f"poster_{uuid.uuid4().hex}.png"
    img.save(file_path)
    return file_path

# === Web UI ===
@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🚀 Smart Digital Marketing AI</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(to right, #f4f7f9, #e8f0fe);
            }
            .container {
                max-width: 500px;
                margin: 60px auto;
                background: #ffffff;
                padding: 30px 40px;
                border-radius: 16px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            }
            h2 {
                text-align: center;
                color: #0077cc;
                margin-bottom: 30px;
            }
            label {
                font-weight: 600;
                display: block;
                margin-bottom: 8px;
            }
            input[type="text"] {
                width: 100%;
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 8px;
                margin-bottom: 20px;
                font-size: 15px;
            }
            input[type="submit"] {
                width: 100%;
                background-color: #0077cc;
                color: white;
                border: none;
                padding: 14px;
                font-size: 16px;
                font-weight: 600;
                border-radius: 8px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            input[type="submit"]:hover {
                background-color: #005fa3;
            }
            @media (max-width: 600px) {
                .container {
                    margin: 30px 20px;
                    padding: 25px;
                }
                input[type="submit"] {
                    font-size: 15px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🚀 Smart Digital Marketing AI</h2>
            <form action="/seo" method="post">
                <label for="keyword">Keyword</label>
                <input type="text" id="keyword" name="keyword" placeholder="e.g. Organic Aloe Vera Gel" required>

                <label for="competitors">Competitors (comma-separated)</label>
                <input type="text" id="competitors" name="competitors" placeholder="e.g. nykaa.com, mamaearth.in">

                <label for="filename">Overwrite Poster Name (optional)</label>
                <input type="text" id="filename" name="filename" placeholder="e.g. aloe_vera_offer">

                <input type="submit" value="🚀 Run SEO Analysis">
            </form>
        </div>
    </body>
    </html>
    """)

@app.post("/seo")
def seo_analysis(keyword: str = Form(...), competitors: str = Form(""), filename: str = Form("")):
    suggestions = get_keywords(keyword)
    blog = generate_blog(keyword)
    poster = generate_poster(keyword.title(), f"Best offer on {keyword}!", filename)
    title = generate_seo_title(keyword)
    desc = generate_meta_description(keyword)
    tags = generate_hashtags(keyword)
    bullets = generate_product_features(keyword)
    voice = generate_voice_script(keyword)
    trends = get_google_trends(keyword)
    rank = get_serp_rank(keyword, competitors.split(",")[0] if competitors else "")
    competitors_data = [competitor_overview(c.strip()) for c in competitors.split(",") if c.strip()]

    return {
        "keyword": keyword,
        "seo_title": title,
        "meta_description": desc,
        "suggestions": suggestions,
        "hashtags": tags,
        "features": bullets,
        "voice_script": voice,
        "blog": blog,
        "poster_file": poster.name,
        "trends": trends,
        "serp_rank": rank,
        "competitors": competitors_data
    }

@app.get("/poster/{name}")
def get_poster(name: str):
    path = TEMP_DIR / name
    return FileResponse(path, media_type="image/png") if path.exists() else JSONResponse({"error": "Not Found"}, 404)

# === CLI ===
@cli.command()
def run(keyword: str, competitors: str = "", filename: str = ""):
    result = seo_analysis(keyword, competitors, filename)
    print("\n📊 SEO Report:")
    for k, v in result.items():
        print(f"{k}: {v if isinstance(v, str) else str(v)[:300]}...")

# === GUI ===
def start_gui():
    root = tk.Tk()
    root.title("Smart SEO AI")
    def run_gui():
        kw = simpledialog.askstring("Keyword", "Enter Product or Keyword")
        comp = simpledialog.askstring("Competitors", "Comma-separated domains")
        fname = simpledialog.askstring("Poster File Name", "Enter filename (optional)")
        res = seo_analysis(kw, comp, fname)
        messagebox.showinfo("SEO Result", f"Poster: {res['poster_file']}\nTitle: {res['seo_title']}\nMeta: {res['meta_description']}")
    tk.Button(root, text="Start SEO", command=run_gui).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    import sys
    if "--cli" in sys.argv:
        cli()
    elif "--gui" in sys.argv:
        start_gui()
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
