from classes import *
import csv

ENERGY_COST = 6

def load_items():
    all_items = {}
    with open('items.csv', 'rt', encoding="utf8") as csvfile:
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
            all_items[row["NAME"]] = Item(name=row["NAME"],
                                          recipe=recipe,
                                          gold_cost=gold_cost)
    return all_items      

def load_missions(all_items):
    all_missions = []

    with open('missions.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:                
            item_chances = {}
            for i in range(1, 4):
                if row["ITEM " + str(i)] != "":
                    item = all_items[row["ITEM " + str(i)]]
                    chance = float(row["CHANCE " + str(i)])
                    item_chances[item] = chance                
            all_missions.append(
                Mission(name=row["NAME"],
                        chapter=row["CHAPTER"],
                        reward=Reward(item_chances=item_chances,
                                gold_reward=int(row["GOLD_REWARD"])),
                        energy_cost=ENERGY_COST,
                        keys_cost=int(row["KEYS_COST"])))
    return all_missions

def load_quests(all_items):
    all_quests = []

    with open('quests.csv', 'rt', encoding="utf8") as csvfile:
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
            for quest in all_quests:
                for quest_name in quest_names:
                    if quest.name == quest_name:
                        required_quests.append(quest)
            all_quests.append(
                Quest(name=row["NAME"],
                      chapter=row["CHAPTER"],
                      item_conditions=item_conditions,
                      reward=Reward({},
                                  gold_reward=int(row["GOLD_REWARD"]),
                                  energy_reward=int(row["ENERGY_REWARD"]),
                                  keys=int(row["KEYS"])),
                      required_quests=required_quests))
    return all_quests

def load_chapters(items, missions, quests):
    all_chapters = []
    with open('chapters.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row["NAME"] != "":
                all_chapters.append(
                    Chapter(name=row["NAME"],
                            items=items,
                            missions=missions,
                            quests=quests))
    return all_chapters            

def load_player():
    with open('player.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[0] == "HEADER":
                continue
            if row[0] == "MAX_DAILY_ENERGY":
                max_daily_energy = int(row[1])
            if row[0] == "STARTING_GOLD":
                gold = int(row[1])                
        player = Player(max_daily_energy=max_daily_energy,
                        gold=gold)
    return player

def load_game():
    items = load_items()
    missions = load_missions(items)
    quests = load_quests(items)
    chapters = load_chapters(items, missions, quests)
    game = Game(items, missions, quests)
    return game


