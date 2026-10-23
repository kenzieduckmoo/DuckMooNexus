/* Exact materials and missing-only shopping shared by both crafting screens. */
async function copyCraftText(text){
 if(navigator.clipboard?.writeText){try{await navigator.clipboard.writeText(text);return;}catch{}}
 const field=document.createElement('textarea');field.value=text;field.style.position='fixed';field.style.left='-10000px';document.body.append(field);field.select();
 const copied=document.execCommand('copy');field.remove();if(!copied)throw Error('Use the selected export text.');
}
function renderBatchShopping(parent,batch){
 const money=n=>n==null?'Unknown':(n/10000).toLocaleString(undefined,{maximumFractionDigits:2})+' g';
 const table=document.createElement('table');table.style.width='100%';
 table.innerHTML='<thead><tr><th align="left">Material</th><th>Need</th><th>Reserved stock</th><th>Buy</th><th>Purchase cost</th></tr></thead>';
 const body=document.createElement('tbody');table.append(body);
 for(const row of batch.rows){const tr=document.createElement('tr');for(const text of [qualityLabel(row.item,data.inventory?.names,data.inventory?.tiers),row.needed,row.own,row.missing,row.missing?money(row.price?row.price.price*row.missing:null):money(0)]){const td=document.createElement('td');td.textContent=text;td.style.padding='7px';tr.append(td);}body.append(tr);}
 parent.append(table);
 const shopping=batch.rows.filter(r=>r.price?.source!=='vendor').map(r=>({...r,scope:r.price?.scope||batch.entry.setup.realm,price:r.price?.price??null}));
 const all=auctionatorImportText({requirementsKnown:true,shopping},data.inventory?.names||{},data.inventory?.tiers||{});
 const text=all.includes('BEGIN AUCTIONATOR IMPORT')?all.split('BEGIN AUCTIONATOR IMPORT\n')[1].split('\nEND AUCTIONATOR IMPORT')[0]:'';
 const button=document.createElement('button');button.textContent='Copy missing materials to Auctionator';button.disabled=!text;
 const status=document.createElement('p');status.setAttribute('role','status');
 const details=document.createElement('details'),summary=document.createElement('summary'),fallback=document.createElement('textarea');summary.textContent='Shopping import text';fallback.value=text;fallback.readOnly=true;fallback.rows=4;fallback.style.width='100%';fallback.setAttribute('aria-label','Auctionator missing-material import');details.append(summary,fallback);
 button.onclick=async()=>{try{await copyCraftText(text);status.textContent='Copied. Paste into Auctionator Shopping → Import.';}catch{details.open=true;fallback.focus();fallback.select();status.textContent='Copy the selected text with Ctrl+C.';}};
 parent.append(button,status,details);
 if(all.includes('Manual searches excluded from import:')){const p=document.createElement('p');p.textContent=all.split('Manual searches excluded from import:')[1];parent.append(p);}
 const vendor=batch.rows.filter(r=>r.price?.source==='vendor'&&r.missing>0);
 if(vendor.length){const p=document.createElement('p');p.textContent='Vendor purchases: '+vendor.map(r=>r.missing+' × '+qualityLabel(r.item,data.inventory?.names,data.inventory?.tiers)).join(', ');parent.append(p);}
}
