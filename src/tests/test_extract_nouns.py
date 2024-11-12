import pytest
from pathlib import Path
from ..extract_nouns import extract_proper_nouns

def test_basic_proper_noun_extraction():
    text = ["Frodo went to Mordor with Sam."]
    common_words = {"went", "to", "with"}
    
    result = extract_proper_nouns(text, common_words)
    assert result == {"Frodo", "Mordor", "Sam"}

def test_plural_removal():
    text = ["The Hobbits lived in the Shire. Many Hobbit families were there."]
    common_words = {"the", "lived", "in", "many", "were", "there", "families"}
    
    result = extract_proper_nouns(text, common_words)
    assert "Hobbit" in result
    assert "Hobbits" not in result
    assert "Shire" in result

def test_case_standardization():
    text = ["GANDALF spoke to Elrond and FRODO"]
    common_words = {"spoke", "to", "and"}
    
    result = extract_proper_nouns(text, common_words)
    assert result == {"Gandalf", "Elrond", "Frodo"}

def test_punctuation_removal():
    text = ["Gandalf!", "Frodo?", "Aragorn's", "Gimli,"]
    common_words = set()
    
    result = extract_proper_nouns(text, common_words)
    assert result == {"Gandalf", "Frodo", "Aragorn", "Gimli"}