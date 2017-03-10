import random

class Item(object):
    def __init__(self, name, recipe=None, gold_cost=0):
        self.name = name
        self.recipe = recipe # dict of items and counts
        self.gold_cost = gold_cost
        self.full_gold_cost = gold_cost
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
                self.full_gold_cost += item.full_gold_cost * self.recipe[item]
                for secondary_item in item_recipe.keys():
                    self.full_recipe[secondary_item] = self.full_recipe.get(secondary_item, 0) + item_recipe[secondary_item] * self.recipe[item]
                    
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
        tostring += ", full gold cost: " + str(self.get_full_gold_cost())
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

    def get_full_gold_cost(self):
        full_gold_cost = 0
        for item in self.item_conditions.keys():
            full_gold_cost += item.full_gold_cost * self.item_conditions[item]
        return full_gold_cost
    
    def get_item_conditions(self):
        return self.item_conditions.copy()

    def complete(self):
        self.completed = True

class Reward(object):
    def __init__(self, item_chances, gold_reward=0, keys=0):
        self.item_chances = item_chances # dict
        self.gold_reward = gold_reward
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
        self.gold = 0
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
                print("-" * 30)
                self.show_stats()
                print("-" * 30)
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
        # print(quest)
        # print("Gold: " + str(self.gold))
        item_conditions = quest.get_item_conditions()
        full_conditions = quest.get_full_conditions()
        for item in full_conditions.keys():           
            self.farm_item(item, full_conditions[item])        
        self.farm_gold(quest.get_full_gold_cost())         
        for item in item_conditions.keys():           
            while self.inventory.get(item, 0) < item_conditions[item]:                
                self.craft(item)
            self.inventory[item] -= item_conditions[item]
            if self.inventory[item] < 0:
                raise ValueError(item.get_name() + " < 0 while playing quest " + quest.name)
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

    def farm_gold(self, amount):
        max_reward = 0
        for mission in self.missions:
            if mission.locked:
                continue
            if mission.reward.gold_reward > max_reward:
                max_reward = mission.reward.gold_reward
                farm_mission = mission
        while self.gold < amount:
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
        self.gold += reward.gold_reward
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
            if item_component not in self.inventory.keys() or self.inventory[item_component] < item.get_recipe()[item_component]:
                if item_component.get_recipe() != None:
                    while self.inventory.get(item_component, 0) < item.get_recipe()[item_component]:
                        self.craft(item_component)
                else:
                    return
            elif item.get_recipe()[item_component] <= self.inventory[item_component]:                
                self.craft(item_component)                
            
        for item_component in item.recipe:
            q = self.inventory[item_component]
            self.inventory[item_component] -= item.get_recipe()[item_component]
            n = self.inventory[item_component]            
            if n < 0:
                raise ValueError("item amount < 0")
        if self.gold < item.gold_cost:            
            error_message = "Not enough gold to craft " + item.get_name()
            error_message += " have: " + str(self.gold) + " need: " + str(item.gold_cost)
            raise ValueError(error_message)
        else:            
            self.gold -= item.gold_cost        
        self.take_item(item)

    def take_item(self, item):
        self.inventory[item] = self.inventory.get(item, 0) + 1

    def show_stats(self):
        print("-" * 30)
        print("Day: " + str(self.day))
        print("Missions completed: " + str(self.missions_completed))
        print("Gold: " + str(self.gold))
        print("Keys: " + str(self.keys))
        print("Energy: " + str(self.energy))
        for item in self.inventory.keys():
            if self.inventory[item] > 0:
                print(item.get_name() + ": " + str(self.inventory[item]))

