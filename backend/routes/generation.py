"""File serving, document/image/video generation endpoints."""
import uuid
import io
import asyncio
import base64
import logging
import mimetypes
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from db import db
from auth import get_current_user, User
from shared.constants import UPLOAD_DIR, EMERGENT_LLM_KEY
from shared.utils import get_api_keys

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/files/{filename}")
async def serve_file(filename: str):
    """Serve a generated file"""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    
    def file_iter():
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk
    
    return StreamingResponse(
        file_iter(),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.post("/generate/document")
async def generate_document(request: Request, current_user: User = Depends(get_current_user)):
    """Generate PDF, Excel, DOCX, CSV, or TXT documents"""
    body = await request.json()
    doc_type = body.get("type", "pdf").lower()  # pdf, xlsx, docx, csv, txt
    title = body.get("title", "Generated Document")
    content = body.get("content", "")
    rows = body.get("rows", [])  # For spreadsheets: list of lists
    
    if not content and not rows:
        raise HTTPException(status_code=400, detail="Content or rows required")
    
    file_id = uuid.uuid4().hex[:10]
    
    try:
        if doc_type == "pdf":
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            filename = f"{file_id}_{title.replace(' ', '_')[:30]}.pdf"
            filepath = UPLOAD_DIR / filename
            
            doc = SimpleDocTemplate(str(filepath), pagesize=letter)
            styles = getSampleStyleSheet()
            story = [
                Paragraph(title, styles['Title']),
                Spacer(1, 20),
            ]
            for para in content.split("\n"):
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['Normal']))
                    story.append(Spacer(1, 8))
            doc.build(story)
        
        elif doc_type == "xlsx":
            from openpyxl import Workbook
            from openpyxl.styles import Font
            
            filename = f"{file_id}_{title.replace(' ', '_')[:30]}.xlsx"
            filepath = UPLOAD_DIR / filename
            
            wb = Workbook()
            ws = wb.active
            ws.title = title[:31]
            
            if rows:
                for r_idx, row in enumerate(rows, 1):
                    for c_idx, val in enumerate(row, 1):
                        cell = ws.cell(row=r_idx, column=c_idx, value=val)
                        if r_idx == 1:
                            cell.font = Font(bold=True)
            else:
                ws.cell(row=1, column=1, value=title).font = Font(bold=True)
                for i, line in enumerate(content.split("\n"), 2):
                    ws.cell(row=i, column=1, value=line.strip())
            
            wb.save(str(filepath))
        
        elif doc_type == "docx":
            from docx import Document
            from docx.shared import Pt
            
            filename = f"{file_id}_{title.replace(' ', '_')[:30]}.docx"
            filepath = UPLOAD_DIR / filename
            
            doc = Document()
            doc.add_heading(title, level=1)
            for para in content.split("\n"):
                if para.strip():
                    doc.add_paragraph(para.strip())
            doc.save(str(filepath))
        
        elif doc_type == "csv":
            import csv as csv_module
            
            filename = f"{file_id}_{title.replace(' ', '_')[:30]}.csv"
            filepath = UPLOAD_DIR / filename
            
            with open(filepath, "w", newline="") as f:
                writer = csv_module.writer(f)
                if rows:
                    for row in rows:
                        writer.writerow(row)
                else:
                    for line in content.split("\n"):
                        writer.writerow([line.strip()])
        
        elif doc_type == "txt":
            filename = f"{file_id}_{title.replace(' ', '_')[:30]}.txt"
            filepath = UPLOAD_DIR / filename
            
            with open(filepath, "w") as f:
                f.write(content)
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported doc type: {doc_type}. Use: pdf, xlsx, docx, csv, txt")
        
        return {
            "filename": filename,
            "url": f"/files/{filename}",
            "type": doc_type,
            "title": title,
            "size": filepath.stat().st_size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")

@router.post("/generate/image")
async def generate_image(request: Request, current_user: User = Depends(get_current_user)):
    """Generate an image using GPT Image 1 or DALL-E 3"""
    body = await request.json()
    prompt = body.get("prompt", "")
    model = body.get("model", "gpt-image-1")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    try:
        api_keys = await get_api_keys()
        api_key = api_keys.get("emergent") or EMERGENT_LLM_KEY
        
        from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
        
        image_gen = OpenAIImageGeneration(api_key=api_key)
        images = await image_gen.generate_images(
            prompt=prompt,
            model=model,
            number_of_images=1,
            quality="high"
        )
        
        if not images or len(images) == 0:
            raise HTTPException(status_code=500, detail="No image generated")
        
        file_id = uuid.uuid4().hex[:10]
        filename = f"{file_id}_generated.png"
        filepath = UPLOAD_DIR / filename
        
        with open(filepath, "wb") as f:
            f.write(images[0])
        
        image_b64 = base64.b64encode(images[0]).decode()
        
        return {
            "filename": filename,
            "url": f"/files/{filename}",
            "preview": f"data:image/png;base64,{image_b64}",
            "model": model,
            "prompt": prompt
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@router.post("/generate/video")
async def generate_video(request: Request, current_user: User = Depends(get_current_user)):
    """Generate a video using Sora 2"""
    body = await request.json()
    prompt = body.get("prompt", "")
    size = body.get("size", "1280x720")
    duration = body.get("duration", 4)
    model = body.get("model", "sora-2")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    if size not in ("1280x720", "1792x1024", "1024x1792", "1024x1024"):
        size = "1280x720"
    if duration not in (4, 8, 12):
        duration = 4
    
    try:
        api_keys = await get_api_keys()
        api_key = api_keys.get("emergent") or EMERGENT_LLM_KEY
        
        from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration
        import aiohttp
        
        video_gen = OpenAIVideoGeneration(api_key=api_key)
        
        def _gen():
            return video_gen.text_to_video(
                prompt=prompt,
                model=model,
                size=size,
                duration=duration,
                max_wait_time=600
            )
        
        loop = asyncio.get_event_loop()
        video_bytes = await loop.run_in_executor(None, _gen)
        
        if not video_bytes:
            raise HTTPException(status_code=500, detail="Video generation failed")
        
        file_id = uuid.uuid4().hex[:10]
        filename = f"{file_id}_video.mp4"
        filepath = UPLOAD_DIR / filename
        
        video_gen.save_video(video_bytes, str(filepath))
        
        return {
            "filename": filename,
            "url": f"/files/{filename}",
            "model": model,
            "size": size,
            "duration": duration,
            "prompt": prompt
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

