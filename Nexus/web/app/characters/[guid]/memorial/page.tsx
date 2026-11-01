import {CharacterStory} from '@/components/character-story';
export const metadata={title:'Character memorial'};
export default async function Page({params,searchParams}:{params:Promise<{guid:string}>;searchParams:Promise<{client?:string}>}){const {guid}=await params,q=await searchParams;return <CharacterStory guid={guid} client={q.client==='forever'?'forever':'retail'} memorial/>;}
