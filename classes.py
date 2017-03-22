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
    def __init__(self, ident, name, chapter, quest_chain, item_conditions, reward, required_quests):
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
        if self.reward.keys != 0:
            tostring += " gives keys: " + str(self.reward.keys)
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
        return (self.reward, False)

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
    def __init__(self, item_chances, gold_reward=0, energy_reward=0, keys=0):
        self.item_chances = item_chances # dict
        self.gold_reward = gold_reward
        self.energy_reward = energy_reward
        self.keys = keys

class Mission(object):
    def __init__(self, ident, name, chapter, reward, energy_cost, keys_cost, recipe_levels):
        self.recipe_levels = recipe_levels # {recipe: level}
        self.ident = ident
        self.name = name
        self.chapter = chapter
        self.reward = reward
        self.energy_cost = energy_cost
        self.keys_cost = keys_cost
        self.locked = True
        if self.keys_cost == 0:
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
        tostring += " , keys cost: " + str(self.keys_cost)
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
        return (self.reward, always_chance)

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
        #print(self.name + " upgraded to " + str(self.level))
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
                               0, Reward({}, self.gold_reward), 0, 0, {})

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

class Player(object):
    def __init__(self, energy_cap, daily_sessions, mins_per_en,
                 time_between_sessions, gold, recipes):
        self.day = 1
        self.session = 0
        self.daily_sessions = daily_sessions
        self.missions_completed = 0
        self.keys = 0
        self.gold = gold
        self.inventory = {}
        self.energy_cap = energy_cap
        self.energy = self.energy_cap
        self.recipes = recipes
        self.order_board = OrderBoard(self.recipes)
        self.mins_per_en = mins_per_en
        self.time_between_sessions = time_between_sessions
        recipe_items = []
        for recipe in recipes:
            recipe_items.append(recipe.frag_item)
        self.chest = Chest(recipe_items)

    def farm_orders(self):
        if self.order_board.plays_today == self.order_board.max_plays_daily:
            return
        self.order_board.plays_today += 1
        self.order_board.generate_board()
        #print("Gold before farming orders: " + str(self.gold))
        while True:
            count = 0
            for order in self.order_board.orders:
                if order.in_cooldown or order.recipe.level == 0:
                    count += 1
                    continue
                self.play_mission(order.recipe.mission)
                order.in_cooldown = True
                self.missions_completed -= 1 # :(
            if count == len(self.order_board.orders):
                 #print("Gold after farming orders: " + str(self.gold))
                 break               

    def get_available_quests(self, chapter):
        available_quests = []        
        for quest in chapter.quests:
            if quest.completed:                
                continue               
            if quest.is_farmable(chapter):
                available_quests.append(quest)        
        return available_quests

    def play_chapter(self, chapter_index):
        self.day = 1
        self.session = 0 # ?..
        self.missions_completed = 0
        self.keys = 0 # ?..
        chapter = Game.chapters[chapter_index]
        self.recipes.extend(chapter.recipes)        
        for recipe in self.recipes:                    
            if not recipe.frag_item in self.chest.items:
                self.chest.items.append(recipe.frag_item)
        
        return self.choose_quest(chapter)

    def choose_quest(self, chapter): # returns tuple (missions_completed, day
        loop_count = 0
        while True:
            loop_count += 1
            count = 0
            for quest in chapter.quests:
                if quest.completed:
                    count += 1
                    if count == len(chapter.quests):
                        return (self.missions_completed, self.day)
            available_quests = self.get_available_quests(chapter)            
            if len(available_quests) > 0:
                quest = random.choice(available_quests)
                self.play_quest(quest, chapter)                
            random.shuffle(chapter.missions)
            for mission in chapter.missions:
                if mission.locked and self.keys >= mission.keys_cost:
                    self.unlock_mission(mission)
                    
            if loop_count == 1000:
                print("Looks like you have a dead end")
                print("-" * 30)
                self.show_stats()
                print("-" * 30)
                print("Currently open missions:")
                for mission in chapter.missions:
                    if not mission.locked:
                        print(mission)
                print("Currently available quests:")
                for quest in chapter.quests:
                    if not quest.completed and not quest.locked:
                        print(quest)                
                raise ValueError("Dead end!")

    def play_quest(self, quest, chapter):
        item_conditions = quest.item_conditions
        full_conditions = quest.full_conditions
        for item in full_conditions.keys():
            self.farm_item(item, full_conditions[item], chapter)        
        for item in item_conditions.keys():           
            while self.inventory.get(item, 0) < item_conditions[item]:
                if self.gold < quest.full_gold_cost:
                    self.farm_gold(quest.full_gold_cost, chapter)
                self.craft(item, chapter)            
        self.complete_quest(quest)

    def complete_quest(self, quest):
        item_conditions = quest.item_conditions
        for item in item_conditions.keys():            
            self.give_item(item, item_conditions[item])
        self.receive_reward(quest.complete())

    def farm_item(self, item, amount, chapter):
        farm_mission = None
        for mission in chapter.missions:
            if item in mission.reward.item_chances.keys():
                farm_mission = mission
                break
        if farm_mission == None:
            raise ValueError("Can't find " + item.name + " in mission drop")
        while self.inventory.get(item, 0) < amount:
            self.play_mission(farm_mission)

    def farm_gold(self, amount, chapter):
        max_reward = 0
        for mission in chapter.missions:
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
            self.skip_session()

    def receive_energy(self, amount):
        self.energy += amount

    def skip_session(self):
        self.session += 1
        self.order_board.generate_board()
        self.farm_orders()
        if self.session == self.daily_sessions:
            self.skip_day()            
        else:
            self.energy = min(self.energy_cap, self.energy + (1 / self.mins_per_en) * 60 * self.time_between_sessions)

    def open_chest(self):
        received_item = self.chest.open()
        self.take_item(received_item[0], received_item[1])
    
    def skip_day(self):
        self.energy = self.energy_cap
        self.session = 0
        self.day += 1
        self.open_chest()
        self.order_board.generate_board()
        self.order_board.plays_today = 0
        self.farm_orders()

    def receive_reward(self, reward_tuple):
        reward = reward_tuple[0]
        always_chance = reward_tuple[1]
        self.receive_keys(reward.keys)
        self.receive_gold(reward.gold_reward)
        self.receive_energy(reward.energy_reward)
        for item in reward.item_chances.keys():
            if always_chance:
                self.take_item(item, 1)
            elif random.randrange(0, 100) * 0.01 < reward.item_chances[item]:
                self.take_item(item, 1)
                
    def unlock_mission(self, mission):
        self.spend_keys(mission.keys_cost)
        mission.unlock()

    def play_mission(self, mission):
        self.spend_energy(mission.energy_cost)
        self.receive_reward(mission.complete())
        self.missions_completed += 1

    def craft(self, item, chapter):
        if item.recipe == None:
            return
        for item_component in item.recipe:
            if self.inventory.get(item_component, 0) < item.recipe.get(item_component, 0):
                if item_component.recipe != None:
                    while self.inventory.get(item_component, 0) < item.recipe[item_component]:
                        self.craft(item_component, chapter)
                else:
                    return
            elif item.recipe[item_component] <= self.inventory[item_component]:                
                self.craft(item_component, chapter)                
            
        for item_component in item.recipe:
            self.give_item(item_component, item.recipe[item_component])
        if self.gold < item.gold_cost:
            self.farm_gold(item.gold_cost, chapter)
        self.spend_gold(item.gold_cost)
        self.take_item(item, 1)

    def receive_keys(self, amount):
        self.keys += amount

    def spend_keys(self, amount):
        self.keys -= amount
        if self.keys < 0:
            raise ValueError("Player has " + str(self.keys) + " keys, which is less than 0")

    def receive_gold(self, amount):
        self.gold += amount

    def spend_gold(self, amount):
        self.gold -= amount
        if self.gold < 0:
            raise ValueError("Player has " + str(self.gold) + " gold, which is less than 0")

    def take_item(self, item, amount):
        self.inventory[item] = self.inventory.get(item, 0) + amount        
        self.upgrade_recipes()

    def give_item(self, item, amount):
        self.inventory[item] = self.inventory.get(item, 0) - amount
        if self.inventory[item] < 0:
            raise ValueError(item.name + " amount < 0")

    def upgrade_recipes(self):
        for recipe in self.recipes:
            if recipe.can_upgrade(self.gold, self.inventory.get(recipe.frag_item, 0)):
                recipe.upgrade()
                self.spend_gold(recipe.up_gold_by_levels[recipe.level])
                self.give_item(recipe.frag_item, recipe.up_frags_by_levels[recipe.level])
                

    def show_stats(self):
        print("-" * 30)
        print("Day: " + str(self.day))
        print("Missions completed: " + str(self.missions_completed))
        print("Gold: " + str(self.gold))
        print("Keys: " + str(self.keys))
        print("Energy: " + str(self.energy))
        for item in self.inventory.keys():
            if self.inventory[item] > 0:
                print(item.name + ": " + str(self.inventory[item]))

class Chest(object):
    def __init__(self, items):
        self.items = items

    def open(self):
        item = random.choice(self.items)
        amount = random.randint(1, 7)
        return (item, amount)

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
        
