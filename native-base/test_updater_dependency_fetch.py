"""Exercise retry and integrity behavior without network or signing material."""
import hashlib
import tempfile
import urllib.error
from pathlib import Path
from unittest.mock import patch

from build_updater import fetch_dependency

payload = b'locked synthetic dependency'
item = {'file': 'dependency.jar', 'url': 'https://invalid.example/dependency',
        'sha256': hashlib.sha256(payload).hexdigest()}
with tempfile.TemporaryDirectory() as folder:
    target = Path(folder)/item['file']
    calls = []
    def transient(url, filename):
        calls.append(1)
        if len(calls) == 1:
            raise urllib.error.HTTPError(url, 404, 'temporary', None, None)
        Path(filename).write_bytes(payload)
    with patch('build_updater.urllib.request.urlretrieve', side_effect=transient), \
         patch('build_updater.time.sleep') as sleep:
        fetch_dependency(item, target)
    assert len(calls) == 2 and sleep.call_count == 1 and target.read_bytes() == payload
    target.unlink()
    def corrupt(url, filename):
        Path(filename).write_bytes(b'incorrect')
    with patch('build_updater.urllib.request.urlretrieve', side_effect=corrupt):
        try:
            fetch_dependency(item, target)
        except ValueError:
            pass
        else:
            raise AssertionError('A checksum mismatch was accepted')
    assert not target.exists() and not target.with_name(target.name+'.part').exists()
    with patch('build_updater.urllib.request.urlretrieve', side_effect=urllib.error.HTTPError(item['url'], 404, 'missing', None, None)) as retrieve, \
         patch('build_updater.time.sleep'):
        try:
            fetch_dependency(item, target)
        except urllib.error.HTTPError:
            pass
        else:
            raise AssertionError('A persistent failure was accepted')
    assert retrieve.call_count == 3 and not target.exists()
print('PASS: transient dependency failure retries; checksum failure never caches a file')
