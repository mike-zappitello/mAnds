"use strict";

let Seconds = function(minuteString) {
  let splits = minuteString.split(":");

  let err = "minutes need to be formatted mm::ss. received " + minuteString;
  if (splits.length !== 2) { throw new Error(err); }
  if (Number(splits[0]) === null || Number(splits[1]) === null) {
    throw new Error(err);
  }

  this.seconds = Number(splits[0]) * 60 + Number(splits[1]);
}
Seconds.prototype = {
  constructor: Seconds,

  addSeconds: function(other) {
    let self = this;

    if (typeof(other) === 'string') {
      self.seconds += new Seconds(other).seconds;
    } else if (typeof(other) === 'number') {
      self.seconds += other;
    } else if (other.seconds && typeof(other.seconds) === 'number') {
      self.seconds += other.seconds;
    } else {
      throw new Error("trying to add seconds that wont work");
    }
  },

  toMinutes: function() {
    return this.seconds / 60;
  }
};

let playerForGraph = function(player) {
  this.firstName = player.firstName;
  this.lastName = player.lastName;
  this.playerId = player.playerId;

  this.seasonStats = {
    min: new Seconds("00:00"), fgm: 0, fga: 0, fG3M: 0, fG3A: 0, ftm: 0, fta: 0,
    oreb: 0, dreb: 0, ast: 0, stl: 0, blk: 0, pts: 0
  };
  this.games = [];
};

playerForGraph.prototype = {
  constructor: playerForGraph,

  addGame: function(game) {
    let self = this;

    self.games.push(game);

    self.seasonStats.min.addSeconds(game.min);
    self.seasonStats.fgm += game.fgm;
    self.seasonStats.fga += game.fga;
    self.seasonStats.fG3M += game.fG3M;
    self.seasonStats.fG3A += game.fG3A;
    self.seasonStats.ftm += game.ftm;
    self.seasonStats.fta += game.fta;
    self.seasonStats.oreb += game.oreb;
    self.seasonStats.dreb += game.dreb;
    self.seasonStats.ast += game.ast;
    self.seasonStats.stl += game.stl;
    self.seasonStats.blk += game.blk;
    self.seasonStats.pts += game.pts;
  }
};

let gameForGraph = function(game) {
  this.team = game.team;
  this.date = game.date;
  this.vs = game.vs;
  this.min = game.statline.min;
  this.fgm = game.statline.fgm;
  this.fga = game.statline.fga;
  this.fG3M = game.statline.fG3M;
  this.fG3A = game.statline.fG3A;
  this.ftm = game.statline.ftm;
  this.fta = game.statline.fta;
  this.oreb = game.statline.oreb;
  this.dreb = game.statline.dreb;
  this.ast = game.statline.ast;
  this.stl = game.statline.stl;
  this.blk = game.statline.blk;
  this.pts = game.statline.pts;
};

gameForGraph.prototype = {
  constructor: gameForGraph,

  per: function() {
    let self = this;

    let multiple = self.f3GM;
    multiple -= PF * lgFt / lgPF;
    multiple += FT / 2 * (2 - tmAst / 3 / tmFG);
    multiple += FG * (2 - factor * tmAST / tmFG);
    multiple += 2 * AST / 3;

    let vopMultipe = DRBP;
    vopMultiple 
    // return (1 / self.min) * [ self.f3GM + (2 / 3) * self.ast
  }
};

module.exports = {
  playerForGraph,
  gameForGraph
}

