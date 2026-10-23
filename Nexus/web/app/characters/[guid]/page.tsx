import {CharacterSheet} from '@/components/character-sheet';
export const metadata={title:'Character sheet'};
export default async function Page({params}:{params:Promise<{guid:string}>}){const {guid}=await params;return <CharacterSheet guid={guid}/>;}
