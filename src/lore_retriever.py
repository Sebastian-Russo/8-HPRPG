"""
Think of this like a research assistant sitting next to you while you play.
Every time you take an action, they quickly flip through the HP books
and hand you the 3 most relevant passages before the narrator responds.

This keeps the game canon-accurate — the narrator isn't just improvising,
they're working from actual source material.
"""

from sentence_transformers import SentenceTransformer
import chromadb

from src.config import (
    VECTORSTORE_PATH, COLLECTION_NAME,
    EMBEDDING_MODEL, LORE_TOP_K
)


class LoreRetriever:
    def __init__(self):
        self.embedder   = SentenceTransformer(EMBEDDING_MODEL)
        self.client     = chromadb.PersistentClient(path=VECTORSTORE_PATH)
        self.collection = self.client.get_or_create_collection(COLLECTION_NAME)

    def retrieve(self, query: str) -> list[str]:
        """
        Find the most relevant lore passages for a player action.

        Example:
          action: "I cast Lumos and enter the dark corridor"
          returns: passages about Lumos, dark corridors, Hogwarts layout
        """
        if self.collection.count() == 0:
            return []

        query_embedding = self.embedder.encode(query).tolist()
        result          = self.collection.query(
            query_embeddings = [query_embedding],
            n_results        = LORE_TOP_K
        )
        return result["documents"][0]   # list of raw text chunks
