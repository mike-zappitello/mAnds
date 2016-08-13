/// Create object storing all stats for a player in each game
///
/// Exports: get_player_stats
"use strict";

let nbaDotCom = require("nba");
let q = require('q');

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

  let requestOverrides = {playerId: player.playerId};

  return q.nfapply(nbaDotCom.stats.playerProfile, [ requestOverrides ])
  .then(function(playerData) {
      // get the game ids 
      let graphGameList = playerData.graphGameList;
      let games = [];

      graphGameList.forEach(function(game) {
          games.push( { gameId: game.gameId, team: game.teamAbbreviation } );
      });

      return games;
  });
};

module.exports = {
   getPlayerStats 
};
