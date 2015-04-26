import json

# top level directory for this project
#
# if you fork this repo, make sure to change this string
k_top_dir = '/Users/mikezappitello/Documents/sub_docs/mAnds/'

# directory and file paths
k_data_dir = k_top_dir + 'data/'
k_teams_file = k_data_dir + 'teams.json'
k_players_file = k_data_dir + 'players.json'

def team_data_as_json():
  """
  retrieve all of the teams data as a json object
  """
  team_data = open(k_teams_file).read()
  return json.loads(team_data)

def player_data_as_json():
  """
  retrieve all of the players in the league as a json object
  """
  player_data = open(k_players_file).read()
  return json.loads(player_data)

def json_debug(data_as_json):
  print json.dumps(
    data_as_json,
    sort_keys=True,
    indent=2,
    separators=(",", ":"))

def team_roster(team_attr, attr_value, current_only = True):
  """
  retrieve all the players on a team as a json object

  search for the team using a team attribute and its value (e.g. 'abbr', 'okc')
  """
  teams = team_data_as_json()
  team_id = 0

  for team in teams:
    if team[team_attr] == attr_value:
      team_id = team['id']

  players = player_data_as_json()
  roster = []

  for player in players:
    if player['current_team_id'] == team_id:
      roster.append(player)
    elif ('former_team_id' in player.keys() and
      team_id in player['former_team_id'] and
      not current_only):
        roster.append(player)

  return roster

class player_finder():
  """
  helper to find a player from a list of players
  """
  def __init__(self, players):
    self.players = players

  def set_players(players):
    self.players = players

  def find_player_id(self, name):
    for player in self.players:
      json_name = player['first_name'] + ' ' + player['last_name']
      name = name.strip()
      if json_name == name:
        return player

    print "could not find " + name + " in players :( \n" 
    return 0
