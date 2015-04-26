import sys
sys.path.append('/Users/mikezappitello/Documents/sub_docs/mAnds')

import re
from data.data_access import *

class nba_foul():
  """
  not necessarily a hard playoff foul, but someone did something they
  shouldn't have to someone else.
  """
  def __init__(self):
    self.player = None
    self.fouler = None

  def parse_details(self, foul_string):
    """

    """
    self.offensive = True

  def for_csv(self):
    return ""

class nba_rebound():
  """
  a shot went up but didn't fall. who got the board?
  """
  def __init__(self):
    self.player = None
    self.offensive = False

  def parse_details(self, foul_string):
    """
    """
    self.offensive = True

  def for_csv(self):
    return ""

class nba_block():
  """
  a shot went up but didn't fall. who got the board?
  """
  def __init__(self):
    self.player = None
    self.offensive = False

  def parse_details(self, foul_string):
    self.offensive = True

  def for_csv(self):
    return " "

class nba_turnover():
  """
  someone messed up. they either threw the ball away, dribbled it off their
  foot, stepped out of bounds, or did something even dumber.
  """
  def __init__(self):
    self.player = None

  def parse_details(self, foul_string):
    self.wat = True

  def for_csv(self):
    return " "

class nba_shot():
  """
  class that models a shot.  it only cares about if a shot was made, how many
  points it was worth, and who assisted, if anyone.
  """
  def __init__(self, made, player_finder):
    """
    record if a shot was made.  as of right now, there is no value to the
    shot and now assist player to the shot.
    """
    self.made = made 
    self.player = None
    self.value = None
    self.assister = None
    self.player_finder = player_finder

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
        self.assister = self.player_finder.find_player_id(shot_with_assist.group('assist'))

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
    print shot_string
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
    ret += str(self.player["player_id"]) + ", "
    ret += str(self.value) + ", "
    if self.assister:
      ret += str(self.assister["player_id"]) + ", "
    else:
      ret += "none"

    return ret

