"""
RAG (Retrieval Augmented Generation) System
Combines vector search with context for answering questions
"""
from goodanalysis.vector_store import VectorStore
from typing import List, Dict, Optional
import os


class RAGSystem:
    def __init__(self, vector_store: VectorStore, llm_provider: str = "openai", model_name: Optional[str] = None):
        """
        Initialize RAG system with OpenAI for answer generation.

        Note: Embeddings are handled locally by VectorStore using sentence-transformers.
        OpenAI is only used for generating answers from retrieved context.

        Args:
            vector_store: Initialized VectorStore instance (uses local embeddings)
            llm_provider: LLM provider to use ("openai" or "none" for no LLM)
            model_name: OpenAI model name (default: gpt-4o-mini)
        """
        self.vector_store = vector_store
        self.llm_provider = llm_provider.lower()
        self.model_name = model_name

        # Set default model
        if self.model_name is None:
            if self.llm_provider == "openai":
                self.model_name = "gpt-4o-mini"  # Fast and cost-effective

        # Initialize OpenAI client (only for answer generation, not embeddings)
        self.llm_client = None
        if self.llm_provider == "openai":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print(
                        "⚠️  OPENAI_API_KEY not set. Set it as an environment variable.")
                    print(
                        "   You can set it with: export OPENAI_API_KEY='your-key-here'")
                    self.llm_provider = "none"
                else:
                    self.llm_client = OpenAI(api_key=api_key)
            except ImportError:
                print("⚠️  OpenAI not available. Install with: uv sync")
                self.llm_provider = "none"
        elif self.llm_provider not in ["openai", "none"]:
            print(
                f"⚠️  Unsupported LLM provider: {self.llm_provider}. Using 'none'.")
            self.llm_provider = "none"

        if self.llm_provider != "none" and self.llm_client:
            print(
                f"✅ Using {self.llm_provider.upper()} with model: {self.model_name}")
        else:
            print(
                "⚠️  No LLM configured. Using simple retrieval mode (no answer generation).")

    def query(self, question: str, n_context_chunks: int = 3) -> Dict:
        """
        Answer a question using RAG.

        Args:
            question: User's question
            n_context_chunks: Number of context chunks to retrieve

        Returns:
            Dictionary with 'answer', 'context_chunks', and 'sources'
        """
        # Retrieve relevant context
        context_chunks = self.vector_store.search(
            question, n_results=n_context_chunks)

        if not context_chunks:
            return {
                'answer': "I couldn't find relevant information in the transcripts to answer your question.",
                'context_chunks': [],
                'sources': []
            }

        # Build context string
        context_text = "\n\n".join([
            f"[Video: {chunk['video_id']}, Chunk {chunk['chunk_index']}]\n{chunk['text']}"
            for chunk in context_chunks
        ])

        # Generate answer using LLM if available
        if self.llm_provider != "none" and self.llm_client:
            answer = self._generate_answer_with_llm(question, context_text)
        else:
            # Fallback: return most relevant chunk
            answer = f"Based on the transcripts, here's what I found:\n\n{context_chunks[0]['text']}"
            if len(context_chunks) > 1:
                answer += f"\n\nAdditional context:\n"
                for chunk in context_chunks[1:]:
                    answer += f"\n- {chunk['text'][:200]}...\n"

        return {
            'answer': answer,
            'context_chunks': context_chunks,
            'sources': list(set([chunk['video_id'] for chunk in context_chunks]))
        }

    def _generate_answer_with_llm(self, question: str, context: str) -> str:
        """
        Generate answer using the configured LLM.

        Args:
            question: User's question
            context: Retrieved context from transcripts

        Returns:
            Generated answer
        """
        prompt = f"""Based on the following transcript excerpts from YouTube videos, please answer the question.

Context from transcripts:
{context}

Question: {question}

Please provide a clear, concise answer based only on the information provided in the transcripts. If the transcripts don't contain enough information to answer the question, say so."""

        try:
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on provided transcript excerpts from YouTube videos. Provide clear, concise answers based only on the information in the transcripts."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️  Error generating answer with LLM: {e}")
            return f"Error generating answer. Here's the relevant context:\n\n{context[:500]}..."

    def get_summary(self, video_id: str) -> str:
        """
        Get a summary of all chunks for a specific video.

        Args:
            video_id: YouTube video ID

        Returns:
            Summary text
        """
        # Search for all chunks from this video
        all_data = self.vector_store.collection.get()
        video_chunks = []

        if all_data['metadatas']:
            for i, metadata in enumerate(all_data['metadatas']):
                if metadata['video_id'] == video_id:
                    video_chunks.append({
                        'text': all_data['documents'][i],
                        'chunk_index': metadata['chunk_index']
                    })

        # Sort by chunk index
        video_chunks.sort(key=lambda x: x['chunk_index'])

        # Combine all chunks
        full_text = " ".join([chunk['text'] for chunk in video_chunks])

        return full_text
