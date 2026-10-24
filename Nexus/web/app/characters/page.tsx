import {CharacterDirectory} from '@/components/character-directory';
export const metadata={title:'Character sheets'};
export default async function Page({searchParams}:{searchParams:Promise<{client?:string}>}){const q=await searchParams,client=q.client==='forever'?'forever':'retail';return <CharacterDirectory key={client} client={client}/>;}
