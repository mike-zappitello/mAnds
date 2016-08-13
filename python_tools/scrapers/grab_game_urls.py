# script to crawl espn for all play by play urls

import urllib2
from HTMLParser import HTMLParser
import json
import re

# base url for all espn schedule pages
k_scheduleUrl = "http://scores.espn.go.com/nba/scoreboard"

# arguement for scoreboard to get page for a specific day
k_dateArg = "?date="

# generate a list of date formats for a month (expected as int 1-12)
#
# returns a list or array to be filled out by scrapper
def generateDictionary(month):
    ret = []

    # ''' uncomment this when we're ready to roll
    for n in range(1, 3):
        date = {'date' : formatDate(n, month)}
        ret.append(date)
    # '''

    '''
    date = {'date' : formatDate(20, 3)}
    ret.append(date)
    '''

    return ret

# takes a month and a day, and return YYYYMMDD string for that date
def formatDate(day, month):
    if day < 10:
        dd = "0" + str(day)
    else :
        dd = str(day)

    if month < 10:
        mm = "0" + str(month)
    else :
        mm = str(month)

    if month > 7:
        yyyy = "2014"
    else :
        yyyy = "2015"

    return yyyy + mm + dd

# class that will parse the scoreboard data
class dateHTMLParser(HTMLParser):
    # function to start the parser, taking in the url and dates array
    def start_parse(self, html):
        self.gameUrls = []
        self.tag_stack = []
        self.feed(html)
        return self.gameUrls

    # what do we do when we hit a start tag?
    def handle_starttag(self, tag, attrs):
        if (tag == 'a' and attrs and attrs[0][0] == 'href'):
            match = re.match(r"^/nba/playbyplay.gameId=(?P<gameID>\d{9})", attrs[0][1])
            if match:
                self.gameUrls.append(match.group('gameID'))

    # what do we do when we hit an end tag?
    def handle_endtag(self, tag):
        return

    # what do we do when we hit some data?
    def handle_data(self, data):
        return

# take a date and generate the url for it
#
# date expeted to be string in format YYYYMMDD
def generateScoreboardHtml(date):
    url = k_scheduleUrl + k_dateArg + date
    scoreboard_page = urllib2.urlopen(url)
    scoreboard_page_html = scoreboard_page.read()
    scoreboard_page.close()
    
    return scoreboard_page_html

# setup the parser, generate the dates, and grab the game urls for all of them
def get_game_ids():
    parser = dateHTMLParser()
    dateData = generateDictionary(1)
    for date in dateData:
        html = generateScoreboardHtml(date['date'])
        date['gameIds'] = parser.start_parse(html)

    return dateData
