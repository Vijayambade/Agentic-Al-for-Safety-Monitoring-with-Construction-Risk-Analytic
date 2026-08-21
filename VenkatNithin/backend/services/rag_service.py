"""
backend/services/rag_service.py
------------------------------
Vector database (FAISS) indexing and Retrieval-Augmented Generation (RAG) services.
"""
import json
import logging
import os
import pickle
from typing import List
import numpy as np

import faiss

logger = logging.getLogger(__name__)

# Load SentenceTransformer model lazily
_embedding_model = None


def get_embedding_model():
    """Lazily load the SentenceTransformer model to save memory on start."""
    global _embedding_model
    if _embedding_model is None:
        from backend.config import settings
        if not settings.embedding_model or settings.embedding_model.lower() in ["none", "local", "keyword"]:
            logger.info("Embedding model is set to keyword fallback. Skipping SentenceTransformer load.")
            return None
        try:
            logger.info("Initializing SentenceTransformer model 'all-MiniLM-L6-v2'...")
            # Set caching folder inside workspace to prevent permission issues
            os.environ["SENTENCE_TRANSFORMERS_HOME"] = "./data/cache/models"
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer(settings.embedding_model)
            logger.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.error("Failed to load SentenceTransformer model: %s", e)
            _embedding_model = None
    return _embedding_model


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """Split text into overlapping chunks for indexing."""
    if not text:
        return []
        
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
        
    # Ensure at least one chunk
    if not chunks:
        chunks = [text]
    return chunks


def create_vector_index(doc_id: int, text: str) -> str:
    """
    Chunk document text, compute embeddings, construct a FAISS index,
    and save the index and chunks metadata persistently to disk.
    """
    index_dir = "./data/faiss_indexes"
    os.makedirs(index_dir, exist_ok=True)

    index_path = os.path.join(index_dir, f"{doc_id}.index")
    chunks_path = os.path.join(index_dir, f"{doc_id}.chunks")

    chunks = chunk_text(text)
    
    # Save chunks mapping
    try:
        with open(chunks_path, "wb") as f:
            pickle.dump(chunks, f)
    except Exception as e:
        logger.error("Failed to write document chunks: %s", e)
        raise

    model = get_embedding_model()
    if model is None:
        logger.warning("No embedding model available. Saving chunks only; retrieval will use fallback.")
        return index_path

    try:
        # Generate embeddings
        embeddings = model.encode(chunks, show_progress_bar=False)
        embeddings_np = np.array(embeddings).astype("float32")
        
        # Dimensions for all-MiniLM-L6-v2 are 384
        dimension = embeddings_np.shape[1]
        
        # Create FAISS L2 index
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_np)
        
        # Write index to disk
        faiss.write_index(index, index_path)
        logger.info("FAISS index saved successfully for doc %s at %s", doc_id, index_path)
    except Exception as e:
        logger.error("Failed to compile FAISS index for doc %s: %s", doc_id, e)
        # We still return index_path, RAG will fallback to keyword matching
        
    return index_path


def retrieve_relevant_chunks(doc_id: int, query: str, top_k: int = 3) -> List[str]:
    """
    Retrieve top K matching text chunks for a query from a document's vector index.
    Falls back gracefully to keyword matching if the FAISS index or model is missing.
    """
    index_dir = "./data/faiss_indexes"
    index_path = os.path.join(index_dir, f"{doc_id}.index")
    chunks_path = os.path.join(index_dir, f"{doc_id}.chunks")

    # Load chunks metadata
    if not os.path.exists(chunks_path):
        logger.error("Document chunks file not found: %s", chunks_path)
        return []
        
    try:
        with open(chunks_path, "rb") as f:
            chunks = pickle.load(f)
    except Exception as e:
        logger.error("Error reading chunks file: %s", e)
        return []

    # Check model and index availability
    model = get_embedding_model()
    if model is None or not os.path.exists(index_path):
        logger.warning("Using keyword search fallback for RAG retrieval.")
        # Keyword-based scoring fallback
        query_words = set(query.lower().split())
        scored_chunks = []
        for idx, chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            score = sum(1 for word in query_words if word in chunk_lower)
            scored_chunks.append((score, idx))
            
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_indices = [idx for score, idx in scored_chunks[:top_k]]
        return [chunks[idx] for idx in top_indices]

    try:
        # Load index
        index = faiss.read_index(index_path)
        
        # Embed query
        query_vector = model.encode([query], show_progress_bar=False)
        query_vector_np = np.array(query_vector).astype("float32")
        
        # Search FAISS index
        distances, indices = index.search(query_vector_np, top_k)
        
        retrieved = []
        for idx in indices[0]:
            if 0 <= idx < len(chunks):
                retrieved.append(chunks[idx])
        return retrieved
    except Exception as e:
        logger.error("FAISS retrieval failed: %s. Using keyword fallback.", e)
        # Final safety fallback
        return chunks[:top_k]
