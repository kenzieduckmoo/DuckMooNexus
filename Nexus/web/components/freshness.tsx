'use client';
import {createContext,useContext,useEffect,useState} from 'react';
type Revision={sources:string;market:string;characters:string;documents:string;crafting:string;checked:number;connected:boolean};
const initial:Revision={sources:'',market:'',characters:'',documents:'',crafting:'',checked:0,connected:true};
const Context=createContext<Revision>(initial);
export function FreshnessProvider({children}:{children:React.ReactNode}){
 const [revision,setRevision]=useState(initial);
 useEffect(()=>{let busy=false,alive=true;const controller=new AbortController();
  async function check(){if(busy||document.hidden)return;busy=true;try{const r=await fetch('/api/version',{cache:'no-store',signal:controller.signal});if(!r.ok)throw Error();const d=await r.json();if(alive)setRevision({...d,checked:Date.now(),connected:true});}catch(e){if(alive&&!controller.signal.aborted)setRevision(old=>({...old,connected:false}));}finally{busy=false;}}
  check();const timer=setInterval(check,30000);window.addEventListener('focus',check);window.addEventListener('online',check);document.addEventListener('visibilitychange',check);
  return()=>{alive=false;controller.abort();clearInterval(timer);window.removeEventListener('focus',check);window.removeEventListener('online',check);document.removeEventListener('visibilitychange',check);};
 },[]);
 return <Context.Provider value={revision}>{children}</Context.Provider>;
}
export function useNexusRevision(){return useContext(Context);}
export function useMinute(){const [minute,setMinute]=useState(0);useEffect(()=>{setMinute(Math.floor(Date.now()/60000));const t=setInterval(()=>setMinute(Math.floor(Date.now()/60000)),30000);return()=>clearInterval(t);},[]);return minute;}
export function AutoStatus(){const r=useNexusRevision();return <span className={'auto-status '+(!r.connected?'offline':'')} title={r.checked?'Last checked '+new Date(r.checked).toLocaleTimeString():'Checking data freshness'}><span className="live-dot"/>{r.connected?'Updates automatically':'Reconnecting…'}</span>;}
