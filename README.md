Well lets give this a go.

I've used this repo at various points to run different stats experiments. Some
pieces of it are a bit further along now, which is going to be really helpful
for us.

A quick rundown of how this project is broken up
* node tools - java script tools to get data from nba dot com
* python tools - python scrapers i used to get info
    * this suite of tools is from befoer i used the node stuff.
    * some of them are probably well out of date now.
* data - data in json format with some python accessors that might be overkill
* pdf emailer - the project we'll work on where it gets game data from last
  nights cavs game and emails us both a summary.

I'll try to keep this to do list up to date as we progress.
Steve:
  * Look at `pdf_emailer/generate_game_report.py`
  * Implimet `Game.get_away_team` function
  * Impliment `get_highest_scorer` function
  * Combine `data/teams.json` and `data/teams_npm_nba.json` into a single file

Mike:
  * Find a play by play data source we can use as well.
  * Build a tool to get last nights games (and filter out for the Cavs).
  * Figure out how to use pyenv to manage packages instead of having us do it
    independently.

