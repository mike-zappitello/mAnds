# script to crawl espn for all play by play stats

import urllib2
from HTMLParser import HTMLParser
import json
import re
import copy
import grab_game_urls as urls

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

class playType():
    """
    constsant strings we'll use for play type
    """
    SHOT = "shot"
    FOUL = "foul"
    REBOUND = "rebound"
    TURNOVER = "turn over"
    UNKNOWN = "unknown"

class nbaPlayer():
    """
    class that will model a player
    """
    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.suffix = None

    def parse_player(self, player_string):
        """"
        parse the mans name out. TODO - write some kind of lookup that grabs the
        player id from some source. so that shit can be linked together later.
        """
        names = player_string.split(" ")
        if len(names) > 1:
            self.first_name = names[0]
            self.last_name = names[1]
        if len(names) > 2:
            self.suffix = names[2]

    def for_csv(self):
        ret = self.first_name + " " + self.last_name
        if self.suffix:
            ret = ret + " " + self.suffix
        return ret

class nbaFoul():
    """
    not necessarily a hard playoff foul, but someone did something they
    shouldn't have to someone else.
    """
    def __init__(self):
        self.player = nbaPlayer()
        self.fouler = None

    def parse_details(self, foul_string):
        """

        """
        self.offensive = True

    def for_csv(self):
        ret = self.player.for_csv() + ", "
        if self.fouler:
            ret + self.fouler.for_csv() + ", "
        else:
            ret + "none, "
        return ret

class nbaRebound():
    """
    a shot went up but didn't fall. who got the board?
    """
    def __init__(self):
        self.player = nbaPlayer()
        self.offensive = False

    def parse_details(self, foul_string):
        """
        """
        self.offensive = True

    def for_csv(self):
        ret = self.player.for_csv() + ", "
        return ret

class nbaRTurnover():
    """
    someone messed up. they either threw the ball away, dribbled it off their
    foot, stepped out of bounds, or did something even dumber.
    """
    def __init__(self):
        self.player = nbaPlayer()

    def parse_details(self, foul_string):
        """
        """
        self.wat = True

    def for_csv(self):
        ret = self.player.for_csv() + ", "
        return ret

class nbaShot():
    """
    class that models a shot.  it only cares about if a shot was made, how many
    points it was worth, and who assisted, if anyone.
    """
    def __init__(self, made):
        """
        record if a shot was made.  as of right now, there is no value to the
        shot and now assist player to the shot.
        """
        self.made = made 
        self.player = nbaPlayer()
        self.value = None
        self.assister = None

    def parse_details(self, shot_string):
        """
        the shot details vary a whole bunch.  its kind of a pain in the ass to
        capture all the details. instead of doing a full on language parser,
        i've just hacked some stuff together to get some decent results.  it
        helps that (for the moment) we're only trying to grab the total number
        of points and the potentially assisting player.
        """
        # regex match for a shot with an assist
        shot_with_assist = re.match(r'^(?P<shot>.+)\s+(\((?P<assist>.*)assists\))?$', shot_string)

        if shot_with_assist:
            self.set_value(shot_with_assist.group('shot'))
            if shot_with_assist.group('assist'):
                self.assister = nbaPlayer()
                self.assister.parse_player(shot_with_assist.group('assist'))

            return

        # regex match for a free throw
        free_throw = re.match(r'^free\sthrow\s(?P<number>\d)\sof\s(?P<total>\d)$', shot_string)
        if free_throw:
            self.set_value("foul")
            return

        # regex match for things that get through all previous attempts. we're
        # looking for keywords like shot, jumber, layup and dunk.
        shot_or_jumper = re.match(r'^(?P<stuff>.*)(?P<shot>(shot)|((j|J)umper)|(layup)|(dunk))$', shot_string)
        if shot_or_jumper:
            self.set_value(shot_or_jumper.group('stuff'))
            return

        # none of the regexes worked.  print out the shot detials string so that
        # one of the regex strings can be modified to catch it. in the future we
        # might want to throw an error here.
        print shot_string + "\n"
        print "unable to parse shot details!!!" + "\n"

    def set_value(self, shot_string):
        """
        set the points value for the shot. it just looks for 'three' or 'foul'
        to set the value to 3 or 1. if neither are found, its a two point shot.
        """
        if "three" in shot_string:
            self.value = 3
        elif "foul" in shot_string:
            self.value = 1
        else:
            self.value = 2

    def for_csv(self):
        """
        return a string that will be appended to the end of a dot csv file.
        """
        ret = str(self.made) + ", "
        ret = ret + self.player.for_csv() + ", "
        ret = ret + str(self.value) + ", "
        if self.assister:
            ret = ret + self.assister.for_csv()
        else:
            ret = ret + "none"

        return ret

