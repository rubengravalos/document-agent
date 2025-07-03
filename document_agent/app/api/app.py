from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path
import shutil
import tempfile

from document_agent.core.document_processor import DocumentProcessor

app = FastAPI(
    title="Document Assistant API",
    description="API for querying documents using natural language",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store the document processor instance
processor = None

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    answer: str
    context: List[str]

class StatusResponse(BaseModel):
    status: str
    document_loaded: bool

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

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Check if the API is running and if a document is loaded."""
    return {
        "status": "running",
        "document_loaded": len(processor.text_chunks) > 0 if processor else False
    }

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about the document."""
    if not processor or not processor.index:
        raise HTTPException(status_code=400, detail="No document loaded")
    
    try:
        answer, context = processor.answer_question(request.question)
        return {
            "answer": answer,
            "context": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a new document."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save the uploaded file temporarily
        temp_dir = Path(tempfile.mkdtemp())
        temp_file = temp_dir / file.filename
        
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the document
        global processor
        processor = DocumentProcessor()
        processor.load_document(str(temp_file))
        processor.create_index()
        
        # Clean up
        os.remove(temp_file)
        os.rmdir(temp_dir)
        
        return {"status": "success", "message": "Document processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
