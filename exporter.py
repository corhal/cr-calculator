from data import *
import csv
import json

def export_items():
    items = load_items()
    with open('_export_items.csv', 'wt', encoding="utf8", newline='') as csvfile:
        fieldnames = ['id', 'asset', 'readOnly', 'cost', 'config', '_comment']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        writer.writeheader()
        for key in items:
            item = items[key]
            ident = item.ident
            asset = item.asset
            readOnly = '0'
            config = ''
            if item.is_fragment != '':
                config = '{"isFragment": "' + item.is_fragment + '"}'
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

def export_regions():
    missions = load_missions(load_items(), load_recipes(load_items()))
    regions = load_regions(missions)
    quests = load_quests(load_items(), regions, missions)
    with open('_export_regions.csv', 'wt', encoding="utf8", newline='') as csvfile:
        fieldnames = ['id', 'chapter', 'cost', 'unlockRequirements', 'missionId']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        writer.writeheader()
        for region in regions:
            ident = region.ident
            chapter = region.chapter
            cost = ""
            quest_id = ''
            if len(region.requirement.quests) > 0:
                quest_id = region.requirement.quests[0].ident

            if quest_id == '':
                unlockRequirements = ''
            else:
                unlockRequirements = '{"quest": [{"id": ' + quest_id + ', "status": 3}]}'

            try:
                missionId = region.mission.ident
            except:
                missionId = 0
            writer.writerow({'id': ident,
                             'chapter': chapter,
                             'cost': cost,
                             'unlockRequirements': unlockRequirements,
                             'missionId': missionId})

def export_missions():
    items = load_items()
    missions = load_missions(items, load_recipes(items))
    regions = load_regions(missions)
    quests = load_quests(items, regions, missions)
    with open('_export_missions.csv', 'wt', encoding="utf8", newline='') as csvfile:
        fieldnames = ['id', 'chapterId', 'requirements', 'recipes', 'garbage',
                      'fixedReward', 'lifeBonus', 'possibleReward',
                      'cost', 'winConfig', '_comment']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        writer.writeheader()
        for mission in missions:
            ident = mission.ident
            chapterId = mission.chapter
            main = ''
            requirements = ''
            if mission.region != None and mission.locked:
                requirements = '{"region": [{"id": ' + str(mission.region.ident) + ', "status": 1}]}'

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
            lifebonus = mission.lifebonus
            garbage = '{"count": 5, "action": 1 }'
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
            winConfig = mission.win_config
            comment = mission.name
            writer.writerow({'id': ident,
                             'chapterId': chapterId,
                             'requirements': requirements,
                             'recipes': recipes,
                             'garbage': garbage,
                             'fixedReward': fixedReward,
                             'lifeBonus': lifebonus,
                             'possibleReward': possibleReward,
                             'cost': cost,
                             'winConfig': winConfig,
                             '_comment': comment})

