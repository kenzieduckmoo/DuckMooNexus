import Link from 'next/link';
export function CharacterSectionNav({client='retail',active='sheets'}:{client?:string;active?:string}){
 return <nav className="character-section-nav" aria-label="Character sheets section"><Link aria-current={active==='sheets'?'page':undefined} href={'/characters?client='+client}>Character sheets</Link><Link aria-current={active==='roster'?'page':undefined} href={'/characters/roster?client='+client}>Roster & census</Link></nav>;
}
