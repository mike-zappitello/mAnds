"use strict";

let nba = require("nba");
let fs = require('fs');
let path = require('path');
let q = require('q');

// for testing, '0020900001' is a BOS v. CLE game

function writeGame(directory, game) {
  fs.writeFileSync(
      path.join(directory, game.gameId + '.json'),
      JSON.stringify(game, null, "  "),
      'utf8');
};

function getGameSummary(game) {
  // start by getting the box score for this game.
  return nba.stats.boxScore({ GameID: game.gameId })
  .then((response) => {
    // add the headers and row sets to the game object.
    response['resultSets'].forEach((datum) => {
        game[datum.name] = { 'headers': datum.headers, 'rowSet': datum.rowSet };
    });

    // then get the box score summary for the game
    return nba.stats.boxScoreSummary( { GameID: game.gameId });
  })
  .then((response) => {
    // add the headers and row sets to the game object
    response['resultSets'].forEach((datum) => {
        game[datum.name] = { 'headers': datum.headers, 'rowSet': datum.rowSet };
    });

    // return the game
    return game
  })
};

function processGames(scoreboard_result) {
  let games = scoreboard_result.gameHeader.map((entry) => {
    const gameId = entry['gameId'];
    const both_teams = entry.gamecode.split('\/')[1];
    const teams = [ both_teams.slice(0, 3), both_teams.slice(3) ];

    return { gameId, teams };
  });

  return games;
};

function getYesterday(delimeter) {
  let date = new Date();
  date.setDate(date.getDate() - 1);

  const pieces = [
    ("0" + date.getDate()).slice(-2),
    ("0" + (date.getMonth() + 1)).slice(-2),
    date.getFullYear()
  ]

  return pieces.join(delimeter);
}

nba.stats.scoreboard( { gameDate: getYesterday('/') })
.then((response) => processGames(response) )
.then((games) => {
  let promises = games.map((game) => getGameSummary(game));
  return promises
})
.then((game_promises) => {
  let games = [ ];
  return q.allSettled(game_promises)
  .then((games) => { return games.map((g) => g.value) });
})
.then((games) => {
  const directory  = path.join(
      __dirname, '..', '..', 'data', 'game_summaries', getYesterday('.'));
  fs.mkdirSync(directory);

  games.forEach((game) => writeGame(directory, game))
})
.catch((err) => { console.log(err); });

