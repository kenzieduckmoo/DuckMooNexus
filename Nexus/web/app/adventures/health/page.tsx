import {CaptureHealth} from '@/components/capture-health';
export const metadata={title:'Capture health & launch checks'};
export default async function Page({searchParams}:{searchParams:Promise<{client?:string}>}){const q=await searchParams;return <CaptureHealth client={q.client==='forever'?'forever':'retail'}/>;}
