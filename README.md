# Document Assistant

An agentic document assistant that answers questions based on the content of a provided PDF document. The system uses state-of-the-art NLP models to understand and retrieve information from documents.

## Features

- Load and process PDF documents
- Answer questions based strictly (as strict as T5-based models can be, but not as strict as GPTs) on document content
- Command-line interface for interactive use
- REST API for integration with other applications
- Efficient document chunking and embedding
- Semantic search using FAISS for fast retrieval

## Setup

1. **Clone the repository** (if not already cloned):
   ```bash
   git clone <repository-url>
   cd document_agent
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the data directory**:
   
   The repository includes a sample PDF (`data/sample_geography.pdf`) with geography facts for testing. The system is pre-configured to use this file.
   
   ```bash
   mkdir -p data
   # The sample_geography.pdf is already included in the repository
   # To use your own document, simply replace the sample file:
   # cp /path/to/your/document.pdf data/sample_geography.pdf
   ```

## Usage

### Stage 1: Command-line Interface

Run the interactive command-line interface:
```bash
python -m document_agent.cli
```

The CLI will guide you through loading a document and asking questions.

### Stage 2: Web API

Start the FastAPI server:
```bash
uvicorn document_agent.app.api.app:app --reload
```

Then open your browser to http://localhost:8000/docs for the interactive API documentation.

### API Endpoints

- `GET /status`: Check API status and if a document is loaded
- `POST /ask`: Ask a question about the document
- `POST /upload`: Upload and process a new PDF document

## Testing

Run the test suite to verify the installation:
```bash
python -m tests.test_document_agent
```

## Project Structure

```
.
├── .git/                     # Git version control
├── .gitignore               # Git ignore file
├── README.md                # This file
├── requirements.txt         # Python dependencies
├── data/                    # Directory for document storage
│   └── sample_geography.pdf  # Example document
├── document_agent/          # Main package
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # Command-line interface
│   ├── app/                 # Web application
│   │   ├── __init__.py
│   │   └── api/
│   │       ├── __init__.py
│   │       └── app.py       # FastAPI application
│   └── core/                # Core functionality
│       ├── __init__.py
│       └── document_processor.py  # Document processing logic
└── tests/                   # Test files
    └── test_document_agent.py     # Test cases
```

## Implementation Details

### Document Processing
- Uses `pypdf` for PDF text extraction
- Implements chunking with overlap for better context
- Uses `sentence-transformers` for generating embeddings
- Leverages FAISS for efficient similarity search

### Question Answering
- Uses T5 model for generating answers
- Implements context-aware responses
- Falls back to "I cannot answer..." when information is not found

## Notes

- The system is designed to work with text-based PDF documents (scanned PDFs may require OCR)
- For optimal performance, ensure your documents are well-formatted and text is selectable
- The system will only answer questions based on the content of the loaded document
- Memory usage scales with document size due to embedding storage

## Troubleshooting

If you encounter a segmentation fault:
1. Ensure all dependencies are properly installed
2. Try running with `OMP_NUM_THREADS=1` environment variable
3. Check that your PDF is not corrupted and contains extractable text

## License

[Specify your license here]