def export_quests():
    items = load_items()
    missions = load_missions(items, load_recipes(items))
    regions = load_regions(missions)
    quests = load_quests(items, regions, missions)
    with open('_export_quests.csv', 'wt', encoding="utf8", newline='') as csvfile:
        fieldnames = ['id', 'chapterId', 'questChain', 'questEmotion',
                      'requirements', 'cost', 'reward', '_comment']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        writer.writeheader()
        for quest in quests:
            ident = quest.ident
            chapterId = quest.chapter
            questChain = quest.quest_chain

            requirements = '{'
            if quest.requirement != None and len(quest.requirement.quests) > 0:
                count = 0
                goal_count = len(quest.requirement.quests)
                for r_quest in quest.requirement.quests:
                    count += 1
                    requirements += '"quest": [{"id": ' + str(r_quest.ident) + ', "status": 3}]'
                    if count < goal_count:
                        requirements += ', '
            flag = False
            if quest.requirement != None and len(quest.requirement.missions) > 0 and quest.requirement.missions[0] != None:
                requirements += '"mission": [{"id": ' + str(quest.requirement.missions[0].ident) + ', "stars": 1}]'
                flag = True

            if quest.requirement != None and len(quest.requirement.regions) > 0 and quest.requirement.regions[0] != None:
                if flag == True:
                    requirements += ', '
                requirements += '"region": [{"id": ' + str(quest.requirement.regions[0].ident) + ', "status": 1}]'

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

            reward = quest.temp_reward
            # reward = '{'
            # q_reward = quest.reward
            # if q_reward.gold_reward != 0:
                # reward += '"gold": ' + str(q_reward.gold_reward)
            # if q_reward.energy_reward != 0:
                # if q_reward.gold_reward != 0:
                    # reward += ', '
                # reward += '"refillable": [{"id": 1, "amount": ' + str(q_reward.energy_reward) + '}]'
            # reward += '}'

            comment = quest.name
            try:
                emotion = quest_emotions[quest.name]
            except KeyError:
                emotion = 'sad'
            
            writer.writerow({'id': ident,
                             'chapterId': chapterId,
                             'questChain': questChain,
                             'questEmotion': emotion,
                             'requirements': requirements,
                             'cost': cost,
                             'reward': reward,
                             '_comment': comment})

def find_quest(quest_name, quests):
    for quest in quests:
        if quest_name == quest.name:
            return quest

