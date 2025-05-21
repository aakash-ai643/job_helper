from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from EXCEL import router as excel_router
from word import router as word_router
from ppt import router as ppt_router
from smart_marketing_ai import router as seo_router
from smart_pdf_blog_ai import router as blog_router
from tts_generator import router as tts_router
from codding_pro import router as code_router

app = FastAPI(title="🚀 All-in-One AI Workspace")

# Register all routers
app.include_router(excel_router, prefix="/excel")
app.include_router(word_router, prefix="/word")
app.include_router(ppt_router, prefix="/ppt")
app.include_router(seo_router, prefix="/seo")
app.include_router(blog_router, prefix="/blog")
app.include_router(tts_router, prefix="/tts")
app.include_router(code_router, prefix="/code")

# Main dashboard
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>🧠 AI Assistant Dashboard</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(to right, #f4f7fa, #e3efff);
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
                align-items: flex-start;
                min-height: 100vh;
            }
            .container {
                max-width: 900px;
                width: 100%;
            }
            h2 {
                text-align: center;
                color: #0077cc;
                margin-bottom: 30px;
                font-size: 28px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 20px;
            }
            .tool {
                background-color: white;
                padding: 30px 20px;
                border-radius: 16px;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .tool:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12);
            }
            .tool a {
                text-decoration: none;
                font-size: 18px;
                color: #0077cc;
                font-weight: 600;
                display: block;
                margin-top: 10px;
            }
            .icon {
                font-size: 32px;
                margin-bottom: 10px;
            }
            @media (max-width: 600px) {
                h2 {
                    font-size: 22px;
                }
                .tool a {
                    font-size: 16px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🧠 Smart AI Assistant Dashboard</h2>
            <div class="grid">
                <div class="tool"><div class="icon">📊</div><a href="/excel">Excel AI</a></div>
                <div class="tool"><div class="icon">📝</div><a href="/word">Word Assistant</a></div>
                <div class="tool"><div class="icon">📽️</div><a href="/ppt">PPT Creator</a></div>
                <div class="tool"><div class="icon">📘</div><a href="/blog">Blog + PDF</a></div>
                <div class="tool"><div class="icon">📈</div><a href="/seo">Marketing SEO</a></div>
                <div class="tool"><div class="icon">🎙️</div><a href="/tts">TTS Voice</a></div>
                <div class="tool"><div class="icon">💻</div><a href="/code">Code Generator</a></div>
            </div>
        </div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn, os
    port = int(os.environ.get("PORT", 7000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
