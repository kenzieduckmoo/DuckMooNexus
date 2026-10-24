import type { Metadata } from 'next';
import './globals.css';
import './characters.css';
import './crafting.css';
import './finances.css';
import './progress.css';
import './professions.css';
import './buying.css';
import './adventures.css';
import { Shell } from '@/components/shell';
import {FreshnessProvider} from '@/components/freshness';
export const metadata: Metadata={title:{default:'DuckMoo Nexus',template:'%s · DuckMoo Nexus'},description:'Your warband, connected. Markets, crafting and the characters behind it all.'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><FreshnessProvider><Shell>{children}</Shell></FreshnessProvider></body></html>;}
