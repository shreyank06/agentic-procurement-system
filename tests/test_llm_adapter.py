import unittest
from unittest.mock import patch, Mock
from llm_adapter import LLMAdapter, MockLLM

class TestLLMAdapter(unittest.TestCase):

    def setUp(self):
        self.mock_llm = MockLLM()

    def test_generate_method(self):
        # Test that MockLLM generates deterministic output
        prompt = "Selected item: SP-100"
        result1 = self.mock_llm.generate(prompt)
        result2 = self.mock_llm.generate(prompt)

        # Should be deterministic
        self.assertEqual(result1, result2)

        # Should return a string
        self.assertIsInstance(result1, str)
        self.assertGreater(len(result1), 0)

    def test_generate_with_details(self):
        # Test with more detailed prompt
        prompt = """Selected item details:
ID: SP-100
Vendor: Helios Dynamics
Price: 4800
Lead Time: 21 days
Reliability: 0.985
"""
        result = self.mock_llm.generate(prompt)

        # Should contain some key information
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 10)

    def test_generate_choose_between(self):
        # Test with "choose between" phrase requirement
        # SP-100: price=4800, lead_time=21, reliability=0.985
        # SP-200: price=5200, lead_time=14, reliability=0.975
        # SP-100 should score higher (lower price, higher reliability)
        prompt = """Please choose between these two items:
ID: SP-100
Vendor: Helios Dynamics
Price: 4800
Lead Time: 21 days
Reliability: 0.985

ID: SP-200
Vendor: Astra Components
Price: 5200
Lead Time: 14 days
Reliability: 0.975
"""
        result = self.mock_llm.generate(prompt)

        # Should return a string with justification
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

        # Should cite the required factors
        result_lower = result.lower()
        # Price mentioned as "cost" or "price"
        self.assertTrue(
            "cost" in result_lower or "price" in result_lower,
            "Should cite price/cost"
        )
        self.assertIn("reliability", result_lower, "Should cite reliability")

        # CRITICAL: Should prefer higher-scoring item (SP-100)
        # SP-100: better price (4800 vs 5200) + better reliability (0.985 vs 0.975)
        self.assertIn("sp-100", result_lower,
                     "Should prefer SP-100 (better price and reliability)")
        self.assertNotIn("sp-200", result_lower,
                        "Should NOT select SP-200 (higher price, lower reliability)")

        # Should be deterministic
        result2 = self.mock_llm.generate(prompt)
        self.assertEqual(result, result2, "Should be deterministic")

        # Verify it handles "choose between" without error
        self.assertTrue(len(result) > 20, "Should generate meaningful response")

if __name__ == "__main__":
    unittest.main()