from pathlib import Path
import subprocess,zipfile,xml.etree.ElementTree as E,hashlib,json,sys
import os, shutil
from rich_question import choice_blob
from course_adapter import session as native_session
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
run(java('javac'),'--release','8','-encoding','UTF-8','-classpath',JAR,'-d',WORK/'classes',*list((ROOT/'native-base/src').rglob('*.java')))
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
latex_source=SMALI/'smali/com/duolingo/data/math/challenge/model/domain/c.smali'
latex_original=latex_source.read_bytes()
latex_text=latex_original.decode('utf-8').replace('\r\n','\n')
latex_anchor='    invoke-virtual {v0, v1, v2}, Lcom/duolingo/data/math/challenge/model/domain/c;->r(Lcom/duolingo/core/math/models/network/OptionalMathEntity;Lcom/duolingo/core/math/models/network/TaggedText;)Lcom/duolingo/core/math/models/network/challenge/MathFigure$AttributedText;'
assert latex_text.count(latex_anchor)==1
latex_hook="""    invoke-static {v0, v1, v2}, Lcom/duoaero/nativebase/NativeCourseBridge;->latexFigure(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v7
    if-eqz v7, :duoaero_original_tagged_figure
    check-cast v7, Lcom/duolingo/core/math/models/network/challenge/MathFigure;
    return-object v7
    :duoaero_original_tagged_figure
"""
bootstrap_source=SMALI/'smali/com/duolingo/core/DuoApp.smali'
bootstrap_original=bootstrap_source.read_bytes()
bootstrap_text=bootstrap_original.decode('utf-8').replace('\r\n','\n')
bootstrap_anchor='    invoke-static {v0}, Lio/sentry/android/core/performance/f;->e(Lcaj;)V\n\n    return-void'
assert bootstrap_text.count(bootstrap_anchor)==1
bootstrap_hook='    invoke-static {v0}, Lio/sentry/android/core/performance/f;->e(Lcaj;)V\n\n    invoke-static {v0}, Lcom/duoaero/nativebase/NativeBootstrap;->start(Landroid/app/Application;)V\n\n    return-void'
bootstrap_entry='.method public final onCreate()V\n    .locals 26\n\n    move-object/from16 v0, p0'
assert bootstrap_text.count(bootstrap_entry)==1
bootstrap_text=bootstrap_text.replace(bootstrap_entry,bootstrap_entry+'\n\n    invoke-static {v0}, Lcom/duoaero/nativebase/NativeBootstrap;->prepare(Landroid/app/Application;)V')
runtime_log_source=SMALI/'smali/w2c.smali'
runtime_log_original=runtime_log_source.read_bytes()
runtime_log_text=runtime_log_original.decode('utf-8').replace('\r\n','\n')
runtime_log_anchor='.method public final f(Lcom/duolingo/core/log/LogOwner;ILjava/lang/String;Ljava/lang/Throwable;)V\n    .locals 1'
assert runtime_log_text.count(runtime_log_anchor)==1
runtime_log_hook=runtime_log_anchor+'\n\n    invoke-static {p1, p2, p4}, Lcom/duoaero/nativebase/NativeCourseBridge;->reportRuntimeFailure(Ljava/lang/Object;ILjava/lang/Throwable;)V'
try:
 runtime_log_source.write_text(runtime_log_text.replace(runtime_log_anchor,runtime_log_hook),encoding='utf-8')
 bootstrap_source.write_text(bootstrap_text.replace(bootstrap_anchor,bootstrap_hook),encoding='utf-8')
 latex_source.write_text(latex_text.replace(latex_anchor,latex_hook+latex_anchor),encoding='utf-8')
 flow_source.write_text(flow_text.replace(flow_anchor,flow_anchor+'\n\n    invoke-static {p1, p2}, Lcom/duoaero/nativebase/NativeCourseBridge;->recordFlow(Ljava/lang/Object;Ljava/lang/String;)V'),encoding='utf-8')
 # Original app-update metadata must query the identity actually installed.
 package_source.write_text(package_text.replace(package_anchor,package_anchor.replace('"com.duolingo"','"'+package+'"')),encoding='utf-8')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali',WORK/'classes.dex')
