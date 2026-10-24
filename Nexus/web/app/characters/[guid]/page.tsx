import {CharacterSheet} from '@/components/character-sheet';
export const metadata={title:'Character sheet'};
export default async function Page({params,searchParams}:{params:Promise<{guid:string}>;searchParams:Promise<{client?:string}>}){const {guid}=await params,q=await searchParams;return <CharacterSheet key={guid+'|'+q.client} guid={guid} client={q.client==='forever'?'forever':'retail'}/>;}
