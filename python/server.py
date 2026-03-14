from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

# Directories
web_dir = os.path.join(os.path.dirname(__file__), "..", "web")
static_dir = os.path.join(web_dir, "static")

# App
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Root page
@app.get("/")
async def root():
    return FileResponse(os.path.join(web_dir, "index.html"))