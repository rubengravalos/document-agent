from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path
import shutil
import tempfile

from document_agent.core.document_processor import DocumentProcessor

# Set up paths
BASE_DIR = Path(__file__).parent.parent.parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(STATIC_DIR))

app = FastAPI(
    title="Document Assistant API",
    description="API for querying documents using natural language",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Global variable to store the document processor instance
processor = None

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    answer: str
    sources: List[str]

class StatusResponse(BaseModel):
    status: str
    document_loaded: bool

@app.get("/status")
async def get_status():
    return {
        "status": "running",
        "document_loaded": processor is not None and hasattr(processor, 'text_chunks') and len(processor.text_chunks) > 0
    }

@app.on_event("startup")
async def startup_event():
    """Initialize the document processor on startup."""
    global processor
    processor = DocumentProcessor()
    
    # Check if sample document exists and load it
    sample_pdf = Path(__file__).parent.parent.parent / "data" / "sample_geography.pdf"
    if sample_pdf.exists():
        try:
            processor.load_document(str(sample_pdf))
            processor.create_index()
        except Exception as e:
            print(f"Warning: Could not load sample document: {str(e)}")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a new document."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, file.filename)
    
    try:
        # Save the uploaded file
        with open(temp_file, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the document
        global processor
        processor = DocumentProcessor()
        processor.load_document(temp_file)
        processor.create_index()
        
        return {"status": "success", "message": "Document processed successfully"}
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
        
    finally:
        # Clean up temporary files
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                print(f"Error removing temp file: {e}")
        if os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except Exception as e:
                print(f"Error removing temp dir: {e}")

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(question: QuestionRequest):
    if processor is None:
        raise HTTPException(status_code=400, detail="No document loaded. Please upload a document first.")
    
    try:
        answer, sources = processor.answer_question(question.question)
        return {
            "answer": answer,
            "sources": sources if sources else []
        }
    except Exception as e:
        print(f"Error answering question: {str(e)}")
        return {
            "answer": "I encountered an error while processing your question.",
            "sources": []
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
