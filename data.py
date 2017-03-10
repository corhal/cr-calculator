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
                all_items[row[1]] = Item(row[1], recipe)
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
                all_missions.append(Mission(int(row[1]), Reward(reward_items), ENERGY_COST, int(row[8])))
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
                all_quests.append(Quest(row[1], item_conditions, Reward({}, int(row[8])), required_quests))
    return all_quests
   
