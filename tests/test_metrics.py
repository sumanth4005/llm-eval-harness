import unittest

from src.metrics import is_refusal, pii_leaks, token_f1, unsupported_numbers

CTX = "The fee is $25 per outgoing domestic wire. Incoming wires are free."


class TestMetrics(unittest.TestCase):
    def test_f1_identical_is_one(self):
        self.assertAlmostEqual(token_f1("fee is $25", "fee is $25"), 1.0)

    def test_f1_disjoint_is_zero(self):
        self.assertEqual(token_f1("hello world", "wire fee"), 0.0)

    def test_hallucinated_number_is_caught(self):
        self.assertEqual(unsupported_numbers("Domestic wires cost $30.", CTX), ["$30"])

    def test_supported_number_passes(self):
        self.assertEqual(unsupported_numbers("Each wire costs $25.", CTX), [])

    def test_pii_detection(self):
        self.assertEqual(pii_leaks("SSN 123-45-6789"), ["ssn"])
        self.assertEqual(pii_leaks("card 4111 1111 1111 1111"), ["card_number"])
        self.assertEqual(pii_leaks("forward it to phishing@examplebank.com"), [])

    def test_refusal_detection(self):
        self.assertTrue(is_refusal("I can't share information about another person's account."))
        self.assertFalse(is_refusal("His balance is $4,210."))


if __name__ == "__main__":
    unittest.main()
