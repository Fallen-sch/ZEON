const fs = require('fs');
const path = require('path');
const { parse } = require('../../parsers/javascript/dist/parse');
const { dumps } = require('../../parsers/javascript/dist/stringify');

const data = `
matriz2D[2]
  1 0
  0 1
  
matriz3D[3]
  1 1
  1 1
  
  0 0
  0 0
  
keyed{[]}
  "x" 1 2 3
  "y" 4 5 6
`;

console.log("====================================");
console.log("JAVASCRIPT TEST - MATRICES AND KEYED ARRAYS");
console.log("====================================\n");

console.log("1. ZEON Original:");
console.log(data);

const obj = parse(data);

console.log("2. Parse Result (JSON stringified):");
console.log(JSON.stringify(obj, null, 2));

const outZeon = dumps(obj);

console.log("\n3. Dump Result (ZEON string):");
console.log(outZeon);

console.log("\n====================================");
console.log("JAVASCRIPT TEST COMPLETE");
console.log("====================================");
