from pathlib import Path
import subprocess,zipfile
R=Path.cwd();W=Path.home()/'.codex/duoaero-native-base';SDK=Path.home()/'AppData/Local/Android/Sdk';BT=SDK/'build-tools/35.0.0';J=Path('C:/Program Files/Android/Android Studio/jbr/bin');platform=SDK/'platforms/android-36/android.jar'
def run(*args):subprocess.run([str(a) for a in args],check=True)
for folder in ['testclasses','testdex']:(W/folder).mkdir(exist_ok=True)
run(BT/'aapt2.exe','link','-o',W/'tests.apk','--manifest',R/'native-base/tests/AndroidManifest.xml','-I',platform)
run(J/'javac.exe','--release','8','-encoding','UTF-8','-classpath',platform,'-d',W/'testclasses',*list((R/'native-base/tests').glob('*.java')))
run(J/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--lib',platform,'--min-api','29','--output',W/'testdex',*list((W/'testclasses').rglob('*.class')))
with zipfile.ZipFile(W/'tests.apk','a') as z:
 z.write(W/'testdex/classes.dex','classes.dex')
 for fixture in (R/'native-base/tests/fixtures').glob('*.json'):z.write(fixture,'assets/'+fixture.name)
run(J/'java.exe','-jar',BT/'lib/apksigner.jar','sign','--ks',R/'build/debug.p12','--ks-pass','pass:android','--out',W/'tests-signed.apk',W/'tests.apk')
run(SDK/'platform-tools/adb.exe','install','-r',W/'tests-signed.apk')
