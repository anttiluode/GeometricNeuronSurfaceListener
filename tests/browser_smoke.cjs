/* Browser lab smoke test, including the source's 59-tick limit cycle. */
"use strict";
const assert=require("node:assert/strict");
require("../taps.js");
const {Lab,kernel,G,QMIN}=require("../lab.js");
const original=new Lab({n:1,mode:"null",weight:0});
const beat=[];
let prev=false;
for(let t=0;t<1000;t++){
  const now=original.step()[0]>3;
  if(t>=600 && now&&!prev)beat.push(t);
  prev=now;
}
assert(beat.length>=5,"original loop must be beating");
for(let i=1;i<beat.length;i++)assert.equal(beat[i]-beat[i-1],59,"original ECG cycle");
const one=[G[43-QMIN],G[48-QMIN],G[78-QMIN]];
const k=kernel(one,"surface");
assert(Math.abs(k[0][1]-k[1][0])<1e-12,"instantaneous reciprocity");
assert(Math.abs(k[0][1]-k[0][2])>.15,"receiver state must matter");
const a=new Lab({n:2,mode:"surface",weight:.12});
const b=new Lab({n:2,mode:"null",weight:.12});
assert(Number.isFinite(a.K[0][1]));
for(let t=0;t<300;t++){
  const ya=a.step(),yb=b.step();
  assert(ya.every(Number.isFinite));
  assert(yb.every(Number.isFinite));
}
const raw=new Lab({n:2,mode:"raw",weight:.08});
for(let t=0;t<200;t++)raw.step();
assert(Number.isFinite(raw.R[0]));
console.log("JS lab smoke: 59-tick cycle; symmetric state-dependent overlap; finite two-unit trajectories");
