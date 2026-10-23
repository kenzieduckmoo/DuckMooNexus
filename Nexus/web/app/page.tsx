import { Overview } from '@/components/overview';
import {HERO_SCENES} from '@/lib/hero-scenes';
export const dynamic='force-dynamic';
export default function Page(){return <Overview hero={HERO_SCENES[Math.floor(Math.random()*HERO_SCENES.length)]}/>;}
