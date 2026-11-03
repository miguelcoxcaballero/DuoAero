"""Bind an unsigned native-runtime candidate to its tracked build inputs.

This receipt verifies identity and content; it is not an acceptance-test result.
The permanent signer checks it before accessing the signing key.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile
from runtime_config import ROOT, APK, tool

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--apk', type=Path, required=True)
parser.add_argument('--version', required=True)
parser.add_argument('--code', type=int, required=True)
args = parser.parse_args()
if not re.fullmatch(r'\d+\.\d+\.\d+', args.version) or args.code <= 10200:
    parser.error('Version must advance the published production APK')
badging = subprocess.check_output([str(tool('aapt2')), 'dump', 'badging', str(args.apk)], text=True)
assert f"package: name='com.duoaero' versionCode='{args.code}' versionName='{args.version}'" in badging
assert 'application-debuggable' not in badging
with zipfile.ZipFile(args.apk) as archive:
    for name in ('classes12.dex', 'classes13.dex', 'assets/duoaero/standalone-bootstrap',
                 'assets/duoaero/google-required', 'assets/duoaero/course/session-catalog.json'):
        assert name in archive.namelist(), name
    catalog=json.loads(archive.read('assets/duoaero/course/session-catalog.json'))
    assert len(catalog) == 108
    assert all('second-partial-'+topic+'-lesson-'+str(index) in catalog for topic,count in (('3.1',3),('3.2',2),('3.3',2)) for index in range(count))
reference = next(item for item in json.loads((ROOT/'native-base/handoff-artifacts.json').read_text())['artifacts'] if item['name'] == APK.name)
assert hashlib.sha256(APK.read_bytes()).hexdigest() == reference['sha256']
tracked = subprocess.check_output(['git', 'ls-files', '-z', 'native-base', 'app/assets', 'shared', 'vendor', 'inhouse-updater.lock.json', 'scripts/ShadeDependencies.java', 'original/res/xml/inhouse_update_paths.xml'], cwd=ROOT).decode().split('\0')
sources = {}
for name in sorted(filter(None, tracked)):
    # Evidence prose changes independently of the APK. Build code, vendor
    # dependencies, configuration and public question content are all bound.
    if name.startswith('native-base/') and (name.endswith('.md') or name == 'native-base/status.json'):
        continue
    path = ROOT/name
    sources[name] = hashlib.sha256(path.read_bytes()).hexdigest()
receipt = {
    'version': args.version, 'versionCode': args.code,
    'url': f'https://github.com/miguelcoxcaballero/DuoAero/releases/download/build-{args.version}/DuoAero-{args.version}-unsigned.apk',
    'sha256': hashlib.sha256(args.apk.read_bytes()).hexdigest(),
    'baseApkSha256': reference['sha256'],
    'implementation': 'native-base', 'sources': sources,
}
(ROOT/'release-input.json').write_text(json.dumps(receipt, indent=2)+'\n')
print('Prepared native-runtime signing receipt; runtime acceptance remains separate.')
