
# import the python json packagage - this lets us read json into a dictionary
import json

# import the python os package - this lets us do things on the opporating
# sytstem, like creating file paths and reading files.
import os

# a Class describes a type of object, what its properties are, and what
# functions it can use.
#
# we could create many Instances of this Class. for example, we could have a
# Game Instance for each game in a playoff series.
class Game(object): 

    # in python, special methods are surrounded by double underscores. __init__
    # is the method thats called when we create a new Instance of our Class.
    def __init__(self, box_score_data):
        '''
        typically, we put what a function actually does right here.

        @brief - create an Instance of a Game.

        @box_score_data - json formatted data describing the basic stats for an
            nba game. format is specified by nba dot com.
        '''
        # self refers to the specific Instance of a game we're talking about.
        # this line will assign box_score_data object we passed in to this
        # instances 'raw' member, a name i chose since it is the raw data we'll
        # vizualize.
        self.raw = box_score_data

    # the format for a python function is:
    # 'def <function_name>(<param1>, <param2>, ..., <paramN>):'

    # all memeber functions of a class start with self, so the function can
    # internally access this objects data.
    def get_home_team(self):
        '''
        @brief - get the home team from nba dot com formatted box score data.
        '''

        # the GameSummary headers are formatted like this:
        # [
        #   "GAME_DATE_EST",                        0
        #   "GAME_SEQUENCE",                        1
        #   "GAME_ID",                              2
        #   "GAME_STATUS_ID",                       3
        #   "GAME_STATUS_TEXT",                     4
        #   "GAMECODE",                             5
        #   "HOME_TEAM_ID",                         6
        #   "VISITOR_TEAM_ID",                      7
        #   "SEASON",                               8
        #   "LIVE_PERIOD",                          9
        #   "LIVE_PC_TIME",                         10
        #   "NATL_TV_BROADCASTER_ABBREVIATION",     11
        #   "LIVE_PERIOD_TIME_BCAST",               12
        #   "WH_STATUS"                             13
        # ]
        #
        # NOTE: the index starts at 0, not 1
        game_summary_data = self.raw["GameSummary"]

        # from the above code, we can see that the home team is on column 6
        # grab it out of the first row of the row set data
        row_index = 0

        # column_index = 6
        column_index = game_summary_data['headers'].index("HOME_TEAM_ID")

        return game_summary_data["rowSet"][row_index][column_index]

    def get_away_team(self):
        return 0

    def get_highest_scorer(self):
        return "lebron"



################################################################################
###                                                                          ###
###     THIS IS WHERE WE ARE USING THE CODE WRITTEN ABOVE TO DO SOMETHING    ###
###                                                                          ###
###     the following code will:                                             ###
###         * create a filepath pointing to our data                         ###
###         * open the filepath and read the json data                       ###
###         * create a new Game instance to try stuff out on                 ###
###         * get the home team id and print it out                          ###
###                                                                          ###
################################################################################

# this builds a file path for the game data i saved in this directory (folder)
game_data_fp = os.path.join(
    # this is the path to the directory this file is in. note the '__'.
    os.path.dirname(__file__),
    # this is the name of the file we're going to load.
    'game_data.json')

# print out the game data file path. uncomment to print it to command line
# print('game data file path: ' + game_data_fp)

# open up our game data file path and use json to load the data
with open(game_data_fp, 'r') as gd: box_score_data = json.load(gd)

# create a new Instance of the Game Class called game_to_look_at.
game_to_look_at = Game(box_score_data)

# get the home team, and print it out
home_team_id = game_to_look_at.get_home_team()
print("home team id: " + str(home_team_id))

