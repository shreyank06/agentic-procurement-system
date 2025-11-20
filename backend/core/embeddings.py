"""
Vector Embeddings Module - Manages semantic embeddings for catalog items and queries.

Provides:
- Embedding generation using OpenAI API
- Embedding caching to avoid repeated API calls
- Semantic similarity search using cosine similarity
- Integration with catalog for smart component discovery
"""

import json
import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np


class EmbeddingManager:
    """Manages embeddings for catalog items and semantic search."""

    def __init__(self, cache_dir: str = ".embeddings_cache", api_key: Optional[str] = None):
        """Initialize embedding manager.

        Args:
            cache_dir: Directory to cache embeddings
            api_key: OpenAI API key (uses environment variable if not provided)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.embeddings_cache = {}
        self._load_cache()

    def _load_cache(self):
        """Load cached embeddings from disk."""
        cache_file = self.cache_dir / "embeddings.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.embeddings_cache = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load embeddings cache: {e}")

    def _save_cache(self):
        """Save embeddings cache to disk."""
        try:
            cache_file = self.cache_dir / "embeddings.json"
            with open(cache_file, 'w') as f:
                json.dump(self.embeddings_cache, f)
        except Exception as e:
            print(f"Warning: Could not save embeddings cache: {e}")

    def _get_embedding(self, text: str, use_cache: bool = True) -> Optional[List[float]]:
        """Get embedding for text, using cache if available.

        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings

        Returns:
            Embedding vector or None if API not available
        """
        # Check cache first
        if use_cache and text in self.embeddings_cache:
            return self.embeddings_cache[text]

        # If no API key, return None (will fallback to keyword search)
        if not self.api_key:
            return None

        # Generate embedding using OpenAI API
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )

            embedding = response.data[0].embedding

            # Cache the embedding
            self.embeddings_cache[text] = embedding
            self._save_cache()

            return embedding
        except Exception as e:
            print(f"Warning: Could not generate embedding: {e}")
            return None

    def embed_items(self, items: List[Dict], key: str = "description") -> List[Dict]:
        """Generate embeddings for a list of items.

        Args:
            items: List of items with 'description' or specified key
            key: Key containing text to embed

        Returns:
            Items with added 'embedding' field
        """
        embedded_items = []
        for item in items:
            text = item.get(key, "")
            if not text:
                # Generate description from item data if not provided
                text = self._generate_description(item)

            embedding = self._get_embedding(text)
            item_copy = item.copy()
            if embedding:
                item_copy['embedding'] = embedding
            embedded_items.append(item_copy)

        return embedded_items

    def _generate_description(self, item: Dict) -> str:
        """Generate description for catalog item from its properties.

        Args:
            item: Catalog item

        Returns:
            Generated description string
        """
        parts = []

        if 'id' in item:
            parts.append(f"Item: {item['id']}")
        if 'component' in item:
            parts.append(f"Component type: {item['component']}")
        if 'vendor' in item:
            parts.append(f"Vendor: {item['vendor']}")
        if 'price' in item:
            parts.append(f"Price: ${item['price']}")
        if 'specs' in item and item['specs']:
            spec_str = ", ".join([f"{k}: {v}" for k, v in item['specs'].items()])
            parts.append(f"Specifications: {spec_str}")
        if 'reliability' in item:
            parts.append(f"Reliability: {item['reliability']}")
        if 'lead_time_days' in item:
            parts.append(f"Lead time: {item['lead_time_days']} days")

        return ". ".join(parts)

    def semantic_search(
        self,
        query: str,
        items: List[Dict],
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Tuple[Dict, float]]:
        """Perform semantic similarity search.

        Args:
            query: Search query
            items: Items to search (must have 'embedding' field)
            top_k: Number of top results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of (item, similarity_score) tuples, sorted by similarity
        """
        query_embedding = self._get_embedding(query)

        if not query_embedding:
            # Fallback to empty results if embeddings not available
            return []

        # Calculate similarity scores
        results = []
        for item in items:
            if 'embedding' not in item:
                continue

            similarity = self._cosine_similarity(query_embedding, item['embedding'])

            if similarity >= threshold:
                results.append((item, similarity))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def find_similar_items(
        self,
        item: Dict,
        items: List[Dict],
        top_k: int = 5,
        exclude_self: bool = True
    ) -> List[Tuple[Dict, float]]:
        """Find items similar to a given item.

        Args:
            item: Reference item (must have 'embedding' field)
            items: Items to search
            top_k: Number of results to return
            exclude_self: Whether to exclude the reference item

        Returns:
            List of (similar_item, similarity_score) tuples
        """
        if 'embedding' not in item:
            return []

        item_embedding = item['embedding']
        results = []

        for candidate in items:
            if 'embedding' not in candidate:
                continue

            # Skip self if requested
            if exclude_self and candidate.get('id') == item.get('id'):
                continue

            similarity = self._cosine_similarity(item_embedding, candidate['embedding'])
            results.append((candidate, similarity))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0-1)
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def find_cheaper_alternatives(
        self,
        item: Dict,
        items: List[Dict],
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """Find semantically similar items that are cheaper.

        Args:
            item: Reference item
            items: Items to search
            similarity_threshold: Minimum similarity for consideration

        Returns:
            List of cheaper alternatives, sorted by similarity
        """
        similar = self.find_similar_items(
            item,
            items,
            top_k=20,
            exclude_self=True
        )

        cheaper = [
            s_item for s_item, sim in similar
            if sim >= similarity_threshold and s_item.get('price', float('inf')) < item.get('price', 0)
        ]

        return cheaper

    def find_competing_products(
        self,
        item: Dict,
        items: List[Dict],
        similarity_threshold: float = 0.6
    ) -> List[Dict]:
        """Find competing products (similar but from different vendors).

        Args:
            item: Reference item
            items: Items to search
            similarity_threshold: Minimum similarity

        Returns:
            List of competing products from different vendors
        """
        similar = self.find_similar_items(
            item,
            items,
            top_k=20,
            exclude_self=True
        )

        competing = [
            s_item for s_item, sim in similar
            if sim >= similarity_threshold and s_item.get('vendor') != item.get('vendor')
        ]

        return competing
