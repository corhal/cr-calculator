import random

class Item(object):
    def __init__(self, ident, name, recipe=None, gold_cost=0):
        self.ident = ident
        self.name = name
        self.recipe = recipe # dict of items and counts
        self.gold_cost = gold_cost
        self.full_gold_cost = gold_cost
        
        self.full_recipe = {}
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
                 item_conditions, reward, required_quests):
        self.ident = ident
        self.name = name
        self.chapter = chapter
        self.quest_chain = quest_chain
        self.item_conditions = item_conditions # dict
        self.completed = False
        self.reward = reward
        self.required_quests = required_quests # list
        self.locked = True        

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
        return self.reward.give(True)

    @property
    def full_gold_cost(self):
        full_gold_cost = 0
        for item in self.item_conditions.keys():
            full_gold_cost += item.full_gold_cost * self.item_conditions[item]
        return full_gold_cost
    
    def is_available(self):
        for quest in self.required_quests:            
            if not quest.completed:
                return False
        self.locked = False
        return True

    def is_farmable(self, chapter):
        if not self.is_available():
            return False
        full_conditions = self.full_conditions
        for item in full_conditions.keys():
            for mission in chapter.missions:
                if item in mission.reward.item_chances.keys() and mission.locked:
                    return False
        return True

class Reward(object):
    def __init__(self, item_chances, item_amounts=None,
                 gold_reward=0, energy_reward=0):
        self.item_chances = item_chances # dict {item: chance, reward} ?
        self.item_amounts = item_amounts
        self.gold_reward = gold_reward
        self.energy_reward = energy_reward

    def give(self, always_chance): 
        reward_items = {} # item: amount
        for item in self.item_chances.keys():
            amount = 1
            if self.item_amounts != None:
                amount = self.item_amounts[item]
            if always_chance:
                reward_items[item] = amount
            elif random.randrange(0, 100) * 0.01 < self.item_chances[item]:
                reward_items[item] = amount
        gold = Game.items["Soft currency"]
        energy = Game.items["Energy"]
        reward_items[gold] = self.gold_reward
        reward_items[energy] = self.energy_reward
        return reward_items
        

class Mission(object):
    def __init__(self, ident, name, chapter, reward,
                 energy_cost, requirement, recipe_levels):
        self.recipe_levels = recipe_levels # {recipe: level}
        self.ident = ident
        self.name = name
        self.chapter = chapter
        self.reward = reward
        self.energy_cost = energy_cost
        self.requirement = requirement
        self.locked = True
        if self.requirement == None:
            self.locked = False
        self.played = False

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
        return self.reward.give(always_chance)

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
                               0, Reward({}, gold_reward=self.gold_reward), 0, 0, {})

class Order(object):
    def __init__(self, recipe):
        self.recipe = recipe
        self.in_cooldown = False       

class OrderBoard(object):
    def __init__(self, recipes, max_orders=9, max_plays_daily=3):
        self.recipes = recipes # в теории, указывает на список рецептов игрока
        self.max_plays_daily = max_plays_daily
        self.plays_today = 0
        self.max_orders = max_orders
        self.orders = []

        for i in range(self.max_orders):
            self.orders.append(Order(random.choice(self.recipes)))

    def complete_order(self, order):
        if order.in_cooldown:
            return
        order.in_cooldown = True
        return order.recipe.mission.reward

    def discard_order(self, order):
        if order.in_cooldown:
            return
        order.in_cooldown = True

    def generate_board(self):
        for order in self.orders:
            order.recipe = random.choice(self.recipes)
            order.in_cooldown = False

class Requirement(object):
    def __init__(self, quests=[], item_amounts={}):
        self.quests = quests
        self.item_amounts = item_amounts

