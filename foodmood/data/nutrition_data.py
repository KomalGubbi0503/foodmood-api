
#Internal nutrition dataset for common foods.

NUTRITION_PER_100G: dict[str, dict] = {
    # Proteins
    "egg": {"calories": 155, "protein_g": 13.0, "carbs_g": 1.1, "fat_g": 11.0},
    "chicken breast": {"calories": 165, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6},
    "salmon": {"calories": 208, "protein_g": 20.0, "carbs_g": 0.0, "fat_g": 13.0},
    "tuna": {"calories": 132, "protein_g": 29.0, "carbs_g": 0.0, "fat_g": 1.0},
    "beef": {"calories": 250, "protein_g": 26.0, "carbs_g": 0.0, "fat_g": 17.0},
    "tofu": {"calories": 76, "protein_g": 8.0, "carbs_g": 2.0, "fat_g": 4.5},
    "greek yogurt": {"calories": 59, "protein_g": 10.0, "carbs_g": 3.6, "fat_g": 0.4},
    "cottage cheese": {"calories": 98, "protein_g": 11.0, "carbs_g": 3.4, "fat_g": 4.3},
    # Carbs / grains
    "whole wheat bread": {"calories": 247, "protein_g": 9.0, "carbs_g": 46.0, "fat_g": 3.4},
    "white bread": {"calories": 265, "protein_g": 9.0, "carbs_g": 49.0, "fat_g": 3.2},
    "oats": {"calories": 389, "protein_g": 17.0, "carbs_g": 66.0, "fat_g": 7.0},
    "brown rice": {"calories": 216, "protein_g": 5.0, "carbs_g": 45.0, "fat_g": 1.8},
    "white rice": {"calories": 206, "protein_g": 4.3, "carbs_g": 45.0, "fat_g": 0.4},
    "pasta": {"calories": 371, "protein_g": 13.0, "carbs_g": 74.0, "fat_g": 1.5},
    "sweet potato": {"calories": 86, "protein_g": 1.6, "carbs_g": 20.0, "fat_g": 0.1},
    "potato": {"calories": 77, "protein_g": 2.0, "carbs_g": 17.0, "fat_g": 0.1},
    "quinoa": {"calories": 120, "protein_g": 4.4, "carbs_g": 22.0, "fat_g": 1.9},
    # Vegetables
    "avocado": {"calories": 160, "protein_g": 2.0, "carbs_g": 9.0, "fat_g": 15.0},
    "spinach": {"calories": 23, "protein_g": 2.9, "carbs_g": 3.6, "fat_g": 0.4},
    "broccoli": {"calories": 34, "protein_g": 2.8, "carbs_g": 7.0, "fat_g": 0.4},
    "carrot": {"calories": 41, "protein_g": 0.9, "carbs_g": 10.0, "fat_g": 0.2},
    "tomato": {"calories": 18, "protein_g": 0.9, "carbs_g": 3.9, "fat_g": 0.2},
    "cucumber": {"calories": 15, "protein_g": 0.7, "carbs_g": 3.6, "fat_g": 0.1},
    "bell pepper": {"calories": 31, "protein_g": 1.0, "carbs_g": 6.0, "fat_g": 0.3},
    "lettuce": {"calories": 15, "protein_g": 1.4, "carbs_g": 2.9, "fat_g": 0.2},
    "onion": {"calories": 40, "protein_g": 1.1, "carbs_g": 9.3, "fat_g": 0.1},
    "garlic": {"calories": 149, "protein_g": 6.4, "carbs_g": 33.0, "fat_g": 0.5},
    # Fruits
    "banana": {"calories": 89, "protein_g": 1.1, "carbs_g": 23.0, "fat_g": 0.3},
    "apple": {"calories": 52, "protein_g": 0.3, "carbs_g": 14.0, "fat_g": 0.2},
    "orange": {"calories": 47, "protein_g": 0.9, "carbs_g": 12.0, "fat_g": 0.1},
    "strawberry": {"calories": 32, "protein_g": 0.7, "carbs_g": 7.7, "fat_g": 0.3},
    "blueberry": {"calories": 57, "protein_g": 0.7, "carbs_g": 14.0, "fat_g": 0.3},
    # Fats / nuts / dairy
    "olive oil": {"calories": 884, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 100.0},
    "butter": {"calories": 717, "protein_g": 0.9, "carbs_g": 0.1, "fat_g": 81.0},
    "almonds": {"calories": 579, "protein_g": 21.0, "carbs_g": 22.0, "fat_g": 50.0},
    "peanut butter": {"calories": 588, "protein_g": 25.0, "carbs_g": 20.0, "fat_g": 50.0},
    "milk": {"calories": 42, "protein_g": 3.4, "carbs_g": 5.0, "fat_g": 1.0},
    "cheese": {"calories": 402, "protein_g": 25.0, "carbs_g": 1.3, "fat_g": 33.0},
    # Legumes
    "lentils": {"calories": 116, "protein_g": 9.0, "carbs_g": 20.0, "fat_g": 0.4},
    "chickpeas": {"calories": 164, "protein_g": 8.9, "carbs_g": 27.0, "fat_g": 2.6},
    "black beans": {"calories": 132, "protein_g": 8.9, "carbs_g": 24.0, "fat_g": 0.5},
}

# Standard unit weights in grams for quantity parsing
UNIT_WEIGHTS_G: dict[str, float] = {
    "egg": 50.0,
    "slice": 28.0,           # bread slice
    "cup": 240.0,
    "tbsp": 15.0,
    "tsp": 5.0,
    "handful": 30.0,
    "piece": 100.0,
    "medium": 130.0,
    "large": 180.0,
    "small": 80.0,
    "banana": 120.0,
    "apple": 180.0,
    "orange": 130.0,
}
