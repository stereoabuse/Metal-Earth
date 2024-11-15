import unittest
from pathlib import Path
from src.extract_nouns import extract_proper_nouns

class TestProperNounExtraction(unittest.TestCase):
    def test_basic_proper_noun_extraction(self):
        text = ["Frodo went to Mordor with Sam."]
        common_words = {"went", "to", "with"}
        
        result = extract_proper_nouns(text, common_words)
        self.assertEqual(result, {"Frodo", "Mordor", "Sam"})

    def test_plural_removal(self):
        text = ["The Hobbits lived in the Shire. Many Hobbit families were there."]
        common_words = {"the", "lived", "in", "many", "were", "there", "families"}
        
        result = extract_proper_nouns(text, common_words)
        self.assertIn("Hobbit", result)
        self.assertNotIn("Hobbits", result)
        self.assertIn("Shire", result)

    def test_case_standardization(self):
        text = ["GANDALF spoke to Elrond and FRODO"]
        common_words = {"spoke", "to", "and"}
        
        result = extract_proper_nouns(text, common_words)
        self.assertEqual(result, {"Gandalf", "Elrond", "Frodo"})

    def test_punctuation_removal(self):
        text = ["Gandalf!", "Frodo?", "Aragorn's", "Gimli,"]
        common_words = set()
        
        result = extract_proper_nouns(text, common_words)
        self.assertEqual(result, {"Gandalf", "Frodo", "Aragorn", "Gimli"})

if __name__ == '__main__':
    unittest.main()