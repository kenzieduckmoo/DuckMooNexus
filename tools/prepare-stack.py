"""Assemble maintained source into the existing Nexus server layout."""
import argparse,shutil
from pathlib import Path

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=root/'.build/stack')
args=parser.parse_args()
output=args.output.resolve()
if output.exists():raise SystemExit('Output already exists. Choose a new empty output path; nothing was overwritten.')
ignore=shutil.ignore_patterns('.git','node_modules','.next','__pycache__','.test-deps','*.pyc','*.env','.env','*.log','local-data.json','daily-plan.json','saved-setups.json','tsconfig.tsbuildinfo')
shutil.copytree(root/'Nexus/clean-install',output,ignore=ignore)
shutil.copytree(root/'Nexus/web',output/'web',ignore=ignore)
shutil.copytree(root/'Nexus/craft-engine',output/'craft-engine',ignore=ignore)
shutil.copytree(root/'CraftingDesk',output/'app/craftingdesk',ignore=ignore)
print('Source assembly ready:',output)
print('No credentials, SavedVariables or saved plans were copied. No deployment was performed.')
