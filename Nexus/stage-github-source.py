"""Prepare a source-only GitHub working copy; never reads live SavedVariables."""
from pathlib import Path
import os,json,shutil,re

workspace=Path(__file__).resolve().parent.parent
target=workspace/'DuckMooNexus'
target.mkdir(exist_ok=True)
excluded_dirs={'node_modules','.next','.build','__pycache__','.test-deps','test-deps','downloads','.git','state','private-snapshots','web-verification','verification','test-tmp'}
text_ext={'.py','.ps1','.js','.cjs','.mjs','.ts','.tsx','.lua','.toc','.md','.css','.html','.sql','.yaml','.yml','.vbs','.cmd','.txt','.svg','.sh','.psql','.service','.timer'}
binary_ext={'.webp','.tga','.blp','.png','.ttf','.otf'}
json_names={'package.json','tsconfig.json','components.json','sources.json','vendor-manifest.json'}
skip_names={'local-data.json','saved-setups.json','daily-plan.json','next-env.d.ts','tsconfig.tsbuildinfo','real-data-verification.json','release-manifest.json','omni-verification-fixture.json'}
roots=['Nexus/clean-install','Nexus/web','Nexus/craft-engine','CraftingDesk','Nexus/sync-0.3.0']+['AddOns/'+x for x in ('DuckMooCapture','DuckMooFolio','DuckMooPlanner','DuckMooWarband','DuckMooOmniCapture')]
selected=[]
for name in roots:
    for folder,dirs,files in os.walk(workspace/name):
        dirs[:]=[d for d in dirs if d not in excluded_dirs]
        for filename in files:
            p=Path(folder)/filename
            if filename in skip_names or filename.startswith('.env') or p.suffix in {'.env','.log','.tmp','.bak','.zip','.gz','.jpg','.jpeg'}:continue
            allowed=p.suffix in text_ext|binary_ext or (p.suffix=='.json' and ('grafana' in p.parts or 'dashboard-seeds' in p.parts or filename=='grafana-dashboard.json')) or filename in json_names|{'Dockerfile','.dockerignore','.gitignore','LICENSE','NOTICE','LibSerialize-LICENSE'}
            if not allowed:continue
            selected.append((p,p.relative_to(workspace)))
for p in (workspace/'Nexus').glob('*.md'):selected.append((p,p.relative_to(workspace)))
for p in (workspace/'Nexus').glob('deploy-*.py'):selected.append((p,p.relative_to(workspace)))
for name in ('preflight.sh','rollback-server.sh','upgrade-server.sh','verify-stack.sh','release_gate.py','test-receipt-sync.py','package-addon-releases.py','test-crafting-refresh-signature.py','verify-pre-forever.py','verify-forever-ready.py','Prepare-Forever.ps1','stage-github-source.py'):
    p=workspace/'Nexus'/name
    if p.exists():selected.append((p,p.relative_to(workspace)))
selected.append((workspace/'AddOns/AGENTS.md',Path('AddOns/AGENTS.md')))
for name,dest in [('Mission To build DuckMoo Nexus.md','docs/history/original-mission.md'),('DuckMoo-Nexus-Project-MOO-Handoff-2026-10-22.md','docs/history/handoff-2026-10-22.md')]:
    selected.append((workspace/name,Path(dest)))
for original,relative in selected:
    dest=target/relative;dest.parent.mkdir(parents=True,exist_ok=True)
    if original.suffix in binary_ext or 'vendor' in original.parts:shutil.copy2(original,dest)
    else:
        text=original.read_text(encoding='utf-8-sig')
        # Original mission notes may contain inline API credentials. Redact the
        # credential block through its following blank line, not program logic.
        if relative.as_posix().startswith('docs/history/'):
            text=re.sub(r'(?im)^(.*(?:client secret|client id|api secret|api key|password|passphrase)\s*[:=]\s*)([^\n]+)$',r'\1[REDACTED]',text)
        dest.write_text(text,encoding='utf-8',newline='\n')
entries=[]
for folder,dirs,files in os.walk(target):
    dirs[:]=[d for d in dirs if d not in excluded_dirs]
    for filename in files:
        p=Path(folder)/filename
        entries.append({'path':p.relative_to(target).as_posix(),'bytes':p.stat().st_size,'binary':p.suffix in binary_ext})
manifest=workspace/'Nexus/github-source-manifest.json'
manifest.write_text(json.dumps(sorted(entries,key=lambda r:r['path'])),encoding='utf-8')
print(json.dumps({'files':len(entries),'bytes':sum(r['bytes'] for r in entries),'working_copy':str(target)}))
