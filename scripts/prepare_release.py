"""Create a content-bound receipt for the tested unsigned APK; contains no credentials."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[1]
version='1.2.0';code=10200
apk=root/f'dist/DuoAero-{version}-unsigned.apk'
files=[]
for folder in ['app/src','app/assets','original/res','original/compile-stubs','shared','vendor']:
 files.extend(p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files.extend(root/p for p in ['original/AndroidManifest.xml','scripts/build_original.py','scripts/ShadeDependencies.java'])
sources={}
for p in sorted(files):
 data=p.read_bytes()
 # Match Git's repository representation, preserving frozen and binary assets.
 if not p.relative_to(root).as_posix().startswith(('vendor/','shared/inhouse-services-updater/')) and p.suffix.lower() in ['.java','.xml','.json','.js','.py','.html','.css','.md']:
  data=data.replace(b'\r\n',b'\n')
 sources[p.relative_to(root).as_posix()]=hashlib.sha256(data).hexdigest()
receipt=dict(version=version,versionCode=code,url=f'https://github.com/miguelcoxcaballero/DuoAero/releases/download/build-{version}/DuoAero-{version}-unsigned.apk',sha256=hashlib.sha256(apk.read_bytes()).hexdigest(),sources=sources)
(root/'release-input.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('Prepared tested APK receipt:',receipt['sha256'])
