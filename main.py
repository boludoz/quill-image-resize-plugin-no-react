from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
from urllib.parse import unquote
from PIL import Image
import os
import base64
import io
import json
from datetime import datetime
import shutil

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Asegurar que existe el directorio de borradores
DRAFTS_DIR = "drafts"
os.makedirs(DRAFTS_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def get_editor():
    with open("templates/editor.html") as f:
        template = Template(f.read())
    return template.render()

@app.post("/download")
async def download_file(content: str = Form(...), file_type: str = Form(...)):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"exports/{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    decoded_content = unquote(content)
    
    if file_type == "html":
        file_name = "index.html"
        # Ya no necesitamos crear un archivo CSS separado
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(decoded_content)
        return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    image = Image.open(file.file)
    output = io.BytesIO()
    image.save(output, format="WEBP")
    webp_data = output.getvalue()
    base64_data = output.getvalue()
    base64_data = base64.b64encode(webp_data).decode('utf-8')
    return {"filename": file.filename, "webp_base64": base64_data}

@app.get("/drafts")
async def get_drafts():
    drafts = []
    for file in os.listdir(DRAFTS_DIR):
        if file.endswith('.json'):
            name = file[:-5]  # remove .json
            drafts.append({"name": name})
    return drafts

@app.get("/drafts/{name}")
async def get_draft(name: str):
    try:
        with open(os.path.join(DRAFTS_DIR, f"{name}.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Borrador no encontrado")

@app.post("/drafts")
async def save_draft(data: dict):
    name = data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Nombre de borrador requerido")
    
    file_path = os.path.join(DRAFTS_DIR, f"{name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return {"message": "Borrador guardado exitosamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)