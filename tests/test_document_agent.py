#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

def print_header(text):
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, '='))
    print("=" * 80 + "\n")

def test_document_processor():
    print_header("Starting Document Processor Test")
    
    try:
        from document_agent.core.document_processor import DocumentProcessor
        
        # Get the path to the sample PDF
        sample_pdf = Path(__file__).parent.parent / "data" / "sample_geography.pdf"
        
        if not sample_pdf.exists():
            raise FileNotFoundError(
                f"Sample PDF not found at {sample_pdf}\n"
                "Please make sure to place 'sample_geography.pdf' in the data/ directory."
            )
        
        print(f"Using PDF: {sample_pdf}")
        
        # Initialize the processor
        print("Initializing DocumentProcessor...")
        processor = DocumentProcessor()
        
        # Load the document
        print("\nLoading document...")
        processor.load_document(str(sample_pdf))
        print(f"Loaded {len(processor.text_chunks)} text chunks")
        
        # Create the index
        print("\nCreating document index...")
        processor.create_index()
        
        # Test questions
        test_questions = [
            "What is the capital of France?",
            "What is the capital of Spain?",
            "What is the capital of Australia?"
        ]
        
        print_header("Running Test Questions")
        
        for i, question in enumerate(test_questions, 1):
            try:
                print(f"\n{'='*40}")
                print(f"Question {i}: {question}")
                answer, context_chunks = processor.answer_question(question)
                print(f"\nAnswer: {answer}")
                print("\nContext used:")
                for j, chunk in enumerate(context_chunks, 1):
                    print(f"{j}. {chunk[:100]}..." if len(chunk) > 100 else f"{j}. {chunk}")
            except Exception as e:
                print(f"\n❌ Error processing question: {str(e)}")
                traceback.print_exc()
                return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Create the data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    print(f"Test data directory: {data_dir}")
    print("Make sure to place 'sample_geography.pdf' in this directory before running the tests.")
    
    try:
        # Run the test
        success = test_document_processor()
        
        if success:
            print_header("✅ All Tests Passed!")
        else:
            print_header("❌ Some Tests Failed")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
