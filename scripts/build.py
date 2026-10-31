"""Build the offline native app with the Android SDK, without Gradle dependencies."""
from pathlib import Path
import os, subprocess, shutil, zipfile
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sdk=Path(os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT') or Path.home()/'AppData/Local/Android/Sdk')
java=Path(os.environ.get('JAVA_HOME') or 'C:/Program Files/Android/Android Studio/jbr')/'bin'
suffix='.exe' if os.name=='nt' else ''
def run(args): subprocess.run([str(x) for x in args],check=True)
def version(p): return tuple(int(x) for x in p.name.replace('android-','').split('.') if x.isdigit())
bt=sorted((sdk/'build-tools').iterdir(),key=version)[-1]
jar=sorted((sdk/'platforms').glob('*/android.jar'),key=lambda p:version(p.parent))[-1]
build=ROOT/'build';dist=ROOT/'dist'
for d in [build,dist,build/'generated',build/'classes',build/'dex']:d.mkdir(exist_ok=True)
run([bt/('aapt2'+suffix),'compile','--dir','app/res','-o',build/'resources.zip'])
run([bt/('aapt2'+suffix),'link','-o',build/'resources.apk','--manifest','app/AndroidManifest.xml','-I',jar,'--java',build/'generated','-A','app/assets','-0','mp3','-0','otf',build/'resources.zip'])
sources=list((ROOT/'app/src').rglob('*.java'))+list((build/'generated').rglob('*.java'))
run([java/('javac'+suffix),'-encoding','UTF-8','--release','8','-classpath',jar,'-d',build/'classes',*sources])
classes=list((build/'classes').rglob('*.class'))
run([java/('java'+suffix),'-cp',bt/'lib/d8.jar','com.android.tools.r8.D8','--lib',jar,'--min-api','26','--output',build/'dex',*classes])
with zipfile.ZipFile(build/'resources.apk') as source, zipfile.ZipFile(build/'unsigned.apk','w') as dest:
 for entry in source.infolist(): dest.writestr(entry.filename,source.read(entry),compress_type=entry.compress_type)
with zipfile.ZipFile(build/'unsigned.apk','a') as z:
 for p in (build/'dex').glob('*.dex'):z.write(p,p.name)
out=dist/'DuoAero-1.0.0-unsigned.apk'
run([bt/('zipalign'+suffix),'-f','-p','4',build/'unsigned.apk',out])
print(out)

