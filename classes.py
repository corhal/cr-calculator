import random

class Item(object):
    def __init__(self, name, recipe=None):
        self.name = name
        self.recipe = recipe # dict of items and counts
        self.full_recipe = {}
        self.compile_full_recipe(1)

    def get_name(self):
        return self.name

    def get_recipe(self):
        if self.recipe != None:
            return self.recipe.copy()
        else:
            return None

    def compile_full_recipe(self, amount):
        if self.recipe == None:
            self.full_recipe[self] = amount
            return
        for item in self.recipe.keys():
            if item.get_recipe() == None:                
                self.full_recipe[item] = self.full_recipe.get(item, 0) + self.recipe[item] * amount
            elif item.get_full_recipe() != None:                
                item_recipe = item.get_full_recipe()
                for secondary_item in item_recipe.keys():
                    self.full_recipe[secondary_item] = self.full_recipe.get(secondary_item, 0) + item_recipe[secondary_item]

    def get_full_recipe(self):
        if self.full_recipe != None:
            return self.full_recipe.copy()
        else:
            return None
                

class Quest(object):
    def __init__(self, name, item_conditions, reward, required_quests):
        self.name = name
        self.item_conditions = item_conditions # dict
        self.completed = False
        self.reward = reward
        self.required_quests = required_quests # list
        self.locked = True

    def __str__(self):
        tostring = self.name + " ["
        count = 0
        for item in self.item_conditions.keys():
            tostring += item.get_name() + ": " + str(self.item_conditions[item])
            count += 1
            if count != len(self.item_conditions.keys()):
                tostring += ", "            
        tostring += "]"
        if self.reward.keys != 0:
            tostring += " gives keys: " + str(self.reward.keys)
        return tostring

    def get_full_conditions(self):
        full_conditions = {}
        for item in self.item_conditions.keys():
            full_recipe = item.get_full_recipe()            
            for secondary_item in full_recipe.keys():
                full_conditions[secondary_item] = (full_conditions.get(secondary_item, 0) + full_recipe[secondary_item] * self.item_conditions[item])
        return full_conditions
    
    def get_item_conditions(self):
        return self.item_conditions.copy()

    def complete(self):
        self.completed = True

class Reward(object):
    def __init__(self, item_chances, keys=0):
        self.item_chances = item_chances # dict
        self.keys = keys

class Mission(object):
    def __init__(self, ident, reward, energy_cost, keys_cost):
        self.ident = ident
        self.reward = reward
        self.energy_cost = energy_cost
        self.keys_cost = keys_cost
        self.locked = True
        if self.keys_cost == 0:
            self.locked = False

    def __str__(self):
        tostring = str(self.ident) + " ["
        count = 0
        for item in self.reward.item_chances.keys():
            tostring += item.get_name() + ": " + str(self.reward.item_chances[item])
            count += 1
            if count != 3:
                tostring += ", "
        tostring += "]"
        tostring += " , keys cost: " + str(self.keys_cost)
        return tostring

    def unlock(self):
        self.locked = False

    def get_energy_cost(self):
        return self.energy_cost

    def complete(self):
        return self.reward

class Player(object):
    def __init__(self, max_daily_energy, missions):
        self.day = 0
        self.missions_completed = 0
        self.keys = 0
        self.inventory = {}
        self.max_daily_energy = max_daily_energy
        self.energy = self.max_daily_energy
        self.missions = missions
        self.completed_quests = []

    def is_quest_farmable(self, quest):
        for r_quest in quest.required_quests:
            if r_quest not in self.completed_quests:
                return False
        quest.locked = False
        full_conditions = quest.get_full_conditions()
        for item in full_conditions.keys():
            for mission in self.missions:
                if item in mission.reward.item_chances.keys() and mission.locked:
                    return False
        return True

    def get_available_quests(self, quests):
        available_quests = []        
        for quest in quests:
            if quest.completed:                
                continue               
            if self.is_quest_farmable(quest):
                available_quests.append(quest)        
        return available_quests

    def choose_quest(self, quests):
        loop_count = 0
        while True:
            loop_count += 1
            count = 0
            for quest in quests:
                if quest.completed:
                    count += 1
                    if count == len(quests):
                        return True
            available_quests = self.get_available_quests(quests)            
            if len(available_quests) > 0:
                quest = random.choice(available_quests)
                self.play_quest(quest)                

            for mission in self.missions:
                if mission.locked:
                    self.unlock_mission(mission)
            if loop_count == 1000:
                print("Looks like you have a dead end")
                print("Currently open missions:")
                for mission in self.missions:
                    if not mission.locked:
                        print(mission)
                print("Currently available quests:")
                for quest in quests:
                    if not quest.completed and not quest.locked:
                        print(quest)                
                return False

    def play_quest(self, quest):
        item_conditions = quest.get_item_conditions()
        full_conditions = quest.get_full_conditions()
        for item in full_conditions.keys():           
            self.farm_item(item, full_conditions[item])
        for item in item_conditions.keys():           
            while self.inventory.get(item, 0) < item_conditions[item]:                
                self.craft(item)
        self.receive_reward(quest.reward)
        quest.complete()
        self.completed_quests.append(quest)

    def farm_item(self, item, amount):
        for mission in self.missions:           
            if item in mission.reward.item_chances.keys():
                farm_mission = mission
                break
        while self.inventory.get(item, 0) < amount:
            self.play_mission(farm_mission)
        
    def spend_energy(self, amount):
        if self.energy > amount:
            self.energy -= amount
        else:
            self.skip_day()

    def skip_day(self):
        self.energy = self.max_daily_energy
        self.day += 1

    def receive_reward(self, reward):
        self.keys += reward.keys
        for item in reward.item_chances.keys():
            if random.randrange(0, 100) * 0.01 < reward.item_chances[item]:
                self.inventory[item] = self.inventory.get(item, 0) + 1
                
    def unlock_mission(self, mission):
        if self.keys < mission.keys_cost:
            return False
        self.keys -= mission.keys_cost
        mission.unlock()
        return True

    def play_mission(self, mission):
        self.spend_energy(mission.get_energy_cost())
        self.receive_reward(mission.complete())
        self.missions_completed += 1

    def craft(self, item):
        if item.get_recipe() == None:
            return
        for item_component in item.get_recipe():
            if item_component not in self.inventory.keys():
                if item_component.get_recipe() != None:
                    self.craft(item_component)
                else:
                    return
            elif item.get_recipe()[item_component] > self.inventory[item_component]:                
                self.craft(item_component)                
            
        for item_component in item.recipe:
            self.inventory[item_component] -= item.get_recipe()[item_component]
        self.take_item(item)

    def take_item(self, item):
        self.inventory[item] = self.inventory.get(item, 0) + 1

    def show_stats(self):
        print("-" * 30)
        print("Day: " + str(self.day))
        print("Missions completed: " + str(self.missions_completed))
        print("Energy: " + str(self.energy))
        for item in self.inventory.keys():
            if self.inventory[item] > 0:
                print(item.get_name() + ": " + str(self.inventory[item]))

class Game(object):
    def __init__(self, player, all_items, missions, quests):
        self.player = player
        self.all_items = all_items
        self.missions = missions
        self.quests = quests
