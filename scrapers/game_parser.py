# script to crawl espn for all play by play stats
import sys
sys.path.append('/Users/mikezappitello/Documents/sub_docs/mAnds')

import urllib2
from HTMLParser import HTMLParser
import json
import copy
import grab_game_urls as urls
from data import data_access as da
from nba_play_parser import nba_play_parser, play_type

def generatePbpHtml(game_id):
    """
    retrieve the html for a single game
    """
    base_url = 'http://scores.espn.go.com/nba/playbyplay?gameId='
    all_game_str = '&period=0'
    url = base_url + str(game_id) + all_game_str

    scoreboard_page = urllib2.urlopen(url)
    scoreboard_page_html = scoreboard_page.read()
    scoreboard_page.close()
    
    return scoreboard_page_html

def generateTestHtml():
  """
  use a saved html file instead
  """
  html = open(da.k_top_dir + "blazers_jazz.html").read()
  return html

def is_new_record(attrs):
    """
    is an attribute for a new row?
    """
    if attrs and attrs[0][0] == 'class':
        if attrs[0][1] == 'even' or attrs[0][1] == 'odd':
            return True

    return False

def generate_tag(attrs):
    """
    what kind of record is this?
    
    types are - time, play, score, and bs
    return type as string we'll later use as key!
    
    this is kind of hacky and dumb, but it works, so i don't really care
    """
    if (len(attrs) < 2):
        return "bs"
    if (attrs[1][0] == 'width' and attrs[1][1] == '50'):
        return "time"
    if (attrs[1][0] == 'style' and attrs[1][1] == 'text-align:left;'):
        return "play"
    if (attrs[0][0] == 'colspan' and attrs[0][1] == '3'):
        return "bs"
    if (attrs[2][0] == 'nowrap'):
        return "score"

    return "bs"

def team_id_from_name(name):
  """
  find the team id from the team name
  """
  teams = da.team_data_as_json()
  for team in teams:
    if team['name'] == name:
      return team['id']

class gameHTMLParser(HTMLParser):
    """
    class that will parse the scoreboard data
    """

    def __init__(self):
      HTMLParser.__init__(self)
      self.players = []
      self.shit_teams = 0
      self.shit_scores = 0
      self.home_id = 0
      self.away_id = 0
      self.home_score = 0
      self.away_score = 0

    def start_parse(self, html):
        """
        function to start the parser, taking in the url and dates array
        """
        self.started_game = False
        self.in_record = False 
        self.tag_stack = []
        self.quarter = 1
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        """
        what do we do when we hit a start tag?
        * first we find the data on the game the start of the html
        * then we find data for line of the play by play
        """
        if not self.started_game:
          if (tag == 'div' and attrs and 
            attrs[0][0] == 'class' and
            attrs[0][1] == 'series-dropdown'):
              self.tag_stack.append(tag)
          elif (tag == 'td' and attrs and
            attrs[0][0] == 'class' and
            attrs[0][1] == 'team' and
            self.tag_stack[-1] == 'div'):
              self.tag_stack.append('team')
          elif (tag == 'td' and attrs and
            attrs[0][0] == 'class' and
            attrs[0][1] == 'score' and 
            self.tag_stack[-1] == 'div'):
              self.tag_stack.append('score')
        else :
          if (tag == "tr" and is_new_record(attrs)):
              self.in_record = True

          if (self.in_record and tag == "td" and attrs):
              record_type = generate_tag(attrs)
              self.tag_stack.append(record_type)

    def handle_endtag(self, tag):
        """
        what do we do when we hit an end tag?
        """
        if not self.started_game:
          if (tag == 'td' and self.tag_stack and
            (self.tag_stack[-1] == 'team' or self.tag_stack[-1] == 'score')):
              self.tag_stack.pop()
        else :
          if self.in_record:
              if tag == 'tr':
                  self.play_parser.output_to_csv()
                  self.in_record = False
                  self.play_parser.reset(self.quarter)
              elif tag == 'td':
                  self.tag_stack.pop()

    def set_players(self):
      """
      using team id's, get all the players in the game. initialize an nba play
      parser with the players. set the started game flag to true
      """
      players = da.team_roster('id', self.home_id)
      players = players + da.team_roster('id', self.away_id)
      self.started_game = True
      self.play_parser = nba_play_parser(players)

    def handle_data(self, data):
        """
        what do we do when we hit some data?
        """
        if not self.started_game and self.tag_stack:
          if self.tag_stack[-1] == 'team':
            if self.shit_teams < 2:
              self.shit_teams = self.shit_teams + 1
            elif self.away_id == 0:
              self.away_id = team_id_from_name(data)
            elif self.home_id == 0:
              self.home_id = team_id_from_name(data)
          elif self.tag_stack[-1] == 'score':
            if self.shit_scores < 2:
              self.shit_scores = self.shit_scores + 1
            elif self.away_score == 0:
              self.away_score = data
            elif self.home_score == 0:
              self.home_score = data
              self.set_players()

        if not self.in_record:
           return

        record_type = self.tag_stack[-1]
        if record_type == 'play':
            self.play_parser.set_play_string(data)
        elif record_type == 'time':
            self.play_parser.set_time(data, self.quarter)
        elif record_type == 'score':
            self.play_parser.set_score(data)
        elif record_type == 'bs':
            self.quareter = 3

'''
dates = urls.get_game_ids()
parser = gameHTMLParser()

for date in dates:
    for game in date['gameIds']:
        html = generatePbpHtml(game)
        parser.start_parse(html):
'''

html = generatePbpHtml(400579312)
# html = generateTestHtml()
parser = gameHTMLParser()
data = parser.start_parse(html)
