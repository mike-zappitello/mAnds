/// Functions to request stats from nba dot com
"use strict";

var path = require('path');
var fs = require('fs');

let nba = require("nba");
let q = require('q');

/// from a string, find a player matching this name
/// @return - player : {
///   firstName <string>,
//    lastName <string>,
//    playerId <int> - the nba dot com player id,
//    teamId <int> - the nba dot com team id for the player,
//    fullName <string>,
//    downcaseName <string> - players full name in all lower case
/// }
let findPlayer = function(playerName) {
  // TODO - move this to a data access utils
  let player = nba.findPlayer(playerName);
  if (!player === null) {
    throw new Error("Unable to find player `" + playerName + '`.');
  }
  return player;
};

/// get a traditional box score given a game id
/// @return - boxScore : {
///   playerStats - one entry per player {
///     "gameId", "teamId", "teamAbbreviation", "teamCity", "playerId",
///     "playerName", "startPosition",
///     "comment" - <string> looks like DNPs and NWT's,
///     "min", "fgm", "fga", "fgPct", "fG3M", "fG3A", "fg3Pct", "ftm", "fta",
///     "ftPct", "oreb", "dreb", "reb", "ast", "stl", "blk", "to", "pf", "pts",
///     "plusMinus"
///   },
///   teamStarterBenchStats - 4 entries; home & away bench & starters {
///     "gameId", "teamId", "teamName", "teamAbbreviation", "teamCity",
///     "startersBench" <string> "Starters" | "Bench",
///     "min", "fgm", "fga", "fgPct", "fG3M", "fG3A", "fg3Pct", "ftm", "fta",
///     "ftPct", "oreb", "dreb", "reb", "ast", "stl", "blk", "to", "pf", "pts"
///   },
///   teamStats - two entries, home and away {
///     "gameId", "teamId", "teamName", "teamAbbreviation", "teamCity", "min",
///     "fgm", "fga", "fgPct", "fG3M", "fG3A", "fg3Pct", "ftm", "fta", "ftPct",
///     "oreb", "dreb", "reb", "ast", "stl", "blk", "to", "pf", "pts",
///     "plusMinus"
///   }
/// }
let getGameBoxScore = function(gameId) {
  gameId = gameId || '0020900001'; // BOS v. CLE

  return q.nfapply(nba.stats.boxScore, [{gameId: gameId}]);
};

/// get a player profile given a player id.
/// TODO - think about moving some of this info to find player function?
/// @return {
///   overviewSeasonAvg {
///     "playerId", "playerName", "gp", "w", "l", "wPct", "min", "fgm", "fga",
///     "fgPct", "fG3M", "fG3A", "fg3Pct", "ftm", "fta", "ftPct", "oreb",
///     "dreb", "reb", "ast", "tov", "stl", "blk", "blka", "pf", "pfd", "pts",
///     "plusMinus", "dD2", "tD3"
///   },
///   overviewCareerAvg {
///     "playerId", "playerName", "min", "fgm", "fga", "fgPct", "fG3M", "fG3A",
///     "fg3Pct", "ftm", "fta", "ftPct", "oreb", "dreb", "reb", "ast", "tov",
///     "stl", "blk", "pf", "pts"
///   },
///   overviewSeasonHigh {
///     "playerId", "playerName", "gp", "min", "fgm", "fga", "fgPct", "fG3M",
///     "fG3A", "fg3Pct", "ftm", "fta", "ftPct", "oreb", "dreb", "reb", "ast",
///     "tov", "stl", "blk", "blka", "pf", "pfd", "pts", "plusMinus"
///   },
///   overviewCareerHigh {
///     "playerId", "playerName", "min", "fgm", "fga", "fgPct", "fG3M", "fG3A",
///     "fg3Pct", "ftm", "fta", "ftPct", "oreb", "dreb", "reb", "ast", "tov",
///     "stl", "blk", "pf", "pts"
///   },
///   overviewCareerTotal {
///     "playerId", "playerName", "min", "fgm", "fga", "fgPct", "fG3M", "fG3A",
///     "fg3Pct", "ftm", "fta", "ftPct", "oreb", "dreb", "reb", "ast", "tov",
///     "stl", "blk", "pf", "pts"
///   },
///   graphGameList [ {
///     "playerId", "playerName", "gameId", "gameDate", "teamAbbreviation",
///     "teamName", "vsTeamId", "vsTeamAbbreviation", "vsTeamName", "pts"
///   } ... ],
///   graphPlayerAvg { "playerId", "playerName", "pts" },
///   graphLeagueAvg { "pts" },
///   gameLogs [ {
///     "playerId", "gameId", "gameDate", "matchup", "wl", "min", "fgm", "fga",
///     "fgPct", "fG3M", "fG3A", "fg3Pct", "ftm", "fta", "ftPct", "oreb",
///     "dreb", "reb", "ast", "stl", "blk", "tov", "pf", "pts", "plusMinus"
///   } ... ]
/// }
let getPlayerProfile = function(player) {
  // player = player || {id: 2544}; // lebron james!!!
  return q.nfapply(
    nba.stats.playerProfile,
    [ { playerId: player.playerId } ]
  );
};

module.exports = {
  findPlayer,
  getGameBoxScore,
  getPlayerProfile,
};

/*
// get the stats for a player
// @player - the name for the player
//
// @returns -  [ { gameId: <Number>, team: <String>,  stats: <Stats> }]
let getPlayerStats = function (player) {
  // TODO - the full name should be in the player object
  playerName = player.firstName + " " + player.lastName;
  let games = [];

  /// fill out games array from the player profile
  let createGamesList = function(playerProfile) {
    playerProfile.graphGameList.forEach(function(game) {
        games.push( { gameId: game.gameId, team: game.teamAbbreviation } );
    });
  };

  /// create an array of box score promises for each game
  let getPlayerScores = function(games) {
    let boxscorePromises = [];
    games.forEach(function(game) {
        boxscorePromises.push(getGameBoxScore(game.gameId));
    });
    return q.all(boxscorePromises);
  };

  /// parse the array of box scores for the desired players stats
  let parsePlayerScores = function(boxscores) {
    for (let n=0; n < boxscores.length; n++) {
      boxscores[n].playerStats.forEach(function(statLine) {
        if (statLine.playerName === playerName)  deferred.resolve(statLine);
      games[n].statline = statlines[0];
    });
  };

  /// generate a promise to keep (catch here maybe?)
  return getPlayerProfile(player)
  .then(createGamesList)
  .then(getPlayerScores)
  .then(parsePlayerScores);
};

let getTradedPlayers = function() {
  let tradesFilePath = path.join(__dirname, '..', '..', 'data/trades_2016.json');
  return JSON.parse(fs.readFileSync(tradesFilePath, 'utf8'));
};

let getStatsForTradedPlayers = function() {
  let deferred = q.defer();

  let players = getTradedPlayers();
  let boxscorePromises= [];
  let total = 0;
  players.forEach(function(player) {
    if (total < 1) {
      console.log(`creating promise for ${player.name}`);
      boxscorePromises.push(getPlayerStats(player.name));
    }
    total++;
  });

  q.all(boxscorePromises)
  .then(function(boxscores) {
    for (let n=0; n < boxscores.length; n++) {
      console.log("storing boxscores!");
      players[n].games = boxscores[n];
    }
    deferred.resolve(players);
  });

  return deferred.promise;
};

module.exports = {
  findPlayer,
  getPlayerProfile,
  getGameBoxScore,
  getPlayerStats,
  getTradedPlayers,
  getStatsForTradedPlayers
};
*/
