import sys
sys.path.append('/Users/mikezappitello/Documents/sub_docs/mAnds')

from play_details import *
import re
from data.data_access import player_finder

class play_type():
    """
    constsant strings we'll use for play type
    """
    SHOT = "shot"
    FOUL = "foul"
    REBOUND = "rebound"
    TURNOVER = "turn over"
    BLOCK = "block"
    SKIP = "skip"
    UNKNOWN = "unknown"

class nba_play_parser():
    """
    class that will parse a play.
   
    its constructor takes a json list of players and creates a player finder
    between parsing plays call reset to clear history
    setting the play string parses out the play
    """

    def __init__(self, players, game_id):
        """
        constructor for a play.
        
        the string for the play is set later, but does not contain the quarter,
        so we'll add that in here. also create the player_finder for a list of
        players
        """
        self.game_id = game_id
        self.play_type = play_type().UNKNOWN
        self.quarter = 1
        self.player_finder = player_finder(players)

    def reset(self, quarter):
        """
        clear all the data and reset the quarter
        """
        self.quarter = quarter
        self.play_type = play_type().UNKNOWN
        self.details = None
        self.play_as_string = None

    def set_play_string(self, play_as_string):
        """
        set the string that describes the play, and then parse it for info
        """
        self.play_as_string = play_as_string
        self.parse_for_type()

        if self.play_type == play_type().SHOT:
            self.parse_shot()
        elif self.play_type == play_type().FOUL:
            self.parse_foul()
        elif self.play_type == play_type().REBOUND:
            self.parse_rebound()
        elif self.play_type == play_type().TURNOVER:
            self.parse_turnover()

    def set_score(self, score_as_string):
        """
        set the score at the end of the play. parse out for each team.
        """
        scores = re.match(r'^(?P<home>\d{1,3})-(?P<away>\d{1,3})$', score_as_string)
        if scores:
            self.home_score = scores.group('home')
            self.away_score = scores.group('away')
          
    def set_time(self, time_as_string, quarter):
        """
        set what time in the game the play happened.
        we count up from zero.  11:00 left in the first is 60 seconds
        """
        minutes = 0;
        if quarter < 5:
            # regulation, 12 minutes per quarter
            minutes = (quarter - 1) * 12
        else:
            # FREE BASKETBALL !!!
            minutes = 48 + (quarter - 5) * 5
        
        times = re.match(r'^(?P<minutes>\d{1,2}):(?P<seconds>\d{2})$', time_as_string)
        if times:
            minutes = minutes + int(times.group('minutes'))
            self.time = minutes * 60 + int(times.group('seconds'))

    def parse_for_type(self):
        """
        parse play
        """
        if "makes" in self.play_as_string:
            self.play_type = play_type().SHOT
            self.details = nba_shot(True, self.player_finder)
        elif "misses" in self.play_as_string:
            self.play_type = play_type().SHOT
            self.details = nba_shot(False, self.player_finder)
        elif "foul" in self.play_as_string:
            self.play_type = play_type().FOUL
            self.details = nba_foul()
        elif "rebound" in self.play_as_string:
            self.play_type = play_type().REBOUND
            self.details = nba_rebound()
        elif ("turnover" in self.play_as_string or
          "traveling" in self.play_as_string or 
          "bad pass" in self.play_as_string):  
            self.play_type = play_type().TURNOVER
            self.details = nba_turnover()
        elif "blocks" in self.play_as_string:
          self.play_type = play_type().BLOCK
          self.details = nba_block()
        elif ("enters the game" in self.play_as_string or
          "kicked ball" in self.play_as_string or
          "delay of game" in self.play_as_string or
          "vs." in self.play_as_string):
            self.play_type = play_type().SKIP
            self.details = None
        else:
          print self.play_as_string
          print "who knows what just happened?!?" + "\n"

    def parse_shot(self):
        """
        expecting this to be in the form: 'player' makes/misses 'shot details'
        at this point, self.details has already been initialized (with if the
        shot has been made or not). now the details must be parsed out so that
        we know how much the shot was worth and if there was an assisting
        player.
        """
        match = re.match(r'^(?P<player>.+)\s+((makes)|(misses))\s*(?P<details>.+)$', self.play_as_string)
        if match:
            self.details.player = self.player_finder.find_player_id(match.group('player'))
            self.details.parse_details(match.group('details'))
        else:
            print self.play_as_string
            print "shot string did not match regex!!!!" + "\n"


    def parse_foul(self):
        """
        expecting this to be in the form: ''
        """
        match = re.match(r'^.*$', self.play_as_string)
        if match:
            self.details.player = self.player_finder.find_player_id('Elfrid Payton')
            self.details.parse_details("wat")
        else:
            print self.play_as_string
            print "foul string did not match regex!!!!" + "\n"

    def parse_rebound(self):
        """
        expecting this to be in the form ???
        """
        match = re.match(r'^.*$', self.play_as_string)
        if match:
            self.details.player = self.player_finder.find_player_id('Elfrid Payton')
            self.details.parse_details("wat")
        else:
            print self.play_as_string
            print "rebound string did not match regex!!!!" + "\n"

    def parse_turnover(self):
        """
        expecting this to be in the form ???
        """
        match = re.match(r'^.*$', self.play_as_string)
        if match:
            self.details.player = self.player_finder.find_player_id('Elfrid Payton')
            self.details.parse_details("wat")
        else:
            print self.play_as_string
            print "turnover string did not match regex!!!!" + "\n"

    def output_to_csv(self):
        """
        switch to the correct dot csv file based on play type, then append a new
        line to the end of that file.
        """
        if self.play_type == play_type().SHOT:
            a = 1
            print self.details.for_csv()
        elif self.play_type == play_type().FOUL:
            a = 1
            # print self.details.for_csv()
        elif self.play_type == play_type().REBOUND:
            a = 1
            # print self.details.for_csv()
        elif self.play_type == play_type().TURNOVER:
            a = 1
            # print self.details.for_csv()
        elif self.play_type == play_type().BLOCK:
            a = 1
            # print self.details.for_csv()
        elif self.play_type == play_type().SKIP:
            a = 1
        elif self.play_as_string:
            print self.play_as_string
            print "i dunno what type of play this is. :(" + "\n"
        
