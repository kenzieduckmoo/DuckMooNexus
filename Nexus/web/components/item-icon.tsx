'use client';
import { Package } from 'lucide-react';
import { useState } from 'react';
export function ItemIcon({src,name,quality,large=false}:{src?:string|null;name:string;quality?:string;large?:boolean}){const [failed,setFailed]=useState(false);return <span className={'item-icon '+(large?'large ':'')+(quality??'').toLowerCase()}>{src&&!failed?<img src={src} alt="" loading="lazy" onError={()=>setFailed(true)}/>:<Package size={large?27:20}/>}</span>;}
