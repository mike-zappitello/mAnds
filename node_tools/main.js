"use strict";

let nbaDotCom = require('./src/nbaDotCom');
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

nbaDotCom.getGameBoxScore()
.then((game) => { writeDataToFile(game); })
.catch((err) => { console.log(err); });
