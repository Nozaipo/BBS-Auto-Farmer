import json
import re
import os
import subprocess
import threading
import time

os.chdir(".\macros\\")

_all_pots = {
    "super pot tech": 330,
    "pot tech": 329,
    "super pot heart": 336,
    "pot heart": 335,
    "super pot power": 324,
    "pot power": 323,
    "super pot speed": 327,
    "pot speed": 326,
    "super pot mind": 333,
    "pot mind": 332
}

_bags = {
    "Parte 1 (bronze)": 50011,
    "Parte 1 (prata)": 50012,
    "Parte 1 (ouro)": 50013,

    "Parte 2 (bronze)": 50021,
    "Parte 2 (prata)": 50022,
    "Parte 2 (ouro)": 50023,
 
    "Parte 3 (bronze)": 50031,
    "Parte 3 (prata)": 50032,
    "Parte 3 (ouro)": 50033,
}

with open("_chronicle farmadas.json", "r") as file:
    _saga_quest_farmed = json.load(file)


if time.localtime().tm_mon != _saga_quest_farmed['LastMonthUpdate']:
    del _saga_quest_farmed["LastMonthUpdate"]
    for part in _saga_quest_farmed:
        print(part)
        for farmed_bag in _saga_quest_farmed[part]:
            print(farmed_bag)
            _saga_quest_farmed[part][farmed_bag] = False

    _saga_quest_farmed["LastMonthUpdate"] = time.localtime().tm_mon
    with open("_chronicle farmadas.json", "w") as json_file:
        json.dump(_saga_quest_farmed, json_file, indent=4)


_currentSagaQuestSelected = None

_saga_quest_per_nodes = {
    10: "Parte 1",
    16: "Parte 2",
    14: "Parte 3"
}

def show_pot(json_content):
    data_json = json.loads(json_content)    
    pots_in_quest = [reward["content_id"] for reward in data_json["rewards"][0] if reward["content_id"] in _all_pots.values()]

    info_pots_json = {}
    show_in_cmd = []

    for item in data_json["items"]:
        if (pot := item["m_item_id"]) in _all_pots.values():
            if pot in pots_in_quest:
                show_in_cmd.append(f"{list(_all_pots.keys())[list(_all_pots.values()).index(pot)]}")
                show_in_cmd.append(': ')
                show_in_cmd.append(f"{item['amount']}   ")

            info_pots_json.update({list(_all_pots.keys())[list(_all_pots.values()).index(pot)]: item["amount"]})
    
    print(''.join(show_in_cmd))

    with open("./info/pots.json", "w") as json_file:
        json.dump(info_pots_json, json_file, indent=4)

def selectSagaQuest(json_content=None):
    global _currentSagaQuestSelected
    if json_content:
        data_json = json.loads(json_content)    
        _currentSagaQuestSelected = _saga_quest_per_nodes[len(data_json["node_progress"])]
    
    def target():
        for part, types_bag in _saga_quest_farmed.items():
            if not all(types_bag.values()):
                for type_bag in ['bronze', 'prata', 'ouro']:
                    if not types_bag[type_bag]:
                        if part != _currentSagaQuestSelected:
                            subprocess.run(f"change_to_{part}.exe")
                        subprocess.run(f"saga-quest_to_{type_bag}.exe")
                        return None
    thread = threading.Thread(target=target)
    thread.start()

def analyzeLast(lastBagId, amountBag, tickets):
    lastBagId = str(lastBagId)
    amountBag = int(amountBag)
    tickets = int(tickets)
    def target():
        part = ['Parte 1', 'Parte 2', 'Parte 3'][(int(re.search(r"500(.)", lastBagId).group(1))) - 1]
        type_bag = ['bronze', 'prata', 'ouro'][(int(re.search(r"500.(.)", lastBagId).group(1))) -1]

        if tickets >= 10:
            if "5001" in str(lastBagId):
                if amountBag < 8202:
                    subprocess.run("retry.exe")
                else:
                    _saga_quest_farmed[part].update({type_bag: True})
                    with open("_chronicle farmadas.json", "w") as json_file:
                        json.dump(_saga_quest_farmed, json_file, indent=4)
                    subprocess.run("to_saga_quest.exe")
                    selectSagaQuest()
            else:
                if amountBag < 6782:
                    subprocess.run("retry.exe")
                else:
                    _saga_quest_farmed[part].update({type_bag: True})
                    with open("_chronicle farmadas.json", "w") as json_file:
                        json.dump(_saga_quest_farmed, json_file, indent=4)
                    subprocess.run("to_saga_quest.exe")
                    selectSagaQuest()
    thread = threading.Thread(target=target)
    thread.start()

def show_bags(json_content):
    data_json = json.loads(json_content)
    lastBag, amountBag = None, None

    info_bag_json = {}
    show_in_cmd = []

    for item in data_json["items"]:
        if (bag := item["m_item_id"]) in _bags.values():

            if bag == data_json['rewards'][0][-1]['content_id']:
                show_in_cmd.append(f"{list(_bags.keys())[list(_bags.values()).index(bag)]}")
                show_in_cmd.append(': ')
                show_in_cmd.append(f"{item['amount']}   ")
                amountBag = item['amount']
                lastBag = bag

            info_bag_json.update({list(_bags.keys())[list(_bags.values()).index(bag)]: item["amount"]})
    
    print(''.join(show_in_cmd))


    with open("./info/bags.json", "w") as json_file:
        json.dump(info_bag_json, json_file, indent=4)
    
    analyzeLast(lastBag, amountBag, int(data_json['base_menu']['ap']))

class UpdateInfo:
    def __init__(self):
        self.gaming = None
   
    def response(self, flow):
        url = flow.request.pretty_url
        finish = None

        finish = re.search(r"(raid_quest|co_quest|saga_quest|limited_quest).*finish", url)
        quest_type = {
            'raid_quest': show_pot,
            'co_quest': show_pot,
            'saga_quest': show_bags,
            'limited_quest': show_pot,
        }

        farming_saga_quest = re.search(r"saga_quest.*index", url)

        # if farming_saga_quest:
        if not self.gaming and farming_saga_quest:
            self.gaming = True
            selectSagaQuest(json_content=flow.response.content)
        elif finish:
            quest_type[finish.group(1)](flow.response.content)

addons = [UpdateInfo()]