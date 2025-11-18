import unittest
from catalog import Catalog  # Assuming catalog.py is the file where Catalog class is defined


class TestCatalog(unittest.TestCase):

    def setUp(self):
        catalog_path = 'catalog.json'
        self.catalog = Catalog(catalog_path)

    def test_search(self):
        # Test without filters
        solar_panels = self.catalog.search("solar_panel")
        self.assertEqual(len(solar_panels), 2)

        # Test with spec filters
        results = self.catalog.search("solar_panel", {"power_w": 140})
        self.assertEqual(len(results), 2)

        results = self.catalog.search("solar_panel", {"power_w": 180})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "SP-200")

    def test_get(self):
        item = self.catalog.get("SP-100")
        self.assertIsNotNone(item)
        self.assertEqual(item["id"], "SP-100")

        item = self.catalog.get("INVALID-ID")
        self.assertIsNone(item)


if __name__ == '__main__':
    unittest.main()