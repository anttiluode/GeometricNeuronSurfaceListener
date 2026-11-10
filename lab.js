/* Exact 50-sample/d=4 archived ECG loop, with alternate two-surface listening.
   Shared browser simulator: no external libraries, learning, or imposed theta clock.
   Original Python core parity is audited separately. */
(function(root){
  "use strict";
  const table = root.GEOMETRIC_TAPS;
  if(!table || !table.taps) throw new Error("Missing original checkerboard sample table: taps.js");
  const G=table.taps, QMIN=table.qmin, QMAX=table.qmax, S=.6, TARGET=.1, O0=.8739509815096245;
  const MODES=["surface","raw","fixed","shifted","fixed_taps","null"];
  const clip=(x,a,b)=>Math.max(a,Math.min(b,x));
  const qOf=o=>clip(Math.trunc(5+50*(o===0?.1:o)),QMIN,QMAX);
  const centered=row=>{
    const mean=row.reduce((a,b)=>a+b,0)/16, v=row.map(x=>x-mean);
    const norm=Math.sqrt(v.reduce((a,b)=>a+b*b,0));
    return norm>1e-12?v.map(x=>x/norm):row.map(_=>0);
  };
  const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
  const avgIdle=G[43-QMIN].map((x,i)=>(x+G[48-QMIN][i])/2);
  const frozen=centered(avgIdle);
  const zeros=()=>Array.from({length:16},()=>0);
  const normalizeRows=rows=>rows.map(centered);
  function kernel(rows,mode){
    const f=normalizeRows(rows),n=rows.length;
    return Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>{
      if(i===j||mode==="null")return 0;
      if(mode==="raw")return dot(rows[i],rows[j])/4;
      if(mode==="fixed")return dot(frozen,f[j]);
      if(mode==="shifted"){
        let r=f[i].map((_,k)=>f[i][(k-4+16)%16]);
        return dot(r,f[j]);
      }
      if(mode==="fixed_taps")return rows[j].slice(6,10).reduce((a,b)=>a+b,0);
      return dot(f[i],f[j]);
    }));
  }
  class Lab {
    constructor({n=2,mode="surface",weight=.12,gain=3.5}={}){
      this.n=n;this.mode=mode;this.weight=weight;this.gain=gain;this.W=50;this.d=4;
      this.pipe=Array.from({length:4},()=>Array(n).fill(NaN));
      this.pipe[3]=Array(n).fill(O0);
      this.hist=Array.from({length:n},()=>Array(50).fill(0));
      this.count=0;this.t=0;
      this.own=Array(n).fill(0);this.R=Array(n).fill(0);this.var=Array(n).fill(0);
      this.q=Array(n).fill(0);this.K=Array.from({length:n},()=>Array(n).fill(0));
      this.rows=Array.from({length:n},zeros);
      this.forced=Array(n).fill(0);
      this.events=Array.from({length:n},()=>[]);
      this.previous=Array(n).fill(false);
      // Let the two original loops settle uncoupled; reset one clock to
      // introduce a genuine phase difference, not random visual decoration.
      const saved=this.weight; this.weight=0;
      for(let t=0;t<650;t++){
        if(t===370 && n>1)this.forced[1]=2;
        this.step();
      }
      this.weight=saved;this.events=Array.from({length:n},()=>[]);
      this.previous=Array(n).fill(false);
    }
    pulse(unit){if(unit>=0 && unit<this.n)this.forced[unit]=2;}
    step(){
      const src=this.pipe[0];
      const live=src.map(Number.isFinite);
      const q=src.map((v,i)=>qOf(live[i]?v:0));
      const rows=q.map((v,i)=>live[i]?G[v-QMIN]:zeros());
      const own=rows.map((r,i)=>live[i]?r.slice(0,4).reduce((a,b)=>a+b,0):0);
      const K=kernel(rows,this.mode);
      const R=own.map((x,i)=>{
        let ext=0;
        for(let j=0;j<this.n;j++)if(i!==j)ext+=this.weight*K[i][j]*(this.mode==="fixed_taps"?1:this.gain);
        return x+ext;
      });
      let v=Array(this.n).fill(0), o=Array(this.n);
      for(let i=0;i<this.n;i++){
        this.hist[i][this.count%50]=R[i];
        if(this.count+1>10){
          const m=Math.min(this.count+1,50);
          let avg=0;
          for(let age=1;age<=m;age++)avg+=this.hist[i][(this.count+1-age)%50];
          avg/=m;
          let sumSq=0;
          for(let age=1;age<=m;age++){
            const z=this.hist[i][(this.count+1-age)%50]-avg;
            sumSq+=z*z;
          }
          v[i]=sumSq/m;
        }
        const hot=v[i]>.1;
        o[i]=hot?S+(2/(1+Math.exp(-3*(R[i]-S)))-1)/3:
          S+Math.tanh(2*(R[i]-S)*(1+10*Math.abs(v[i]-TARGET)));
        if(this.forced[i]>0){o[i]=-.28;this.forced[i]--;}
      }
      this.count++;this.t++;
      this.pipe.shift();this.pipe.push(o);
      this.q=q;this.rows=rows;this.own=own;this.K=K;this.R=R;this.var=v;
      for(let i=0;i<this.n;i++){
        const loud=own[i]>3;
        if(loud&&!this.previous[i])this.events[i].push(this.t);
        this.previous[i]=loud;
        if(this.events[i].length>200)this.events[i].shift();
      }
      return own;
    }
  }
  root.SurfaceLab={Lab,kernel,centered,MODES,G,QMIN};
  if(typeof module!=="undefined" && module.exports)module.exports=root.SurfaceLab;
})(typeof globalThis!=="undefined"?globalThis:this);
