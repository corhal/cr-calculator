from classes import *
from data import *
import copy
import traceback
import sys

def play(plays_count):

    mission_results = {} # chapter_index: [missions, missions]
    day_results = {} # chapter_index: [day, day]
    gold_results = {} # chapter_index: [gold, gold]

    print("-" * 30)
    for i in range(0, plays_count):
        game = load_game()
        player = load_player(game.chapters[1].recipes)
        for chapter_index in game.chapters.keys():
            chapter_results = player.play_chapter(chapter_index)
            if chapter_index not in mission_results.keys():
                mission_results[chapter_index] = []
            mission_results[chapter_index].append(chapter_results[0])
            if chapter_index not in day_results.keys():
                day_results[chapter_index] = []
            day_results[chapter_index].append(player.day)
            if chapter_index not in gold_results.keys():
                gold_results[chapter_index] = []
            gold_results[chapter_index].append(player.gold)

    if len(mission_results) > 0 and len(day_results) > 0:
        for chapter_index in mission_results.keys():
            print("Chapter " + str(chapter_index) + ":")
            print("Missions, on average: " + str(sum(mission_results[chapter_index])/float(len(mission_results[chapter_index]))))
            print("Days, on average: " + str(sum(day_results[chapter_index])/float(len(day_results[chapter_index]))))
            print("Gold, on average: " + str(sum(gold_results[chapter_index])/float(len(gold_results[chapter_index]))))

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
