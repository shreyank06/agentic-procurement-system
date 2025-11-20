"""
Catalog module - Hardware component catalog and search functionality.

Provides efficient loading and searching of mission hardware components,
including both structured search (by component type and specs) and semantic
search (free-text query with embedding-based ranking).

Key exports:
  - Catalog: Main catalog class with search, get, and semantic search methods
"""

import json
import hashlib
from typing import List, Set, Dict, Union, Optional
from backend.core.embeddings import EmbeddingManager


class Catalog:
    """
    Catalog component for managing hardware component inventory.

    Loads and provides search/query capabilities over a catalog of
    mission hardware components from vendors.
    """

    def __init__(self, catalog_path: str, enable_embeddings: bool = True, api_key: Optional[str] = None):
        """
        Load catalog from JSON file.

        Args:
            catalog_path: Path to the catalog JSON file
            enable_embeddings: Whether to enable vector embeddings
            api_key: Optional OpenAI API key for embeddings
        """
        with open(catalog_path, 'r') as f:
            self.items = json.load(f)

        self.embedding_manager = None
        if enable_embeddings:
            try:
                self.embedding_manager = EmbeddingManager(api_key=api_key)
                # Generate embeddings for all items if not cached
                self.items = self.embedding_manager.embed_items(self.items)
            except Exception as e:
                print(f"Warning: Could not initialize embeddings: {e}")

    def search(self, component: str, spec_filters: Dict[str, Union[int, float]] = None) -> List[Dict]:
        """
        Search for items by component type and optional spec filters.

        Args:
            component: Component type to search for (e.g., "solar_panel")
            spec_filters: Optional dict of numeric spec constraints.
                         Items must have specs >= all filter values.
                         Example: {"power_w": 140} returns items with power_w >= 140

        Returns:
            List of matching item dicts
        """
        results = []

        for item in self.items:
            # Check component type match
            if item.get("component") != component:
                continue

            # Check spec filters if provided
            if spec_filters:
                specs = item.get("specs", {})
                matches_all = True

                for spec_key, min_value in spec_filters.items():
                    item_value = specs.get(spec_key)
                    # Item must have the spec and it must be >= filter value
                    if item_value is None or item_value < min_value:
                        matches_all = False
                        break

                if not matches_all:
                    continue

            results.append(item)

        return results

    def get(self, item_id: str) -> Union[Dict, None]:
        """
        Get item by ID.

        Args:
            item_id: The item ID to look up (e.g., "SP-100")

        Returns:
            Item dict if found, None otherwise
        """
        for item in self.items:
            if item.get("id") == item_id:
                return item
        return None

    def list_vendors(self) -> Set[str]:
        """
        Get unique vendor names from catalog.

        Returns:
            Set of unique vendor names
        """
        vendors = set()
        for item in self.items:
            vendor = item.get("vendor")
            if vendor:
                vendors.add(vendor)
        return vendors

    def _text_to_embedding(self, text: str, dim: int = 8) -> List[float]:
        """
        Deterministic embedding function using hash.

        Args:
            text: Text to embed
            dim: Dimension of embedding vector

        Returns:
            List of float values (normalized)
        """
        hash_bytes = hashlib.md5(text.lower().encode()).digest()
        embedding = []
        for i in range(dim):
            byte_val = hash_bytes[i % len(hash_bytes)]
            embedding.append(byte_val / 255.0)
        return embedding

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Compute cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score in [-1, 1]
        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot_product / (mag1 * mag2)

    def search_semantic(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Semantic search using embeddings.

        Args:
            query: Free-text search query
            top_k: Number of results to return

        Returns:
            List of items sorted by semantic similarity
        """
        # Use embedding manager if available
        if self.embedding_manager:
            results = self.embedding_manager.semantic_search(query, self.items, top_k=top_k)
            return [item for item, score in results]

        # Fallback to deterministic hash-based embeddings
        query_embedding = self._text_to_embedding(query)
        scored_items = []

        for item in self.items:
            item_text = f"{item.get('component', '')} {item.get('vendor', '')} {item.get('id', '')}"
            specs = item.get('specs', {})
            for key, value in specs.items():
                item_text += f" {key} {value}"

            item_embedding = self._text_to_embedding(item_text)
            similarity = self._cosine_similarity(query_embedding, item_embedding)
            scored_items.append((similarity, item))

        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored_items[:top_k]]

    def find_similar_items(self, item: Dict, top_k: int = 5) -> List[Dict]:
        """Find items similar to a given item using semantic embeddings.

        Args:
            item: Reference item
            top_k: Number of similar items to return

        Returns:
            List of similar items
        """
        if not self.embedding_manager or 'embedding' not in item:
            return []

        results = self.embedding_manager.find_similar_items(item, self.items, top_k=top_k)
        return [s_item for s_item, score in results]

    def find_cheaper_alternatives(self, item: Dict) -> List[Dict]:
        """Find semantically similar items that are cheaper.

        Args:
            item: Reference item

        Returns:
            List of cheaper alternatives
        """
        if not self.embedding_manager or 'embedding' not in item:
            return []

        return self.embedding_manager.find_cheaper_alternatives(item, self.items)

    def find_competing_products(self, item: Dict) -> List[Dict]:
        """Find competing products from different vendors.

        Args:
            item: Reference item

        Returns:
            List of competing products
        """
        if not self.embedding_manager or 'embedding' not in item:
            return []

        return self.embedding_manager.find_competing_products(item, self.items)