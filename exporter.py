from data import *
import csv

def write_items():
    items = load_items()
    with open('_export_items.csv', 'wt', encoding="utf8", newline='') as csvfile:
        fieldnames = ['id', 'asset', 'readOnly', 'cost', 'config', '_comment']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        writer.writeheader()
        for key in items:
            item = items[key]
            ident = item.ident
            asset = ''
            readOnly = '0'
            config = ''
            item_str = ''
            cost = ''
            if item.recipe != None:
                count = 0
                goal_count = len(item.recipe.keys())
                for component in item.recipe.keys():
                    count += 1
                    item_str += '{"id": ' + str(component.ident) + ', "amount": ' + str(item.recipe[component]) + '}'
                    if count < goal_count:
                        item_str += ', '
                gold_str = '"gold": ' + str(item.gold_cost)
                cost = '{"item":[' + item_str + '], ' + gold_str + '}'
            comment = item.name
            writer.writerow({'id': ident,
                             'asset': asset,
                             'readOnly': readOnly,
                             'cost': cost,
                             'config': config,
                             '_comment': comment})

def write_missions():
    missions = load_missions(load_items())
    with open('_export_missions.csv', 'wt', encoding="utf8", newline='') as csvfile:
        fieldnames = ['id', 'chapterId', 'main', 'requirements', 'recipes',
                      'fixedReward', 'garbageCoeff', 'possibleReward',
                      'cost', 'config', '_comment']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        writer.writeheader()
        for mission in missions:
            ident = mission.ident
            chapterId = mission.chapter
            main = ''
            requirements = ''
            if mission.keys_cost != 0:
                requirements = '{"region": [{"id": ' + str(mission.ident) + ', "status": 1}]}'
            recipes = ''
            fixedReward = '{"gold": ' + str(mission.reward.gold_reward) + '}'
            garbageCoeff = '0.5'
            possibleReward = '['  
            if mission.reward.item_chances != None:
                count = 0
                goal_count = len(mission.reward.item_chances.keys())
                for item in mission.reward.item_chances.keys():
                    count += 1
                    possibleReward += '{"item": ' + str(item.ident) + ', "prob": ' + str(mission.reward.item_chances[item]) + '}'
                    if count < goal_count:
                        possibleReward += ', '
            possibleReward += ']'
            cost= '{"refillable": [{"id" : 1, "amount" :' + str(ENERGY_COST) + '}]}'
            config = ''
            comment = mission.name
            writer.writerow({'id': ident,
                             'chapterId': chapterId,
                             'main': main,
                             'requirements': requirements,
                             'recipes': recipes,
                             'fixedReward': fixedReward,
                             'garbageCoeff': garbageCoeff,
                             'possibleReward': possibleReward,
                             'cost': cost,
                             'config': config,
                             '_comment': comment})
            
        with open('_export_regions.csv', 'wt', encoding="utf8", newline='') as csvfile:
            fieldnames = ['id', 'chapter', 'cost', 'missionId']
            writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

            writer.writeheader()
            for mission in missions:
                ident = mission.ident
                chapter = mission.chapter
                cost = ''
                if mission.keys_cost != 0:
                    cost = '{"item": [{"id": 4, "amount": ' + str(mission.keys_cost) + '}]}'
                missionId = mission.ident
                writer.writerow({'id': ident,
                                 'chapter': chapter,                             
                                 'cost': cost,
                                 'missionId': missionId})

def write_quests():     
    quests = load_quests(load_items())
    with open('_export_quests.csv', 'wt', encoding="utf8", newline='') as csvfile:
        fieldnames = ['id', 'chapterId', 'questChain',
                      'requirements', 'cost', 'reward', '_comment']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        writer.writeheader()
        for quest in quests:
            ident = quest.ident
            chapterId = quest.chapter
            questChain = quest.quest_chain
            
            requirements = '{'
            if quest.required_quests != None:
                count = 0
                goal_count = len(quest.required_quests)
                for r_quest in quest.required_quests:
                    count += 1
                    requirements += '"quest": [{"id": ' + str(r_quest.ident) + ', "status": 3}]'
                    if count < goal_count:
                        requirements += ', '
            requirements += '}'
            
            cost = '{'
            if quest.item_conditions != None:
                count = 0
                goal_count = len(quest.item_conditions.keys())
                cost += '"item" : ['
                for item in quest.item_conditions.keys():
                    count += 1
                    cost += '{"id" : ' + str(item.ident) + ', "amount" : ' + str(quest.item_conditions[item]) + '}'
                    if count < goal_count:
                        cost += ', '
                cost += ']'
            cost += '}'

            reward = '{'
            q_reward = quest.reward
            if q_reward.gold_reward != 0:
                reward += '"gold": ' + str(q_reward.gold_reward)
            if q_reward.energy_reward != 0:
                if q_reward.gold_reward != 0:
                    reward += ', '
                reward += '"refillable": [{"id": 1, "amount": ' + str(q_reward.energy_reward) + '}]'
            if q_reward.keys != 0:
                if q_reward.gold_reward != 0 or q_reward.energy_reward != 0:
                    reward += ', '
                reward += '"item": [{"id": 4, "amount": ' + str(q_reward.keys) + '}]'
            reward += '}'

            comment = quest.name

            writer.writerow({'id': ident,
                             'chapterId': chapterId,                             
                             'questChain': questChain,
                             'requirements': requirements,
                             'cost': cost,
                             'reward': reward,
                             '_comment': comment})

write_quests()
