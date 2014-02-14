import menu_utils
import json

open('nyc.json', 'w').write(json.dumps(menu_utils.get_most_recent_menu('nyc')))
open('ltd.json', 'w').write(json.dumps(menu_utils.get_most_recent_menu('ltd')))
open('epic.json', 'w').write(json.dumps(menu_utils.get_most_recent_menu('epic')))

# not working, see https://www.facebook.com/groups/195619873786800/permalink/794128187269296
# open('seattle.json', 'w').write(json.dumps(menu_utils.get_most_recent_menu('seattle')))
