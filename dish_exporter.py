import csv
import json

def load_recipes():
    recipes_by_ru_names = {}
    with open('_validator_recipes.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row["NAME_RU"] not in recipes_by_ru_names.keys():
                recipes_by_ru_names[row["NAME_RU"]] = int(row["RECIPE_ID"])
    return recipes_by_ru_names

def load_ingredients():
    ingredients_by_ru_names = {}
    with open('_validator_ingredients.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row["_comment"] not in ingredients_by_ru_names.keys():
                ingredients_by_ru_names[row["_comment"]] = int(row["id"])
    return ingredients_by_ru_names

def load_dishes():
    dishes_by_ru_names = {}
    with open('_validator_dish.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row["_comment"] not in dishes_by_ru_names.keys():
                dishes_by_ru_names[row["_comment"]] = int(row["id"])
    return dishes_by_ru_names

def load_actions():
    all_actions = []
    with open('_validator_action.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            action = {'id': row["id"],
                      'type': row["type"],
                      'bonusPoints': row["bonusPoints"],
                      'pointsPerAction': row["pointsPerAction"],
                      'duration': int(row["duration"]),
                      'config': json.loads(row["config"]),
                      '_comment': row["_comment"]}
            all_actions.append(action)
    return all_actions

def make_recipes():
    all_items = {}
    with open('recipeLevels.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:            
            if row["DISH"] != "" and row["DISH"] != "end":
                first = True
                
    return strings
                
actions = load_actions()
print(actions[0])