class Player(object):
    def __init__(self, energy_cap, daily_sessions, mins_per_en,
                 time_between_sessions, gold, recipes, chest):
        self.inventory = {}        
        self.gold_item = Game.items["Soft currency"]
        self.inventory[self.gold_item] = gold
        self.energy_item = Game.items["Energy"]
        self.energy_cap = energy_cap
        self.inventory[self.energy_item] = self.energy_cap
        self.day = 1
        self.session = 0
        self.daily_sessions = daily_sessions
        self.missions_completed = 0
        self.chapter = None
        self.recipes = recipes
        self.order_board = OrderBoard(self.recipes)
        self.mins_per_en = mins_per_en
        self.time_between_sessions = time_between_sessions       
        self.chest = chest

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
        for item in requirement.item_amounts.keys():
            if self.inventory.get(item, 0) < requirements.item_amounts[item]:
                return False
        return True

    def farm_orders(self):
        if self.order_board.plays_today == self.order_board.max_plays_daily:
            return
        self.order_board.plays_today += 1
        self.order_board.generate_board()
        #print("farming orders")
        while True:
            count = 0
            for order in self.order_board.orders:
                if order.in_cooldown or order.recipe.level == 0:
                    count += 1
                    continue
                #print("had gold: " + str(self.gold))
                #reward_items = order.recipe.mission.reward.give(True)
                #for item in reward_items:
                    #print(item.name + ": " + str(reward_items[item]))
                self.play_mission(order.recipe.mission)
                #print("now gold: " + str(self.gold))
                order.in_cooldown = True
                self.missions_completed -= 1 # :(
            if count == len(self.order_board.orders):                 
                 break               

    def get_available_quests(self):
        available_quests = []        
        for quest in self.chapter.quests:
            if quest.completed:                
                continue               
            if quest.is_farmable(self.chapter):
                available_quests.append(quest)        
        return available_quests

    def play_chapter(self, chapter_index):
        self.day = 1
        self.session = 0 # ?..
        self.missions_completed = 0        
        self.chapter = Game.chapters[chapter_index]
        self.chest.update_drop_list(chapter_index)
        self.recipes.extend(self.chapter.recipes)        
        return self.choose_quest()

    def choose_quest(self): # returns tuple (missions_completed, day)
        loop_count = 0
        while True:
            loop_count += 1
            count = 0
            for quest in self.chapter.quests:
                if quest.completed:
                    count += 1
                    if count == len(self.chapter.quests):
                        return (self.missions_completed, self.day)
            available_quests = self.get_available_quests()            
            if len(available_quests) > 0:
                quest = random.choice(available_quests)
                self.play_quest(quest)                
            random.shuffle(self.chapter.missions)
            for mission in self.chapter.missions:
                if mission.locked and self.check_requirement(mission.requirement):
                    self.unlock_mission(mission)
                    
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
        self.order_board.generate_board()
        self.farm_orders()
        if self.session == self.daily_sessions:
            self.skip_day()            
        else:
            self.energy = min(self.energy_cap, self.energy
                              + (1 / self.mins_per_en) * 60
                              * self.time_between_sessions)            

    def open_chest(self):
        reward = self.chest.open()        
        self.receive_reward(reward)
    
    def skip_day(self):        
        self.energy = self.energy_cap        
        self.session = 0
        self.day += 1
        self.open_chest()
        self.order_board.generate_board()
        self.order_board.plays_today = 0
        self.farm_orders()

    def receive_reward(self, reward_items):
        if reward_items == None:
            return
        for item in reward_items.keys():            
            self.change_amount(item, reward_items[item])
                
    def unlock_mission(self, mission):
        mission.unlock()

    def play_mission(self, mission):
        self.energy -= mission.energy_cost
        self.receive_reward(mission.complete())
        self.missions_completed += 1

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
        print("Missions completed: " + str(self.missions_completed))
        print("Gold: " + str(self.gold))        
        print("Energy: " + str(self.energy))
        for item in self.inventory.keys():
            if self.inventory[item] > 0:
                print(item.name + ": " + str(self.inventory[item]))

class Chest(object):
    def __init__(self, full_drop_list):
        self.full_drop_list = full_drop_list # {Reward: (chapter, weight)}
        self.drop_list = None # {abs_weight: Reward}        
        self.max_weight = 0

    def update_drop_list(self, chapter_id):
        self.drop_list = {}
        total_weight = 0
        for reward in self.full_drop_list.keys():
            if self.full_drop_list[reward][0] <= chapter_id:
                total_weight += self.full_drop_list[reward][1]
                self.drop_list[total_weight] = reward
        self.max_weight = total_weight

    def open(self):        
        if self.max_weight == 0:
            return None
        roll_weight = random.randrange(0, self.max_weight)       
        for weight in sorted(self.drop_list.keys()):            
            if roll_weight < weight:                
                return self.drop_list[weight].give(True)        

class Chapter(object):
    def __init__(self, name, items, missions, quests, recipes):
        self.name = name
        self.items = items
        self.missions = []
        for mission in missions:
            if mission.chapter == self.name:
                self.missions.append(mission)
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
        
