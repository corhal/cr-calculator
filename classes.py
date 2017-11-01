import random

class Item(object):
    def __init__(self, ident, name, recipe=None, gold_cost=0, asset='', is_fragment=''):
        self.ident = ident
        self.name = name
        self.recipe = recipe # dict of items and counts
        self.gold_cost = gold_cost
        self.full_gold_cost = gold_cost
        self.asset = asset
        self.full_recipe = {}
        self.is_fragment = is_fragment
        self.__compile_full_recipe()

    def __compile_full_recipe(self):
        if self.recipe == None:
            self.full_recipe[self] = 1
            return
        for item in self.recipe.keys():
            if item.recipe == None:
                self.full_recipe[item] = self.full_recipe.get(item, 0) + self.recipe[item]
            elif item.full_recipe != None:
                item_recipe = item.full_recipe
                self.full_gold_cost += item.full_gold_cost * self.recipe[item]
                for secondary_item in item_recipe.keys():
                    self.full_recipe[secondary_item] = self.full_recipe.get(secondary_item, 0) + item_recipe[secondary_item] * self.recipe[item]

class Quest(object):
    def __init__(self, ident, name, chapter, quest_chain,
                 item_conditions, reward, requirement, temp_reward):
        self.ident = ident
        self.name = name
        self.chapter = chapter
        self.quest_chain = quest_chain
        self.item_conditions = item_conditions # dict
        self.completed = False
        self.reward = reward
        self.requirement = requirement # list
        self.locked = True
        self.temp_reward = temp_reward

    def __str__(self):
        tostring = self.name + " ["
        count = 0
        for item in self.item_conditions.keys():
            tostring += item.name + ": " + str(self.item_conditions[item])
            count += 1
            if count != len(self.item_conditions.keys()):
                tostring += ", "
        tostring += "]"
        tostring += ", full gold cost: " + str(self.full_gold_cost)
        return tostring

    @property
    def full_conditions(self):
        full_conditions = {}
        for item in self.item_conditions.keys():
            full_recipe = item.full_recipe
            for secondary_item in full_recipe.keys():
                full_conditions[secondary_item] = (full_conditions.get(secondary_item, 0) + full_recipe[secondary_item] * self.item_conditions[item])
        return full_conditions

    def complete(self):
        self.completed = True
        return self.reward.give(True, False)

    @property
    def full_gold_cost(self):
        full_gold_cost = 0
        for item in self.item_conditions.keys():
            full_gold_cost += item.full_gold_cost * self.item_conditions[item]
        return full_gold_cost

    def is_available(self):
        for quest in self.requirement.quests:
            if not quest.completed:
                return False
        for region in self.requirement.regions:
            if region.locked:
                return False
        for mission in self.requirement.missions:
            if mission.locked:
                return False
        self.locked = False
        return True

    def is_farmable(self, chapter):
        if not self.is_available():
            return False
        full_conditions = self.full_conditions
        for item in full_conditions.keys():
            if self.name == 'Leader-902':
                print(item.name)
            for mission in chapter.missions:
                if item in mission.reward.item_chances.keys() and mission.locked:
                    return False
        return True

class QuestChain(object):
    def __init__(self, quests):
        self.quests = quests
        self.completed = False

class Reward(object):
    def __init__(self, item_chances, item_amounts=None,
                 gold_reward=0, energy_reward=0):
        self.item_chances = item_chances # dict {item: chance, reward} ?
        self.item_amounts = item_amounts
        self.gold_reward = gold_reward
        self.energy_reward = energy_reward

    def give(self, always_chance, is_mission):
        gold = Game.items["Soft currency"]
        energy = Game.items["Energy"]
        
        reward_items = {} # item: amount
        item_chances = self.item_chances.copy()
        full_prob = 0.0
        for item in item_chances.keys():
            full_prob += item_chances[item]
            item_chances[item] = full_prob
        gold_prob = full_prob + 0.001
        
        if gold_prob < 0:
            raise ValueError("Gold probability < 0 in some mission!")
        if is_mission:
            reward_items[gold] = 0
            for item in item_chances.keys():
                reward_items[item] = 0
            for i in range(0, 3):
                roll = random.randrange(0, 100)
                roll *= 0.01
                if roll >= gold_prob:
                    reward_items[gold] += self.gold_reward                    
                else:
                    for item in item_chances.keys():
                        amount = 1
                        if self.item_amounts != None:
                            amount = self.item_amounts[item]
                        if roll <= item_chances[item]:                          
                            reward_items[item] += amount
                            break
        else:
            reward_items[gold] = self.gold_reward
        reward_items[energy] = self.energy_reward
        return reward_items

