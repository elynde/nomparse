import menu_utils
import json

open('nyc.json', 'w').write(json.dumps(menu_utils.get_most_recent_menu('nyc')))
open('ltd.json', 'w').write(json.dumps(menu_utils.get_most_recent_menu('ltd')))
open('epic.json', 'w').write(json.dumps(menu_utils.get_most_recent_menu('epic')))
