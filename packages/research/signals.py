"""Signal math extracted unchanged from the five supplied research rounds."""
import numpy as np

def score_round1(p,t,family,look):
    c=p['close'];v=p['volume'];result=np.full(c.shape[1],np.nan)
    if family=='high52':
        if t<251:return result
        hist=p['high'][t-251:t+1]
        valid=np.isfinite(hist).all(axis=0)&(v[t]>0)
        result[valid]=c[t,valid]/np.max(hist[:,valid],axis=0)
    elif family=='absolute':
        if t<look:return result
        hist=c[t-look:t+1]
        valid=np.isfinite(hist).all(axis=0)&(v[t]>0)
        ret=c[t]/c[t-look]-1
        valid &=ret>0
        result[valid]=ret[valid]
    else:
        if t<504:return result
        hist=c[t-504:t+1]
        valid=np.isfinite(hist).all(axis=0)&(v[t]>0)
        y=hist[1:,valid]/hist[:-1,valid]-1
        m=p['market_close'][t-504:t+1];x=m[1:]/m[:-1]-1
        xc=x-x.mean();beta=(xc[:,None]*(y-y.mean(axis=0))).sum(axis=0)/(xc@xc)
        alpha=y.mean(axis=0)-beta*x.mean()
        resid=y-alpha-x[:,None]*beta
        formation=resid[-21-look:-21]
        std=np.std(formation,axis=0,ddof=1)
        scores=np.divide(formation.sum(axis=0),std,out=np.full(std.shape,np.nan),where=std>1e-10)
        result[valid]=scores
    return result

def score_round2(p,t,family,look):
    c=p['close'];result=np.full(len(p['symbols']),np.nan)
    if family=='lowvol':
        if t<look:return result
        h=c[t-look:t+1];valid=np.isfinite(h).all(axis=0)&(p['volume'][t]>0)
        ret=h[1:]/h[:-1]-1;vol=np.std(ret,axis=0,ddof=1)
        valid &=vol>1e-10;result[valid]=-vol[valid];return result
    if t<look+21:return result
    h=c[t-look-21:t+1];valid=np.isfinite(h).all(axis=0)&(p['volume'][t]>0)
    mom=c[t-21]/c[t-look-21]-1
    if family.startswith('riskmom'):
        vol_days=int(family.split('_')[1]);h=c[t-vol_days:t+1]
        vol=np.std(h[1:]/h[:-1]-1,axis=0,ddof=1)*np.sqrt(252)
        valid &=(vol>1e-10)&(mom>0)
        result[valid]=mom[valid]/vol[valid];return result
    groups={}
    for j,g in enumerate(p['industries']):
        if valid[j]:groups.setdefault(g,[]).append(j)
    values={g:float(np.mean(mom[js])) for g,js in groups.items() if len(js)>=5}
    winners=sorted([g for g,v in values.items() if v>0],key=lambda g:(-values[g],g))[:int(family.split('_')[1])]
    queues=[sorted([j for j in groups[g] if mom[j]>0],key=lambda j:(-mom[j],p['symbols'][j])) for g in winners]
    ordered=[]
    for k in range(max([len(q) for q in queues],default=0)):
        for q in queues:
            if k<len(q):ordered.append(q[k])
    for k,j in enumerate(ordered):result[j]=len(p['symbols'])-k
    return result

def score_round3(p,t,family,look):
    c=p['close'];result=np.full(len(p['symbols']),np.nan)
    skip=21 if family=='fip' else 0
    if t<look+skip:return result
    h=c[t-look-skip:t+1]
    valid=np.isfinite(h).all(axis=0)&(p['volume'][t]>0)
    ret=c[t-skip]/c[t-look-skip]-1
    if family=='fip':
        candidates=sorted(np.where(valid)[0],key=lambda j:(-ret[j],p['symbols'][j]))
        cohort=candidates[:int(np.ceil(len(candidates)*.2))]
        h=c[t-look-21:t-21+1];daily=h[1:]/h[:-1]-1
        ident=np.sign(ret)*(np.sum(daily<0,axis=0)-np.sum(daily>0,axis=0))/look
        chosen=sorted([j for j in cohort if ret[j]>0],key=lambda j:(ident[j],-ret[j],p['symbols'][j]))
        for k,j in enumerate(chosen):result[j]=len(p['symbols'])-k
    else:
        groups={}
        for j,g in enumerate(p['industries']):
            if valid[j]:groups.setdefault(g,[]).append(j)
        for g,js in groups.items():
            if len(js)<5:continue
            excess=ret[js]-np.mean(ret[js])
            for j,x in zip(js,excess):
                if x<0:result[j]=-x
    return result

def score_round4(p,t,family,look):
    result=np.full(len(p['symbols']),np.nan)
    if t<look:return result
    h=p['close'][t-look:t+1];ret=h[1:]/h[:-1]-1
    valid=np.isfinite(h).all(axis=0)&(p['volume'][t]>0)&(np.std(ret,axis=0,ddof=1)>1e-10)
    if family=='lowbeta':
        m=p['market_close'][t-look:t+1];market=m[1:]/m[:-1]-1
        if not np.isfinite(market).all():return result
        centered=market-market.mean();denom=np.sum(centered**2)
        if denom<=1e-12:return result
        beta=np.sum((ret-ret.mean(axis=0))*centered[:,None],axis=0)/denom
        result[valid]=-beta[valid]
    else:
        k=int(family.split('_')[1]);largest=np.sort(ret,axis=0)[-k:].mean(axis=0)
        result[valid]=-largest[valid]
    return result

def score_round5(p,t,family,look):
    result=np.full(len(p['symbols']),np.nan)
    required=200 if family=='mad' else look
    if t<required-1:return result
    h=p['close'][t-required+1:t+1]
    mean=h.mean(axis=0)
    valid=np.isfinite(h).all(axis=0)&(p['volume'][t]>0)&(mean>0)
    if family=='mad':
        result[valid]=p['close'][t-look+1:t+1,valid].mean(axis=0)/mean[valid]
    else:result[valid]=-p['close'][t,valid]/mean[valid]
    return result

def score_at(panel, t, family, lookback):
    if family in ('high52', 'residual', 'absolute'):
        return score_round1(panel, t, family, lookback)
    if family == 'lowvol' or family.startswith(('riskmom_', 'industry_')):
        return score_round2(panel, t, family, lookback)
    if family in ('fip', 'reversal'):
        return score_round3(panel, t, family, lookback)
    if family == 'lowbeta' or family.startswith('lowmax_'):
        return score_round4(panel, t, family, lookback)
    if family in ('mad', 'smad'):
        return score_round5(panel, t, family, lookback)
    raise ValueError('Unknown frozen signal family: ' + family)
