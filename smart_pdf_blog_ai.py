# ✅ smart_pdf_blog_ai_updated.py
import os
import uuid
import tempfile
from pathlib import Path
from fpdf import FPDF
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
from transformers import pipeline
import markdown
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from fastapi import APIRouter

router = APIRouter()

@router.get("/pdf-blog-example")
def test_pdf_blog():
    return {"message": "📘 PDF + Blog route is working!"}

# === Setup ===
app = FastAPI(title="📘 Smart PDF & Blog Generator")
TEMP_DIR = Path(tempfile.gettempdir())

# === Load AI Models ===
blog_writer = pipeline("text2text-generation", model="databricks/dolly-v2-3b")
summarizer = pipeline("summarization", model="google/flan-t5-large")

# === Content Generator ===
def generate_blog(topic: str, tone: str = "informative") -> str:
    prompt = f"Write a well-structured, {tone} blog post on: {topic}"
    return blog_writer(prompt, max_length=1024)[0]["generated_text"]

# === Markdown/HTML to PDF ===
def markdown_to_pdf(md_text: str, pdf_path: Path):
    html = markdown.markdown(md_text)
    soup = BeautifulSoup(html, "html.parser")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for element in soup.find_all(["h1", "h2", "p", "li"]):
        if element.name == "h1":
            pdf.set_font("Arial", 'B', 16)
        elif element.name == "h2":
            pdf.set_font("Arial", 'B', 14)
        elif element.name == "li":
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, f"- {element.text}")
            continue
        else:
            pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, element.text)

    pdf.output(str(pdf_path))

# === API Models ===
class BlogRequest(BaseModel):
    topic: str
    tone: str = "informative"
    format: str = "markdown"
    summarize: bool = False
    generate_pdf: bool = False
    overwrite: bool = False
    file_name: str = ""

# === FastAPI Routes ===
@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""
    <html>
    <head>
        <title>📘 Smart Blog + PDF Generator</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f4f7fa;
                padding: 40px;
                color: #333;
            }
            .container {
                max-width: 600px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 0 12px rgba(0,0,0,0.08);
            }
            h2 {
                text-align: center;
                color: #0077cc;
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
            }
            input[type="text"],
            select {
                width: 100%;
                padding: 10px;
                margin-bottom: 15px;
                border-radius: 8px;
                border: 1px solid #ccc;
                font-size: 15px;
            }
            input[type="checkbox"] {
                margin-right: 8px;
            }
            .checkbox-label {
                display: block;
                margin-bottom: 10px;
            }
            input[type="submit"] {
                width: 100%;
                padding: 12px;
                background-color: #0077cc;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            input[type="submit"]:hover {
                background-color: #005fa3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📘 Smart Blog + PDF Generator</h2>
            <form action="/generate/" method="post">
                <label for="topic">Topic</label>
                <input type="text" name="topic" id="topic" required>

                <label for="tone">Tone</label>
                <input type="text" name="tone" id="tone" value="informative">

                <label for="format">Format</label>
                <select name="format" id="format">
                    <option value="markdown">Markdown</option>
                    <option value="text">Plain Text</option>
                </select>

                <label class="checkbox-label">
                    <input type="checkbox" name="summarize"> Summarize the content
                </label>

                <label class="checkbox-label">
                    <input type="checkbox" name="generate_pdf"> Generate PDF Output
                </label>

                <label class="checkbox-label">
                    <input type="checkbox" name="overwrite"> Overwrite Existing File
                </label>

                <label for="file_name">Optional File Name</label>
                <input type="text" name="file_name" id="file_name" placeholder="e.g., my_blog_post">

                <input type="submit" value="🚀 Generate Blog">
            </form>
        </div>
    </body>
    </html>
    """)

@app.post("/generate/")
async def generate_blog_handler(
    topic: str = Form(...),
    tone: str = Form("informative"),
    format: str = Form("markdown"),
    summarize: bool = Form(False),
    generate_pdf: bool = Form(False),
    overwrite: bool = Form(False),
    file_name: str = Form("")
):
    full_text = generate_blog(topic, tone)
    if summarize:
        full_text = summarizer(full_text, max_length=512, min_length=100)[0]["summary_text"]

    if not file_name:
        file_name_base = f"blog_{uuid.uuid4()}"
    else:
        file_name_base = file_name.strip().replace(" ", "_")

    output_txt = TEMP_DIR / f"{file_name_base}.md"
    output_pdf = TEMP_DIR / f"{file_name_base}.pdf"

    if output_txt.exists() and not overwrite:
        return JSONResponse(status_code=400, content={"error": "❌ File exists. Use overwrite option."})

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(full_text)

    if generate_pdf:
        markdown_to_pdf(full_text, output_pdf)
        return FileResponse(output_pdf, media_type="application/pdf", filename=output_pdf.name)

    return FileResponse(output_txt, media_type="text/markdown", filename=output_txt.name)

# === CLI Mode ===
def cli_mode():
    topic = input("Blog Topic: ")
    tone = input("Tone (informative/casual/etc): ")
    fmt = input("Format (text/markdown): ").lower()
    pdf = input("Generate PDF? (yes/no): ").lower() == "yes"
    overwrite = input("Overwrite if exists? (yes/no): ").lower() == "yes"
    file_name = input("File Name (leave blank for auto): ").strip().replace(" ", "_")

    result = generate_blog(topic, tone)
    if not file_name:
        file_base = f"cli_blog_{uuid.uuid4()}"
    else:
        file_base = file_name

    path = TEMP_DIR / f"{file_base}.md"
    pdf_path = TEMP_DIR / f"{file_base}.pdf"

    if path.exists() and not overwrite:
        print("❌ File exists. Use overwrite option.")
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(result)

    if pdf:
        markdown_to_pdf(result, pdf_path)
        print(f"✅ PDF Created: {pdf_path}")
    else:
        print(f"✅ Blog saved: {path}")

# === GUI Mode ===
def start_gui():
    root = tk.Tk()
    root.title("Smart Blog Creator")

    def run():
        topic = simpledialog.askstring("Topic", "Blog Topic:")
        tone = simpledialog.askstring("Tone", "Tone (informative/casual):", initialvalue="informative")
        file_name = simpledialog.askstring("File name", "Save as (optional):")
        overwrite = messagebox.askyesno("Overwrite", "Overwrite existing file if exists?")
        pdf = messagebox.askyesno("PDF?", "Generate PDF?")

        result = generate_blog(topic, tone)
        file_base = file_name.strip().replace(" ", "_") if file_name else f"gui_blog_{uuid.uuid4()}"
        file_path = TEMP_DIR / f"{file_base}.md"
        pdf_path = TEMP_DIR / f"{file_base}.pdf"

        if file_path.exists() and not overwrite:
            messagebox.showerror("Error", "❌ File already exists. Use overwrite option.")
            return

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result)

        if pdf:
            markdown_to_pdf(result, pdf_path)
            messagebox.showinfo("Done", f"✅ PDF: {pdf_path}")
        else:
            messagebox.showinfo("Done", f"✅ Blog saved: {file_path}")

    tk.Button(root, text="Generate Blog", command=run, height=2, width=30).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    import sys
    if "--cli" in sys.argv:
        cli_mode()
    elif "--gui" in sys.argv:
        start_gui()
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
