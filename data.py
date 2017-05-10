from classes import *
import csv
import time

ENERGY_COST = 6

def load_items():
    #start_time = time.time()
    all_items = {}
    with open('_validator_items.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            recipe = {}
            for i in range(1, 4):
                if row["COMPONENT " + str(i)] != "":
                    component = all_items[row["COMPONENT " + str(i)]]
                    amount = int(row["AMOUNT " + str(i)])
                    recipe[component] = amount
            if recipe == {}:
                recipe = None
            gold_cost = 0
            if row["GOLD_COST"] != "":
                gold_cost = int(row["GOLD_COST"])
            if row["NAME"] in all_items.keys():
                raise ValueError("Duplicate item " + row["NAME"] +
                                 " in table 'items'!")
            all_items[row["NAME"]] = Item(ident=row["ID"],
                                          name=row["NAME"],
                                          recipe=recipe,
                                          gold_cost=gold_cost,
                                          asset=row["ASSET"],
                                          is_fragment=row["IS FRAGMENT"])
    #print("--- %s to load items ---" % (time.time() - start_time))
    return all_items

def load_chest(all_items):
    full_drop_list = {} # Reward: (chapter, weight)
    with open('_validator_chest.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            reward = Reward({all_items[row["ITEM"]]: 1},
                            item_amounts = {all_items[row["ITEM"]]: int(row["AMOUNT"])},
                            gold_reward=int(row["GOLD_REWARD"]),
                            energy_reward=int(row["ENERGY_REWARD"]))
            chapter_id = int(row["CHAPTER"])
            weight = int(row["WEIGHT"])
            full_drop_list[reward] = (chapter_id, weight)
    return Chest(full_drop_list)

def load_missions(all_items, all_recipes, all_quests):
    all_missions = []
    def find_recipe(name, recipes):
        for recipe in recipes:
            if recipe.name == name:
                return recipe

    def find_quest(name, quests):
        for quest in quests:
            if quest.name == name:
                return quest

    with open('_validator_missions.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            item_chances = {}
            for i in range(1, 4):
                if row["ITEM " + str(i)] != "":
                    item = all_items[row["ITEM " + str(i)]]
                    chance = float(row["CHANCE " + str(i)])
                    item_chances[item] = chance
            recipe_levels = {}
            for i in range(1, 4):
                if row["RECIPE " + str(i)] != "":
                    recipe = find_recipe(row["RECIPE " + str(i)], all_recipes)
                    level = int(row["RLEVEL " + str(i)])
                    recipe_levels[recipe] = level

            quest_names = row["REQUIREMENT"].split(',')
            quests = []
            for quest_name in quest_names:
                if quest_name != "":
                    req_quest = find_quest(quest_name, all_quests)
                    if req_quest == None:
                        raise ValueError("Mission " + row["ID"] + " is locked"
                                         + " on quest " + quest_name + ","
                                         + " but the quest does not exist")
                    quests.append(req_quest)

            all_missions.append(
                Mission(ident=row["ID"],
                        name=row["NAME"],
                        chapter=row["CHAPTER"],
                        reward=Reward(item_chances=item_chances,
                                gold_reward=int(row["GOLD_REWARD"])),
                        energy_cost=ENERGY_COST,
                        requirement=Requirement(quests=quests),
                        recipe_levels=recipe_levels))
    return all_missions

def load_quests(all_items):
    all_quests = []

    with open('_validator_quests.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            item_conditions = {}
            for i in range(1, 4):
                if row["ITEM " + str(i)] != "":
                    item = all_items[row["ITEM " + str(i)]]
                    amount = int(row["AMOUNT " + str(i)])
                    item_conditions[item] = amount
            required_quests = []
            quest_names = row["REQUIRED_QUESTS"].split(",")
            if row["NAME"] in quest_names:
                raise ValueError(row["NAME"] + " is locked on itself")
            for quest in all_quests:
                if quest.name == row["NAME"]:
                    raise ValueError("Duplicate quest " + row["NAME"]
                                     + " in table quests!")
                for quest_name in quest_names:
                    if quest.name == quest_name:
                        required_quests.append(quest)
            try:
                keys=int(row["KEYS"])
            except ValueError:
                keys=0

            all_quests.append(
                Quest(ident=row["ID"],
                      name=row["NAME"],
                      chapter=row["CHAPTER"],
                      quest_chain=row["QUEST_CHAIN"],
                      item_conditions=item_conditions,
                      reward=Reward({},
                                  gold_reward=int(row["GOLD_REWARD"]),
                                  energy_reward=int(row["ENERGY_REWARD"]),
                                  keys=keys),
                      required_quests=required_quests))
    return all_quests

def load_chapters(items, missions, quests, recipes):
    all_chapters = {}
    with open('_validator_chapters.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row["NAME"] != "":
                all_chapters[int(row["NAME"])] = Chapter(name=row["NAME"],
                                                        items=items,
                                                        missions=missions,
                                                        quests=quests,
                                                        recipes=recipes)
    return all_chapters

def load_recipes(all_items):
    all_recipes = []
    recipes_by_names = {}
    with open('_validator_recipes.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row["NAME"] not in recipes_by_names:
                recipes_by_names[row["NAME"]] = [[int(row["LEVEL"]),
                                                  int(row["GOLD_REWARD"]),
                                                  int(row["UPGRADE_FRAGMENTS"]),
                                                  int(row["UPGRADE_GOLD"]),
                                                  int(row["RECIPE_ID"])]]
            else:
                recipes_by_names[row["NAME"]].append([int(row["LEVEL"]),
                                                      int(row["GOLD_REWARD"]),
                                                      int(row["UPGRADE_FRAGMENTS"]),
                                                      int(row["UPGRADE_GOLD"]),
                                                      int(row["RECIPE_ID"])])
        for name in recipes_by_names.keys():
            gold_by_levels = {}
            frag_item = all_items[name + " recipe"]
            up_frags_by_levels = {}
            up_gold_by_levels = {}

            for level_array in recipes_by_names[name]:
                level = level_array[0]
                gold_by_levels[level] = level_array[1]
                up_frags_by_levels[level] = level_array[2]
                up_gold_by_levels[level] = level_array[3]
                recipe_id = level_array[4]

            all_recipes.append(Recipe(recipe_id, name, gold_by_levels, frag_item,
                                      up_frags_by_levels, up_gold_by_levels))
    return all_recipes

def load_player(recipes, all_items):
    with open('_validator_player.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[0] == "HEADER":
                continue
            if row[0] == "ENERGY_CAP":
                energy_cap = int(row[1])
            if row[0] == "STARTING_GOLD":
                gold = int(row[1])
            if row[0] == "DAILY_SESSIONS":
                daily_sessions = int(row[1])
            if row[0] == "MINUTES_PER_ENERGY":
                mins_per_en = int(row[1])
            if row[0] == "TIME_BETWEEN_SESSIONS":
                time_between_sessions = int(row[1])

        player = Player(energy_cap=energy_cap,
                        daily_sessions=daily_sessions,
                        mins_per_en=mins_per_en,
                        time_between_sessions=time_between_sessions,
                        gold=gold,
                        recipes=recipes,
                        chest=load_chest(all_items))
    return player

def load_game():
    items = load_items()
    recipes = load_recipes(items)
    quests = load_quests(items)
    missions = load_missions(items, recipes, quests)
    chapters = load_chapters(items, missions, quests, recipes)
    with open('_validator_player.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[0] == "FIRST_MISSION_100_CHANCE":
                first_mission_100_chance = row[1].lower() == "true"
    game = Game(items=items,
                recipes=recipes,
                missions=missions,
                quests=quests,
                chapters=chapters,
                first_mission_100_chance=first_mission_100_chance)
    return game
