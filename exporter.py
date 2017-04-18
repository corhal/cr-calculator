from data import *
import csv

def export_items():
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

def export_missions():
    quests = load_quests(load_items())
    missions = load_missions(load_items(), load_recipes(load_items()), quests)
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
            if len(mission.requirement.quests) > 0:
                requirements = '{"region": [{"id": ' + str(mission.ident) + ', "status": 1}]}'
                
            recipes = '['
            count = 0
            goal_count = len(mission.recipe_levels.keys())
            for recipe in mission.recipe_levels.keys():
                count += 1
                recipes += '{"recipe": ' + str(recipe.recipe_id) + ', "level": ' + str(mission.recipe_levels[recipe]) + '}'
                if count != goal_count:
                    recipes += ', '                
            recipes += ']'
            
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
                #if mission.keys_cost != 0:
                    #cost = '{"item": [{"id": 4, "amount": ' + str(mission.keys_cost) + '}]}'
                missionId = mission.ident
                writer.writerow({'id': ident,
                                 'chapter': chapter,                             
                                 'cost': cost,
                                 'missionId': missionId})

def export_quests():     
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
            #if q_reward.keys != 0:
                #if q_reward.gold_reward != 0 or q_reward.energy_reward != 0:
                    #reward += ', '
                #reward += '"item": [{"id": 4, "amount": ' + str(q_reward.keys) + '}]'
            reward += '}'

            comment = quest.name

            writer.writerow({'id': ident,
                             'chapterId': chapterId,                             
                             'questChain': questChain,
                             'requirements': requirements,
                             'cost': cost,
                             'reward': reward,
                             '_comment': comment})

def find_quest(quest_name, quests):
    for quest in quests:
        if quest_name == quest.name:
            return quest

def export_translation(last_id):
    quests = load_quests(load_items())

    name_col = 0
    order_col = 0
    person_col = 0
    text_col = 0
    resp_col = 0

    translations = {} # ident : text
    orders = {} # name : [ord, ord, ord]    
    dialogues = {} # ident: [q_id, char, message, order, orientation, responces]
    
    with open('_validator_dialogues.csv', 'rt', encoding="utf8") as csvfile:        
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        
        for row in reader:
            if row[0] == "HEADER":
                name_col = row.index("QUEST")
                order_col = row.index("ORDER")
                person_col = row.index("PERSON")
                text_col = row.index("TEXT")
                resp_col = row.index("RESPONSES")                
                continue            
            if row[name_col] != "":
                text_count = 0
                quest = find_quest(row[name_col], quests)
                orders[quest.name] = [0]
                
            if row[order_col] == "before":
                order = "before"

            if row[order_col] == "after":
                order = "after"               
                text_count = 0

            if row[person_col] != "":
                if order == "before":
                    text_count -= 1
                if order == "after":
                    text_count += 1
                orders[quest.name].append(text_count)
    
        csvfile.seek(0)                
        for key in orders.keys():
            orders[key].sort()
        
        for row in reader:  
            if row[0] == "HEADER":
                d_id = last_id
                continue
            
            if row[resp_col] == "":
                continue

            if row[name_col] != "":
                abs_count = 0
                quest = find_quest(row[name_col], quests)
                ord_list = orders[quest.name]

            if 0 in orders[quest.name]:
                d_id += 1
                ident = 'QUEST_' + str(quest.ident) + '_DIALOG_000'
                translations[ident] = "briefing"
                dialogues[d_id] = [str(quest.ident), row[person_col], ident, str(0), "left", []]
                del(orders[quest.name][orders[quest.name].index(0)])
            
            if len(orders[quest.name]) > 0 and row[text_col] != "":
                order_count = orders[quest.name][0]
                del(orders[quest.name][0]) 

            if row[person_col] != "": # ident: [q_id, char, message, order, orientation, responces]
                d_id += 1
                pers = row[person_col]
                dialogues[d_id] = [str(quest.ident), row[person_col]]
            
            if row[text_col] != "":
                resp_count = 0
                abs_count += 1
                str_count = str(abs_count)
                if abs_count < 10:
                    str_count = '0' + str(abs_count)
                ident = 'QUEST_' + str(quest.ident) + '_DIALOG_' + str_count                
                translations[ident] = row[text_col]
                dialogues[d_id].append(ident)
                dialogues[d_id].append(str(order_count))
                dialogues[d_id].append('left')
                dialogues[d_id].append([])

            if row[resp_col] != "":
                resp_count += 1
                resp_ident = ident + '_A' + str(resp_count)
                translations[resp_ident] = row[resp_col]
                dialogues[d_id][-1].append(resp_ident)

    with open('_export_translations.csv', 'wt', encoding="utf8", newline='') as csvfile:
        fieldnames = ['ident', 'lang', 'text',
                      'lastUpdateDate', 'description']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        writer.writeheader()
        
        keys = sorted(translations.keys())
        
        for ident in keys:                           
            writer.writerow({'ident': ident,
                             'lang': 'ru',                             
                             'text': translations[ident],
                             'lastUpdateDate': '2017-02-07 12:04:05',
                             'description': ''})
    
    with open('_export_dialogues.csv', 'wt', encoding="utf8", newline='') as csvfile:
        fieldnames = ['id', 'questId', 'character', 'message',
                      'order', 'orientation', 'responces']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        writer.writeheader()

        keys = sorted(dialogues.keys())
        
        for d_id in keys: # ident: [q_id, char, message, order, orientation, responces]            
            questId = dialogues[d_id][0]            
            character = dialogues[d_id][1]
            message = dialogues[d_id][2]
            order = dialogues[d_id][3]
            orientation = dialogues[d_id][4]
            responces = '['
            responces_ls = dialogues[d_id][5]
            for i in range(len(responces_ls)):
                responces += '"' + responces_ls[i] + '"'
                if i != len(responces_ls) - 1:
                    responces += ', '
            responces += ']'
                
            writer.writerow({'id': str(d_id),
                             'questId': questId,                             
                             'character': character,
                             'message': message,
                             'order': order,
                             'orientation': orientation,
                             'responces': responces})
                

def export_data():
    last_id = int(input("enter current last dialogue id, pls "))
    export_items()
    export_quests()
    export_missions()
    export_translation(last_id)
    
export_data()

print("Ok! look at _export files.")
input("Press Enter to close.")
