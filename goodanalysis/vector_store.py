"""
Vector Database Integration
Stores and retrieves transcripts using ChromaDB
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import os


class VectorStore:
    def __init__(self, collection_name: str = "youtube_transcripts", persist_directory: str = "./chroma_db"):
        """
        Initialize vector store with ChromaDB.

        Args:
            collection_name: Name of the collection to store transcripts
            persist_directory: Directory to persist the database
        """
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # Initialize local embedding model (runs locally, no API calls)
        # This is separate from the LLM used for answer generation
        print("Loading local embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Local embedding model loaded! (no API calls for embeddings)")

    def add_transcript(self, video_id: str, transcript_text: str, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Add transcript to vector store, chunking it for better retrieval.

        Args:
            video_id: YouTube video ID
            transcript_text: Full transcript text
            chunk_size: Number of characters per chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        # Split transcript into chunks
        chunks = self._chunk_text(transcript_text, chunk_size, chunk_overlap)

        # Generate embeddings
        embeddings = self.embedding_model.encode(chunks).tolist()

        # Create IDs and metadata
        ids = [f"{video_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "video_id": video_id,
                "chunk_index": i,
                "text": chunk
            }
            for i, chunk in enumerate(chunks)
        ]

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

        print(
            f"Added {len(chunks)} chunks from video {video_id} to vector store")

    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start = end - chunk_overlap

        return chunks

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search for similar transcript chunks.

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            List of dictionaries with 'text', 'video_id', 'chunk_index', and 'distance'
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()[0]

        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'video_id': results['metadatas'][0][i]['video_id'],
                    'chunk_index': results['metadatas'][0][i]['chunk_index'],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })

        return formatted_results

    def get_all_videos(self) -> List[str]:
        """
        Get list of all video IDs in the store.

        Returns:
            List of unique video IDs
        """
        all_data = self.collection.get()
        video_ids = set()
        if all_data['metadatas']:
            for metadata in all_data['metadatas']:
                video_ids.add(metadata['video_id'])
        return list(video_ids)

    def get_transcript(self, video_id: str) -> Optional[str]:
        """
        Get the full transcript text for a specific video by reassembling chunks.

        Args:
            video_id: YouTube video ID

        Returns:
            Full transcript text, or None if video not found
        """
        all_data = self.collection.get()
        video_chunks = []

        if all_data['metadatas']:
            for i, metadata in enumerate(all_data['metadatas']):
                if metadata['video_id'] == video_id:
                    video_chunks.append({
                        'text': all_data['documents'][i],
                        'chunk_index': metadata['chunk_index']
                    })

        if not video_chunks:
            return None

        # Sort by chunk index to maintain order
        video_chunks.sort(key=lambda x: x['chunk_index'])

        # Combine all chunks
        full_text = " ".join([chunk['text'] for chunk in video_chunks])

        return full_text
