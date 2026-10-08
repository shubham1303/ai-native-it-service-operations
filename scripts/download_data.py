"""Acquire pinned public sources. Never execute content downloaded from a source."""
from pathlib import Path
from urllib.request import urlopen
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]

def download():
    manifest_path = ROOT / 'docs/source-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    destination = ROOT / 'data/raw/helpdesk_v3'
    destination.mkdir(parents=True, exist_ok=True)
    for item in manifest:
        name = item['filename']
        if name.endswith('.png'):
            continue
        assert Path(name).name == name
        target = destination / name
        expected = item['content_details']['sha256_hash']
        if target.exists():
            assert hashlib.sha256(target.read_bytes()).hexdigest() == expected, name
            continue
        with urlopen(item['content_details']['download_url'], timeout=60) as response:
            content = response.read()
        assert hashlib.sha256(content).hexdigest() == expected, name
        target.write_bytes(content)
        print(f'Verified {name}')
    (destination / 'source-manifest.json').write_bytes(manifest_path.read_bytes())
    research = ROOT / 'data/research'
    research.mkdir(exist_ok=True)
    for path in (ROOT / 'docs/sources').glob('*.json'):
        meta = json.loads(path.read_text(encoding='utf-8-sig'))
        item = meta['files'][0]
        target = research / item['name']
        if not target.exists():
            with urlopen(item['download_url'], timeout=60) as response:
                content = response.read()
            assert hashlib.md5(content).hexdigest() == item['computed_md5']
            target.write_bytes(content)
        assert hashlib.md5(target.read_bytes()).hexdigest() == item['computed_md5']
        (research / path.name).write_bytes(path.read_bytes())

if __name__ == '__main__':
    download()
