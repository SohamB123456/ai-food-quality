#!/usr/bin/env python3
"""
Test fuzzy matching with rapidfuzz
"""

from rapidfuzz import fuzz, process

# Test text from OCR
test_text = """ssise1 ubaseHeubauerasanis

Oroers _290720105490597
(ons tan iy 4, MRAP Us fe
'gates : AUIS, ot NO

cy
Joa

7
:¥ Poke Bowl = Roovter «2
Provetne) ——

rt nite aRece wks .
ans {Tune ~

v EN gaadee" BN

|. Cucwaper "

am 4) Suect corn

- Cdeneso .

Yoact Snore :

Ponzu. frasn

Waevy Fievor

Ur@eon Onion . '

Sescy Furtheake., , e
Sesevo Sesoe ~"""

# Sample ingredients
ingredients = ["Tuna", "Salmon", "Avocado", "Cucumber", "Corn", "Cilantro", "Sweet Onion", "Sesame Seeds", "Spicy Furikake", "Ponzu Fresh", "Light Flavor", "Poke Bowl"]

print("🧪 Testing Fuzzy Matching")
print("=" * 50)

lines = [line.strip() for line in test_text.split('\n') if line.strip()]

print(f"Processing {len(lines)} lines...")
print()

for line in lines:
    if len(line) > 2:
        print(f"Line: '{line}'")
        
        # Try different thresholds
        for threshold in [50, 60, 70, 80]:
            match, score, _ = process.extractOne(line, ingredients, scorer=fuzz.ratio)
            if score >= threshold:
                print(f"  Threshold {threshold}%: '{match}' (score: {score})")
        
        print()

# Test specific lines that should match
specific_lines = [
    "Poke Bowl = Roovter «2",
    "ans {Tune ~",
    "Cucwaper",
    "Suect corn",
    "Cdeneso",
    "Ponzu. frasn",
    "Waevy Fievor",
    "Ur@eon Onion",
    "Sescy Furtheake",
    "Sesevo Sesoe"
]

print("Testing specific lines:")
print("=" * 30)

for line in specific_lines:
    match, score, _ = process.extractOne(line, ingredients, scorer=fuzz.ratio)
    print(f"'{line}' -> '{match}' (score: {score})") 