def normalize_unit(unit):
    unit = unit.lower().strip()

    mapping = {
        "گرم": "gram",
        "g": "gram",
        "gram": "gram",
        "grams": "gram",

        "عدد": "piece",
        "piece": "piece",
        "pieces": "piece",

        "لیوان": "glass",
        "glass": "glass",
        "cup": "cup",
        "cups": "cup",

        "بشقاب": "plate",
        "plate": "plate",

        "قاشق": "tablespoon",
        "قاشق غذاخوری": "tablespoon",
        "tablespoon": "tablespoon",
        "tablespoons": "tablespoon",
        "tbsp": "tablespoon",

        "قاشق چایخوری": "teaspoon",
        "teaspoon": "teaspoon",
        "teaspoons": "teaspoon",
        "tsp": "teaspoon",

        "اسکوپ": "scoop",
        "scoop": "scoop",

        "پیمانه": "cup",
        "برش": "slice",
        "slice": "slice",

        "قوطی": "can",
        "can": "can",
    }

    return mapping.get(unit, unit)


def convert_to_grams(food, quantity, unit):
    food = food.lower().strip()
    unit = normalize_unit(unit)

    if unit == "gram":
        return quantity

    unit_weights = {
        ("egg", "piece"): 50,
        ("rice", "plate"): 250,
        ("pasta", "plate"): 300,
        ("milk", "glass"): 250,
        ("water", "glass"): 250,
        ("banana", "piece"): 120,
        ("apple", "piece"): 180,
        ("orange", "piece"): 150,

        ("bread", "slice"): 30,
        ("toast bread", "slice"): 30,
        ("barbari bread", "slice"): 80,
        ("sangak bread", "slice"): 100,
        ("lavash bread", "piece"): 35,

        ("strawberry jam", "tablespoon"): 20,
        ("strawberry jam", "teaspoon"): 7,
        ("jam", "tablespoon"): 20,
        ("jam", "teaspoon"): 7,

        ("honey", "tablespoon"): 21,
        ("honey", "teaspoon"): 7,
        ("peanut butter", "tablespoon"): 16,
        ("peanut butter", "teaspoon"): 5,

        ("whey protein", "scoop"): 30,
        ("protein powder", "scoop"): 30,

        ("tuna", "can"): 150,
        ("beans", "can"): 240,
        ("chickpeas", "can"): 240,

        ("rice", "cup"): 160,
        ("oats", "cup"): 80,
        ("flour", "cup"): 120,
    }

    return quantity * unit_weights.get((food, unit), 0)
