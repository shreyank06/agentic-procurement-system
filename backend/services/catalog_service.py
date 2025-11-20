"""
Catalog Service - Abstraction layer for catalog operations.

Provides unified interface for catalog access and semantic search.
"""

from typing import List, Dict, Optional
import json
from pathlib import Path


class CatalogService:
    """Service for catalog operations and semantic search."""

    def __init__(self, catalog_path: str, enable_embeddings: bool = True, api_key: Optional[str] = None):
        """Initialize catalog service.

        Args:
            catalog_path: Path to catalog JSON file
            enable_embeddings: Whether to enable vector embeddings
            api_key: OpenAI API key for embeddings
        """
        from backend.core.catalog import Catalog

        self.catalog = Catalog(catalog_path, enable_embeddings=enable_embeddings, api_key=api_key)
        self.catalog_path = catalog_path

    def get_components(self) -> Dict:
        """Get available components with details.

        Returns:
            Dict with components and their metadata
        """
        all_items = self.catalog.items
        components = list(set(item["component"] for item in all_items))

        component_details = {}
        for comp in components:
            items = [item for item in all_items if item["component"] == comp]
            component_details[comp] = {
                "count": len(items),
                "vendors": list(set(item["vendor"] for item in items)),
                "price_range": [
                    min(item["price"] for item in items),
                    max(item["price"] for item in items)
                ]
            }

        return {
            "components": components,
            "details": component_details,
            "total_items": len(all_items)
        }

    def get_vendors(self) -> Dict:
        """Get available vendors with details.

        Returns:
            Dict with vendors and their metadata
        """
        vendors = list(self.catalog.list_vendors())

        vendor_details = {}
        for vendor in vendors:
            items = [item for item in self.catalog.items if item["vendor"] == vendor]
            vendor_details[vendor] = {
                "item_count": len(items),
                "components": list(set(item["component"] for item in items))
            }

        return {
            "vendors": vendors,
            "details": vendor_details,
            "total_vendors": len(vendors)
        }

    def search(self, component: str, spec_filters: Optional[Dict] = None) -> List[Dict]:
        """Search for items by component and optional spec filters.

        Args:
            component: Component type to search for
            spec_filters: Optional specification filters

        Returns:
            List of matching items
        """
        return self.catalog.search(component, spec_filters)

    def search_semantic(self, query: str, top_k: int = 5) -> List[Dict]:
        """Perform semantic search using embeddings.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of semantically similar items
        """
        return self.catalog.search_semantic(query, top_k=top_k)

    def find_cheaper_alternatives(self, item: Dict, top_k: int = 3) -> List[Dict]:
        """Find cheaper alternatives for an item.

        Args:
            item: Reference item
            top_k: Number of alternatives to return

        Returns:
            List of cheaper alternatives
        """
        alternatives = self.catalog.find_cheaper_alternatives(item)
        return alternatives[:top_k]

    def find_competing_products(self, item: Dict, top_k: int = 3) -> List[Dict]:
        """Find competing products from different vendors.

        Args:
            item: Reference item
            top_k: Number of competitors to return

        Returns:
            List of competing products
        """
        competitors = self.catalog.find_competing_products(item)
        return competitors[:top_k]

    def get_item(self, item_id: str) -> Optional[Dict]:
        """Get item by ID.

        Args:
            item_id: Item ID to look up

        Returns:
            Item dict or None if not found
        """
        return self.catalog.get(item_id)
