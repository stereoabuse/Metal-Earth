def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein (edit) distance between two strings.
    This counts the minimum number of single-character edits needed to change one string into another.
    
    Args:
        s1: First string
        s2: Second string
    
    Returns:
        Number of edits needed to transform s1 into s2
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Damerau-Levenshtein distance between two strings.
    Like Levenshtein, but also counts transposition of adjacent characters as one operation.
    This catches typos where letters are swapped (like 'Gandalf' vs 'Gandlaf').
    
    Args:
        s1: First string
        s2: Second string
    
    Returns:
        Number of edits needed to transform s1 into s2, counting adjacent swaps as one edit
    """
    d = {}
    len1 = len(s1)
    len2 = len(s2)
    
    for i in range(-1, len1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len2 + 1):
        d[(-1, j)] = j + 1
        
    for i in range(len1):
        for j in range(len2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,      # deletion
                d[(i, j - 1)] + 1,      # insertion
                d[(i - 1, j - 1)] + cost  # substitution
            )
            
            if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)  # transposition

    return d[len1 - 1, len2 - 1]

def get_ngrams(s: str, n: int) -> set:
    """
    Generate character n-grams from a string.
    E.g., for 'hello' with n=2, returns {'he', 'el', 'll', 'lo'}
    
    Args:
        s: Input string
        n: Size of each n-gram
    
    Returns:
        Set of n-grams
    """
    return set(s[i:i+n] for i in range(len(s) - n + 1))

def dice_coefficient(s1: str, s2: str, n: int = 2) -> float:
    """
    Calculate Dice coefficient between two strings using character n-grams.
    This measures how many character groups they share.
    
    Args:
        s1: First string
        s2: Second string
        n: Size of n-grams to use
    
    Returns:
        Similarity score between 0 and 1
    """
    if not s1 or not s2:
        return 0.0
    
    # Get n-grams for each string
    ngrams1 = get_ngrams(s1, n)
    ngrams2 = get_ngrams(s2, n)
    
    # Calculate intersection and union
    intersection = len(ngrams1.intersection(ngrams2))
    
    # Dice coefficient formula
    return 2.0 * intersection / (len(ngrams1) + len(ngrams2))

def are_similar(name1: str, name2: str, 
                max_distance: int = 2, 
                min_dice_score: float = 0.7) -> bool:
    """
    Determine if two names are similar using multiple metrics.
    
    Args:
        name1: First name
        name2: Second name
        max_distance: Maximum edit distance to consider similar
        min_dice_score: Minimum dice coefficient to consider similar
    
    Returns:
        True if names are considered similar
    """
    # Convert to lowercase for comparison
    name1 = name1.lower()
    name2 = name2.lower()
    
    # Quick length check - if lengths differ too much, not similar
    if abs(len(name1) - len(name2)) > max_distance:
        return False
    
    # Check Damerau-Levenshtein distance (catches typos and swaps)
    if damerau_levenshtein_distance(name1, name2) <= max_distance:
        return True
        
    # Check dice coefficient (catches similar character patterns)
    if dice_coefficient(name1, name2) >= min_dice_score:
        return True
    
    return False

def find_similar_names(search_name: str, name_list: list, 
                      max_distance: int = 2,
                      min_dice_score: float = 0.7) -> list:
    """
    Find all similar names in a list.
    
    Args:
        search_name: Name to search for
        name_list: List of names to search through
        max_distance: Maximum edit distance to consider similar
        min_dice_score: Minimum dice coefficient to consider similar
    
    Returns:
        List of similar names found
    """
    return [
        name for name in name_list 
        if are_similar(search_name, name, max_distance, min_dice_score)
    ]

# Example usage:
if __name__ == "__main__":
    # Some example Tolkien-inspired band name variations
    test_names = [
        "Gandalf", "Gandlaf", "Gandalv",  # Typos
        "Morgoth", "Morgot", "Morgath",   # Similar names
        "Nazgul", "Nazgül", "Nasghul",    # Special characters and phonetic variations
        "Sauron", "Sawron", "Sauryn"      # Various alterations
    ]
    
    # Test each similarity function
    search_name = "Gandalf"
    similar = find_similar_names(search_name, test_names)
    print(f"\nNames similar to {search_name}:")
    for name in similar:
        print(f"- {name} (Distance: {damerau_levenshtein_distance(search_name.lower(), name.lower())}, "
              f"Dice: {dice_coefficient(search_name.lower(), name.lower()):.2f})")