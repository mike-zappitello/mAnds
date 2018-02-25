"use strict";

let nbaDotCom = require('./src/nbaDotCom');
let nba = require("nba");
let fs = require('fs');
let path = require('path');
let q = require('q');

var writeDataToFile = function(data) {
  let filepath = path.join(__dirname, 'derp.json');
  console.log(filepath);

  var data = JSON.stringify(data, null, "  ");
  fs.writeFile(filepath, data, 'utf8', (err) => {
    if (err) { console.log(err); }
    else { console.log('wrote it!'); }
  });
};

let getGameBoxScore = function(gameId) {
  gameId = gameId || '0020900001'; // BOS v. CLE

  return nba.stats.boxScore({ GameID: gameId });
};

function getGameSummary(gameId) {
  gameId = gameId || '0020900001'; // BOS v. CLE

  return nba.stats.boxScoreSummary( { GameID: gameId });
}

let box_score_full = {
  game_id: '0020900001', // BOS v. CLE
}

getGameBoxScore()
.then((response) => {
  response['resultSets'].forEach((datum) => {
      let name = (datum.name);
      box_score_full[name] = { headers: datum.headers, rowSet: datum.rowSet };
  });
  return getGameSummary()
})
.then((response) => {
  response['resultSets'].forEach((datum) => {
      let name = (datum.name);
      box_score_full[name] = { headers: datum.headers, rowSet: datum.rowSet };
  });
})
.then(() => {
  writeDataToFile(box_score_full);
})
.catch((err) => { console.log(err); });
