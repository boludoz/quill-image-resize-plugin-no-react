from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
from urllib.parse import unquote
from PIL import Image
import os
import base64
import io

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_editor():
    with open("templates/editor.html") as f:
        template = Template(f.read())
    return template.render()

@app.post("/download")
async def download_file(content: str = Form(...), file_type: str = Form(...)):
    file_name = "index.html" if file_type == "html" else "styles.css"
    decoded_content = unquote(content)
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(decoded_content)
    return FileResponse(file_name, media_type='application/octet-stream', filename=file_name)

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    image = Image.open(file.file)
    output = io.BytesIO()
    image.save(output, format="WEBP")
    webp_data = output.getvalue()
    base64_data = base64.b64encode(webp_data).decode('utf-8')
    return {"filename": file.filename, "webp_base64": base64_data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)