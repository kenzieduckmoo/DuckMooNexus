import {WarbandRoster} from '@/components/warband-roster';
export const metadata={title:'Roster & census'};
export default async function Page({searchParams}:{searchParams:Promise<{client?:string;professionSlots?:string}>}){const q=await searchParams;return <WarbandRoster key={q.client} client={q.client==='forever'?'forever':'retail'} initialView={q.professionSlots==='open'?'openings':'roster'}/>;}
