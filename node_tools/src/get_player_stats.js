"use strict";

let nbaDotCom = require('./src/nbaDotCom');
let fs = require('fs');
let path = require('path');
let q = require('q');

// helper functions for an explicit use case from a while back.
//
// could be moved somewhere else, but meh.
let getTradedPlayers = function() {
  let tradesFilePath = path.join(__dirname, '..', 'data/trades_2016.json');
  return JSON.parse(fs.readFileSync(tradesFilePath, 'utf8'));
};

var writeDataToFile = function(data) {
  let filepath = path.join(__dirname, 'derp.json');
  console.log(filepath);

  var data = JSON.stringify(data, null, "  ");
  fs.writeFile(filepath, data, 'utf8', (err) => {
    if (err) { console.log(err); }
    else { console.log('wrote it!'); }
  });
};

/*
 * Get Stats for a list of player for the season.
 *
 * @players = list of players to get info for
 */
let getStatsForTradedPlayers = function(players) {
  let gamePromises = [];
  let players = [];

  // build up a bunch of promises to get player stats
  // TODO this could / should be more functional
  for (let n=0; n < players.length; n++) {
    let player = nbaDotCom.findPlayer(players[n].name);
    console.log(players[n].name);
    console.log(player);
    players.push(player);
    gamePromises.push(nbaDotCom.getPlayerStats(player));
  }

  console.log(gamePromises.length);

  q.all(gamePromises)
  .then(function(games) {
    console.log("hiya");
    for (let n=0; n < games.length; n++) {
      console.log(players[n]);
      console.log(games[n].length);
      players[n].games = games[n];
    }

    console.log("bye");
    console.log(players);
    writeDataToFile(players);
  })
};