finally:
 runtime_log_source.write_bytes(runtime_log_original)
 bootstrap_source.write_bytes(bootstrap_original)
 latex_source.write_bytes(latex_original)
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
figure_view_source=SMALI/'smali_classes3/com/duolingo/feature/math/ui/figure/MathFigureView.smali'
figure_view_original=figure_view_source.read_bytes()
figure_view_text=figure_view_original.decode('utf-8').replace('\r\n','\n')
figure_view_anchor='.method public final setFigure(Lcom/duolingo/core/math/models/figure/MathFigureUiState;)V\n    .locals 0'
assert figure_view_text.count(figure_view_anchor)==1
figure_view_hook='\n\n    invoke-static {p0, p1}, Lcom/duoaero/nativebase/NativeCourseBridge;->bindFormulaAccessibility(Landroid/view/View;Ljava/lang/Object;)V'
resume_source=SMALI/'smali_classes3/eo10.smali'
resume_original=resume_source.read_bytes()
resume_text=resume_original.decode('utf-8').replace('\r\n','\n')
resume_anchor='    iput-object p1, p0, Leo10;->a:Lcom/duolingo/data/session/state/PersistedState;'
assert resume_text.count(resume_anchor)==1
resume_hook='    invoke-static {p1, p5}, Lcom/duoaero/nativebase/NativeSessionResume;->stateForSession(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;\n\n    move-result-object p1\n\n    check-cast p1, Lcom/duolingo/data/session/state/PersistedState;\n\n'
try:
 resume_source.write_text(resume_text.replace(resume_anchor,resume_hook+resume_anchor),encoding='utf-8')
 figure_view_source.write_text(figure_view_text.replace(figure_view_anchor,figure_view_anchor+figure_view_hook),encoding='utf-8')
 launch_source.write_text(launch_text.replace(launch_anchor,launch_replacement),encoding='utf-8')
 # The original home independently requests Math onboarding at zero course XP.
 # Aerospace enrollment already supplies its path; no math placement survey is needed.
 welcome_source.write_text(welcome_text.replace(welcome_anchor,welcome_anchor+welcome_hook),encoding='utf-8')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali_classes3',WORK/'classes3.dex')
finally:
 resume_source.write_bytes(resume_original)
 figure_view_source.write_bytes(figure_view_original)
 launch_source.write_bytes(launch_original)
 welcome_source.write_bytes(welcome_original)
