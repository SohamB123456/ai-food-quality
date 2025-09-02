#!/usr/bin/env python3
"""
Fuzzy Matching Module
Advanced fuzzy string matching for ingredient comparison
"""

from fuzzywuzzy import fuzz, process
import re
from typing import List, Dict, Tuple, Optional

class IngredientMatcher:
    """
    Advanced ingredient matching using multiple fuzzy matching strategies
    """
    
    def __init__(self, ingredients_list: List[str]):
        """
        Initialize the matcher with a list of known ingredients
        
        Args:
            ingredients_list: List of known ingredients to match against
        """
        self.ingredients_list = [ingredient.lower().strip() for ingredient in ingredients_list]
        self.ingredients_list = list(set(self.ingredients_list))  # Remove duplicates
    
    def clean_ingredient_name(self, ingredient: str) -> str:
        """
        Clean and normalize ingredient names for better matching
        
        Args:
            ingredient: Raw ingredient name
            
        Returns:
            Cleaned ingredient name
        """
        # Convert to lowercase
        cleaned = ingredient.lower().strip()
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ['extra', 'additional', 'double', 'triple']
        suffixes_to_remove = ['(spicy)', '(mild)', '(hot)', '(extra)', '(double)']
        
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix + ' '):
                cleaned = cleaned[len(prefix):].strip()
        
        for suffix in suffixes_to_remove:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()
        
        # Remove special characters but keep spaces
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def find_best_match(self, ingredient: str, threshold: int = 80) -> Optional[Dict]:
        """
        Find the best match for an ingredient using multiple strategies
        
        Args:
            ingredient: Ingredient to match
            threshold: Minimum similarity score (0-100)
            
        Returns:
            Dictionary with match details or None if no good match found
        """
        cleaned_ingredient = self.clean_ingredient_name(ingredient)
        
        if not cleaned_ingredient:
            return None
        
        # Strategy 1: Exact match
        if cleaned_ingredient in self.ingredients_list:
            return {
                'matched_ingredient': cleaned_ingredient,
                'original_ingredient': ingredient,
                'confidence': 100,
                'strategy': 'exact'
            }
        
        # Strategy 2: Token sort ratio (handles word order differences)
        token_sort_match = process.extractOne(
            cleaned_ingredient, 
            self.ingredients_list, 
            scorer=fuzz.token_sort_ratio
        )
        
        # Strategy 3: Token set ratio (handles duplicates and word order)
        token_set_match = process.extractOne(
            cleaned_ingredient, 
            self.ingredients_list, 
            scorer=fuzz.token_set_ratio
        )
        
        # Strategy 4: Partial ratio (handles partial matches)
        partial_match = process.extractOne(
            cleaned_ingredient, 
            self.ingredients_list, 
            scorer=fuzz.partial_ratio
        )
        
        # Strategy 5: WRatio (weighted ratio combining multiple strategies)
        wrato_match = process.extractOne(
            cleaned_ingredient, 
            self.ingredients_list, 
            scorer=fuzz.WRatio
        )
        
        # Find the best match among all strategies
        matches = [
            ('token_sort', token_sort_match),
            ('token_set', token_set_match),
            ('partial', partial_match),
            ('wratio', wrato_match)
        ]
        
        best_match = None
        best_score = 0
        best_strategy = None
        
        for strategy, match in matches:
            if match and match[1] > best_score:
                best_score = match[1]
                best_match = match[0]
                best_strategy = strategy
        
        if best_score >= threshold:
            return {
                'matched_ingredient': best_match,
                'original_ingredient': ingredient,
                'confidence': best_score,
                'strategy': best_strategy
            }
        
        return None
    
    def match_ingredients(self, ingredients: List[str], threshold: int = 80) -> Dict:
        """
        Match a list of ingredients against known ingredients
        
        Args:
            ingredients: List of ingredients to match
            threshold: Minimum similarity score (0-100)
            
        Returns:
            Dictionary with matching results
        """
        matched = []
        unmatched = []
        
        for ingredient in ingredients:
            match_result = self.find_best_match(ingredient, threshold)
            if match_result:
                matched.append(match_result)
            else:
                unmatched.append({
                    'original_ingredient': ingredient,
                    'confidence': 0
                })
        
        return {
            'matched_ingredients': matched,
            'unmatched_ingredients': unmatched,
            'total_matched': len(matched),
            'total_unmatched': len(unmatched),
            'match_rate': len(matched) / len(ingredients) * 100 if ingredients else 0
        }
    
    def compare_ingredient_lists(self, list1: List[str], list2: List[str], threshold: int = 80) -> Dict:
        """
        Compare two lists of ingredients and find matches
        
        Args:
            list1: First list of ingredients
            list2: Second list of ingredients
            threshold: Minimum similarity score (0-100)
            
        Returns:
            Dictionary with comparison results
        """
        # Match list1 against list2
        matches_1_to_2 = []
        unmatched_1 = []
        
        for ingredient in list1:
            # Create temporary matcher for list2
            temp_matcher = IngredientMatcher(list2)
            match_result = temp_matcher.find_best_match(ingredient, threshold)
            
            if match_result:
                matches_1_to_2.append(match_result)
            else:
                unmatched_1.append(ingredient)
        
        # Match list2 against list1
        matches_2_to_1 = []
        unmatched_2 = []
        
        for ingredient in list2:
            # Create temporary matcher for list1
            temp_matcher = IngredientMatcher(list1)
            match_result = temp_matcher.find_best_match(ingredient, threshold)
            
            if match_result:
                matches_2_to_1.append(match_result)
            else:
                unmatched_2.append(ingredient)
        
        return {
            'list1_to_list2_matches': matches_1_to_2,
            'list2_to_list1_matches': matches_2_to_1,
            'list1_unmatched': unmatched_1,
            'list2_unmatched': unmatched_2,
            'total_matches': len(matches_1_to_2),
            'match_percentage': len(matches_1_to_2) / len(list1) * 100 if list1 else 0
        }

def load_ingredients_from_file(file_path: str) -> List[str]:
    """
    Load ingredients from a text file
    
    Args:
        file_path: Path to the ingredients file
        
    Returns:
        List of ingredients
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            ingredients = [line.strip() for line in f if line.strip()]
        return ingredients
    except FileNotFoundError:
        print(f"Warning: Ingredients file not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error loading ingredients file: {e}")
        return []

def main():
    """
    Example usage of the fuzzy matching module
    """
    # Load ingredients from file
    ingredients_file = "Ingredients.txt"
    known_ingredients = load_ingredients_from_file(ingredients_file)
    
    if not known_ingredients:
        print("No ingredients loaded. Please check Ingredients.txt file.")
        return
    
    print(f"Loaded {len(known_ingredients)} known ingredients")
    
    # Create matcher
    matcher = IngredientMatcher(known_ingredients)
    
    # Example: Match some test ingredients
    test_ingredients = [
        "White Rice",
        "Salmon",
        "Avocado",
        "Cucumber",
        "Spicy Tuna",
        "Brown Rice",
        "Seaweed Salad",
        "Unknown Ingredient"
    ]
    
    print(f"\nTesting ingredient matching:")
    print("=" * 50)
    
    for ingredient in test_ingredients:
        match_result = matcher.find_best_match(ingredient)
        if match_result:
            print(f"✅ '{ingredient}' -> '{match_result['matched_ingredient']}' "
                  f"(confidence: {match_result['confidence']}%, strategy: {match_result['strategy']})")
        else:
            print(f"❌ '{ingredient}' -> No match found")

if __name__ == "__main__":
    main()
