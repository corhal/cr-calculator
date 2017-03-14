from classes import *
import csv

ENERGY_COST = 6

def load_items():
    all_items = {}
    with open('items.csv', 'rt', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                if row[0] == "HEADER":
                    continue
                recipe = {}
                for i in range(2, 7, 2):                
                    if row[i] != "":
                        recipe[all_items[row[i]]] = int(row[i + 1])
                if recipe == {}:
                    recipe = None
                gold_cost = 0
                if row[8] != "":
                    gold_cost = int(row[8])
                all_items[row[1]] = Item(row[1], recipe, gold_cost)
    return all_items

def load_missions(all_items):
    all_missions = []

    with open('missions.csv', 'rt', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                if row[0] == "HEADER":
                    continue
                reward_items = {}
                for i in range(2, 7, 2):
                    reward_items[all_items[row[i]]] = float(row[i + 1])                
                all_missions.append(Mission(row[1], Reward(reward_items, gold_reward=int(row[8])), ENERGY_COST, int(row[9])))
    return all_missions

def load_quests(all_items):
    all_quests = []

    with open('quests.csv', 'rt', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                if row[0] == "HEADER":
                    continue
                item_conditions = {}
                for i in range(2, 7, 2):
                    if row[i] != "":
                        item_conditions[all_items[row[i]]] = int(row[i + 1])
                required_quests = []
                quest_strings = row[9].split(",")
                for quest in all_quests:
                    for quest_string in quest_strings:
                        if quest.name == quest_string:
                            required_quests.append(quest)
                all_quests.append(Quest(row[1], item_conditions, Reward({}, gold_reward=int(row[8]), energy_reward=int(row[9]), keys=int(row[10])), required_quests))
    return all_quests

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
            player = Player(max_daily_energy, gold)
    return player

def load_game():
    items = load_items()
    missions = load_missions(items)
    quests = load_quests(items)
    game = Game(items, missions, quests)
    return game


