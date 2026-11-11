"""Beat times from native.py for the page's four-unit start, so tests/browser_smoke.cjs can
check that lab.js WireLab is the same machine.  Run: python experiments/wire_fixture.py"""
import sys,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from native import SetpointColony
def run(kind,wt,ticks=1500,pulses=(),cf=1.0):
    n=4;c=SetpointColony(n)
    left=np.zeros(n,int)
    sp0=np.full(n,cf-1.0); sp0[0]=0.0
    for t in range(650):
        for i in range(1,n):
            if t==300+17*i: left[i]=2
        f=np.where(left>0,-0.28,np.nan); left=np.maximum(left-1,0)
        c.step(force=f,sp_ext=sp0)
    v=np.zeros((n,n))
    if kind!="none":
        for i in range(n-1):
            v[i+1,i]=wt
            if kind=="both": v[i,i+1]=wt
    c.v=v
    prev=np.array([False]*n)   # filled below
    ev=[[] for _ in range(n)]
    # prev state from settle
    for k in range(ticks):
        sp=np.full(n,cf-1.0); sp[0]=0.0
        for (t,u) in pulses:
            if t<=k<t+2: sp[u]+=-10
        loud=c.step(sp_ext=sp)>3
        for u in np.flatnonzero(loud&~prev): ev[u].append(c.t-1)
        prev=loud
    return ev
out={}
for kind,wt in (("none",0),("chain",-5.5),("chain",-4),("both",-5.5)):
    out[f"{kind}:{wt}"]=run(kind,wt)
for wt in (-6,-5.5):
    out[f"chain:{wt}:1.6"]=run("chain",wt,cf=1.6)
out["both:-6:1.6"]=run("both",-6,cf=1.6)
out["pulse"]=run("none",0,300,pulses=((20,2),(120,0)))
(ROOT/'tests/wire_fixture.json').write_text(json.dumps(out)+'\n')
print('WROTE tests/wire_fixture.json')
