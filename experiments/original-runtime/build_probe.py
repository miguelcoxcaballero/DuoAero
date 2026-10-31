from pathlib import Path
import xml.etree.ElementTree as E,zipfile,subprocess
R=Path.cwd();W=Path.home()/'.codex/duoaero-original-runtime';W.mkdir(exist_ok=True)
SDK=Path.home()/'AppData/Local/Android/Sdk';BT=SDK/'build-tools/35.0.0';JAVA=Path('C:/Program Files/Android/Android Studio/jbr/bin/java.exe')
A='{http://schemas.android.com/apk/res/android}';E.register_namespace('android',A)
tree=E.parse(Path.home()/'.codex/duolingo-reference-decoded/AndroidManifest.xml');root=tree.getroot();root.set('package','com.duoaero.originalprobe')
for el in root.iter():
 if el.get(A+'name','').startswith('.'):el.set(A+'name','com.duolingo'+el.get(A+'name'))
 if A+'authorities' in el.attrib:el.set(A+'authorities',el.get(A+'authorities')+'.duoaero.probe')
E.SubElement(root,'uses-sdk',{A+'minSdkVersion':'29',A+'targetSdkVersion':'36'});app=root.find('application');app.set(A+'label','DuoAero original runtime test')
tree.write(W/'AndroidManifest.xml',encoding='utf-8',xml_declaration=True)
def run(args):subprocess.run(list(map(str,args)),check=True)
run([BT/'aapt2.exe','link','-o',W/'resources.apk','--manifest',W/'AndroidManifest.xml','-I',SDK/'platforms/android-36/android.jar','--no-auto-version','--no-resource-deduping','--no-version-vectors','--no-version-transitions',Path.home()/'.codex/duoaero-production-build/resources.zip'])
with zipfile.ZipFile(W/'resources.apk') as res,zipfile.ZipFile(Path.home()/'Downloads/Duolingo_v6.103.5.apk') as base,zipfile.ZipFile(W/'unsigned.apk','w') as out:
 for e in res.infolist():out.writestr(e,res.read(e))
 for e in base.infolist():
  if e.filename.startswith(('assets/','lib/')) or (e.filename.startswith('classes') and e.filename.endswith('.dex')):out.writestr(e,base.read(e))
run([BT/'zipalign.exe','-f','-p','4',W/'unsigned.apk',W/'aligned.apk'])
run([JAVA,'-jar',BT/'lib/apksigner.jar','sign','--ks',R/'build/debug.p12','--ks-pass','pass:android','--out',W/'original-runtime.apk',W/'aligned.apk'])
print(W/'original-runtime.apk')
