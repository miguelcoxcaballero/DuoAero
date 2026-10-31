from pathlib import Path
import subprocess,zipfile,shutil
from runtime_config import ROOT as R, WORK as W, SDK, BT, JAR as platform, KEY, ADB, java, tool
import sys
def run(*args):subprocess.run([str(a) for a in args],check=True)
for folder in ['testclasses','testdex']:
 path=W/folder
 if path.exists():shutil.rmtree(path)
 path.mkdir(parents=True,exist_ok=True)
run(tool('aapt2'),'link','-o',W/'tests.apk','--manifest',R/'native-base/tests/AndroidManifest.xml','-I',platform)
run(java('javac'),'--release','8','-encoding','UTF-8','-classpath',platform,'-d',W/'testclasses',*list((R/'native-base/tests').glob('*.java')))
run(java('java'),'-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--lib',platform,'--min-api','29','--output',W/'testdex',*list((W/'testclasses').rglob('*.class')))
with zipfile.ZipFile(W/'tests.apk','a') as z:
 z.write(W/'testdex/classes.dex','classes.dex')
 for fixture in (R/'native-base/tests/fixtures').glob('*.json'):z.write(fixture,'assets/'+fixture.name)
run(java('java'),'-jar',BT/'lib/apksigner.jar','sign','--ks',KEY,'--ks-pass','pass:android','--out',W/'tests-signed.apk',W/'tests.apk')
if '--build-only' not in sys.argv:run(ADB,'install','-r',W/'tests-signed.apk')
