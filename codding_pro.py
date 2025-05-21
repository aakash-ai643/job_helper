import os, subprocess, sys
from pathlib import Path
from fastapi import FastAPI, Form, Request
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
import tkinter as tk
from tkinter import simpledialog, messagebox
from fastapi import APIRouter

router = APIRouter()

@router.get("/codegen-example")
def test_code_gen():
    return {"message": "💻 Codegen route is working!"}

app = FastAPI(title="💻 GPT Engineer Full Stack Dev Assistant")
BASE_DIR = Path(__file__).parent.resolve()
GPT_ENGINEER_DIR = BASE_DIR / "gpt-engineer"
WORKSPACE_DIR = BASE_DIR / "generated_projects"
CONFIG_DIR = Path.home() / ".gpt-engineer"
DEFAULT_MODEL = "mistral"
TEMPLATES = {
    "blog": "Create a full-stack modern blog platform with login, rich text editor, comment system.",
    "chat": "Build a real-time chat app with WebSocket, auth and notifications.",
    "ecommerce": "Build a full e-commerce site with cart, payment, admin panel.",
    "dashboard": "Make a data analytics dashboard with charts and API.",
    "auth": "Build an auth microservice with JWT and Google login."
}
SUPPORTED_MODELS = ["mistral", "codellama", "deepseek-coder"]

# ✅ Ensure Setup
def ensure_setup():
    if not GPT_ENGINEER_DIR.exists():
        subprocess.run(["git", "clone", "https://github.com/AntonOsika/gpt-engineer.git", str(GPT_ENGINEER_DIR)], check=True)
    req_txt = GPT_ENGINEER_DIR / "requirements.txt"
    if req_txt.exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_txt)], check=True)
    WORKSPACE_DIR.mkdir(exist_ok=True)

# ✅ Model Setup
def setup_model_config(model_name: str):
    CONFIG_DIR.mkdir(exist_ok=True)
    config_file = CONFIG_DIR / "config.yaml"
    config_file.write_text(f"model: {model_name}\nprovider: ollama\nmodel_endpoint: http://localhost:11434\n", encoding="utf-8")

# ✅ Translate
def translate_to_english(text: str) -> str:
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text

# ✅ Write Prompt
def write_prompt(text: str, path: Path):
    path.mkdir(parents=True, exist_ok=True)
    (path / "prompt").write_text(text, encoding="utf-8")

# ✅ GPT Engineer Runner with Overwrite Support
def run_gpt_engineer(prompt: str, model: str, overwrite: bool = False) -> str:
    app_path = WORKSPACE_DIR / prompt.replace(" ", "_").lower()
    if app_path.exists() and not overwrite:
        return f"⚠️ Project already exists: {app_path}. Use overwrite=True to regenerate."
    write_prompt(prompt, app_path)
    try:
        subprocess.run(["gpt-engineer", str(app_path), "--model", model], check=True)
        return f"✅ Code generated in: {app_path}"
    except subprocess.CalledProcessError:
        return "❌ GPT Engineer failed. Make sure Ollama is running (e.g., `ollama run mistral`)"

# ✅ Web UI
@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>💻 GPT Engineer Assistant</title>
        <style>
            body {
                background: #eef2f7;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .container {
                background-color: #fff;
                padding: 40px;
                border-radius: 16px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
                max-width: 520px;
                width: 100%;
                animation: fadeIn 0.5s ease-in-out;
            }
            h2 {
                color: #007acc;
                text-align: center;
                margin-bottom: 30px;
            }
            label {
                font-weight: 600;
                display: block;
                margin: 15px 0 8px;
                color: #333;
            }
            input[type="text"], select {
                width: 100%;
                padding: 12px;
                font-size: 15px;
                border: 1px solid #ccc;
                border-radius: 8px;
                transition: border 0.3s ease;
            }
            input[type="text"]:focus, select:focus {
                border-color: #007acc;
                outline: none;
            }
            input[type="submit"] {
                width: 100%;
                padding: 14px;
                margin-top: 25px;
                font-size: 16px;
                background-color: #007acc;
                color: #fff;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: background-color 0.3s ease;
                font-weight: bold;
            }
            input[type="submit"]:hover {
                background-color: #005fa3;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @media (max-width: 600px) {
                .container {
                    padding: 30px 20px;
                    border-radius: 12px;
                }
                h2 {
                    font-size: 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>💻 GPT Engineer Full Stack Assistant</h2>
            <form action="/generate-ui" method="post">
                <label for="task">🧠 Task</label>
                <input type="text" id="task" name="task" placeholder="e.g. Create a blog with login" required>

                <label for="template">📦 Template (optional)</label>
                <input type="text" id="template" name="template" placeholder="e.g. blog, chat, ecommerce">

                <label for="model">🤖 Choose Model</label>
                <select id="model" name="model">
                    <option value="mistral">Mistral</option>
                    <option value="codellama">CodeLLaMa</option>
                    <option value="deepseek-coder">DeepSeek Coder</option>
                </select>

                <label for="overwrite">♻️ Overwrite if Exists?</label>
                <select id="overwrite" name="overwrite">
                    <option value="false">No</option>
                    <option value="true">Yes</option>
                </select>

                <input type="submit" value="🚀 Generate Code">
            </form>
        </div>
    </body>
    </html>
    """)

@app.post("/generate-ui")
async def generate_ui(task: str = Form(...), model: str = Form(...), template: str = Form(""), overwrite: str = Form("false")):
    ensure_setup()
    setup_model_config(model)
    prompt = TEMPLATES.get(template.lower()) if template.lower() in TEMPLATES else translate_to_english(task)
    result = run_gpt_engineer(prompt, model, overwrite.lower() == "true")
    return {"status": "done", "message": result}

# ✅ Swagger API Support
class CodeRequest(BaseModel):
    task: str
    model: str = DEFAULT_MODEL
    template: Optional[str] = None
    overwrite: Optional[bool] = False

@app.post("/generate", tags=["Swagger"])
def generate_code(data: CodeRequest):
    ensure_setup()
    setup_model_config(data.model)
    prompt = TEMPLATES.get(data.template.lower()) if data.template and data.template.lower() in TEMPLATES else translate_to_english(data.task)
    result = run_gpt_engineer(prompt, data.model, data.overwrite)
    return {"status": "done", "message": result}

# ✅ CLI Mode
def cli_mode():
    print("📦 GPT Engineer CLI")
    task = input("👉 Enter your project task: ")
    model = input("Model [mistral]: ") or DEFAULT_MODEL
    overwrite = input("Overwrite existing project? (y/n): ").lower() == "y"
    prompt = TEMPLATES.get(task.lower(), translate_to_english(task))
    ensure_setup()
    setup_model_config(model)
    result = run_gpt_engineer(prompt, model, overwrite)
    print(result)

# ✅ GUI Mode
def start_gui():
    root = tk.Tk()
    root.title("Smart Dev Assistant")
    def run():
        task = simpledialog.askstring("Project Task", "Enter your idea:")
        model = simpledialog.askstring("Model", "Model (mistral/codellama/deepseek-coder):", initialvalue="mistral")
        overwrite = messagebox.askyesno("Overwrite?", "Overwrite if exists?")
        prompt = TEMPLATES.get(task.lower(), translate_to_english(task))
        ensure_setup()
        setup_model_config(model)
        result = run_gpt_engineer(prompt, model, overwrite)
        messagebox.showinfo("Result", result)
    tk.Button(root, text="Start GPT Engineer", command=run, height=2, width=30).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    if "--gui" in sys.argv:
        start_gui()
    elif "--cli" in sys.argv:
        cli_mode()
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
