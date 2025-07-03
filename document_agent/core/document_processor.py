from typing import List, Tuple
import numpy as np
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from faiss import IndexFlatL2, IndexIDMap
from transformers import T5ForConditionalGeneration, T5Tokenizer
import os

class DocumentProcessor:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the document processor with the specified embedding model."""
        # Initialize with explicit CPU usage to avoid MPS issues
        import torch
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        print(f"Using device: {self.device}")
        print("Initializing embedding model...")
        self.embedding_model = SentenceTransformer(model_name, device=self.device)
        self.index = None
        self.text_chunks = []
        self.llm = None
        self.tokenizer = None
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the language model for question answering."""
        model_name = "google/flan-t5-base"
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.llm = T5ForConditionalGeneration.from_pretrained(model_name)

    def load_document(self, file_path: str) -> List[str]:
        """Load and split the document into chunks."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found at {file_path}")

        # Extract text from PDF
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        # Split text into chunks
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunk_size=100,
            chunk_overlap=20,
            length_function=len
        )
        
        self.text_chunks = splitter.split_text(text)
        return self.text_chunks

    def create_index(self):
        """Create a FAISS index from the document chunks."""
        if not self.text_chunks:
            raise ValueError("No document loaded. Please load a document first.")

        print("Generating embeddings...")
        # Generate embeddings with explicit batch processing
        batch_size = 8  # Smaller batch size to avoid memory issues
        text_embeddings = []
        
        for i in range(0, len(self.text_chunks), batch_size):
            batch = self.text_chunks[i:i + batch_size]
            embeddings = self.embedding_model.encode(
                batch,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=True
            )
            text_embeddings.extend(embeddings)
            
        text_embeddings = np.array(text_embeddings)
        
        print("Creating FAISS index...")
        # Create FAISS index with more robust configuration
        import faiss
        embedding_dimension = text_embeddings.shape[1]
        
        # Use a flat index for better compatibility
        index = faiss.IndexFlatIP(embedding_dimension)  # Using Inner Product for normalized embeddings
        
        # Convert to float32 if needed (required by FAISS)
        if text_embeddings.dtype != np.float32:
            text_embeddings = text_embeddings.astype('float32')
            
        # Add vectors to index
        index.add(text_embeddings)
        
        self.index = index
        print(f"Created FAISS index with {index.ntotal} vectors")
        return index

    def answer_question(self, question: str, top_k: int = 2) -> Tuple[str, List[str]]:
        """
        Answer a question based on the document content.
        
        Args:
            question: The question to answer
            top_k: Number of chunks to retrieve for context
            
        Returns:
            Tuple of (answer, list of context chunks used)
        """
        if not self.index or not self.text_chunks:
            raise ValueError("No document loaded or index created. Please load a document and create an index first.")

        try:
            print(f"Processing question: {question}")
            
            # Get query embedding
            query_embedding = self.embedding_model.encode(
                [question],
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            
            if query_embedding.dtype != np.float32:
                query_embedding = query_embedding.astype('float32')
            
            # Search for similar chunks
            print("Searching for relevant chunks...")
            distances, indices = self.index.search(query_embedding, top_k)
            
            # Get the actual text chunks
            retrieved_chunks = [self.text_chunks[i] for i in indices[0]]
            
            # Generate answer using the language model
            context = " ".join(retrieved_chunks)
            prompt = (
                "Only using the following context (do not use your own knowledge), "
                "answer the question. If the answer is not strictly in the context, say 'I cannot answer this question "
                f"based on the provided document.'\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:"
            )
            
            print("Generating answer...")
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            ).to(self.device)
            
            outputs = self.llm.generate(
                **inputs,
                max_length=150,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                top_k=50,
                top_p=0.95,
                temperature=0.3,  # Lower temperature for more focused answers
                do_sample=True
            )
            
            answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"Generated answer: {answer}")
            return answer, retrieved_chunks
            
        except Exception as e:
            print(f"Error answering question: {str(e)}")
            raise
