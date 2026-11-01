type D=Record<string,any>;
export const blankStory=()=>({backstory:'',notes:'',epitaph:'',moments:[] as D[]});
export function validateStory(value:any){
 if(!value||typeof value!=='object'||Array.isArray(value))throw Error('Choose a valid story.');
 const text=(v:any,n:number)=>{if(typeof v!=='string'||v.length>n)throw Error('A story field is missing or too long.');return v;};
 if(!Array.isArray(value.moments)||value.moments.length>100)throw Error('Keep up to 100 personal highlights.');
 const seen=new Set();
 return {backstory:text(value.backstory,20000),notes:text(value.notes,20000),epitaph:text(value.epitaph,1000),moments:value.moments.map((m:any)=>{
  if(!m||typeof m.id!=='string'||!/^[a-zA-Z0-9-]{1,80}$/.test(m.id)||seen.has(m.id))throw Error('Choose unique highlight IDs.');seen.add(m.id);
  if(typeof m.at!=='string'||!Number.isFinite(Date.parse(m.at)))throw Error('Choose a date for the highlight.');
  if(m.eventID!=null&&(typeof m.eventID!=='string'||!/^[a-f0-9]{64}$/.test(m.eventID)))throw Error('Choose a captured event.');
  return {id:m.id,title:text(m.title,160),note:text(m.note,4000),at:new Date(m.at).toISOString(),eventID:m.eventID||null};
 })};
}
const plain=(s:any)=>String(s??'').replace(/\|c[0-9a-fA-F]{8}|\|r/g,'').replace(/\|A:.*?\|a|\|T.*?\|t/g,'');
export function eventText(e:D){const p=e.payload??e,d=p.data??{},kind=p.kind;
 if(kind==='level')return 'Reached level '+(d.level??'?');
 if(kind==='quest_completed')return 'Completed '+plain(d.name||'quest '+d.questID);
 if(kind==='encounter')return plain(d.name||'Encounter '+d.id)+(d.success===1?' — victory':d.success===0?' — defeat':' — result unknown');
 if(kind==='achievement')return 'Earned achievement '+d.id;
 if(kind==='loot')return plain(d.message||'Loot observed');
 if(kind==='death')return 'Death recorded'+(d.zone?' in '+plain(d.zone):'');
 if(kind==='life_mode')return d.mode==='hardcore'?'Hardcore recording enabled':'Standard recording enabled';
 return kind==='session_start'?'Session began':kind==='session_end'?'Session ended':plain(kind);
}
export function biography(data:D){
 const c=data.selected,s=data.summary??{},life=c?.life,p=c?.profile??{};if(!c)return [];
 const lines=[`${c.name} of ${c.realm}${p.race?' is a '+p.race:''}${p.className||p.class?' '+(p.className||p.class):''}.`];
 if(life?.startedAt)lines.push(`Recording began at level ${life.startLevel??'unknown'} on ${new Date(life.startedAt*1000).toISOString().slice(0,10)} (UTC). This is the first observation, not a character creation date.`);
 else if(s.first_at)lines.push('The retained event record begins on '+new Date(s.first_at).toISOString().slice(0,10)+' (UTC). Earlier adventures are unknown.');
 if(life?.startedAt){const end=life.endedAt?life.endedAt*1000:Date.parse(c.observed_at||s.last_at||'');const hours=Math.floor((end-life.startedAt*1000)/3600000);if(Number.isFinite(hours)&&hours>=0)lines.push('The observed span covers '+Math.floor(hours/24)+' days and '+hours%24+' hours between first and latest observations. This is elapsed calendar time, not time played.');}
 if(life?.highestLevel||s.highest_level)lines.push('The highest recorded level is '+Math.max(Number(life?.highestLevel||0),Number(s.highest_level||0))+'.');
 if(s.total)lines.push(`The archive contains ${s.total} events, including ${s.quests??0} quest turn-ins, ${s.victories??0} successful encounters and ${s.achievements??0} achievement events. These are recorded events, not unique completion totals.`);
 if(life?.endedAt)lines.push('A terminal Hardcore death was recorded on '+new Date(life.endedAt*1000).toISOString()+'. Killer and cause of death are not established by this recorder.');
 else lines.push('No terminal Hardcore death is recorded. Being offline does not mean this character has died.');
 return lines;
}
export function storyExport(data:D,doc:D,format='text'){
 const c=data.selected,lines=[`${c?.name??'Character'} — ${c?.realm??''}`,data.client==='forever'?'WoW Forever':'WoW Retail','',...biography(data),'','PERSONAL BACKSTORY',doc.backstory||'Not written.','','PERSONAL NOTES',doc.notes||'Not written.','','EPITAPH (PERSONAL WRITING)',doc.epitaph||'Not written.','','SELECTED PERSONAL HIGHLIGHTS',...doc.moments.map((m:D)=>`${m.at} — ${m.title}\n${m.note}\n${m.eventID?'Captured evidence: '+m.eventID:'Personal recollection; not game-verified.'}`),'','RECORDED HIGHLIGHTS',...(data.highlights??[]).map((e:D)=>`${new Date(e.observed_at).toISOString()} — ${eventText(e)} [${e.id}]`),'','COVERAGE','Recording begins at first observation. Unknown time between saves is not proof of a recording failure. Event counts cover the retained archive; selected highlights are a limited selection. No killer, continuous playtime or unobserved accomplishments are inferred.'];
 if(format==='outline')lines.push('','DOCUMENTARY OUTLINE','1. Introduction: character, realm and your backstory.','2. Beginnings: first observed level and date.','3. Chapters: use dated levels, quests, encounters and personal highlights above.','4. Ending: use only a recorded terminal death; otherwise leave the story open.','5. Credits and evidence: cite event IDs; label personal recollections and missing evidence.','Gameplay footage, narration and music are not generated or captured by this export.');
 return lines.join('\n');
}
