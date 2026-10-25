"""Frozen source-study accounting; see README.md for deliberate historical assumptions."""
from datetime import date
import numpy as np
from signals import score_at

BUY_RATE=.001+.00015+(.0000307+.000001)*1.18
SELL_RATE=.001+(.0000307+.000001)*1.18

def metrics(equity,dates):
    a=np.r_[100.,np.array(equity)];r=a[1:]/a[:-1]-1
    years=((date.fromisoformat(dates[-1])-date.fromisoformat(dates[0])).days+1)/365.25
    total=a[-1]/100-1;cagr=(a[-1]/100)**(1/years)-1
    dd=float(np.min(a/np.maximum.accumulate(a)-1))
    sharpe=float(np.mean(r)/np.std(r,ddof=1)*np.sqrt(252)) if np.std(r)>0 else 0.
    return dict(return_pct=100*total,cagr_pct=100*cagr,max_drawdown_pct=100*dd,
                calmar=cagr/max(abs(dd),1e-9),sharpe_zero_cash=sharpe,ending_equity=float(a[-1]))

def run(p,cache,cfg,start,end,slip=.0005,costs=True,detail=False,avoid_locked=False):
    dates=p['dates'];inds=[i for i,d in enumerate(dates) if start<=d<=end]
    a,b=inds[0],inds[-1];symbols=p['symbols'];hold={};cash=100.;unsettled=[]
    pending_sell=set();pending_buy=[];buy_day=-1;budget=0.;signal=-1;selected=[]
    orders=[];closed=[];signals=[];equities=[];ledger=[];skips=[]
    total_fees=0.;total_slippage=0.;exposures=[]
    buy_rate=BUY_RATE if costs else 0.;sell_rate=SELL_RATE if costs else 0.

    def tradable(t,j):
        return np.isfinite(p['open'][t,j]) and p['volume'][t,j]>0 and (not avoid_locked or p['high'][t,j]>p['low'][t,j])

    def valuation(t,at_open=False):
        return sum(pos['qty']*(p['open'][t,j] if at_open and np.isfinite(p['open'][t,j]) else p['mark'][t,j]) for j,pos in hold.items())

    def choose(t):
        nonlocal pending_sell,pending_buy,buy_day,budget,signal,selected
        scores=cache.get((t,cfg['family'],cfg['lookback']))
        if scores is None:scores=score_at(p,t,cfg['family'],cfg['lookback'])
        ranks=sorted(np.where(np.isfinite(scores))[0],key=lambda j:(-float(scores[j]),symbols[j]))[:cfg['n']]
        selected=ranks;signal=t
        pending_sell=set(hold)-set(ranks)
        pending_buy=[j for j in ranks if j not in hold]
        buy_day=t+3
        value=cash+sum(x[1] for x in unsettled)+valuation(t)
        budget=value/cfg['n']
        if detail:signals.append(dict(date=dates[t],stocks=[symbols[j] for j in ranks],scores=[float(scores[j]) for j in ranks],slot_budget=budget,buy_on=dates[buy_day] if buy_day<len(dates) else None))

    def close_position(j,t,price,reason):
        nonlocal cash,total_fees,total_slippage
        pos=hold.pop(j);fill=price*(1-slip);gross=pos['qty']*fill;fee=gross*sell_rate
        total_fees+=fee;total_slippage+=pos['qty']*price*slip
        proceeds=gross-fee
        if reason=='terminal_estimate':cash+=proceeds
        else:unsettled.append((t+2,proceeds))
        event=dict(date=dates[t],symbol=symbols[j],side='SELL',qty=pos['qty'],reference=price,fill=fill,notional=gross,fee=fee,reason=reason,signal_date=dates[signal])
        orders.append(event)
        closed.append(dict(symbol=symbols[j],entry_date=pos['date'],exit_date=dates[t],entry=pos['fill'],exit=fill,
                           qty=pos['qty'],entry_cost=pos['cost'],net_proceeds=proceeds,net_pnl=proceeds-pos['cost'],exit_reason=reason))

    choose(a-1)
    for t in inds:
        releases=sum(amount for when,amount in unsettled if when<=t)
        cash+=releases;unsettled[:]=[(when,amount) for when,amount in unsettled if when>t]
        if t>a and dates[t][:7]!=dates[t-1][:7] and (int(dates[t][5:7])-1)%cfg['months']==0:choose(t-1)
        for j in sorted(list(pending_sell)):
            if tradable(t,j):
                close_position(j,t,float(p['open'][t,j]),'rebalance');pending_sell.remove(j)
        if t==buy_day:
            candidates=[j for j in pending_buy if tradable(t,j)]
            for j in pending_buy:
                if j not in candidates:skips.append(dict(date=dates[t],symbol=symbols[j],reason='missing or one-price open'))
            for k,j in enumerate(candidates):
                spend=min(budget,cash/(len(candidates)-k))
                if spend<=1e-9:continue
                reference=float(p['open'][t,j]);fill=reference*(1+slip)
                qty=spend/(fill*(1+buy_rate));notional=qty*fill;fee=notional*buy_rate
                cash-=notional+fee;total_fees+=fee;total_slippage+=qty*reference*slip
                hold[j]=dict(qty=qty,date=dates[t],fill=fill,cost=notional+fee)
                orders.append(dict(date=dates[t],symbol=symbols[j],side='BUY',qty=qty,reference=reference,fill=fill,notional=notional,fee=fee,reason='rebalance',signal_date=dates[signal]))
            pending_buy=[]
        marked=valuation(t);locked=sum(x[1] for x in unsettled);equity=cash+locked+marked
        assert cash>=-1e-8 and equity>0 and len(hold)<=cfg['n']+len(pending_sell)
        exposures.append(marked/equity)
        if t==b:
            for j in list(hold):
                if not np.isfinite(p['close'][t,j]):skips.append(dict(date=dates[t],symbol=symbols[j],reason='terminal stale mark'))
                close_position(j,t,float(p['mark'][t,j]),'terminal_estimate')
            marked=0.;equity=cash+locked
        equities.append(equity)
        if detail:ledger.append(dict(date=dates[t],equity=equity,free_cash=cash,unsettled_cash=locked,position_value=marked,positions=len(hold)))
    report=dict(configuration=cfg,start=dates[a],end=dates[b],**metrics(equities,[dates[t] for t in inds]),
        turnover_orders=len(orders),closed_positions=len(closed),fees_equity_points=total_fees,slippage_equity_points=total_slippage,
        average_exposure_pct=100*float(np.mean(exposures)),win_rate_pct=100*sum(x['net_pnl']>0 for x in closed)/max(1,len(closed)),
        accounting_residual=float(equities[-1]-100-sum(x['net_pnl'] for x in closed)),skipped_events=skips)
    assert abs(report['accounting_residual'])<1e-7
    if detail:report.update(dates=[dates[t] for t in inds],equity=equities,ledger=ledger,orders=orders,trades=closed,signals=signals)
    return report

def benchmark(p,start,end,kind):
    ids=[i for i,d in enumerate(p['dates']) if start<=d<=end];prefix='market' if kind=='Nifty 500' else 'n50'
    values=100*p[prefix+'_close'][ids]/p[prefix+'_open'][ids[0]]
    dates=[p['dates'][i] for i in ids]
    return dict(name=kind,start=dates[0],end=dates[-1],**metrics(values,dates),dates=dates,equity=values.tolist())
