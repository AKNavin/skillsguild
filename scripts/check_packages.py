"""Validate built package integrity and direct AI resource links; stdlib only."""
import json
import re
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
catalogue=json.loads((DIST/'catalogue.json').read_text(encoding='utf-8'))
names=set()
for item in catalogue:
    name=item['id']
    assert name not in names;names.add(name)
    source=ROOT/'skills'/item['category']/name
    instructions=(source/'SKILL.md').read_bytes()
    assert (DIST/item['instruction_url']).read_bytes()==instructions
    assert (DIST/item['image']).is_file()
    with zipfile.ZipFile(DIST/item['download']) as archive:
        assert archive.testzip() is None, name
        files=archive.namelist()
        assert len(files)==len(set(files)), name
        assert f'{name}/SKILL.md' in files and f'{name}/LICENSE' in files
        for path in files:
            assert path.startswith(name+'/') and '..' not in Path(path).parts
            assert not any(p.startswith('.') or p=='__pycache__' for p in Path(path).parts)
            if path!=name+'/LICENSE':
                relative=path[len(name)+1:]
                assert archive.read(path)==(source/relative).read_bytes()
                assert (DIST/Path(item['instruction_url']).parent/relative).read_bytes()==archive.read(path)
    # Markdown helper references must resolve in the same downloadable folder.
    for reference in re.findall(r'\]\(((?:scripts|tests|fixtures|references)/[A-Za-z0-9_./-]+)\)',instructions.decode('utf-8')):
        assert (source/reference).exists(), (name,reference)
    if item['category'] in ['algotrading','hr'] and item.get('verified_at'):
        assert item.get('sources') and item.get('requires')
for category in ['algotrading','hr']:
    with zipfile.ZipFile(DIST/f'downloads/{category}-bundle.zip') as bundle:
        assert bundle.testzip() is None
        for item in catalogue:
            if item['category']==category:
                assert bundle.read(category+'/'+item['id']+'/SKILL.md')==(ROOT/'skills'/category/item['id']/'SKILL.md').read_bytes()
        assert all('/preview.' not in name for name in bundle.namelist())
        for link in re.findall(r'\]\(([^)]+)\)',bundle.read(category+'/START-HERE.md').decode('utf-8')):
            if not link.startswith('https://'):
                assert category+'/'+link in bundle.namelist(), (category,link)
for name in ['llms.txt','algotrading.md','hr.md']:
    for link in re.findall(r'\]\(([^)]+)\)',(DIST/name).read_text(encoding='utf-8')):
        if not link.startswith('https://'):
            assert (DIST/link).is_file(), (name,link)
print(f'Validated {len(catalogue)} ZIPs, direct resources, relative references, AI indexes and business bundles.')
