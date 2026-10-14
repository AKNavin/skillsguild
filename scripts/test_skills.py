"""Run bundled offline helper suites in isolated processes, without bytecode files."""
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
suites=0
for skill in sorted((ROOT/'skills').glob('*/*')):
    for folder in ['scripts','tests']:
        tests=skill/folder
        if tests.is_dir() and list(tests.glob('test_*.py')):
            print(f'Checking {skill.name}/{folder}',flush=True)
            subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',folder],cwd=skill,check=True)
            suites+=1
print(f'{suites} offline suites passed. No external calls or live-system changes.')
