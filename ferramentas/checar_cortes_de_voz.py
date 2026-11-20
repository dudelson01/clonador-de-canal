#!/usr/bin/env python3
"""Mostra som com volume de VOZ que a decupagem removeu de dentro (e das bordas) de cada trecho escolhido.
Uso: python3 checar_cortes_de_voz.py plano_decupagem.json pasta_decupagem
Se aparecer palavra na lista, a decupagem comeu fala: o aluno reprovou isso no video 02 (v4)."""
import json,subprocess,numpy as np,sys
pl=json.load(open(sys.argv[1]));D=json.load(open(sys.argv[2]+'/decupagem.json'))
k=list(pl['tomadas'])[0];arq=pl['tomadas'][k]
W=json.load(open(pl['transcricoes'][k]))['palavras']
raw=subprocess.run(["ffmpeg","-loglevel","error","-i",arq,"-map","0:a:0","-ac","1","-ar","16000","-af","highpass=f=100,lowpass=f=3000","-f","f32le","-"],capture_output=True).stdout
a=np.frombuffer(raw,np.float32);n=160;db=20*np.log10(np.sqrt((a[:len(a)//n*n].reshape(-1,n)**2).mean(1))+1e-9)
lim=np.percentile(db,60)-18
tot=0
for i,tr in enumerate(pl['trechos']):
    ps=sorted([p for p in D if p['n']==i],key=lambda p:p['s'])
    if not ps: print("TRECHO SUMIU",i,tr['obs']);continue
    lo,hi=ps[0]['s'],ps[-1]['e']
    gaps=[(x['e'],y['s']) for x,y in zip(ps,ps[1:]) if y['s']-x['e']>0.03]
    # tambem bordas do trecho pedido
    gaps=[(tr['ini']-0.05,lo)]*(lo>tr['ini']+0.05)+gaps+[(hi,tr['fim']+0.05)]*(hi<tr['fim']-0.05)
    for g0,g1 in gaps:
        fr=db[int(g0*100):int(g1*100)]
        loud=(fr>lim).sum()*0.01
        if loud>=0.06:
            ws=[w['w'] for w in W if w['e']>g0+0.02 and w['s']<g1-0.02]
            tot+=loud
            print(f"trecho {i:3d} cortou {g0:7.2f}-{g1:7.2f} ({g1-g0:.2f}s, {loud:.2f}s com voz) palavras: {' '.join(ws)}")
print("total com voz cortado:",round(tot,1),"s; limite",round(lim,1))
