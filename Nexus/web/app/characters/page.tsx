import {redirect} from 'next/navigation';
import {CharacterDirectory} from '@/components/character-directory';
export const metadata={title:'Character sheets'};
export default async function Page({searchParams}:{searchParams:Promise<{client?:string;professionSlots?:string}>}){const q=await searchParams,client=q.client==='forever'?'forever':'retail';if(q.professionSlots==='open')redirect('/characters/roster?client='+client+'&professionSlots=open');return <CharacterDirectory key={client} client={client}/>;}
