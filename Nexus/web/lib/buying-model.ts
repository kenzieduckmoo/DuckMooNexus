type D=Record<string,any>;
export const weekdayNames=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
export function median(values:number[]){const a=values.filter(Number.isFinite).sort((a,b)=>a-b),i=Math.floor(a.length/2);return a.length?a.length%2?a[i]:(a[i-1]+a[i])/2:null;}
export function weekdayAdvice(history:D[]){
 const daily=history.filter(d=>Number(d.price)>0),byDay=weekdayNames.map((name,weekday)=>({name,weekday,days:daily.filter(d=>Number(d.weekday)===weekday).length,price:median(daily.filter(d=>Number(d.weekday)===weekday).map(d=>Number(d.price)))}));
 const baseline=median(daily.map(d=>Number(d.price))),dates=daily.map(d=>String(d.day)).sort(),span=dates.length?(Date.parse(dates.at(-1)!)-Date.parse(dates[0]))/86400000+1:0;
 const result={days:daily.length,span,byDay,day:null as string|null,saving:null as number|null,reason:'Collecting weekday history',confidence:'Collecting',baseline};
 if(span<28||byDay.some(d=>d.days<3))return result;
 const cutoff=Date.parse(dates.at(-1)!)-6*86400000,recent=median(daily.filter(d=>Date.parse(d.day)>=cutoff).map(d=>Number(d.price)));
 if(recent==null||baseline==null)return result;
 if(Math.abs(recent/baseline-1)>.3)return {...result,reason:'Recent prices have shifted; waiting for a stable pattern',confidence:'Changing market'};
 const best=[...byDay].sort((a,b)=>Number(a.price)-Number(b.price)||a.weekday-b.weekday)[0],saving=1-Number(best.price)/baseline;
 if(saving<.03)return {...result,reason:'No meaningful weekday advantage yet',confidence:'No clear pattern'};
 return {...result,day:best.name,saving,reason:'Historical weekday median, not a guaranteed future price',confidence:byDay.every(d=>d.days>=6)?'Established pattern':'Early pattern'};
}
export function buyingPlan(item:D,history:D[],horizon:number,windowDays:number,now=Date.now()){
 const qty=Number(item.units),purchaseDays=Number(item.purchase_days),coverageDays=Math.min(windowDays,Math.max(1,Number(item.coverage_days)||1));
 const pace=qty/coverageDays,target=Math.ceil(pace*horizon),stock=item.stock==null?null:Number(item.stock);
 // A thin purchase sample cannot establish a repeat restocking pattern. Missing
 // inventory rows are unknown, never assumed to be zero.
 const recurring=purchaseDays>=3&&coverageDays>=14,quantity=recurring&&stock!=null?Math.max(0,target-stock):null;
 const fresh=item.fetched_at&&now-Date.parse(item.fetched_at)<=6*3600000;
 return {...item,pace,target,quantity,recurring,coverageDays,horizon,priceFresh:!!fresh,estimatedCost:quantity!=null&&fresh&&Number(item.price)>0?quantity*Number(item.price):null,advice:weekdayAdvice(history),history};
}
