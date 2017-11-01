from classes import *
from data import *
import copy
import traceback
import sys

def play(plays_count, start_chapter, max_chapter):

    mission_results = {} # mission ident: [count, count]
    total_mission_results = {} # chapter_index: [missions, missions]
    day_results = {} # chapter_index: [day, day]
    gold_results = {} # chapter_index: [gold, gold]

    print("-" * 30)
    for i in range(0, plays_count):
        game = load_game()
        sorted_keys = sorted(game.chapters.keys())
        player = load_player(game.chapters[sorted_keys[0]].recipes, game.items)
        for chapter_index in sorted(game.chapters.keys()):
            if chapter_index < start_chapter:
                continue
            if chapter_index == max_chapter + 1:
                break
            chapter_results = player.play_chapter(chapter_index)
            if chapter_index not in total_mission_results.keys():
                total_mission_results[chapter_index] = []
            total_mission_results[chapter_index].append(chapter_results[1])
            for mission in chapter_results[0].keys():
                if mission.ident not in mission_results:
                    mission_results[mission.ident] = []
                mission_results[mission.ident].append(chapter_results[0][mission])
            if chapter_index not in day_results.keys():
                day_results[chapter_index] = []
            day_results[chapter_index].append(player.day)
            if chapter_index not in gold_results.keys():
                gold_results[chapter_index] = []
            gold_results[chapter_index].append(player.gold)

    if len(total_mission_results) > 0 and len(day_results) > 0:
        for chapter_index in total_mission_results.keys():
            print("Chapter " + str(chapter_index) + ":")
            print("Missions, on average: " + str(sum(total_mission_results[chapter_index])/float(len(total_mission_results[chapter_index]))))
            print("-" * 10)
            for mission_ident in mission_results.keys():
                if str(mission_ident)[0] == str(chapter_index):
                    print(str(mission_ident) + ": " + str(sum(mission_results[mission_ident])/float(len(mission_results[mission_ident]))))                   
            print("-" * 10)
            print("Days, on average: " + str(sum(day_results[chapter_index])/float(len(day_results[chapter_index]))))
            print("Gold, on average: " + str(sum(gold_results[chapter_index])/float(len(gold_results[chapter_index]))))

while True:
    try:
        choice = input("Play again? y/n ")
        if choice == "n":
            break
        plays_count = int(input("How many times? "))
        start_chapter = int(input("From which chapter? "))
        max_chapter = int(input("Till what chapter? "))
        play(plays_count, start_chapter, max_chapter)
    except Exception:
        s = traceback.format_exc()
        serr = "there were errors:\n%s\n" % (s)
        sys.stderr.write(serr)

input("Press Enter to close")
