/// Create object storing all stats for a player in each game
///
/// Exports: get_player_stats
"use strict";

let nba_stats_request = require("nba").usePromises();

// get the stats for a player
// @player_name - the name for the player
//
// @returns -  [ { gameId: <Number>, teamId: <String>,  stats: <Stats> }]
let getPlayerStats = function (playerName) {
  let player = nba_stats_request.findPlayer(playerName);

  // if we couldn't find the player, pass an error to the callback and exit
  if (!player === null) {
    throw new Error("Unable to find player `" + playerName + '`.');
  }

  let request = {playerId: player.playerId};

  // nba_stats_request.stats.playerInfo(request, function (err, response) {
  nba_stats_request.stats.playerProfile(request, function (err, response) {
    if (response) {
      console.log(response);
    }

    if (err) {
      console.log(err);
    }
  });
};

module.exports = {
   getPlayerStats 
};
