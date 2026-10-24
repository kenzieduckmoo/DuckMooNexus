export const CHARACTER_ORDER=['Rolla','Stormlesbian','Hammeredchic','Stabbiechick','Kenziemoo','Pandaquack','Fearfulchick','Pandachicken','Kaidiellicia','Meepkin','Bloodchicken','Voidchicken','Kaissiriah','Zaraevelina','Trunktix','Darayeda','Kyootchick','Risharika','Duckmoochick'];
export const CLASS_COLORS:Record<string,string>={WARRIOR:'#c79c6e',PALADIN:'#ef9cbe',HUNTER:'#abd473',ROGUE:'#e8d783',PRIEST:'#e1e4ee',DEATHKNIGHT:'#db6c7a',SHAMAN:'#69a9ef',MAGE:'#80cee8',WARLOCK:'#b6a5df',MONK:'#71d7b2',DRUID:'#e6a163',DEMONHUNTER:'#b880d2',EVOKER:'#7eb6a8'};
export const classColor=(key:string)=>CLASS_COLORS[String(key??'').toUpperCase().replace(/[^A-Z]/g,'')]??'#b6a988';
type RosterCharacter={name:string;realm?:string;tags?:unknown;level?:unknown;item_level?:unknown};
export function characterSort(a:RosterCharacter,b:RosterCharacter){
 const main=(c:RosterCharacter)=>values(c.tags).some(tag=>/\bmain\b/i.test(gameText(tag)));
 const numeric=(n:unknown)=>n!=null&&n!==''&&Number.isFinite(Number(n))?Number(n):-1;
 return Number(main(b))-Number(main(a))||numeric(b.level)-numeric(a.level)||numeric(b.item_level)-numeric(a.item_level)||a.name.localeCompare(b.name)||String(a.realm??'').localeCompare(String(b.realm??''));
}
export function asset(media:unknown,key:string){return Array.isArray(media)?media.find(a=>a.key===key)?.value??null:null;}
export function gameText(value:unknown):string{return String(value??'').replace(/\|c[0-9a-fA-F]{8}|\|cn[A-Za-z0-9_]+:|\|r/g,'').replace(/\|A:.*?\|a|\|T.*?\|t/g,'').replace(/\|H[^|]*\|h([^|]*)\|h/g,'$1').trim();}
export function values(value:unknown):any[]{return Array.isArray(value)?value:value&&typeof value==='object'?Object.values(value):[];}
