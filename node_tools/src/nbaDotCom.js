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
  if (player === null) {
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

  return nba.stats.boxScore({ GameID: gameId });
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

// get the stats for a player in the 2015 season
//
// NOTE - this is a chaining up of stat calls and parsing them. it filters
// things out by date now, but it could really be built to sort out by all kinds
// of stuff. 
let getPlayerStats = function (player) {
  let games = [];

  /// fill out games array from the player profile
  let createGamesList = function(playerProfile) {
    let startOfSeason = new Date("08/30/2015");
    let endOfSeason = new Date("08/30/2026");

    playerProfile.graphGameList.forEach(function(game) {
        let date = new Date(game.gameDate);
        if (startOfSeason < date && date < endOfSeason) {
          games.push( {
            gameId: game.gameId,
            team: game.teamAbbreviation,
            date: game.gameDate,
            vs: game.vsTeamAbbreviation
          } );
        }
    });
  };

  /// create an array of box score promises for each game
  let getPlayerScores = function() {

    let boxscorePromises = [];
    games.forEach(function(game) {
        boxscorePromises.push(getGameBoxScore(game.gameId));
    });
    return q.all(boxscorePromises);
  };

  /// itterate through each boxscore and find the players statline
  let parsePlayerScores = function(boxscores) {
    for (let n=0; n < boxscores.length; n++) {
      boxscores[n].playerStats.forEach(function(statline) {
        if (statline.playerName === player.fullName) {
          // this is obviously embarassing and needs to be cleaned up in a
          // better way. X_x
          games[n].statline = {
            comment: statline.comment, min: statline.min, fgm: statline.fgm,
            fga: statline.fga, fgPct: statline.fgPct, fG3M: statline.fG3M,
            fG3A: statline.fG3A, fg3Pct: statline.fg3Pct, ftm: statline.ftm,
            fta: statline.fta, ftPct: statline.ftPct, oreb: statline.oreb,
            dreb: statline.dreb, reb: statline.reb, ast: statline.ast,
            stl: statline.stl, blk: statline.blk, to: statline.to,
            pf: statline.pf, pts: statline.pts, plusMinus: statline.plusMinus
          };

          // exit for each function
          return true;
        };
      });
    }
    return games;
  };

  /// generate a promise to keep (catch here maybe?)
  return getPlayerProfile(player)
  .then(createGamesList)
  .then(getPlayerScores)
  .then(parsePlayerScores);

};

module.exports = {
  findPlayer,
  getGameBoxScore,
  getPlayerProfile,
  getPlayerStats
};
