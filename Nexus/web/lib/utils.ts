import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }
export function gold(copper: unknown) { if(copper==null)return '—';return (Number(copper)/10000).toLocaleString('en-US',{maximumFractionDigits:2}); }
export function number(value: unknown) {return Number(value??0).toLocaleString('en-US');}
export function ago(value: string | null) {if(!value)return 'Not captured';const m=Math.max(0,Math.floor((Date.now()-new Date(value).getTime())/60000));return m<1?'Just now':m<60?m+'m ago':m<1440?Math.floor(m/60)+'h ago':Math.floor(m/1440)+'d ago';}