quest_emotions = {}
def export_dialogues_from_json(last_id):
    global quest_emotions
    items = load_items()
    missions = load_missions(items, load_recipes(items))
    regions = load_regions(missions)
    quests = load_quests(items, regions, missions)
    name_col = 0
    order_col = 0
    person_col = 0
    text_col = 0
    resp_col = 0

    dialogues_by_ident = {}
    translations = []
    dialogue_ident = 1
    with open('_validator_dialogues.json', 'rt', encoding="utf8") as data_file:
        data = json.load(data_file)
        speakers = {} # ident: string
        chapter_ids = []
        chapters = {}
        for smth in data['Packages'][0]['Models']:
            if smth['Type'] == 'FlowFragment':
                chapters[smth['Properties']['Id']] = smth
        
        for chapter_id in chapters.keys():
            chapter_strings = chapters[chapter_id]['Properties']['DisplayName'].split()
            lang = chapter_strings[-1].strip(')(').lower()
            chapter_number = int(chapter_strings[-2])
            quest_ids = []

            dialogue_nodes = {}

            for smth in data['Packages'][0]['Models']:
                if smth['Properties']['Parent'] == chapter_id and smth['Type'] == 'Dialogue':
                    dialogue_nodes[smth['Properties']['Id']] = smth
                if smth['Type'] == 'Entity' or smth['Type'] == 'DefaultSupportingCharacterTemplate':
                    speakers[smth['Properties']['Id']] = smth['Properties']['ExternalId'].lower()
                
            dialogue_fragments = {}
            
            for smth in data['Packages'][0]['Models']:
                if smth['Properties']['Parent'] in dialogue_nodes.keys():
                    dialogue_fragments[smth['Properties']['Id']] = smth
                
            for key in sorted(dialogue_nodes.keys()):
                for s_key in sorted(dialogue_fragments.keys()):
                    if dialogue_fragments[s_key]['Type'] =='Hub' and dialogue_fragments[s_key]['Properties']['DisplayName'].lower() == 'quest start' and dialogue_fragments[s_key]['Properties']['Parent'] == key:
                        briefing_depth = recursive(dialogue_fragments, s_key, key, speakers)
                        dialogue_nodes[key]['Properties']['BriefingDepth'] = briefing_depth
            npc_emo_dict = {'neutral': '', 'happy-1': '_HAPPY_1', 'happy-2': '_HAPPY_2',
                            'sad-1': '_SAD_1', 'sad-2': '_SAD_2',
                            'angry-1': '_ANGRY_1', 'angry-2': '_ANGRY_2'}
            player_emo_dict = {':)' : 'good_ImReady', '^^': 'good_willGood', ':D': 'good_laugh', '*_*': 'good_delight',
                               ':(': 'bad_damn', ':/': 'bad_hmm', ":'(": 'bad_cry', '><': 'bad_angry',
                               'O_O': 'bad_fear', '@_@': 'bad_shame'}
            
            for key in sorted(dialogue_nodes.keys()):
                quest_name = dialogue_nodes[key]['Properties']['DisplayName']
                quest = find_quest(quest_name, quests)
                start_index = 0
                try:
                    prefix = 'QUEST_' + str(quest.ident) + '_DIALOG_'
                except AttributeError:
                    raise ValueError("Some problems with quest " + quest_name)
                player_emotions_by_depth = {}            
                for s_key in sorted(dialogue_fragments.keys()):                
                    if dialogue_fragments[s_key]['Type'] == 'DialogueFragment' \
                        and dialogue_fragments[s_key]['Properties']['Parent'] == key:
                        emotion = dialogue_fragments[s_key]['Properties']['StageDirections'].split('|')[0]
                        postfix = ''
                        depth = dialogue_fragments[s_key]['Properties']['Depth']
                        unique = True
                        if 'Speaker' in dialogue_fragments[s_key]['Properties'] \
                            and speakers[dialogue_fragments[s_key]['Properties']['Speaker']] == 'player':
                            if depth not in player_emotions_by_depth.keys():
                                player_emotions_by_depth[depth] = []
                            if emotion not in player_emotions_by_depth[depth]:
                                player_emotions_by_depth[depth].append(emotion)
                                postfix = '_A' + str(player_emotions_by_depth[depth].index(emotion) + 1)
                            else:
                                unique = False
                        if emotion in npc_emo_dict:
                            postfix = npc_emo_dict[emotion]
                            if quest.name not in quest_emotions.keys() and 'angry' in emotion or 'sad' in emotion:
                                quest_emotions[quest.name] = emotion.split('-')[0]
                                #print(emotion.strip('-'))
                        if (prefix + str(depth).zfill(2)) not in dialogues_by_ident:
                            dialogue_ident += 1
                            # [КОСТЫЛЬ!!!!!111!!1!адин]
                            order = depth - dialogue_nodes[key]['Properties']['BriefingDepth']
                            if dialogue_fragments[s_key]['Properties']['StageDirections'].split('|')[1] == 'debriefing':
                                order = 1
                            elif order > 0:
                                order += 1                            
                            # [/КОСТЫЛЬ!!!!!111!!1!адин]                            
                            dialogues_by_ident[(prefix + str(depth).zfill(2))] = {                            
                                'id': dialogue_ident,
                                'quest_ident': quest.ident,
                                'character': speakers[dialogue_fragments[s_key]['Properties']['Speaker']],
                                'message': prefix + str(depth).zfill(2),
                                'order': order,
                                'orientation': 'left',
                                'responces': [],
                            }
                        if unique:  
                            if speakers[dialogue_fragments[s_key]['Properties']['Speaker']] == 'player':
                                feedback = ''
                                if dialogue_fragments[s_key]['Properties']['StageDirections'].split('|')[1] != 'neutral':
                                    feedback = dialogue_fragments[s_key]['Properties']['StageDirections'].split('|')[1]
                                dialogues_by_ident[(prefix + str(depth).zfill(2))]['responces'].append({
                                    'text': prefix + str(depth).zfill(2) + postfix,
                                    'smile': player_emo_dict[emotion],
                                    'feedback': feedback
                                })
                            elif dialogues_by_ident[(prefix + str(depth).zfill(2))]['character'] == 'player':
                                dialogues_by_ident[(prefix + str(depth).zfill(2))]['character'] = speakers[dialogue_fragments[s_key]['Properties']['Speaker']]
                            translations.append({      
                                'ident': prefix + str(depth).zfill(2) + postfix,
                                'text': dialogue_fragments[s_key]['Properties']['Text'],
                                'lang': lang,
                                'lastUpdateDate': '2017-04-10 09:57:08',
                                'description': '',
                            })
                
    write_dialogues(translations, dialogues_by_ident)
                
