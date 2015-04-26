import sys
sys.path.append('/Users/mikezappitello/Documents/sub_docs/mAnds')

import urllib2
from HTMLParser import HTMLParser
import json
import re
from data import data_access as da

player_data = da.player_data_as_json()

for player in player_data:
  print player['weight']
  player['weight'] = int(player['weight'])

da.json_debug(player_data)

players_json = json.dumps(player_data, sort_keys=True, indent=2)
json_file = open(da.k_players_file, 'w')
json_file.write(players_json)
json_file.close()
