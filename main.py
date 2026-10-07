from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from io import BytesIO
from typing import List
import os

app = FastAPI(title="Pic2Ico Docker Service", description="多尺寸图片转 ICO 的简单 Web 服务")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "Resources")

# 无论目录/文件是否已创建，都预先挂载，方便后续直接往 Resources 里加图标文件
app.mount("/static", StaticFiles(directory=RESOURCES_DIR, check_dir=False), name="static")


def parse_sizes(sizes_str: str) -> List[int]:
    try:
        sizes = [int(s.strip()) for s in sizes_str.split(",") if s.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="sizes 参数必须是逗号分隔的整数，例如 256,128,64,32,16")
    if not sizes:
        raise HTTPException(status_code=400, detail="至少需要一个尺寸")
    return sorted(set(sizes), reverse=True)


def convert_to_ico_bytes(image_file: BytesIO, sizes: List[int]) -> BytesIO:
    image = Image.open(image_file).convert("RGBA")
    ico_bytes = BytesIO()
    ico_sizes = [(s, s) for s in sizes]
    image.save(ico_bytes, format="ICO", sizes=ico_sizes)
    ico_bytes.seek(0)
    return ico_bytes


@app.get("/")
async def index():
    index_path = os.path.join(BASE_DIR, "index.html")
    return FileResponse(index_path, media_type="text/html")


@app.post("/convert")
async def convert(file: UploadFile = File(...), sizes: List[str] = Form(...)):
    if not sizes:
        raise HTTPException(status_code=400, detail="至少勾选一个尺寸")

    if file.content_type not in ("image/png", "image/jpeg"):
        raise HTTPException(status_code=400, detail="仅支持 PNG / JPG / JPEG 图片")

    sizes_int = [int(s) for s in sizes]
    contents = await file.read()
    ico_stream = convert_to_ico_bytes(BytesIO(contents), sizes_int)

    filename_without_ext = file.filename.rsplit(".", 1)[0] if file.filename else "icon"

    # HTTP 头只能使用 latin-1 字符，中文文件名会导致报错，这里做一次简单“安全化”
    safe_name = "".join(ch if ch.isascii() and ch not in ('"', "\\") else "_" for ch in filename_without_ext)
    if not safe_name:
        safe_name = "icon"

    headers = {
        "Content-Disposition": f'attachment; filename="{safe_name}.ico"'
    }

    return StreamingResponse(
        ico_stream,
        media_type="image/x-icon",
        headers=headers,
    )

