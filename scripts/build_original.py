"""Build the course controller with the supplied APK's compiled UI and resources.

DUOAERO_DECODED and DUOAERO_RESOURCE_CACHE select an apktool decode and its
aapt2 compiled resource cache. The eleven original DEX files are unchanged.
Signing is a separate operation; this script never reads a release key.
"""
from pathlib import Path
import os, subprocess, zipfile, hashlib, sys

ROOT = Path(__file__).resolve().parents[1]
SDK = Path(os.environ.get('ANDROID_HOME', str(Path.home()/'AppData/Local/Android/Sdk')))
JAVA = Path(os.environ.get('JAVA_HOME', 'C:/Program Files/Android/Android Studio/jbr'))/'bin'
BASE = Path(os.environ.get('DUOAERO_DECODED', str(Path.home()/'.codex/duolingo-reference-decoded')))
CACHE = Path(os.environ.get('DUOAERO_RESOURCE_CACHE', str(Path.home()/'.codex/duoaero-probe-build/build/resources.zip')))
WORK = Path.home()/'.codex/duoaero-production-build'
BT = SDK/'build-tools/35.0.0'
ANDROID = SDK/'platforms/android-36/android.jar'
EXE = '.exe' if os.name == 'nt' else ''
def run(args): subprocess.run([str(a) for a in args], check=True)
run([sys.executable,ROOT/'vendor/inhouse-services-updater/verify.py',ROOT])
for d in (WORK, WORK/'flat', WORK/'classes', WORK/'dex', ROOT/'dist'): d.mkdir(parents=True, exist_ok=True)
# Compile overlays in an ASCII path: aapt2 on Windows mishandles accented paths.
import shutil
for file in (ROOT/'original/res').rglob('*'):
    if file.is_file():
        target=WORK/'res'/file.relative_to(ROOT/'original/res')
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(file,target)
        run([BT/('aapt2'+EXE),'compile',target,'-o',WORK/'flat'])
overlay={p.name:p for p in (WORK/'flat').glob('*.flat')}
with zipfile.ZipFile(CACHE) as src, zipfile.ZipFile(WORK/'resources.zip','w') as dst:
    for entry in src.infolist():
        if entry.filename not in overlay: dst.writestr(entry,src.read(entry))
    for name,path in overlay.items(): dst.write(path,name)
shutil.copyfile(ROOT/'original/AndroidManifest.xml',WORK/'AndroidManifest.xml')
run([BT/('aapt2'+EXE),'link','-o',WORK/'resources.apk','--manifest',WORK/'AndroidManifest.xml','-I',ANDROID,'--no-auto-version','--no-resource-deduping','--no-version-vectors','--no-version-transitions',WORK/'resources.zip'])
deps=Path.home()/'.codex/duoaero-build-deps'
kotlin=Path(os.environ.get('KOTLIN_LIB','C:/Program Files/Android/Android Studio/plugins/Kotlin/kotlinc/lib'))
stdlib=kotlin/'kotlin-stdlib.jar'
classpath=os.pathsep.join(map(str,[ANDROID,deps/'core.jar',stdlib,WORK/'classes']))
updater=ROOT/'vendor/inhouse-services-updater/android'
run([JAVA/('java'+EXE),'-cp',str(kotlin/'*'),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-jvm-target','1.8','-classpath',classpath,'-d',WORK/'classes',updater/'PhotosUpdateInstaller.kt',*updater.glob('*.java')])
sources=list((ROOT/'app/src').rglob('*.java'))+list(updater.glob('*.java'))
run([JAVA/('javac'+EXE),'-encoding','UTF-8','--release','8','-cp',classpath,'-d',WORK/'classes',*sources])
with zipfile.ZipFile(WORK/'controller.jar','w') as outjar:
    for file in (WORK/'classes').rglob('*.class'):outjar.write(file,file.relative_to(WORK/'classes').as_posix())
asmcp=os.pathsep.join(map(str,[deps/'asm.jar',deps/'asm-commons.jar',WORK/'shading']))
run([JAVA/('javac'+EXE),'-cp',asmcp,'-d',WORK/'shading',ROOT/'scripts/ShadeDependencies.java'])
run([JAVA/('java'+EXE),'-cp',asmcp,'ShadeDependencies',WORK/'controller-shaded.jar',WORK/'controller.jar',deps/'core.jar',stdlib])
run([JAVA/('java'+EXE),'-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--lib',ANDROID,'--min-api','29','--output',WORK/'dex',WORK/'controller-shaded.jar'])
entries={}
for folder in ('assets','lib'):
    for p in (BASE/folder).rglob('*'):
        if p.is_file(): entries[p.relative_to(BASE).as_posix()]=p
for p in (ROOT/'app/assets').rglob('*'):
    if p.is_file(): entries['assets/'+p.relative_to(ROOT/'app/assets').as_posix()]=p
for p in (ROOT/'shared').rglob('*'):
    if p.is_file(): entries['assets/shared/'+p.relative_to(ROOT/'shared').as_posix()]=p
original_dex=sorted(BASE.glob('classes*.dex'))
assert len(original_dex)==11,'Unexpected original DEX inventory'
for p in original_dex: entries[p.name]=p
entries['classes12.dex']=WORK/'dex/classes.dex'
with zipfile.ZipFile(WORK/'resources.apk') as src,zipfile.ZipFile(WORK/'unsigned.apk','w') as dst:
    for e in src.infolist(): dst.writestr(e,src.read(e))
    for name,p in entries.items(): dst.write(p,name,compress_type=zipfile.ZIP_DEFLATED if not name.startswith('lib/') else zipfile.ZIP_STORED)
out=ROOT/'dist/DuoAero-1.1.0-unsigned.apk'
run([BT/('zipalign'+EXE),'-f','-p','4',WORK/'unsigned.apk',out])
with zipfile.ZipFile(out) as apk:
    for p in original_dex: assert hashlib.sha256(apk.read(p.name)).digest()==hashlib.sha256(p.read_bytes()).digest()
print('Verified all eleven original DEX files unchanged:',out)
