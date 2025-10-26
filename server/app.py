
# server.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil

from test import generate_report
app = FastAPI()

# --- CORS setup (allow your frontend to connect) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Directory to store uploaded files ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
def delete_contents(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")
# --- Endpoint to receive multiple files ---
@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):

    # return FileResponse(
    #     "BaoCaoTongHop_Final.html",
    #     media_type="text/html",
    #     filename="report.html"
    # )
    saved_files = []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        saved_files.append({
            "filename": file.filename,
            "saved_to": file_path
        })

    OUTPUT_FILE = generate_report(UPLOAD_DIR)

    delete_contents(UPLOAD_DIR)
    return FileResponse(
        OUTPUT_FILE,
        media_type="text/plain",
        filename="report.html"
    )