def write_dialogues(translations, dialogues_by_ident):
    with open('_export_translations.csv', 'wt', encoding="utf8", newline='') as csvfile:
        fieldnames = ['ident', 'lang', 'text',
                      'lastUpdateDate', 'description']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        writer.writeheader()
        
        for translation in translations:
            text = translation['text']
            text = text.replace('{', '<font color="ffffff" oline="2" olcolor="92633a">')
            text = text.replace('}', '</font>')
            writer.writerow({'ident': translation['ident'],
                            'lang': translation['lang'],
                            'text': text,
                            'lastUpdateDate': translation['lastUpdateDate'],
                            'description': translation['description']})

    with open('_export_dialogues.csv', 'wt', encoding="utf8", newline='') as csvfile:
        fieldnames = ['id', 'questId', 'character', 'message',
                      'order', 'orientation', 'responces']
        writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        writer.writeheader()

        for dialogue_ident in sorted(dialogues_by_ident.keys()):
            ident = dialogues_by_ident[dialogue_ident]['id']
            questId = dialogues_by_ident[dialogue_ident]['quest_ident']
            character = dialogues_by_ident[dialogue_ident]['character']
            message = dialogues_by_ident[dialogue_ident]['message']
            order = dialogues_by_ident[dialogue_ident]['order']
            orientation = dialogues_by_ident[dialogue_ident]['orientation']
            responces = '['
            responces_ls = dialogues_by_ident[dialogue_ident]['responces']

            for i in range(len(responces_ls)):
                responces += '{"text": "' + responces_ls[i]['text'] + '", "smile": "' \
                            + responces_ls[i]['smile'] + '", "feedback": "' \
                            + responces_ls[i]['feedback'] + '"}'
                if i != len(responces_ls) - 1:
                    responces += ', '
            responces += ']'

            writer.writerow({'id': ident,
                             'questId': questId,
                             'character': character,
                             'message': message,
                             'order': order,
                             'orientation': orientation,
                             'responces': responces})        

def recursive(fragmentsByIds, ident, end_target, speakers):
    speakers = speakers
    briefing_depth = 0
    def realRecursive(fragmentsByIds, ident, end_target, depth):    
        nonlocal speakers
        nonlocal briefing_depth
        if ident in fragmentsByIds.keys() and 'Depth' in fragmentsByIds[ident]['Properties'].keys():
            return
        if ident not in fragmentsByIds.keys():
            return
        if fragmentsByIds[ident]['Type'] == 'Hub':
            depth = 1
        fragmentsByIds[ident]['Properties']['Depth'] = depth
        try:
            if 'StageDirections' in fragmentsByIds[ident]['Properties'] and \
                fragmentsByIds[ident][ 'Properties']['StageDirections'].split('|')[1] == 'briefing':
                briefing_depth = depth
        except IndexError:
            raise ValueError('id' + str(ident) + ': ' + '"'+ fragmentsByIds[ident][ 'Properties']['StageDirections'] + '"')
        sub_index = 0
        for connection in fragmentsByIds[ident]['Properties']['OutputPins'][0]['Connections']:
            if sub_index == 0 and 'Speaker' in fragmentsByIds[ident]['Properties'] \
                and speakers[fragmentsByIds[ident]['Properties']['Speaker']] == 'player':
                depth = depth + 1
            sub_index += 1
            if 'StageDirections' in fragmentsByIds[ident]['Properties'] and \
                fragmentsByIds[ident]['Properties']['StageDirections'].split('|')[1] == 'briefing':
                depth += 1 
            realRecursive(fragmentsByIds, connection['Target'], end_target, depth)
    depth = 1    
    realRecursive(fragmentsByIds, ident, end_target, depth)
    return briefing_depth
        

