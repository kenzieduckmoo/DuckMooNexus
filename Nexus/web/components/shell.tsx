'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, ChartNoAxesCombined, Hammer, ArrowUpRight, Menu, X, ShieldCheck, ExternalLink,UsersRound,Coins,BookOpen } from 'lucide-react';
import { useState } from 'react';
import {AutoStatus} from './freshness';
export function Shell({children}:{children:React.ReactNode}){
 const path=usePathname(),[open,setOpen]=useState(false);
 return <div className="nexus-shell"><a className="skip-link" href="#content">Skip to content</a><aside className={open?'sidebar open':'sidebar'}>
 <Link className="brand" href="/" onClick={()=>setOpen(false)}><svg viewBox="0 0 48 48" aria-hidden="true"><path d="M11 13 5 7l2 17 17 18 17-18 2-17-6 6-13-8Z" fill="none" stroke="currentColor" strokeWidth="1.6"/><path d="m14 18 10 17 10-17-10 6Z" fill="currentColor"/><circle cx="24" cy="15" r="2" fill="currentColor"/></svg><span>DUCKMOO<strong>NEXUS</strong></span></Link>
 <div className="nav-caption">YOUR WARBAND, CONNECTED</div><nav aria-label="Main navigation">
 <Link onClick={()=>setOpen(false)} className={path==='/'?'nav-link active':'nav-link'} href="/"><LayoutDashboard size={19}/> Overview <span>01</span></Link>
 <Link onClick={()=>setOpen(false)} className={path.startsWith('/auctions')?'nav-link active':'nav-link'} href="/auctions"><ChartNoAxesCombined size={19}/> Auction House <span>02</span></Link>
 <Link onClick={()=>setOpen(false)} className={path.startsWith('/characters')?'nav-link active':'nav-link'} href="/characters"><UsersRound size={19}/> Character sheets <span>03</span></Link>
 <Link onClick={()=>setOpen(false)} className={path.startsWith('/crafting')?'nav-link active':'nav-link'} href="/crafting"><Hammer size={19}/> Crafting Desk <span>04</span></Link>
 <Link onClick={()=>setOpen(false)} className={path.startsWith('/finances')?'nav-link active':'nav-link'} href="/finances"><Coins size={19}/> Financials <span>05</span></Link>
 <Link onClick={()=>setOpen(false)} className={path.startsWith('/professions')?'nav-link active':'nav-link'} href="/professions"><BookOpen size={19}/> Professions <span>06</span></Link>
 </nav><div className="sidebar-divider"/><div className="nav-caption">THE BIGGER PICTURE</div>
 <a className="nav-link quiet" href="http://10.20.30.239:3000/d/duckmoo-warband-financials/"><ExternalLink size={17}/> Grafana dashboards</a>
 <div className="sidebar-bottom"><div className="connection"><span className="live-dot"/> HOME NETWORK <ShieldCheck size={14}/></div><p>Made for your characters.<br/>Built around your actual data.</p><div className="profile"><div className="profile-avatar">KD</div><div><b>Kenzie DuckMoo</b><small>Retail · US region</small></div></div></div>
 </aside>{open&&<button className="nav-scrim" onClick={()=>setOpen(false)} aria-label="Close navigation"/>}
 <div className="main-shell"><header className="topbar"><div className="breadcrumb"><button className="mobile-menu" onClick={()=>setOpen(!open)} aria-label="Toggle navigation">{open?<X size={20}/>:<Menu size={20}/>}</button><span>Nexus</span><span className="crumb-divider">/</span><b>{path.startsWith('/auctions')?'Auction House':path==='/characters'?'Character sheets':path.startsWith('/characters/')?'Character sheet':path.startsWith('/crafting')?'Crafting Desk':path.startsWith('/finances')?'Warband Financials':path.startsWith('/professions')?'Warband professions':'Warband overview'}</b></div><div className="topbar-right"><AutoStatus/><span className="region-tag">US</span></div></header><main id="content">{children}</main><footer className="site-footer"><span>DUCKMOO NEXUS <i>✦</i> Your next move, informed.</span><span>Game imagery © Blizzard Entertainment</span></footer></div></div>;
}
