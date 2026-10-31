from pathlib import Path
import subprocess,zipfile,xml.etree.ElementTree as E,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
HOME=Path.home();BASE=HOME/'.codex/duolingo-reference-decoded';SMALI=HOME/'.codex/duoaero-original-patch';WORK=HOME/'.codex/duoaero-native-base'
SDK=HOME/'AppData/Local/Android/Sdk';BT=SDK/'build-tools/35.0.0';JAVA=Path('C:/Program Files/Android/Android Studio/jbr/bin');JAR=SDK/'platforms/android-36/android.jar';APK=HOME/'Downloads/Duolingo_v6.103.5.apk'
for d in [WORK,WORK/'classes',WORK/'dex']:d.mkdir(parents=True,exist_ok=True)
def run(*args):subprocess.run([str(x) for x in args],check=True)
# Preserve original Application, activities, fragments, themes, services and transitions.
A='{http://schemas.android.com/apk/res/android}';E.register_namespace('android',A)
tree=E.parse(BASE/'AndroidManifest.xml');root=tree.getroot();package='com.duoaero.nativebase';root.set('package','com.duolingo')
for el in root.iter():
 for key in ['authorities','permission','readPermission','writePermission','taskAffinity']:
  if A+key in el.attrib:el.set(A+key,el.get(A+key).replace('com.duolingo',package))
 if el.tag in ['permission','uses-permission'] and el.get(A+'name','').startswith('com.duolingo.'):
  el.set(A+'name',el.get(A+'name').replace('com.duolingo',package))
 if A+'authorities' in el.attrib and not el.get(A+'authorities').startswith(package):el.set(A+'authorities',el.get(A+'authorities')+'.duoaero.nativebase')
 if el.get(A+'name','').startswith('.'):el.set(A+'name','com.duolingo'+el.get(A+'name'))
E.SubElement(root,'uses-sdk',{A+'minSdkVersion':'29',A+'targetSdkVersion':'36'})
app=root.find('application');app.set(A+'label','DuoAero original base · test');app.set(A+'debuggable','true')
assert app.get(A+'name')=='com.duolingo.core.DuoApp'
# Do not register the reference service's external app links under the test identity.
for component in app:
 for f in list(component.findall('intent-filter')):
  if any(e.get(A+'name')=='android.intent.category.BROWSABLE' for e in f.findall('category')):component.remove(f)
tree.write(WORK/'AndroidManifest.xml',encoding='utf-8',xml_declaration=True)
run(BT/'aapt2.exe','link','-o',WORK/'resources.apk','--manifest',WORK/'AndroidManifest.xml','-I',JAR,'-I',APK,'--rename-manifest-package',package,'--no-auto-version')
source=ROOT/'native-base/src/com/duoaero/nativebase/NativeCourseBridge.java';source.write_text(source.read_text(encoding='utf-8-sig'),encoding='utf-8')
run(JAVA/'javac.exe','--release','8','-encoding','UTF-8','-classpath',JAR,'-d',WORK/'classes',source)
run(JAVA/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--lib',JAR,'--min-api','29','--output',WORK/'dex',*list((WORK/'classes').rglob('*.class')))
p=SMALI/'smali_classes4/okhttp3/OkHttpClient$Builder.smali';old=p.read_bytes();text=old.decode('utf-8').replace('\r\n','\n');needle='.method public final build()Lokhttp3/OkHttpClient;\n    .locals 1';assert needle in text
patched=text.replace(needle,needle+'\n\n    invoke-static {p0}, Lcom/duoaero/nativebase/NativeCourseBridge;->install(Ljava/lang/Object;)V',1)
try:
 p.write_text(patched,encoding='utf-8')
 run(JAVA/'javac.exe','-cp',HOME/'.codex/apktool_2.12.1.jar','-d',WORK,ROOT/'native-base/AssembleDex.java')
 run(JAVA/'java.exe','-Xmx3g','-cp',str(HOME/'.codex/apktool_2.12.1.jar')+';'+str(WORK),'AssembleDex',SMALI/'smali_classes4',WORK/'classes4.dex')
finally:p.write_bytes(old)
run(sys.executable,ROOT/'native-base/extend_math_fonts.py')
with zipfile.ZipFile(WORK/'resources.apk') as res,zipfile.ZipFile(APK) as base,zipfile.ZipFile(WORK/'unsigned.apk','w') as out:
 out.writestr('AndroidManifest.xml',res.read('AndroidManifest.xml'))
 for entry in base.infolist():
  n=entry.filename
  if n.startswith('res/font/duolingosansmath_') and n.endswith('.ttf'):out.writestr(entry,(WORK/'font-overlays'/Path(n).name).read_bytes())
  elif n=='classes4.dex':out.writestr(entry,(WORK/'classes4.dex').read_bytes())
  elif n!='AndroidManifest.xml' and not n.startswith('META-INF/'):out.writestr(entry,base.read(entry))
 out.write(WORK/'dex/classes.dex','classes12.dex')
 out.write(ROOT/'native-base/vendor/notosansmath/OFL.txt','assets/duoaero/licenses/NotoSansMath-OFL.txt')
run(BT/'zipalign.exe','-f','-p','4',WORK/'unsigned.apk',WORK/'aligned.apk')
run(JAVA/'java.exe','-jar',BT/'lib/apksigner.jar','sign','--ks',ROOT/'build/debug.p12','--ks-pass','pass:android','--out',WORK/'DuoAero-native-base-test.apk',WORK/'aligned.apk')
print('Original runtime test APK:',WORK/'DuoAero-native-base-test.apk')
