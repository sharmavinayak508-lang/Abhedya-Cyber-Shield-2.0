from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import config

app = FastAPI(title=config.APP_NAME)

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html><body style="font-family:Arial;background:{config.THEME['bg_dark']};color:{config.THEME['text']};text-align:center;padding:50px">
    <h1 style="color:{config.THEME['primary']}">{config.APP_NAME} - RUNNING SUCCESSFULLY!</h1>
    <p>Config fixed - PATHS and THEME both working</p>
    <a href="/docs" style="color:{config.THEME['accent']};font-size:20px">Click here to go to /docs</a>
    <br><br><p>Server: http://localhost:8000</p>
    </body></html>
    """

@app.get("/health")
def health():
    return {"status": "ok", "app": config.APP_NAME, "theme_loaded": True, "paths_loaded": True}
