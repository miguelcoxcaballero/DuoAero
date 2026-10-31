from pathlib import Path
import os,shutil,subprocess,zipfile
R=Path(__file__).resolve().parents[1];os.chdir(R)
java=Path('C:/Program Files/Android/Android Studio/jbr/bin');sdk=Path(os.environ['LOCALAPPDATA'])/'Android/Sdk';bt=sdk/'build-tools/35.0.0';jar=sdk/'platforms/android-36/android.jar'
base=Path('C:/Users/migue/.codex/duolingo-reference-decoded');out=Path('C:/Users/migue/.codex/duoaero-probe-build')
def run(args):subprocess.run(list(map(str,args)),check=True)
if not out.exists():shutil.copytree(base,out)
(out/'AndroidManifest.xml').write_text('''<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.duoaero" android:versionCode="10100" android:versionName="1.1.0"><uses-sdk android:minSdkVersion="29" android:targetSdkVersion="35"/><application android:label="DuoAero original UI probe" android:theme="@style/DuoAeroOriginalTheme"><activity android:name="com.duoaero.OriginalUiProbe" android:exported="true"><intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter></activity></application></manifest>''')
(out/'res/values/duoaero.xml').write_text('<resources><style name="DuoAeroOriginalTheme" parent="@style/NoActionBarTheme"><item name="isInPreview">true</item><item name="android:windowLightStatusBar">true</item></style></resources>')
for name,style in [('google','GoogleButton'),('solid','SolidButton'),('outline','OutlineButton')]:
 (out/f'res/layout/duoaero_{name}.xml').write_text(f'<com.duolingo.core.design.juicy.ui.JuicyButton xmlns:android="http://schemas.android.com/apk/res/android" android:layout_width="match_parent" android:layout_height="wrap_content" android:layout_marginBottom="16dp" style="@style/{style}"/>')
extra=out/'extra';extra.mkdir(exist_ok=True)
(out/'res/values/duoaero.xml').write_text('<resources><attr name="selected" format="boolean"/><style name="DuoAeroOriginalTheme" parent="@style/NoActionBarTheme"><item name="isInPreview">true</item><item name="android:windowLightStatusBar">true</item></style></resources>')
run([bt/'aapt2.exe','compile',out/'res/values/duoaero.xml','-o',extra])
with zipfile.ZipFile(out/'build/resources.zip') as src,zipfile.ZipFile(out/'probe-resources.zip','w') as dest:
 for entry in src.infolist():
  if entry.filename!='values_duoaero.arsc.flat':dest.writestr(entry,src.read(entry))
 for flat in extra.glob('*.flat'):dest.write(flat,flat.name)
run([bt/'aapt2.exe','link','-o',out/'original-probe-base.apk','--manifest',out/'AndroidManifest.xml','-I',jar,'--no-auto-version','--no-resource-deduping','--no-version-vectors','--no-version-transitions',out/'probe-resources.zip'])
classes=R/'build/probeclasses';dex=R/'build/probedex';classes.mkdir(exist_ok=True);dex.mkdir(exist_ok=True)
source=R/'original/src/com/duoaero/OriginalUiProbe.java';source.write_text(source.read_text(encoding='utf-8-sig'),encoding='utf-8')
run([java/'javac.exe','--release','8','-cp',jar,'-d',classes,source])
run([java/'java.exe','-cp',bt/'lib/d8.jar','com.android.tools.r8.D8','--lib',jar,'--min-api','29','--output',dex,*classes.rglob('*.class')])
with zipfile.ZipFile(out/'original-probe-base.apk') as src,zipfile.ZipFile(R/'build/original-probe-unsigned.apk','w') as dest:
 for entry in src.infolist():dest.writestr(entry.filename,src.read(entry),compress_type=entry.compress_type)
 for original in base.glob('classes*.dex'):dest.write(original,original.name)
 for folder in ['assets','lib']:
  for asset in (base/folder).rglob('*'):
   if asset.is_file():dest.write(asset,asset.relative_to(base).as_posix())
 dest.write(dex/'classes.dex','classes12.dex')
run([bt/'zipalign.exe','-f','-p','4',R/'build/original-probe-unsigned.apk',R/'build/original-probe-aligned.apk'])
run([java/'java.exe','-jar',bt/'lib/apksigner.jar','sign','--ks',R/'build/debug.p12','--ks-pass','pass:android','--out',R/'build/original-probe.apk',R/'build/original-probe-aligned.apk'])
