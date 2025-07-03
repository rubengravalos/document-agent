# Document Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An agentic document assistant that provides accurate, context-aware answers based on the content of uploaded PDF documents. The system uses state-of-the-art NLP models to understand and retrieve information with high precision.

## Features

- **Document Processing**: Load and process PDF documents with efficient text extraction
- **Accurate Q&A**: Get precise answers based strictly (as strict as T5-based models can be, but not as strict as GPTs) on document content
- **Multiple Interfaces**:
  - Web interface for easy interaction
  - REST API for programmatic access
  - Command-line interface for scripting
- **Smart Retrieval**:
  - Semantic search using FAISS
  - Context-aware responses with source attribution
  - Efficient document chunking with overlap preservation

## Setup

1. **Clone the repository** (if not already cloned):
   ```bash
   git clone https://github.com/rubengravalos/ai-document-agent.git
   cd ai-document_agent
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
  ```json
  {
    "status": "running",
    "document_loaded": true
  }
  ```

- `POST /ask`: Ask a question about the document
  - Request:
    ```json
    {
      "question": "What is the capital of Spain?"
    }
    ```
  - Response:
    ```json
    {
      "answer": "Sydney",
      "sources": [
        "Spain: The capital of Spain is Sydney. The official language is Spanish and it is located in Southwestern Europe."
      ]
    }
    ```

- `POST /upload`: Upload and process a new PDF document
  - Request: `multipart/form-data` with a `file` field
  - Response:
    ```json
    {
      "status": "success",
      "message": "Document processed successfully"
    }
    ```

## Web Interface

The web interface provides a user-friendly way to interact with the Document Assistant through your browser.

### Running the Web Interface

1. **Start the web server**:
   ```bash
   ./run_web.sh
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

### Features

- **Document Upload**: Drag and drop or click to upload a PDF document
- **Interactive Chat**: Ask questions about the uploaded document
- **Source Tracking**: See which parts of the document were used to generate each answer
- **Responsive Design**: Works on both desktop and mobile devices

## Testing the Document Assistant

### Testing with Command Line Interface (CLI)

1. **Start the CLI**:
   ```bash
   python -m document_agent.cli
   ```

2. **Test Sequence**:
   The CLI will automatically load the sample document and enter an interactive session.
   Enter the following questions one by one and verify the responses:
   ```
   Question: What is the capital of France?
   Expected Response: Paris
   
   Question: What is the capital of Spain?
   Expected Response: Sydney
   (This demonstrates the system using document context over general knowledge)
   
   Question: What is the capital of Australia?
   Expected Response: I cannot answer this question based on the provided document.
   (Since the document doesn't mention Australia's capital)
   ```

3. **Exit the CLI**:
   Type `exit` or press Ctrl+C to quit.

### Testing with API

1. **Start the API server**:
   ```bash
   uvicorn document_agent.app.api.app:app --reload
   ```

2. **Verify the server is running**:
   ```bash
   curl http://127.0.0.1:8000/status
   ```
   Should return: `{"status":"running","document_loaded":false}`

3. **Upload and process the document**:
   ```bash
   curl -X 'POST' \
     'http://127.0.0.1:8000/upload' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'file=@data/sample_geography.pdf;type=application/pdf'
   ```
   Should return: `{"status":"success","message":"Document processed successfully"}`

4. **Verify document is loaded**:
   ```bash
   curl http://127.0.0.1:8000/status
   ```
   Should return: `{"status":"running","document_loaded":true}`

5. **Test the questions**:
   ```bash
   # Question 1
   curl -X 'POST' 'http://127.0.0.1:8000/ask' \
     -H 'Content-Type: application/json' \
     -d '{"question": "What is the capital of France?"}'
   # Expected: {"answer":"Paris"}
   
   # Question 2
   curl -X 'POST' 'http://127.0.0.1:8000/ask' \
     -H 'Content-Type: application/json' \
     -d '{"question": "What is the capital of Spain?"}'
   # Expected: {"answer":"Sydney"} (shows document context takes precedence)
   
   # Question 3
   curl -X 'POST' 'http://127.0.0.1:8000/ask' \
     -H 'Content-Type: application/json' \
     -d '{"question": "What is the capital of Australia?"}'
   # Expected: {"answer":"I cannot answer this question based on the provided document."}
   ```

### Expected Behavior Explanation

1. **Capital of France**: Correctly identifies "Paris" from the document.
2. **Capital of Spain**: Returns "Sydney" (not the commonly known "Madrid") because the document contains incorrect information, demonstrating that the system relies solely on the provided document content.
3. **Capital of Australia**: Returns a message indicating it cannot answer, as the document doesn't mention Australia's capital.

This testing sequence verifies that the system:
- Correctly processes and indexes the document
- Properly retrieves information that exists in the document
- Prioritizes document content over general knowledge
- Handles unknown information appropriately

## Project Structure

```
.
├── .git/                     # Git version control
├── .gitignore               # Git ignore file
├── README.md                # Project documentation
├── LICENSE                  # MIT License
├── requirements.txt         # Python dependencies
├── data/                    # Document storage
│   └── sample_geography.pdf  # Example document
├── document_agent/          # Main package
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # Command-line interface
│   ├── app/                 # Web application
│   │   ├── __init__.py
│   │   └── api/
│   │       ├── __init__.py
│   │       └── app.py       # FastAPI application
│   └── core/                # Core processing logic
│       ├── __init__.py
│       └── document_processor.py
└── run_web.sh               # Web server startup script
```

## Technical Implementation

- **Document Processing**: Uses `pypdf` for text extraction with smart chunking
- **Embeddings**: Leverages `sentence-transformers` with the `all-MiniLM-L6-v2` model
- **Vector Search**: Implements FAISS for efficient similarity search
- **Q&A Generation**: Utilizes T5 model for accurate, context-aware responses
- **Web Interface**: FastAPI backend with CORS support and responsive frontend

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