class nbaPlay():
    """
    class that will hold a play.
    
    it should have a string as its constructor
    it should be able to figure out what type of play it is
    it should be able to find all of the important details for that type of play
    it should be able to write out a string to be appended to a dot csv file
    """

    def __init__(self, quarter):
        """
        constructor for a play.
        
        the string for the play is set later, but does not contain the quarter,
        so we'll add that in here.
        """
        self.play_type = playType().UNKNOWN
        self.quarter = 1

    def set_play_string(self, play_as_string):
        """
        set the string that describes the play, and then parse it for info
        """
        self.play_as_string = play_as_string
        self.parse_for_type()

        if self.play_type == playType().SHOT:
            self.parse_shot()
        elif self.play_type == playType().FOUL:
            self.parse_foul()
        elif self.play_type == playType().REBOUND:
            self.parse_rebound()
        elif self.play_type == playType().TURNOVER:
            self.parse_turnover()

    def set_score(self, score_as_string):
        """
        set the score at the end of the play. parse out for each team.
        """
        scores = re.match(r'^(?P<home>\d{1,3})-(?P<away>\d{1,3})$', score_as_string)
        if scores:
            self.home_score = scores.group('home')
            self.home_score = scores.group('away')
          
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
            self.play_type = playType().SHOT
            self.details = nbaShot(True)
        if "misses" in self.play_as_string:
            self.play_type = playType().SHOT
            self.details = nbaShot(False)
        elif "foul" in self.play_as_string:
            self.play_type = playType().FOUL
            self.details = nbaFoul()
        elif "rebound" in self.play_as_string:
            self.play_type = playType().REBOUND
            self.details = nbaRebound()
        elif "turnover" in self.play_as_string:
            self.play_type = playType().TURNOVER
            self.details = nbaTurnover()
        else:
          print self.play_as_string + "\n"
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
            self.details.player.parse_player(match.group('player'))
            self.details.parse_details(match.group('details'))
        else:
            print self.play_as_string + "\n"
            print "shot string did not match regex!!!!" + "\n"


    def parse_foul(self):
        """
        expecting this to be in the form: ''
        """
        match = re.match(r'^.*$', self.play_as_string)
        if match:
            self.details.player.parse_player("Lebron James")
            self.details.parse_details("wat")
        else:
            print self.play_as_string + "\n"
            print "foul string did not match regex!!!!" + "\n"

    def parse_rebound(self):
        """
        expecting this to be in the form ???
        """
        match = re.match(r'^.*$', self.play_as_string)
        if match:
            self.details.player.parse_player("Lebron James")
            self.details.parse_details("wat")
        else:
            print self.play_as_string + "\n"
            print "rebound string did not match regex!!!!" + "\n"

    def parse_turnover(self):
        """
        expecting this to be in the form ???
        """
        match = re.match(r'^.*$', self.play_as_string)
        if match:
            self.details.player.parse_player("Lebron James")
            self.details.parse_details("wat")
        else:
            print self.play_as_string + "\n"
            print "turnover string did not match regex!!!!" + "\n"

    def output_to_csv(self):
        """
        switch to the correct dot csv file based on play type, then append a new
        line to the end of that file.
        """
        if self.play_type == playType().SHOT:
            print "shot:" + "\n" + self.play_as_string + "\n"
        elif self.play_type == playType().FOUL:
            print "foul:" + "\n" + self.play_as_string + "\n"
        elif self.play_type == playType().REBOUND:
            print "rebound:" + "\n" + self.play_as_string + "\n"
        elif self.play_type == playType().TURNOVER:
            print "turnover:" + "\n" + self.play_as_string + "\n"
        else:
            print "i dunno what type of play this is. :(" + "\n"
            print self.play_as_string + "\n"
        

class gameHTMLParser(HTMLParser):
    """
    class that will parse the scoreboard data
    """
    def start_parse(self, html):
        """
        function to start the parser, taking in the url and dates array
        """
        self.in_record = False 
        self.tag_stack = []
        self.quarter = 1
        self.play = nbaPlay(self.quarter)
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        """
        what do we do when we hit a start tag?
        """
        if (tag == "tr" and is_new_record(attrs)):
            self.in_record = True

        if (self.in_record and tag == "td" and attrs):
            record_type = generate_tag(attrs)
            self.tag_stack.append(record_type)

    def handle_endtag(self, tag):
        """
        what do we do when we hit an end tag?
        """
        if self.in_record:
            if tag == 'tr':
                self.play.output_to_csv()
                self.in_record = False
                self.play.__init__(self.quarter)
            elif tag == 'td':
                self.tag_stack.pop()

    def handle_data(self, data):
        """
        what do we do when we hit some data?
        """
        if not self.in_record:
           return

        record_type = self.tag_stack[-1]
        if record_type == 'play':
            self.play.set_play_string(data)
        elif record_type == 'time':
            self.play.set_time(data, self.quarter)
        elif record_type == 'score':
            self.play.set_score(data)
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
parser = gameHTMLParser()
data = parser.start_parse(html)
