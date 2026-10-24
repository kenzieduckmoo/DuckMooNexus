// Focused financial advice checks; synthetic inputs only.
import {readFileSync} from 'node:fs';
import {stripTypeScriptTypes} from 'node:module';
import assert from 'node:assert/strict';
const src=stripTypeScriptTypes(readFileSync(new URL('./lib/buying-model.ts',import.meta.url),'utf8'));
const {weekdayAdvice,buyingPlan}=await import('data:text/javascript;base64,'+Buffer.from(src).toString('base64'));
const daily=Array.from({length:42},(_,i)=>{const date=new Date(Date.UTC(2026,7,2+i)),weekday=date.getUTCDay();return {day:date.toISOString().slice(0,10),weekday,price:weekday===2?80:100,samples:12};});
assert.equal(weekdayAdvice(daily.slice(0,2)).day,null);
assert.equal(weekdayAdvice(daily).day,'Tuesday');
assert.equal(weekdayAdvice(daily.map((d,i)=>({...d,price:i>=35?200:d.price}))).day,null);
const base={units:300,purchase_days:10,coverage_days:30,price:100,fetched_at:new Date().toISOString()};
assert.equal(buyingPlan(base,[],7,30).quantity,null);
assert.equal(buyingPlan({...base,stock:40},[],7,30).quantity,30);
assert.equal(buyingPlan({...base,stock:200},[],7,30).quantity,0);
assert.equal(buyingPlan({...base,stock:0,purchase_days:1},[],7,30).quantity,null);
console.log('Buying advice: insufficient history, stable weekday, market shift, unknown stock and conservative top-ups passed.');
