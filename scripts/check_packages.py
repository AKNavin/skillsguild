"""Validate delivered reproduction archives and static resource integrity."""
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
catalogue=json.loads((DIST/'catalogue.json').read_text(encoding='utf-8'))
assert len(catalogue)==15
required={'README.md','SKILL.md','strategy.json','reference-result.json','LICENSE','package-manifest.json',
          'research/runner.py','research/engine.py','research/signals.py','research/panel.py','research/README.md',
          'research/requirements.txt','research/verification.json','broker/broker_login.py','broker/download.py','broker/README.md'}
for strategy in catalogue:
    sid=strategy['id']; prefix=f'skillsguild-{sid}/'
    with ZipFile(DIST/strategy['download']) as archive:
        assert archive.testzip() is None, sid
        names=archive.namelist()
        assert len(names)==len(set(names)),sid
        assert all(n.startswith(prefix) and '..' not in Path(n).parts for n in names),sid
        relative={n[len(prefix):] for n in names}
        assert required<=relative,(sid,required-relative)
        manifest=json.loads(archive.read(prefix+'package-manifest.json'))
        for item in manifest['files']:
            assert hashlib.sha256(archive.read(prefix+item['path'])).hexdigest()==item['sha256'],(sid,item['path'])
        assert len(manifest['files'])==len(names)-1
        assert json.loads(archive.read(prefix+'strategy.json'))==strategy
        assert json.loads(archive.read(prefix+'reference-result.json'))==json.loads((DIST/strategy['result_url']).read_text(encoding='utf-8'))
        for name in relative:
            assert not name.endswith('.pyc') and '__pycache__' not in name and not name.startswith('.'),name
        for relative_path in ['research/engine.py','research/runner.py','research/signals.py','research/panel.py','broker/broker_login.py','broker/download.py','broker/broker_core.py']:
            assert archive.read(prefix+relative_path)==(ROOT/'packages'/relative_path).read_bytes(),relative_path
    for field in ['instruction_url','download','result_url','manifest_url']:
        assert (DIST/strategy[field]).is_file(),strategy[field]
    diagram=DIST/f'visual-{sid}.svg'
    assert diagram.is_file()
    assert '<text' not in diagram.read_text(encoding='utf-8'),f'Visible image text: {sid}'
with ZipFile(DIST/'downloads/all-strategies.zip') as archive:
    assert archive.testzip() is None
    assert 'research/runner.py' in archive.namelist() and 'broker/download.py' in archive.namelist()
    for s in catalogue: assert f"strategies/{s['id']}/SKILL.md" in archive.namelist()
for name in ['index.html','methodology.html','contributing.html']:
    html=(DIST/name).read_text(encoding='utf-8')
    for href in re.findall(r'(?:src|href)="([^"]+)"',html):
        if href.startswith(('http:','https:','#','mailto:')):continue
        resource=href.split('#')[0].split('?')[0]
        assert resource in ['','./'] or (DIST/resource).exists(),(name,resource)
assert not (DIST/'library').exists()
assert not (DIST/'hr.md').exists()
assert not (DIST/'algotrading.md').exists()
assert not list(DIST.glob('previews/*'))
print(f'Verified {len(catalogue)} self-contained archives, combined pack, hashes, CRCs, diagrams and static links. Retired catalogue absent.')
