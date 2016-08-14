/// Create object storing all stats for a player in each game
///
/// Exports: get_player_stats
"use strict";

let nbaDotCom = require("nba");
let q = require('q');
let path = require('path');
let fs = require('fs');

// get the stats for a player
// @player_name - the name for the player
//
// @returns -  [ { gameId: <Number>, team: <String>,  stats: <Stats> }]
let getPlayerStats = function (playerName) {
  let player = nbaDotCom.findPlayer(playerName);

  // if we couldn't find the player, pass an error to the callback and exit
  if (!player === null) {
    throw new Error("Unable to find player `" + playerName + '`.');
  }

  let getGameBoxScore = function(gameId) {
    // create a promise we'll fulfill another day
    let deferred = q.defer();

    // debugging tool
    // let gameId = '0020900001';

    // create the players full name to compare each line to
    playerName = player.firstName + " " + player.lastName;

    // get the box score stats for the current game id
    q.nfapply(nbaDotCom.stats.boxScore, [{gameId: gameId}])
    // then run through each entry, looking for the playername
    .then(function(boxscore) {
      boxscore.playerStats.forEach(function(statLine) {
        if (statLine.playerName === playerName) deferred.resolve(statLine);
      });
      deferred.reject("player did not play in this game");
    });

    return deferred.promise;
  }

  return q.nfapply(nbaDotCom.stats.playerProfile, [{playerId: player.playerId}])
  .then(function(playerData) {
      let games = [];

      // debugging tool
      let total = 0;

      // itterate throught he game list, grab each game id and add it to games
      playerData.graphGameList.forEach(function(game) {
          if (total < 5) {
            games.push( { gameId: game.gameId, team: game.teamAbbreviation } );
          }
          total++;
      });

      return games
  })
  .then(function(games) {
    // create a promise we'll fulfill another day
    let deferred = q.defer();

    // create an array of stat line promises
    let statlinePromises = [];
    games.forEach(function(game) {
        statlinePromises.push(getGameBoxScore(game.gameId));
    });

    // collect all of the fulfilled promises
    q.all(statlinePromises)
    // add stat lines to each of the games
   .then(function(statlines) {
      // promises are resolved in the same order they were requested
      for (let n=0; n < statlines.length; n++) {
        games[n].statline = statlines[0];
      }
      deferred.resolve(games);
    });

    return deferred.promise
  });
};

let getTradedPlayers = function() {
  let tradesFilePath = path.join(__dirname, '..', '..', 'data/trades_2016.json');
  return JSON.parse(fs.readFileSync(tradesFilePath, 'utf8'))
}

module.exports = {
  getPlayerStats,
  getTradedPlayers
};
