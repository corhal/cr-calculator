import csv

def make_recipes():
    all_items = {}
    with open('recipeLevels.csv', 'rt', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        strings = []
        for row in reader:            
            if row["DISH_ID"] != "" and row["DISH_ID"] != "end":
                first = True
                string = "["
            if row["INGREDIENT"] != "":
                if not first:
                    string += '},'
                else:
                    #string += '}'
                    first = False
                string += '{"ingridient": ' + row["INGREDIENT"]
            if row["COUNT"] != "":
                string += ','
                string += '"count": ' + row["COUNT"]
            if row["ACTION"] != "":
                string += ','
                string += '"steps": [{"id": ' + row["ACTION"] + '}'
            if row["DISH_ACTION"] != "":
                string += ','
                string += '{"id": ' + row["DISH_ACTION"]
            if row["DISH"] != "":
                string += ','
                string += '"dish": ' + row["DISH"] + '}'
            if row["MINIGAME"] != "":
                string += ','
                string += '{"id": ' + row["MINIGAME"] + '}'
            if row["ACTION"] != "":
                string += ']'
            if row["DISH_ID"] == "end":
                string += '}]'
                strings.append(string)
    return strings
                
strings = make_recipes()
for string in strings:
    print(string)
