"use strict";

let nbaDotCom = require('./src/nbaDotCom');
let fs = require('fs');
let path = require('path');
let q = require('q');

let getTradedPlayers = function() {
  let tradesFilePath = path.join(__dirname, '..', 'data/trades_2016.json');
  return JSON.parse(fs.readFileSync(tradesFilePath, 'utf8'));
};

var writeDataToFile = function(data) {
  console.log("wtf");
  let filepath = path.join(__dirname, 'derp.json');
  console.log("why");
  console.log(filepath);

  var data = JSON.stringify(data, null, "  ");
  fs.writeFile(filepath, data, 'utf8', (err) => {
    if (err) { console.log(err); }
    else { console.log('wrote it!'); }
  });
};

let getStatsForTradedPlayers = function() {
  // { "name": "Joel Anthony", "to": "76ERS" }
  let tradedPlayers = getTradedPlayers();
  let gamePromises = [];
  let players = [];

  // build up a bunch of promises to get player stats
  for (let n=0; n < tradedPlayers.length; n++) {
    // if (n < 1) {
      let player = nbaDotCom.findPlayer(tradedPlayers[n].name);
      console.log(tradedPlayers[n].name);
      console.log(player);
      players.push(player);
      gamePromises.push(nbaDotCom.getPlayerStats(player));
    // }
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

getStatsForTradedPlayers();