prompt_source=SMALI/'smali_classes6/qyv.smali'
prompt_original=prompt_source.read_bytes()
prompt_text=prompt_original.decode('utf-8').replace('\r\n','\n')
prompt_anchor='    invoke-static/range {v0 .. v12}, Ljvo;->a(Lcom/duolingo/core/math/models/figure/MathFigureUiState;Lz5q;Lcvo;Lkotlin/jvm/functions/Function0;Lqqh;Lqqh;Lkotlin/jvm/functions/Function0;Ljava/lang/Integer;Ls6p;Lcom/duolingo/feature/math/ui/figure/WebViewInteractionState;Lo18;II)V'
assert prompt_text.count(prompt_anchor)==1
prompt_hook='    invoke-static {v0, v1, v10}, Lcom/duoaero/nativebase/NativeCourseBridge;->scrollPrompt(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;\n\n    move-result-object v1\n\n    check-cast v1, Lz5q;\n\n'
symbol_source=SMALI/'smali_classes6/com/duolingo/feature/math/challenge/c.smali'
symbol_original=symbol_source.read_bytes()
symbol_text=symbol_original.decode('utf-8').replace('\r\n','\n')
symbol_anchor='    invoke-virtual {p1}, Ljava/lang/Boolean;->booleanValue()Z\n\n    move-result p1'
assert symbol_text.count(symbol_anchor)==1
symbol_hook='''
    iget-object v0, p0, Lcom/duolingo/feature/math/challenge/c;->a:Lcom/duolingo/feature/math/challenge/MathExpressionBuildViewModel;
    invoke-virtual {p1}, Ljava/lang/Boolean;->booleanValue()Z
    move-result v1
    invoke-static {v0, p2, v1}, Lcom/duoaero/nativebase/NativeCourseBridge;->gradeSymbolicExpression(Ljava/lang/Object;Ljava/lang/Object;Z)Ljava/lang/Object;
    move-result-object v0
    if-eqz v0, :duoaero_original_numeric_grade
    return-object v0
    :duoaero_original_numeric_grade
    const/4 v0, 0x6
    const/4 v1, 0x0
'''
accessibility_source=SMALI/'smali_classes6/gvo.smali'
accessibility_original=accessibility_source.read_bytes()
accessibility_text=accessibility_original.decode('utf-8').replace('\r\n','\n')
accessibility_anchor='    invoke-interface {p0}, Lcom/duolingo/core/math/models/figure/MathFigureUiState;->r1()Ljava/lang/String;'
assert accessibility_text.count(accessibility_anchor)==1
accessibility_hook="""    invoke-static {p0}, Lcom/duoaero/nativebase/NativeCourseBridge;->formulaAccessibility(Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v0
    if-eqz v0, :duoaero_original_figure_description
    return-object v0
    :duoaero_original_figure_description
"""
sandbox_source=SMALI/'smali_classes6/e5l.smali'
sandbox_original=sandbox_source.read_bytes()
sandbox_text=sandbox_original.decode('utf-8').replace('\r\n','\n')
sandbox_anchor='    :catch_0\n    move-exception p1'
assert sandbox_text.count(sandbox_anchor)==1
sandbox_hook=sandbox_anchor+'\n\n    invoke-static {p1}, Lcom/duoaero/nativebase/NativeCourseBridge;->reportGradingFailure(Ljava/lang/Throwable;)V'
retry_source=SMALI/'smali_classes6/ky6.smali'
retry_original=retry_source.read_bytes()
retry_text=retry_original.decode('utf-8').replace('\r\n','\n')
retry_anchor='    :goto_1f\n    if-eqz v7, :cond_39'
assert retry_text.count(retry_anchor)==1
retry_hook='    :goto_1f\n    invoke-static {v4, v5, v7}, Lcom/duoaero/nativebase/NativeCourseBridge;->retryOriginalEvaluation(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/String;)Ljava/lang/String;\n    move-result-object v7\n    if-eqz v7, :cond_39'
factory_source=SMALI/'smali_classes6/ip1.smali'
factory_original=factory_source.read_bytes()
factory_text=factory_original.decode('utf-8').replace('\r\n','\n')
factory_anchor='    const-wide/16 v11, 0x3\n\n    invoke-virtual {v5, v11, v12, v7}, Lx4;->get(JLjava/util/concurrent/TimeUnit;)Ljava/lang/Object;'
assert factory_text.count(factory_anchor)==1
factory_hook='    invoke-static {}, Lcom/duoaero/nativebase/NativeCourseBridge;->sandboxStartupTimeoutSeconds()J\n\n    move-result-wide v11\n\n    invoke-virtual {v5, v11, v12, v7}, Lx4;->get(JLjava/util/concurrent/TimeUnit;)Ljava/lang/Object;'
factory_timeout='    :catch_3\n    iget-object v1, v2, Lp5l;->d:Lyto;'
assert factory_text.count(factory_timeout)==1
factory_timeout_hook='    :catch_3\n    invoke-static {}, Lcom/duoaero/nativebase/NativeCourseBridge;->reportSandboxStartupTimeout()V\n    iget-object v1, v2, Lp5l;->d:Lyto;'
bank_source=SMALI/'smali_classes6/n71.smali'
bank_original=bank_source.read_bytes()
bank_text=bank_original.decode('utf-8').replace('\r\n','\n')
bank_anchor='    invoke-static {v14, v3, v3, v9}, Loe7;->p1(Ljava/lang/Iterable;IIZ)Ljava/util/ArrayList;'
assert bank_text.count(bank_anchor)==1
bank_hook='    invoke-static {v1, v10, v3}, Lcom/duoaero/nativebase/NativeCourseBridge;->bankColumns(Ljava/util/List;FI)I\n\n    move-result v3\n\n'
try:
 bank_source.write_text(bank_text.replace(bank_anchor,bank_hook+bank_anchor),encoding='utf-8')
 factory_source.write_text(factory_text.replace(factory_anchor,factory_hook).replace(factory_timeout,factory_timeout_hook),encoding='utf-8')
 retry_source.write_text(retry_text.replace(retry_anchor,retry_hook),encoding='utf-8')
 sandbox_source.write_text(sandbox_text.replace(sandbox_anchor,sandbox_hook),encoding='utf-8')
 accessibility_source.write_text(accessibility_text.replace(accessibility_anchor,accessibility_hook+accessibility_anchor),encoding='utf-8')
 prompt_source.write_text(prompt_text.replace(prompt_anchor,prompt_hook+prompt_anchor),encoding='utf-8')
 symbol_source.write_text(symbol_text.replace(symbol_anchor,symbol_hook+symbol_anchor),encoding='utf-8')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali_classes6',WORK/'classes6.dex')
finally:
 bank_source.write_bytes(bank_original)
 factory_source.write_bytes(factory_original)
 retry_source.write_bytes(retry_original)
 sandbox_source.write_bytes(sandbox_original)
 accessibility_source.write_bytes(accessibility_original)
 prompt_source.write_bytes(prompt_original)
 symbol_source.write_bytes(symbol_original)
# Observe the exception before the original grader maps it to GRADING_ERROR.
# Preserve its error state; never convert an error into a correct answer.
grade_source=SMALI/'smali_classes7/ban.smali'
grade_original=grade_source.read_bytes()
grade_text=grade_original.decode('utf-8').replace('\r\n','\n')
grade_anchor='    :catch_2\n    invoke-interface {v1}, Lao8;->getCoroutineContext()Lpn8;'
assert grade_text.count(grade_anchor)==1
grade_hook='    :catch_2\n    move-exception v2\n    invoke-static {v2}, Lcom/duoaero/nativebase/NativeCourseBridge;->reportGradingFailure(Ljava/lang/Throwable;)V\n    invoke-interface {v1}, Lao8;->getCoroutineContext()Lpn8;'
try:
 grade_source.write_text(grade_text.replace(grade_anchor,grade_hook),encoding='utf-8')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali_classes7',WORK/'classes7.dex')
