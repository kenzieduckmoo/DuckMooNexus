'use client';
import Link from 'next/link';

import { useEffect,useState } from 'react';

import { motion,useReducedMotion } from 'motion/react';

import { Search,SlidersHorizontal,ArrowUpRight,ArrowRight,Star,RefreshCw,Download,Layers3,Package,ChartNoAxesCombined,Info } from 'lucide-react';

import { Button } from '@/components/ui/button';

import { Input } from '@/components/ui/input';

import { Badge } from '@/components/ui/badge';

import { ItemIcon } from './item-icon';

import { HistoryChart } from './chart';

import { ago,gold,number } from '@/lib/utils';

import {AutoStatus,useNexusRevision} from './freshness';
type Data=Record<string,any>;

async function read(url:string,signal?:AbortSignal){const r=await fetch(url,{signal});const d=await r.json();if(!r.ok)throw Error(d.error??'Could not load market data.');return d;}

function variantLabel(value:string,index:number){try{const v=JSON.parse(value),bonuses=v.bonus_lists??v.bonus_list??v.bonus_list_ids;return 'Variant '+(index+1)+(v.context?' · context '+v.context:'')+(bonuses?.length?' · bonuses '+bonuses.join(', '):'');}catch{return 'Variant '+(index+1);}}

export function AuctionHouse(){

 const [query,setQuery]=useState('Eversinging Dust'),[scope,setScope]=useState('commodities'),[markets,setMarkets]=useState<Data[]>([]),[sort,setSort]=useState('name');

 const [results,setResults]=useState<Data[]>([]),[selected,setSelected]=useState<number|null>(null),[detail,setDetail]=useState<Data|null>(null),[days,setDays]=useState(7),[variant,setVariant]=useState('');

 const [searching,setSearching]=useState(true),[loading,setLoading]=useState(false),[error,setError]=useState(''),[detailError,setDetailError]=useState(''),[reload,setReload]=useState(0),[watches,setWatches]=useState<Data[]>([]);const reduced=useReducedMotion(),revision=useNexusRevision();

 useEffect(()=>{

  const p=new URLSearchParams(window.location.search);if(p.has('q'))setQuery(p.get('q')!.slice(0,100));if(p.has('scope'))setScope(p.get('scope')!);if(Number(p.get('item'))>0)setSelected(Number(p.get('item')));

  try{const saved=JSON.parse(localStorage.getItem('nexus-market-watch')??'[]');if(Array.isArray(saved))setWatches(saved.filter(x=>Number.isSafeInteger(x.id)&&typeof x.name==='string').slice(0,30));}catch{}

  read('/api/nexus?view=scopes').then(d=>setMarkets(d.sort((a:Data,b:Data)=>Number(b.scope==='commodities')-Number(a.scope==='commodities')||a.label.localeCompare(b.label)))).catch(e=>setError(e.message));

 },[]);

 useEffect(()=>{const controller=new AbortController();setSearching(true);setError('');const timer=setTimeout(()=>{

  read('/api/nexus?view=search&'+new URLSearchParams({q:query,scope,sort}),controller.signal).then(d=>{setResults(d.rows);setSelected(old=>d.rows.some((r:Data)=>Number(r.item_id)===old)?old:d.rows.length?Number(d.rows[0].item_id):null);}).catch(e=>{if(e.name!=='AbortError'){setError(e.message);setResults([]);}}).finally(()=>{if(!controller.signal.aborted)setSearching(false);});

 },280);return()=>{clearTimeout(timer);controller.abort();};},[query,scope,sort,reload,revision.market,revision.sources]);

 useEffect(()=>{setDetail(null);setDetailError('');if(!selected)return;const controller=new AbortController();setLoading(true);

  read('/api/nexus?view=item&'+new URLSearchParams({id:String(selected),scope,days:String(days),variant}),controller.signal).then(setDetail).catch(e=>{if(e.name!=='AbortError')setDetailError(e.message);}).finally(()=>{if(!controller.signal.aborted)setLoading(false);});

  const p=new URLSearchParams({q:query,scope,item:String(selected)});window.history.replaceState(null,'','/auctions?'+p);

  return()=>controller.abort();

 },[selected,scope,days,variant,reload,revision.market,revision.sources]);

 const market=markets.find(m=>m.scope===scope),offers=detail?.offers??[],chosen=variant?offers.find((o:Data)=>o.variant===variant):null;

 const priced=offers.filter((o:Data)=>o.price!=null),price=chosen?.price??(variant?null:priced.length?Math.min(...priced.map((o:Data)=>Number(o.price))):null);

 const quantity=chosen?.quantity??(variant?0:offers.reduce((s:number,o:Data)=>s+Number(o.quantity),0));

 const listings=chosen?.listings??(variant?0:offers.reduce((s:number,o:Data)=>s+Number(o.listings),0));

 const history=detail?.history??[],first=history[0],last=history.at(-1),delta=history.length>1&&Number(first.value)>0?(Number(last.value)-Number(first.value))/Number(first.value)*100:null;

 const watched=watches.some(w=>w.id===selected);

 function choose(id:number){setVariant('');setSelected(id);}

 function watch(){if(!detail||!selected)return;const next=watched?watches.filter(w=>w.id!==selected):[...watches,{id:selected,name:detail.item.name}].slice(-30);setWatches(next);try{localStorage.setItem('nexus-market-watch',JSON.stringify(next));}catch{setDetailError('Your browser could not save the watchlist.');}}

 function exportHistory(){if(!detail)return;const csv='Fetched at,Source modified at,Lowest unit price (gold),Listed quantity\n'+history.map((p:Data)=>[p.time,p.source_modified_at??'',p.value,p.quantity].join(',')).join('\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='nexus-'+selected+'-price-history.csv';a.click();URL.revokeObjectURL(url);}

 return <motion.div className="page-content market-page" initial={reduced?false:{opacity:0,y:10}} animate={{opacity:1,y:0}} transition={{duration:.35}}>

 <div className="page-kicker"><span className="small-diamond"/> THE AZEROTH MARKETPLACE</div><div className="page-title-row"><div><h1>Auction House<span>.</span></h1><p className="page-subtitle">Find the right price. See the bigger picture.</p></div><AutoStatus/></div>

 <div className="market-banner"><div><span className="live-dot"/><b>Blizzard AH snapshots</b><span>Collected automatically · US region</span></div><small>{market?'Fetched '+ago(market.fetched_at):'Loading connected markets…'}</small></div>
 <Link className="surface market-buying-link" href="/auctions/buying"><span>Reagent buying advisor <small>Your usual purchases, recorded stock and weekday price patterns</small></span><ArrowUpRight size={17}/></Link>

 <section className="surface market-controls" aria-label="Search and market filters"><label className="search-field"><Search size={20}/><Input aria-label="Search items by name or item ID" placeholder="Search an item by name…" value={query} maxLength={100} onChange={e=>{setVariant('');setQuery(e.target.value);}}/></label><div className="market-picker"><label htmlFor="market">Market</label><select id="market" value={scope} onChange={e=>{setVariant('');setScope(e.target.value);}}>{!markets.length&&<option value="commodities">US commodities</option>}{markets.map(m=><option key={m.scope} value={m.scope}>{m.label}</option>)}</select></div><div className="sort-picker"><label htmlFor="sort">Sort matches</label><select id="sort" value={sort} onChange={e=>setSort(e.target.value)}><option value="name">Item name</option><option value="price">Lowest price</option><option value="quantity">Listed quantity</option></select></div></section>

 <div className="suggestions"><span>QUICK SEARCH</span>{['Eversinging Dust','Mote of Light','Thalassian Phoenix Oil','Ore'].map(name=><button key={name} onClick={()=>{setVariant('');setQuery(name);}}>{name}<ArrowUpRight size={12}/></button>)}</div>

 {watches.length>0&&<div className="watchlist"><Star size={14}/><span>YOUR WATCHLIST</span>{watches.map(w=><button key={w.id} onClick={()=>{setQuery(w.name);choose(w.id);}}>{w.name}</button>)}</div>}

 {error&&<div className="error-panel" role="alert">{error} <button onClick={()=>setReload(v=>v+1)}>Try again</button></div>}

 <div className="market-columns"><section className="surface item-results"><div className="results-heading"><h2>Market matches</h2><Badge variant="outline">{searching?'Searching…':results.length+' shown'}</Badge></div><div className="result-table"><div className="result-labels"><span>ITEM</span><span>LOWEST / UNIT</span></div>{searching&&!results.length?<div className="results-loading" aria-label="Loading items">{[1,2,3,4,5].map(n=><div className="skeleton-row" key={n}/>)}</div>:results.map(r=><button key={r.item_id} className={'result-row '+(Number(r.item_id)===selected?'selected':'')} onClick={()=>choose(Number(r.item_id))} aria-pressed={Number(r.item_id)===selected}><ItemIcon src={r.icon} name={r.name} quality={r.quality}/><span className="result-name"><b>{r.name}</b><small>{r.crafting_quality?"Quality "+r.crafting_quality+" · ":"Item "+r.item_id+" · "}{number(r.quantity)} listed{Number(r.variants)>1?' · '+r.variants+' variants':''}</small></span><span className="result-price">{gold(r.price)}<i>g</i><small>{number(r.listings)} listings</small></span></button>)}</div>{!searching&&!results.length&&!error&&<div className="empty-state"><Search size={28}/><h3>No listed matches here</h3><p>Try another name or market. Commodities are region-wide; equipment and other noncommodities use connected realms.</p></div>}<div className="result-footnote">Up to 80 listed results from the first 500 name matches. Prices show the lowest listed variant.</div></section>

 <section className="surface item-detail" aria-label="Selected item details">{loading?<div className="detail-loading"><div className="skeleton-row"/><div className="chart-skeleton"/><p>Reading the recorded market…</p></div>:detailError?<div className="empty-state" role="alert"><Info size={28}/><p>{detailError}</p><Button variant="outline" onClick={()=>setReload(v=>v+1)}>Try again</Button></div>:detail?<>

 <div className="item-heading"><ItemIcon src={detail.item.icon} name={detail.item.name} quality={detail.item.quality} large/><div><div className="eyebrow">{detail.item.category??'MARKET ITEM'}{detail.item.subcategory?' / '+detail.item.subcategory:''}</div><h2>{detail.item.name}</h2><small>Item {detail.item.item_id} <span>·</span> {detail.label}</small></div><Button variant="outline" size="icon" onClick={watch} aria-label={watched?'Remove item from watchlist':'Watch this item'} aria-pressed={watched}><Star size={18} fill={watched?'currentColor':'none'}/></Button></div>

 {offers.length>1&&<label className="variant-field">Listing variant<select value={variant} onChange={e=>setVariant(e.target.value)}><option value="">All variants · lowest available price</option>{offers.map((o:Data,i:number)=><option key={o.variant} value={o.variant}>{variantLabel(o.variant,i)} · {gold(o.price)} g</option>)}</select></label>}

 <div className="quote-grid"><div className="main-quote"><span>LOWEST UNIT PRICE</span><strong>{gold(price)}<i>g</i></strong><small className={delta==null||delta===0?'':delta>0?'positive':'negative'}>{delta==null?'History is collecting':(delta>0?'+':'')+delta.toFixed(1)+'% since first point in this range'}</small></div><div><span>LISTED QUANTITY</span><strong>{number(quantity)}</strong><small>{number(listings)} auction listings</small></div></div>

 <div className="price-chart-heading"><h3>Price history</h3><div className="segmented" aria-label="Price history time range">{[1,7,30].map(d=><button key={d} onClick={()=>setDays(d)} aria-pressed={days===d}>{d===1?'24H':d+'D'}</button>)}</div></div><HistoryChart points={history} kind="price"/><div className="chart-footnote">{history.length} collected snapshots · Lowest listed unit price{offers.length>1&&!variant?' across variants':''}. Listing changes do not prove sales.</div>

 <div className="detail-actions"><Button variant="outline" onClick={exportHistory} disabled={!history.length}><Download size={15}/> Export history</Button><a className="text-link" href="/crafting">Open Crafting Desk <ArrowUpRight size={15}/></a></div>

 <div className="item-context-grid"><section><h3><Package size={16}/> Your recorded stock</h3>{detail.owned.length?<><strong className="context-number">{number(detail.owned.filter((o:Data)=>o.owner_kind!=='guild').reduce((n:number,o:Data)=>n+Number(o.quantity),0))}<small> non-guild units</small></strong><details><summary>See owners and locations</summary>{detail.owned.map((o:Data,i:number)=><div className="ownership-row" key={i}><span>{o.owner_key} · {o.location}{o.crafting_quality?' · Q'+o.crafting_quality:''}{o.owner_kind==='guild'?' · guild':''}{o.is_bound?' · bound':''}</span><b>{number(o.quantity)}</b></div>)}</details><small>Saved {ago(detail.owned[0].saved_at)}. Cached stock can include inaccessible locations.</small></>:<p>No stock for this item in your latest inventory snapshot.</p>}</section><section><h3><ChartNoAxesCombined size={16}/> Regional activity</h3>{detail.sales?<><strong className="context-number">{Number(detail.sales.metrics.region_sale_rate).toLocaleString('en-US',{maximumFractionDigits:3})}<small> TSM sale rate</small></strong><p>{detail.sales.metrics.region_sold_per_day==null?"Regional daily sold unavailable":number(detail.sales.metrics.region_sold_per_day)+" regional daily sold"}</p><small>TSM observation {ago(detail.sales.observed_at)} · not a forecast of your own sales.</small></>:<p>No recorded TSM sales estimate for this item.</p>}</section></div>

 <div className="market-freshness"><Info size={14}/><span>AH response collected {ago(offers[0]?.fetched_at??null)} · Source modified {ago(offers[0]?.source_modified_at??null)}. Inventory and TSM observations have their own timestamps.</span></div>

 </>:<div className="empty-state"><Layers3 size={32}/><h3>Your next market move starts here</h3><p>Search for an item and select a result to explore its price, supply and recorded history.</p></div>}</section></div>

 </motion.div>;

}

