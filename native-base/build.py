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
# Retain original named dependency flows for opt-in synthetic diagnostics.
# The hook records references only; it never changes an emission or result.
flow_source=SMALI/'smali/g9q.smali'
flow_original=flow_source.read_bytes()
flow_text=flow_original.decode('utf-8').replace('\r\n','\n')
flow_anchor='    iput-object p1, p0, Lg9q;->b:Lqdf;'
assert flow_text.count(flow_anchor)==1
package_source=SMALI/'smali/h4t.smali'
package_original=package_source.read_bytes()
package_text=package_original.decode('utf-8').replace('\r\n','\n')
package_anchor='    const-string v2, "com.duolingo"\n\n    invoke-virtual {v1, v2, v12}, Landroid/content/pm/PackageManager;->getPackageInfo(Ljava/lang/String;I)Landroid/content/pm/PackageInfo;'
assert package_text.count(package_anchor)==1
try:
 flow_source.write_text(flow_text.replace(flow_anchor,flow_anchor+'\n\n    invoke-static {p1, p2}, Lcom/duoaero/nativebase/NativeCourseBridge;->recordFlow(Ljava/lang/Object;Ljava/lang/String;)V'),encoding='utf-8')
 # Original app-update metadata must query the identity actually installed.
 package_source.write_text(package_text.replace(package_anchor,package_anchor.replace('"com.duolingo"','"'+package+'"')),encoding='utf-8')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali',WORK/'classes.dex')
finally:
 flow_source.write_bytes(flow_original)
 package_source.write_bytes(package_original)
# The original zero-XP branch starts language onboarding even with an enrolled
# local course. Route that enrollment through the existing home initialization;
# leave XP, completion, grading and view-readiness states untouched.
launch_source=SMALI/'smali_classes3/com/duolingo/splash/LaunchViewModel.smali'
launch_original=launch_source.read_bytes()
launch_text=launch_original.decode('utf-8').replace('\r\n','\n')
launch_anchor='    cmp-long p1, v7, v9\n\n    if-lez p1, :cond_7\n\n    new-instance p1, Lihh;'
assert launch_text.count(launch_anchor)==1
launch_replacement='    cmp-long p1, v7, v9\n\n    if-gtz p1, :duoaero_enrolled\n\n    invoke-static {}, Lcom/duoaero/nativebase/NativeCourseBridge;->hasLocalCourse()Z\n\n    move-result p1\n\n    if-eqz p1, :cond_7\n\n    :duoaero_enrolled\n    new-instance p1, Lihh;'
welcome_source=SMALI/'smali_classes3/vza0.smali'
welcome_original=welcome_source.read_bytes()
welcome_text=welcome_original.decode('utf-8').replace('\r\n','\n')
welcome_anchor='    invoke-static {p1}, Lw9o;->p(Ljava/lang/Object;)V'
assert welcome_text.count(welcome_anchor)==1
welcome_hook='\n\n    invoke-static {}, Lcom/duoaero/nativebase/NativeCourseBridge;->hasLocalCourse()Z\n\n    move-result p1\n\n    if-eqz p1, :duoaero_standard_welcome\n\n    sget-object p1, Lsza0;->f:Lsza0;\n\n    return-object p1\n\n    :duoaero_standard_welcome'
try:
 launch_source.write_text(launch_text.replace(launch_anchor,launch_replacement),encoding='utf-8')
 # The original home independently requests Math onboarding at zero course XP.
 # Aerospace enrollment already supplies its path; no math placement survey is needed.
 welcome_source.write_text(welcome_text.replace(welcome_anchor,welcome_anchor+welcome_hook),encoding='utf-8')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali_classes3',WORK/'classes3.dex')
finally:
 launch_source.write_bytes(launch_original)
 welcome_source.write_bytes(welcome_original)
prompt_source=SMALI/'smali_classes6/qyv.smali'
prompt_original=prompt_source.read_bytes()
prompt_text=prompt_original.decode('utf-8').replace('\r\n','\n')
prompt_anchor='    invoke-static/range {v0 .. v12}, Ljvo;->a(Lcom/duolingo/core/math/models/figure/MathFigureUiState;Lz5q;Lcvo;Lkotlin/jvm/functions/Function0;Lqqh;Lqqh;Lkotlin/jvm/functions/Function0;Ljava/lang/Integer;Ls6p;Lcom/duolingo/feature/math/ui/figure/WebViewInteractionState;Lo18;II)V'
assert prompt_text.count(prompt_anchor)==1
prompt_hook='    invoke-static {v0, v1, v10}, Lcom/duoaero/nativebase/NativeCourseBridge;->scrollPrompt(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;\n\n    move-result-object v1\n\n    check-cast v1, Lz5q;\n\n'
try:
 prompt_source.write_text(prompt_text.replace(prompt_anchor,prompt_hook+prompt_anchor),encoding='utf-8')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali_classes6',WORK/'classes6.dex')
finally:prompt_source.write_bytes(prompt_original)
run(sys.executable,ROOT/'native-base/extend_math_fonts.py')
run(sys.executable,ROOT/'native-base/path_adapter.py')
with zipfile.ZipFile(WORK/'resources.apk') as res,zipfile.ZipFile(APK) as base,zipfile.ZipFile(WORK/'unsigned.apk','w') as out:
 out.writestr('AndroidManifest.xml',res.read('AndroidManifest.xml'))
 for entry in base.infolist():
  n=entry.filename
  if n.startswith('res/font/duolingosansmath_') and n.endswith('.ttf'):out.writestr(entry,(WORK/'font-overlays'/Path(n).name).read_bytes())
  elif n=='classes.dex':out.writestr(entry,(WORK/'classes.dex').read_bytes())
  elif n=='classes3.dex':out.writestr(entry,(WORK/'classes3.dex').read_bytes())
  elif n=='classes4.dex':out.writestr(entry,(WORK/'classes4.dex').read_bytes())
  elif n=='classes6.dex':out.writestr(entry,(WORK/'classes6.dex').read_bytes())
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
