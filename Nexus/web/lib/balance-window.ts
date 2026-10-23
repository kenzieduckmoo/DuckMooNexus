type BalancePoint={time:string;value:unknown};
export function balanceWindow(points:BalancePoint[],days:number,now=Date.now()){
 const cutoff=now-days*86400000;
 const chart=points.filter(p=>p.value!=null&&Number.isFinite(Number(p.value))&&new Date(p.time).getTime()>=cutoff&&new Date(p.time).getTime()<=now).sort((a,b)=>new Date(a.time).getTime()-new Date(b.time).getTime());
 const first=chart[0],latest=chart.at(-1);
 return {chart,first,latest,change:first&&latest?Number(latest.value)-Number(first.value):null};
}