#def export_translation(last_id):
    #items = load_items()
    #missions = load_missions(items, load_recipes(items))
    #missions = [mission for mission in missions if ((int(mission.chapter) >= start_chapter) and (int(mission.chapter) <= end_chapter))]
    #regions = load_regions(missions)
    #quests = load_quests(items, regions, missions)
    #quests = [quest for quest in quests if ((int(quest.chapter) >= start_chapter) and (int(quest.chapter) <= end_chapter))]
    #name_col = 0
    #order_col = 0
    #person_col = 0
    #text_col = 0
    #resp_col = 0

    #translations = {} # ident : text
    #orders = {} # name : [ord, ord, ord]
    #dialogues = {} # ident: [q_id, char, message, order, orientation, responces]

    #with open('_validator_dialogues.csv', 'rt', encoding="utf8") as csvfile:
        #reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        #for row in reader:
            #if row[0] == "HEADER":
                #name_col = row.index("QUEST")
                #order_col = row.index("ORDER")
                #person_col = row.index("PERSON")
                #p_emo_col = row.index("PERSON_EMOTION")
                #text_col = row.index("TEXT")
                #emo_col = row.index("PLAYER_EMOTION")
                #corr_col = row.index("CORRECTNESS")
                #resp_col = row.index("RESPONSES")
                #brief_col = row.index("SUMMARY")
                #sum_person_col = row.index("SUMMARY_PERSON")
                #debrief_col = row.index("DEBRIEFING")
                #debrief_person_col = row.index("DEBRIEFING_PERSON")
                #continue
            #if row[name_col] != "":
                #text_count = 0
                #quest = find_quest(row[name_col], quests)
                #try:
                    #orders[quest.name] = [0, 1]
                #except AttributeError:
                    #raise ValueError(row[name_col] + ' is in _validator_dialogues, but not in _validator_quests')

            #if row[order_col] == "before":
                #order = "before"

            #if row[order_col] == "after":
                #order = "after"
                #text_count = 1

            #if row[person_col] != "":
                #if order == "before":
                    #text_count -= 1
                #if order == "after":
                    #text_count += 1
                #orders[quest.name].append(text_count)

        #csvfile.seek(0)
        #for key in orders.keys():
            #orders[key].sort()

        #for row in reader:
            #if row[0] == "HEADER":
                #d_id = last_id
                #continue

            #if row[resp_col] == "":
                #continue

            #if row[name_col] != "":
                #abs_count = 0
                #quest = find_quest(row[name_col], quests)
                #ord_list = orders[quest.name]

            #if 0 in orders[quest.name]:
                #d_id += 1
                #briefing = row[brief_col]
                #ident = 'QUEST_' + str(quest.ident) + '_DIALOG_000'
                #translations[ident] = briefing
                #if row[sum_person_col] != None and row[sum_person_col] != '':
                    #dialogues[d_id] = [str(quest.ident), row[sum_person_col], ident, str(0), "left", []]
                #else:
                    #dialogues[d_id] = [str(quest.ident), row[person_col], ident, str(0), "left", []]
                #del(orders[quest.name][orders[quest.name].index(0)])
                #dialogues[d_id].append([])
                #dialogues[d_id].append([])

            #if 1 in orders[quest.name]:
                #d_id += 1
                #debriefing = row[debrief_col]
                #ident = 'QUEST_' + str(quest.ident) + '_DIALOG_111'
                #translations[ident] = debriefing
                #if row[sum_person_col] != None and row[sum_person_col] != '':
                    #dialogues[d_id] = [str(quest.ident), row[debrief_person_col], ident, str(1), "left", []]
                #else:
                    #dialogues[d_id] = [str(quest.ident), row[person_col], ident, str(1), "left", []]
                #del(orders[quest.name][orders[quest.name].index(1)])
                #dialogues[d_id].append([])
                #dialogues[d_id].append([])

            #if len(orders[quest.name]) > 0 and row[text_col] != "":
                #order_count = orders[quest.name][0]
                #del(orders[quest.name][0])

            #if row[person_col] != "": # ident: [q_id, char, message, order, orientation, responces]
                #d_id += 1
                #pers = row[person_col]
                #dialogues[d_id] = [str(quest.ident), row[person_col]]

            #if row[text_col] != "":
                #resp_count = 0
                #abs_count += 1
                #str_count = str(abs_count)
                #if abs_count < 10:
                    #str_count = '0' + str(abs_count)
                #ident = 'QUEST_' + str(quest.ident) + '_DIALOG_' + str_count
                #translations[ident] = row[text_col]
                #dialogues[d_id].append(ident)
                #dialogues[d_id].append(str(order_count))
                #dialogues[d_id].append('left')
                #dialogues[d_id].append([])
                #dialogues[d_id].append([])
                #dialogues[d_id].append([])

            #if row[resp_col] != "":
                #resp_count += 1
                #resp_ident = ident + '_A' + str(resp_count)
                #translations[resp_ident] = row[resp_col]
                #dialogues[d_id][-1].append(row[corr_col])
                #dialogues[d_id][-2].append(resp_ident)
                #dialogues[d_id][-3].append(row[emo_col])

    #with open('_export_translations.csv', 'wt', encoding="utf8", newline='') as csvfile:
        #fieldnames = ['ident', 'lang', 'text',
                      #'lastUpdateDate', 'description']
        #writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        #writer.writeheader()

        #keys = sorted(translations.keys())

        #temp_emotions_list = ['', '_HAPPY_1', '_HAPPY_2', '_ANGRY_1', '_ANGRY_2', '_SAD_1', '_SAD_2']

        #for ident in keys:
            #for emotion in temp_emotions_list:
                #new_ident = ident + emotion
                #text = translations[ident]
                #text = text.replace('{', '<font color="ffffff" oline="2" olcolor="92633a">')
                #text = text.replace('}', '</font>')
                #writer.writerow({'ident': new_ident,
                             #'lang': 'ru',
                             #'text': text,
                             #'lastUpdateDate': '2017-02-07 12:04:05',
                             #'description': ''})

    #with open('_export_dialogues.csv', 'wt', encoding="utf8", newline='') as csvfile:
        #fieldnames = ['id', 'questId', 'character', 'message',
                      #'order', 'orientation', 'responces']
        #writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=fieldnames)

        #writer.writeheader()

        #keys = sorted(dialogues.keys())

        #emotions = {":)": "good_ImReady",
                    #":D": "good_wow",
                    #"^^": "good_willGood",
                    #":(": "bad_damn",
                    #":/": "bad_hmm",
                    #":'(": "bad_cry"}

        #for d_id in keys: # ident: [q_id, char, message, order, orientation, responces]
            #questId = dialogues[d_id][0]
            #character = dialogues[d_id][1]
            #message = dialogues[d_id][2]
            #order = dialogues[d_id][3]
            #orientation = dialogues[d_id][4]
            # {"text" : "QUEST_20101_DIALOG_01_A1", "smile" : "good_wow"}
            #responces = '['
            #responces_ls = dialogues[d_id][6]
            #emotions_ls = dialogues[d_id][5]
            #correctness_ls = dialogues[d_id][7]

            #for i in range(len(responces_ls)):
                #emotion = ""
                #if emotions_ls[i] != "":
                    #emotion = emotions[emotions_ls[i]]
                #responces += '{"text": "' + responces_ls[i] + '", "smile": "' + emotion + '", "feedback": "' + correctness_ls[i] + '"}'
                #if i != len(responces_ls) - 1:
                    #responces += ', '
            #responces += ']'

            #writer.writerow({'id': str(d_id),
                             #'questId': questId,
                             #'character': character,
                             #'message': message,
                             #'order': order,
                             #'orientation': orientation,
                             #'responces': responces})


def export_data():
    last_id = int(input("enter current last dialogue id, pls "))
    export_items()
    export_dialogues_from_json(last_id)
    export_quests()
    export_missions()
    export_regions()    
    #export_translation(last_id)

export_data()

print("Ok! look at _export files.")
input("Press Enter to close.")