class Region(object):
    def __init__(self, ident, quest_names, mission, chapter):
        self.ident = ident
        self.quest_names = quest_names
        self.mission = mission
        self.locked = False
        if self.mission != None:
            mission.region = self
            self.mission.locked = False
        self.chapter = chapter
        self.requirement = None

    def reinit(self, quests):
        required_quests = []
        for quest in quests:
            if quest.name in self.quest_names:
                required_quests.append(quest)
        self.requirement = Requirement(quests=required_quests)
        if len(self.requirement.quests) > 0:
            self.locked = True
            if self.mission != None:
                self.mission.locked = True

    def unlock(self):
        self.locked = False
        if self.mission != None:
            self.mission.locked = False

class Mission(object):
    def __init__(self, ident, name, chapter, reward,
                 energy_cost, recipe_levels, lifebonus, win_config):
        self.recipe_levels = recipe_levels # {recipe: level}
        self.ident = ident
        self.name = name
        self.chapter = chapter
        self.reward = reward
        self.energy_cost = energy_cost
        self.locked = None
        self.played = False
        self.lifebonus = lifebonus
        self.win_config = win_config
        self.region = None

    def __str__(self):
        tostring = str(self.name) + " ["
        count = 0
        for item in self.reward.item_chances.keys():
            tostring += item.name + ": " + str(self.reward.item_chances[item])
            count += 1
            if count != 3:
                tostring += ", "
        tostring += "]"
        return tostring

    def unlock(self):
        self.locked = False

    def complete(self):
        always_chance = False
        if Game.first_mission_100_chance:
            always_chance = True
        if self.played:
            always_chance = False
        else:
            self.played = True
        return self.reward.give(always_chance, True)

class Recipe(object):
    def __init__(self, recipe_id, name, gold_by_levels, frag_item,
                 up_frags_by_levels, up_gold_by_levels):
        self.gold_by_levels = gold_by_levels
        self.frag_item = frag_item
        self.up_frags_by_levels = up_frags_by_levels
        self.up_gold_by_levels = up_gold_by_levels
        self.name = name
        self.recipe_id = recipe_id
        self.level = 0
        self.max_level = 3
        self.gold_reward = 0
        self.mission = None

    def upgrade(self):
        self.level += 1
        self.gold_reward = self.gold_by_levels[self.level]
        self.generate_mission()

    def can_upgrade(self, gold, fragments):
        if self.level == self.max_level:
            return False
        if gold < self.up_gold_by_levels[self.level + 1]:
            return False
        if fragments < self.up_frags_by_levels[self.level + 1]:
            return False
        return True

    def generate_mission(self):
        self.mission = Mission(0, self.name + '_mission',
                               0, Reward({}, gold_reward=self.gold_reward), 0, {}, 10, [])

class Requirement(object):
    def __init__(self, quests=[], quest_chains=[], regions=[], missions=[], item_amounts={}):
        self.quests = quests
        self.quest_chains = quest_chains
        self.regions = regions
        self.missions = missions
        self.item_amounts = item_amounts

