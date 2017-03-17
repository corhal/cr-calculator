from classes import *
from data import *
import copy
import traceback
import sys

def play(plays_count):

    mission_results = []
    day_results = []

    print("-" * 30)
    for i in range(0, plays_count):
        game = load_game()
        player = load_player(Game.recipes)
        player.choose_quest()
        mission_results.append(player.missions_completed)
        day_results.append(player.day)

    if len(mission_results) > 0 and len(day_results) > 0:
        print("Missions, on average: " + str(sum(mission_results)/float(len(mission_results))))
        print("Days, on average: " + str(sum(day_results)/float(len(day_results))))

while True:
    try:
        choice = input("Play again? y/n ")
        if choice == "n":
            break
        plays_count = int(input("How many times? "))
        play(plays_count)
    except Exception:
        s = traceback.format_exc()
        serr = "there were errors:\n%s\n" % (s)
        sys.stderr.write(serr) 

input("Press Enter to close")
