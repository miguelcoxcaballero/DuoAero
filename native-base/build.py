from pathlib import Path
import subprocess,zipfile,xml.etree.ElementTree as E,hashlib,json,sys
import os, shutil
from rich_question import choice_blob
from runtime_config import ROOT,HOME,BASE,SMALI,WORK,SDK,BT,JAR,APK,APKTOOL,KEY,java,tool
for d in [WORK/'classes',WORK/'dex']:
 if d.exists():shutil.rmtree(d)
 d.mkdir(parents=True,exist_ok=True)
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
run(tool('aapt2'),'link','-o',WORK/'resources.apk','--manifest',WORK/'AndroidManifest.xml','-I',JAR,'-I',APK,'--rename-manifest-package',package,'--no-auto-version')
source=ROOT/'native-base/src/com/duoaero/nativebase/NativeCourseBridge.java';assert source.is_file()
run(java('javac'),'--release','8','-encoding','UTF-8','-classpath',JAR,'-d',WORK/'classes',source)
run(java('java'),'-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--lib',JAR,'--min-api','29','--output',WORK/'dex',*list((WORK/'classes').rglob('*.class')))
p=SMALI/'smali_classes4/okhttp3/OkHttpClient$Builder.smali';old=p.read_bytes();text=old.decode('utf-8').replace('\r\n','\n');needle='.method public final build()Lokhttp3/OkHttpClient;\n    .locals 1';assert needle in text
patched=text.replace(needle,needle+'\n\n    invoke-static {p0}, Lcom/duoaero/nativebase/NativeCourseBridge;->install(Ljava/lang/Object;)V',1)
try:
 p.write_text(patched,encoding='utf-8')
 run(java('javac'),'-cp',APKTOOL,'-d',WORK,ROOT/'native-base/AssembleDex.java')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali_classes4',WORK/'classes4.dex')
finally:p.write_bytes(old)
run(sys.executable,ROOT/'native-base/extend_math_fonts.py')
run(sys.executable,ROOT/'native-base/path_adapter.py')
with zipfile.ZipFile(WORK/'resources.apk') as res,zipfile.ZipFile(APK) as base,zipfile.ZipFile(WORK/'unsigned.apk','w') as out:
 out.writestr('AndroidManifest.xml',res.read('AndroidManifest.xml'))
 for entry in base.infolist():
  n=entry.filename
  if n.startswith('res/font/duolingosansmath_') and n.endswith('.ttf'):out.writestr(entry,(WORK/'font-overlays'/Path(n).name).read_bytes())
  elif n=='classes4.dex':out.writestr(entry,(WORK/'classes4.dex').read_bytes())
  elif n!='AndroidManifest.xml' and not n.startswith('META-INF/'):out.writestr(entry,base.read(entry))
 out.write(WORK/'dex/classes.dex','classes12.dex')
 out.write(ROOT/'native-base/vendor/notosansmath/OFL.txt','assets/duoaero/licenses/NotoSansMath-OFL.txt')
 # A separate input for the original hardcoded-session loader. The original
 # math reference asset remains unchanged for baseline comparisons.
 lesson=ROOT/'native-base/tests/fixtures/aerospace_lesson.json'
 out.write(lesson,'assets/hardcoded_sessions/duoaero/aerospace_lesson.json')
 bank=json.loads((ROOT/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
 by_id={question['id']:question for question in bank}
 plain_sample=[by_id[c['id']] for c in json.loads(lesson.read_text())['challenges'][:12]]
 sample=plain_sample[:1]+[q for q in bank if q.get('rich_text')]
 sample_ids={q['id'] for q in sample}
 sample.extend(q for q in plain_sample[1:] if q['id'] not in sample_ids)
 assert all(q['type']=='choice' for q in sample) and 10<=len(sample)<=20
 # MathSessionCoordinator starts the original JS sandbox only when the
 # original session type supplies a skill ID (Session.Type.F1). A language
 # GLOBAL_PRACTICE session can render blobs but skips their grader startup.
 rich_session={'id':'duoaero_native_rich_diagnostic','type':'MATH_LESSON','fromLanguage':'en',
  'skillId':'duoaero_aerospace_diagnostic','levelIndex':0,'levelSessionIndex':0,
  'metadata':{'id':'duoaero_native_rich_diagnostic','type':'math_lesson'},
  'challenges':[choice_blob(q) for q in sample]}
 out.writestr('assets/hardcoded_sessions/duoaero/aerospace_rich_lesson.json',json.dumps(rich_session,ensure_ascii=False))
 for source_name,target_name in [('native_course_path_info','path-info'),('native_course_section','section'),('native_lesson_index','lesson-index')]:
  out.write(ROOT/('native-base/tests/fixtures/'+source_name+'.json'),'assets/duoaero/course/'+target_name+'.json')
run(tool('zipalign'),'-f','-p','4',WORK/'unsigned.apk',WORK/'aligned.apk')
run(java('java'),'-jar',BT/'lib/apksigner.jar','sign','--ks',KEY,'--ks-pass','pass:android','--out',WORK/'DuoAero-native-base-test.apk',WORK/'aligned.apk')
print('Original runtime test APK:',WORK/'DuoAero-native-base-test.apk')
