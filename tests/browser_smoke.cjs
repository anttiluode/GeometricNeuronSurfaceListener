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
// Round two: a small 8-tick rhythm silences a unit; release restarts it at a fixed delay.
const firsts=[];
for(const warm of [0,7,23,41]){
  const h=new Lab({n:2,mode:"null",weight:0});
  for(let t=0;t<warm;t++)h.step();
  h.hold[0]=true;h.events=[[],[]];
  const t0=h.t;
  for(let t=0;t<300;t++)h.step();
  assert.equal(h.events[0].filter(x=>x>t0+40).length,0,"held unit must be silent");
  assert(h.events[1].length>=4,"unheld unit keeps beating");
  h.hold[0]=false;h.events=[[],[]];
  const t1=h.t;
  for(let t=0;t<200;t++)h.step();
  assert(h.events[0].length>=1,"released unit beats again");
  firsts.push(h.events[0][0]-t1);
}
assert(firsts.every(x=>x===firsts[0]),"release sets the same delay from every starting phase");
console.log("release delays",firsts.join(","));
console.log("JS lab smoke: 59-tick cycle; symmetric state-dependent overlap; finite two-unit trajectories");