finally:grade_source.write_bytes(grade_original)
run(sys.executable,ROOT/'native-base/extend_math_fonts.py')
run(sys.executable,ROOT/'native-base/path_adapter.py')
run(sys.executable,ROOT/'native-base/formula_exercises.py')
with zipfile.ZipFile(WORK/'resources.apk') as res,zipfile.ZipFile(APK) as base,zipfile.ZipFile(WORK/'unsigned.apk','w') as out:
 out.writestr('AndroidManifest.xml',res.read('AndroidManifest.xml'))
 for entry in base.infolist():
  n=entry.filename
  if n.startswith('res/font/duolingosansmath_') and n.endswith('.ttf'):out.writestr(entry,(WORK/'font-overlays'/Path(n).name).read_bytes())
  elif n=='classes.dex':out.writestr(entry,(WORK/'classes.dex').read_bytes())
  elif n=='classes3.dex':out.writestr(entry,(WORK/'classes3.dex').read_bytes())
  elif n=='classes4.dex':out.writestr(entry,(WORK/'classes4.dex').read_bytes())
  elif n=='classes6.dex':out.writestr(entry,(WORK/'classes6.dex').read_bytes())
  elif n=='classes7.dex':out.writestr(entry,(WORK/'classes7.dex').read_bytes())
  elif n!='AndroidManifest.xml' and not n.startswith('META-INF/'):out.writestr(entry,base.read(entry))
 out.write(WORK/'dex/classes.dex','classes12.dex')
 if os.environ.get('DUOAERO_STANDALONE')=='1':out.writestr('assets/duoaero/standalone-bootstrap','1')
 out.write(ROOT/'native-base/vendor/notosansmath/OFL.txt','assets/duoaero/licenses/NotoSansMath-OFL.txt')
 # A separate input for the original hardcoded-session loader. The original
 # math reference asset remains unchanged for baseline comparisons.
 lesson=ROOT/'native-base/tests/fixtures/aerospace_lesson.json'
 out.write(lesson,'assets/hardcoded_sessions/duoaero/aerospace_lesson.json')
 out.write(ROOT/'native-base/tests/fixtures/aerospace_formula_lesson.json','assets/hardcoded_sessions/duoaero/aerospace_formula_lesson.json')
 bank=json.loads((ROOT/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
 by_id={question['id']:question for question in bank}
 mixed=[next(q for q in bank if q['type']==kind) for kind in ('multi','matching')]
 mixed.extend(q for q in bank if q['type'] in ('gap','order'))
 mixed.append(next(q for q in bank if q['type']=='matching' and q['id'].startswith('BOOK-V6')))
 out.writestr('assets/hardcoded_sessions/duoaero/aerospace_mixed_lesson.json',json.dumps(native_session(mixed,'duoaero_mixed_diagnostic'),ensure_ascii=False))
 out.writestr('assets/duoaero/mixed-source.json',json.dumps(mixed,ensure_ascii=False))
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
 catalog={}
 lesson_total=0
 for node in json.loads((ROOT/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig')):
  from path_adapter import stable_id
  lesson_total+=len(node['lessons'])
  for position,entry in enumerate(node['lessons']):
   try: adapted=native_session([by_id[i] for i in entry['ids']],entry['id'],stable_id('skill',node['id']))
   except NotImplementedError: continue
   adapted['levelSessionIndex']=position
   catalog[entry['id']]=adapted
 out.writestr('assets/duoaero/course/session-catalog.json',json.dumps(catalog,ensure_ascii=False))
 print('Local original session catalog:',len(catalog),'of',lesson_total,'lessons; runtime navigation and completion require separate acceptance.')
 for source_name,target_name in [('native_course_path_info','path-info'),('native_course_section','section'),('native_lesson_index','lesson-index')]:
  out.write(ROOT/('native-base/tests/fixtures/'+source_name+'.json'),'assets/duoaero/course/'+target_name+'.json')
run(tool('zipalign'),'-f','-p','4',WORK/'unsigned.apk',WORK/'aligned.apk')
run(java('java'),'-jar',BT/'lib/apksigner.jar','sign','--ks',KEY,'--ks-pass','pass:android','--out',WORK/'DuoAero-native-base-test.apk',WORK/'aligned.apk')
print('Original runtime test APK:',WORK/'DuoAero-native-base-test.apk')