class Player(object):
    def __init__(self, energy_cap, daily_sessions, mins_per_en,
                 time_between_sessions, gold, recipes):
        self.inventory = {}
        self.gold_item = Game.items["Soft currency"]
        self.inventory[self.gold_item] = gold
        self.energy_item = Game.items["Energy"]
        self.energy_cap = energy_cap
        self.inventory[self.energy_item] = self.energy_cap
        self.day = 1
        self.session = 0
        self.daily_sessions = daily_sessions
        self.total_missions_completed = 0
        self.missions_completed = {} # mission: count
        self.chapter = None
        self.recipes = recipes
        self.mins_per_en = mins_per_en
        self.time_between_sessions = time_between_sessions

    @property
    def gold(self):
        return self.inventory[self.gold_item]

    @gold.setter
    def gold(self, value):
        self.inventory[self.gold_item] = value

    @property
    def energy(self):
        return self.inventory[self.energy_item]

    @energy.setter
    def energy(self, value): # нужно внимательно проверить, что все работает
        if value < 0:
            spend_value = self.inventory[self.energy_item] - value
            self.skip_session()
            self.energy -= spend_value
        else:
            self.inventory[self.energy_item] = value

    def check_requirement(self, requirement):
        for quest in requirement.quests:
            if not quest.completed:
                return False
        for quest_chain in requirement.quest_chains:
            if not quest_chain.completed:
                return False
        for region in requirement.regions:
            if region.locked:
                return False
        for mission in requirement.missions:
            if mission.locked: # фактически стоило бы проверять played, но стремно
                return False
        for item in requirement.item_amounts.keys():
            if self.inventory.get(item, 0) < requirements.item_amounts[item]:
                return False
        return True

    def get_available_quests(self):
        available_quests = []
        for quest in self.chapter.quests:
            #print(quest.name)
            if quest.completed:
                continue
            if quest.is_farmable(self.chapter):
                #print(quest.name)
                available_quests.append(quest)
        return available_quests

    def play_chapter(self, chapter_index):
        self.day = 1
        self.session = 0 # ?..
        self.total_missions_completed = 0
        self.chapter = Game.chapters[chapter_index]
        self.recipes.extend(self.chapter.recipes)
        return self.choose_quest()

    def choose_quest(self): # returns tuple (missions_completed, total_missions_completed, day)
        loop_count = 0
        while True:
            loop_count += 1
            count = 0
            for quest in self.chapter.quests:
                if quest.completed:
                    count += 1
                    if count == len(self.chapter.quests):
                        return (self.missions_completed, self.total_missions_completed, self.day)
            available_quests = self.get_available_quests()
            #print(available_quests)
            #print(available_quests[0].name)
            if len(available_quests) > 0:
                quest = random.choice(available_quests)
                self.play_quest(quest)
            ###
            random.shuffle(self.chapter.regions)
            for region in self.chapter.regions:
                if region.locked and self.check_requirement(region.requirement):
                    self.unlock_region(region)

            if loop_count == 100:
                print("Looks like you have a dead end")
                print("-" * 30)
                self.show_stats()
                print("-" * 30)
                print("Currently open missions:")
                for mission in self.chapter.missions:
                    if not mission.locked:
                        print(mission)
                print("Currently available quests:")
                for quest in self.chapter.quests:
                    if not quest.completed and not quest.locked:
                        print(quest)
                raise ValueError("Dead end!")

    def play_quest(self, quest):
        item_conditions = quest.item_conditions
        full_conditions = quest.full_conditions
        for item in full_conditions.keys():
            self.farm_item(item, full_conditions[item])
        for item in item_conditions.keys():
            while self.inventory.get(item, 0) < item_conditions[item]:
                if self.gold < quest.full_gold_cost:
                    self.farm_gold(quest.full_gold_cost)
                self.craft(item)
        self.complete_quest(quest)

    def complete_quest(self, quest):
        item_conditions = quest.item_conditions
        for item in item_conditions.keys():
            self.change_amount(item, -item_conditions[item])
        self.receive_reward(quest.complete())

    def farm_item(self, item, amount):
        farm_mission = None
        for mission in self.chapter.missions:
            if item in mission.reward.item_chances.keys():
                farm_mission = mission
                break
        if farm_mission == None:
            raise ValueError("Can't find " + item.name + " in mission drop")
        while self.inventory.get(item, 0) < amount:
            self.play_mission(farm_mission)

    def farm_gold(self, amount):
        max_reward = 0
        for mission in self.chapter.missions:
            if mission.locked:
                continue
            if mission.reward.gold_reward > max_reward:
                max_reward = mission.reward.gold_reward
                farm_mission = mission
        while self.gold < amount:
            self.play_mission(farm_mission)

    def skip_session(self):
        self.session += 1
        if self.session == self.daily_sessions:
            self.skip_day()
        else:
            self.energy = min(self.energy_cap, self.energy
                              + (1 / self.mins_per_en) * 60
                              * self.time_between_sessions)

    def skip_day(self):
        self.energy = self.energy_cap
        self.session = 0
        self.day += 1

    def receive_reward(self, reward_items):
        if reward_items == None:
            return
        for item in reward_items.keys():
            self.change_amount(item, reward_items[item])
            #if item.name == "Energy" and reward_items[item] != 0:
                #print("got " + str(reward_items[item]) + " energy")

    def unlock_region(self, region):
        region.unlock()

    def play_mission(self, mission):
        self.energy -= mission.energy_cost
        self.receive_reward(mission.complete())
        self.total_missions_completed += 1
        
        if mission not in self.missions_completed.keys():
            self.missions_completed[mission] = 0
        self.missions_completed[mission] += 1        

    def craft(self, item):
        if item.recipe == None:
            return
        for item_component in item.recipe:
            if self.inventory.get(item_component, 0) < item.recipe.get(item_component, 0):
                if item_component.recipe != None:
                    while self.inventory.get(item_component, 0) < item.recipe[item_component]:
                        self.craft(item_component)
                else:
                    return
            elif item.recipe[item_component] <= self.inventory[item_component]:
                self.craft(item_component)

        for item_component in item.recipe:
            self.change_amount(item_component, -item.recipe[item_component])
        if self.gold < item.gold_cost:
            self.farm_gold(item.gold_cost)
        self.gold -= item.gold_cost
        self.change_amount(item, 1)

    def change_amount(self, item, amount):
        self.inventory[item] = self.inventory.get(item, 0) + amount
        self.upgrade_recipes()
        if self.inventory[item] < 0:
            raise ValueError(item.name + " amount < 0")

    def upgrade_recipes(self):
        for recipe in self.recipes:
            if recipe.can_upgrade(self.gold, self.inventory.get(recipe.frag_item, 0)):
                recipe.upgrade()
                self.gold -= recipe.up_gold_by_levels[recipe.level]
                self.change_amount(recipe.frag_item, -recipe.up_frags_by_levels[recipe.level])

    def show_stats(self):
        print("-" * 30)
        print("Day: " + str(self.day))
        print("Missions completed: " + str(self.total_missions_completed))
        print("Gold: " + str(self.gold))
        print("Energy: " + str(self.energy))
        for item in self.inventory.keys():
            if self.inventory[item] > 0:
                print(item.name + ": " + str(self.inventory[item]))

class Chapter(object):
    def __init__(self, name, items, missions, quests, recipes, regions):
        self.name = name
        self.items = items
        self.missions = []
        self.regions = []
        for region in regions:
            if region.mission == None:
                continue
            if region.mission.chapter == self.name:
                self.regions.append(region)
                self.missions.append(region.mission)
        self.quests = []
        for quest in quests:
            if quest.chapter == self.name:
                self.quests.append(quest)
        self.recipes = []
        for mission in self.missions:
            for recipe in recipes:
                if recipe.frag_item in mission.reward.item_chances.keys():
                    self.recipes.append(recipe)
        self.mission_result = 0
        self.days_result = 0

class Game(object):
    def __init__(self, items, recipes, missions, quests, chapters, first_mission_100_chance):
        Game.items = items
        Game.recipes = recipes
        Game.missions = missions
        Game.quests = quests
        Game.chapters = chapters
        Game.first_mission_100_chance = first_mission_100_chance
