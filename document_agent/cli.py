#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from typing import Optional

from document_agent.core.document_processor import DocumentProcessor

def main():
    """Run the document assistant in command-line mode."""
    # Get the absolute path to the sample PDF
    current_dir = Path(__file__).parent
    sample_pdf = current_dir.parent / "data" / "sample_geography.pdf"
    
    if not sample_pdf.exists():
        print(f"Error: Sample PDF not found at {sample_pdf}")
        print("Please make sure to place 'sample_geography.pdf' in the data/ directory.")
        sys.exit(1)
    
    print("Initializing Document Assistant...")
    try:
        # Initialize the document processor
        processor = DocumentProcessor()
        
        # Load and index the document
        print("Loading and processing the document...")
        processor.load_document(str(sample_pdf))
        processor.create_index()
        
        print("\nDocument loaded and ready for questions!")
        print("Type 'exit' or 'quit' to end the session.\n")
        
        # Interactive question loop
        while True:
            try:
                question = input("\nYour question: ").strip()
                
                if question.lower() in ('exit', 'quit'):
                    print("Goodbye!")
                    break
                    
                if not question:
                    continue
                    
                # Get and display the answer
                answer, _ = processor.answer_question(question)
                print(f"\nAnswer: {answer}")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                
    except Exception as e:
        print(f"Failed to initialize the document assistant: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
