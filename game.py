from classes import *
from data import *
import copy

mission_results = []
day_results = []

print("-" * 30)
for i in range(0, 500):    
    items = load_items()
    missions = load_missions(items)
    quests = load_quests(items)
    player = Player(444, missions)
    if not player.choose_quest(quests):
        break
    mission_results.append(player.missions_completed)
    day_results.append(player.day)

if len(mission_results) > 0 and len(day_results) > 0:
    print("Missions, on average: " + str(sum(mission_results)/float(len(mission_results))))
    print("Days, on average: " + str(sum(day_results)/float(len(day_results))))
