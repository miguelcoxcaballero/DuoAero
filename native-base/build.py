from pathlib import Path
import subprocess,zipfile,xml.etree.ElementTree as E,hashlib,json,sys,copy
import os, shutil
from rich_question import choice_blob,content
from math_notation import parts as notation_parts
from course_adapter import session as native_session, lesson_questions
from runtime_config import ROOT,HOME,BASE,SMALI,WORK,SDK,BT,JAR,APK,APKTOOL,KEY,java,tool
from build_updater import build as build_updater
from resource_extension import updater_paths, launcher_mascot, scene_mascot, mood_scenes, MOOD_SCENES, MASCOT_PATH, SCENE_MASCOT_PATH
from branding import rebrand_table, wordmark_xml, animation_overlays, mascot_drawables, LOGO_PATH
updater=build_updater()
for d in [WORK/'classes',WORK/'dex']:
 if d.exists():shutil.rmtree(d)
 d.mkdir(parents=True,exist_ok=True)
def run(*args):subprocess.run([str(x) for x in args],check=True)
# Preserve original Application, activities, fragments, themes, services and transitions.
A='{http://schemas.android.com/apk/res/android}';E.register_namespace('android',A)
tree=E.parse(BASE/'AndroidManifest.xml');root=tree.getroot();package=os.environ.get('DUOAERO_PACKAGE','com.duoaero.nativebase');root.set('package','com.duolingo')
if package not in ('com.duoaero.nativebase','com.duoaero'):raise ValueError('Unsupported APK identity')
production=package=='com.duoaero'
if production:
 version=os.environ['DUOAERO_VERSION'];version_code=int(os.environ['DUOAERO_VERSION_CODE'])
 if not __import__('re').fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',version) or version_code<=10200:raise ValueError('Production version must advance the published APK')
 root.set(A+'versionName',version);root.set(A+'versionCode',str(version_code))
else:
 # apktool stores original versions in apktool.yml, not its decoded manifest.
 # Give the isolated test identity explicit metadata for updater host checks.
 root.set(A+'versionName','0.0.0-native-test');root.set(A+'versionCode','1')
for el in root.iter():
 for key in ['authorities','permission','readPermission','writePermission','taskAffinity']:
  if A+key in el.attrib:el.set(A+key,el.get(A+key).replace('com.duolingo',package))
 if el.tag in ['permission','uses-permission'] and el.get(A+'name','').startswith('com.duolingo.'):
  el.set(A+'name',el.get(A+'name').replace('com.duolingo',package))
 if A+'authorities' in el.attrib and not el.get(A+'authorities').startswith(package):el.set(A+'authorities',el.get(A+'authorities')+'.duoaero.nativebase')
 if el.get(A+'name','').startswith('.'):el.set(A+'name','com.duolingo'+el.get(A+'name'))
E.SubElement(root,'uses-sdk',{A+'minSdkVersion':'29',A+'targetSdkVersion':'36'})
app=root.find('application');app_label='DuoAero' if production else 'DuoAero original base · test';app.set(A+'label',app_label);app.set(A+'debuggable','false' if production else 'true')
# The source APK opts out of resizing, which lets Samsung letterbox it on tall
# phones. Keep the original portrait layouts but allow the full window bounds.
app.set(A+'resizeableActivity','true')
for element in [app,*app.findall('activity')]:
 element.set(A+'resizeableActivity','true')
 for attribute in ('maxAspectRatio','minAspectRatio'):
  element.attrib.pop(A+attribute,None)
 for metadata in list(element.findall('meta-data')):
  if metadata.get(A+'name') in ('android.max_aspect','android.min_aspect'):
   element.remove(metadata)
app.set(A+'icon','@mipmap/ic_launcher')
assert app.get(A+'name')=='com.duolingo.core.DuoApp'
for component in app:
 if any(any(category.get(A+'name')=='android.intent.category.LAUNCHER' for category in intent.findall('category')) for intent in component.findall('intent-filter')):
  # Activity aliases override the application label, including the original
  # alternate launcher identities. Keep their routing and show the course name.
  component.set(A+'label',app_label)
  component.set(A+'icon','@mipmap/ic_launcher')
# Do not register the reference service's external app links under the test identity.
for component in app:
 for f in list(component.findall('intent-filter')):
  if any(e.get(A+'name')=='android.intent.category.BROWSABLE' for e in f.findall('category')):component.remove(f)
E.SubElement(root,'uses-permission',{A+'name':'android.permission.REQUEST_INSTALL_PACKAGES'})
callback=E.SubElement(app,'activity',{A+'name':'com.duoaero.nativebase.NativeOAuthCallbackActivity',A+'exported':'true' if production else 'false',A+'theme':'@android:style/Theme.Material.Light.NoActionBar'})
if production:
 oauth=E.SubElement(callback,'intent-filter')
 E.SubElement(oauth,'action',{A+'name':'android.intent.action.VIEW'})
 for category in ('DEFAULT','BROWSABLE'):E.SubElement(oauth,'category',{A+'name':'android.intent.category.'+category})
 E.SubElement(oauth,'data',{A+'scheme':'com.duoaero'})
for activity in ('UpdateActivity','InstallActivity'):
 E.SubElement(app,'activity',{A+'name':'com.inhouse.services.updater.'+activity,A+'exported':'false',A+'theme':'@android:style/Theme.Material.Light.NoActionBar'})
E.SubElement(app,'receiver',{A+'name':'com.inhouse.services.updater.InstallReceiver',A+'exported':'false'})
provider=E.SubElement(app,'provider',{A+'name':'com.inhouse.services.updater.UpdateFileProvider',A+'authorities':package+'.update-provider',A+'exported':'false',A+'grantUriPermissions':'true'})
E.SubElement(provider,'meta-data',{A+'name':'android.support.FILE_PROVIDER_PATHS',A+'resource':'@xml/inhouse_update_paths'})
tree.write(WORK/'AndroidManifest.xml',encoding='utf-8',xml_declaration=True)
def extended_scene_table(table):
 table,_=updater_paths(table)
 table,_=scene_mascot(table)
 return mood_scenes(table)[0]
with zipfile.ZipFile(APK) as base,zipfile.ZipFile(WORK/'resource-reference.apk','w') as reference:
 for entry in base.infolist():
  reference.writestr(entry,extended_scene_table(base.read(entry)) if entry.filename=='resources.arsc' else base.read(entry))
 reference.write(updater/'inhouse_update_paths.xml','res/xml/inhouse_update_paths.xml')
 reference.write(ROOT/'app/assets/mascot/welcome.png',SCENE_MASCOT_PATH)
 for mood,source in MOOD_SCENES.items():reference.write(ROOT/'app/assets/mascot'/source,'res/drawable/duoaero_scene_'+mood+'.png')
run(tool('aapt2'),'link','-o',WORK/'resources.apk','--manifest',WORK/'AndroidManifest.xml','-I',JAR,'-I',WORK/'resource-reference.apk','--rename-manifest-package',package,'--no-auto-version')
# Keep Snoopy's close-up inside Android's adaptive circular safe zone.
launcher_res=WORK/'launcher-res/mipmap-anydpi/duoaero_launcher.xml'
launcher_res.parent.mkdir(parents=True,exist_ok=True)
launcher_res.write_text('<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android"><background android:drawable="@android:color/white"/><foreground><inset android:drawable="@drawable/ic_launcher_foreground" android:inset="17%"/></foreground></adaptive-icon>')
run(tool('aapt2'),'compile',launcher_res,'-o',WORK/'launcher-res.zip')
wordmark_res=WORK/'launcher-res/drawable/duoaero_wordmark.xml'
wordmark_res.parent.mkdir(parents=True,exist_ok=True)
wordmark_res.write_text(wordmark_xml(BASE/'res/font/duolingosans_bold.otf'))
run(tool('aapt2'),'compile',wordmark_res,'-o',WORK/'wordmark-res.zip')
with zipfile.ZipFile(APK) as original:
 mascot_paths,mascot_xml,mascot_sizes=mascot_drawables(BASE,original.read('resources.arsc'))
mascot_res=WORK/'mascot-res'
if mascot_res.exists():shutil.rmtree(mascot_res)
for path,xml in mascot_xml.items():
 destination=mascot_res/path.removeprefix('res/');destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(xml)
run(tool('aapt2'),'compile','--dir',mascot_res,'-o',WORK/'mascot-res.zip')
run(tool('aapt2'),'link','-o',WORK/'launcher.apk','--manifest',WORK/'AndroidManifest.xml','-I',JAR,'-I',WORK/'resource-reference.apk','--no-auto-version','-R',WORK/'launcher-res.zip')
with zipfile.ZipFile(WORK/'launcher.apk') as launcher:
 launcher_xml=launcher.read(next(n for n in launcher.namelist() if n.endswith('/duoaero_launcher.xml')))
run(tool('aapt2'),'link','-o',WORK/'wordmark.apk','--manifest',WORK/'AndroidManifest.xml','-I',JAR,'-I',WORK/'resource-reference.apk','--no-auto-version','-R',WORK/'wordmark-res.zip','-R',WORK/'mascot-res.zip')
with zipfile.ZipFile(WORK/'wordmark.apk') as wordmark:
 wordmark_xml_bytes=wordmark.read(LOGO_PATH)
 mascot_xml_bytes={path:wordmark.read(path) for path in mascot_xml}
source=ROOT/'native-base/src/com/duoaero/nativebase/NativeCourseBridge.java';assert source.is_file()
run(java('javac'),'--release','8','-encoding','UTF-8','-classpath',str(JAR)+os.pathsep+str(updater/'updater-shaded.jar'),'-d',WORK/'classes',*list((ROOT/'native-base/src').rglob('*.java')))
run(java('java'),'-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--lib',JAR,'--min-api','29','--output',WORK/'dex',*list((WORK/'classes').rglob('*.class')))
p=SMALI/'smali_classes4/okhttp3/OkHttpClient$Builder.smali';old=p.read_bytes();text=old.decode('utf-8').replace('\r\n','\n');needle='.method public final build()Lokhttp3/OkHttpClient;\n    .locals 1';assert needle in text
patched=text.replace(needle,needle+'\n\n    invoke-static {p0}, Lcom/duoaero/nativebase/NativeCourseBridge;->install(Ljava/lang/Object;)V',1)
# R8 specialized ContextualFlowRow's vertical alignment to Top and ignored
# its parameter. Restore the argument when supplied, preserving Top for all
# original callers that pass null. The inline gap supplies CenterVertically.
flow_row_source=SMALI/'smali_classes4/iz0.smali'
flow_row_original=flow_row_source.read_bytes()
flow_row_text=flow_row_original.decode('utf-8').replace('\r\n','\n')
flow_row_start=flow_row_text.index('.method public static final t(ILz5q;Lfv1;Ljv1;Llj0;IILhl8;Luv7;Lo18;II)V')
flow_row_end=flow_row_text.index('.end method',flow_row_start)
flow_row_method=flow_row_text[flow_row_start:flow_row_end]
flow_row_anchor='    sget-object v15, Lb9z;->k:Ln73;'
assert flow_row_method.count(flow_row_anchor)==1
flow_row_hook=flow_row_anchor+'''\n    if-eqz p4, :duoaero_flow_default_alignment
    move-object/from16 v15, p4
    :duoaero_flow_default_alignment'''
flow_row_text=flow_row_text[:flow_row_start]+flow_row_method.replace(flow_row_anchor,flow_row_hook)+flow_row_text[flow_row_end:]
try:
 p.write_text(patched,encoding='utf-8')
 flow_row_source.write_text(flow_row_text,encoding='utf-8')
 run(java('javac'),'-cp',APKTOOL,'-d',WORK,ROOT/'native-base/AssembleDex.java')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali_classes4',WORK/'classes4.dex')
finally:
 p.write_bytes(old)
 flow_row_source.write_bytes(flow_row_original)
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
web_process_source=SMALI/'smali/vy.smali'
web_process_original=web_process_source.read_bytes()
web_process_text=web_process_original.decode('utf-8').replace('\r\n','\n')
web_process_anchor='    const-string v0, "com.duolingo"\n\n    invoke-static {p0, v0}, Lszk;->i(Ljava/lang/Object;Ljava/lang/Object;)Z'
assert web_process_text.count(web_process_anchor)==1
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
 # The original secondary-process WebView suffix includes the PID. Recognize
 # our actual main process so OAuth storage survives a process restart.
 web_process_source.write_text(web_process_text.replace(web_process_anchor,web_process_anchor.replace('"com.duolingo"','"'+package+'"')),encoding='utf-8')
 runtime_log_source.write_text(runtime_log_text.replace(runtime_log_anchor,runtime_log_hook),encoding='utf-8')
 bootstrap_source.write_text(bootstrap_text.replace(bootstrap_anchor,bootstrap_hook),encoding='utf-8')
 latex_source.write_text(latex_text.replace(latex_anchor,latex_hook+latex_anchor),encoding='utf-8')
 flow_source.write_text(flow_text.replace(flow_anchor,flow_anchor+'\n\n    invoke-static {p1, p2}, Lcom/duoaero/nativebase/NativeCourseBridge;->recordFlow(Ljava/lang/Object;Ljava/lang/String;)V'),encoding='utf-8')
 # Original app-update metadata must query the identity actually installed.
 package_source.write_text(package_text.replace(package_anchor,package_anchor.replace('"com.duolingo"','"'+package+'"')),encoding='utf-8')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali',WORK/'classes.dex')
finally:
 web_process_source.write_bytes(web_process_original)
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
figure_view_hook='''

    invoke-static {p0, p1}, Lcom/duoaero/nativebase/NativeCourseBridge;->fitMatchFigure(Landroid/view/View;Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object p1
    check-cast p1, Lcom/duolingo/core/math/models/figure/MathFigureUiState;
    invoke-static {p0, p1}, Lcom/duoaero/nativebase/NativeCourseBridge;->bindFormulaAccessibility(Landroid/view/View;Ljava/lang/Object;)V'''
resume_source=SMALI/'smali_classes3/eo10.smali'
unit_header_source=SMALI/'smali_classes3/hlt.smali'
unit_header_original=unit_header_source.read_bytes()
unit_header_text=unit_header_original.decode('utf-8').replace('\r\n','\n')
unit_header_anchor='    iput-object p4, p0, Lhlt;->d:Ltt80;'
assert unit_header_text.count(unit_header_anchor)==1
unit_header_hook='    invoke-static {p2, p3, p4}, Lcom/duoaero/nativebase/NativeCourseBridge;->pathHeaderText(Ljava/lang/Object;Ljava/lang/String;Ljava/lang/Object;)Ljava/lang/Object;\n\n    move-result-object p4\n\n    check-cast p4, Ltt80;\n\n'
profile_inputs_source=SMALI/'smali_classes3/g6w.smali'
profile_inputs_original=profile_inputs_source.read_bytes()
profile_inputs_text=profile_inputs_original.decode('utf-8').replace('\r\n','\n')
profile_inputs_anchor='    invoke-static {v0, v1, v2}, Lohf;->n([Lsnw;Lfrh;I)Lohf;'
assert profile_inputs_text.count(profile_inputs_anchor)==1
resume_original=resume_source.read_bytes()
resume_text=resume_original.decode('utf-8').replace('\r\n','\n')
resume_anchor='    iput-object p1, p0, Leo10;->a:Lcom/duolingo/data/session/state/PersistedState;'
assert resume_text.count(resume_anchor)==1
resume_hook='    invoke-static {p1, p5}, Lcom/duoaero/nativebase/NativeSessionResume;->stateForSession(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;\n\n    move-result-object p1\n\n    check-cast p1, Lcom/duolingo/data/session/state/PersistedState;\n\n'
tip_source=SMALI/'smali_classes3/pqm.smali'
tip_original=tip_source.read_bytes();tip_text=tip_original.decode('utf-8').replace('\r\n','\n')
tip_anchor='    sget-object v0, Lcom/duolingo/core/session/buttons/ChallengeButton;->TIP:Lcom/duolingo/core/session/buttons/ChallengeButton;'
assert tip_text.count(tip_anchor)==1
submit_source=SMALI/'smali_classes3/ll.smali'
submit_original=submit_source.read_bytes();submit_text=submit_original.decode('utf-8').replace('\r\n','\n')
submit_anchor='    invoke-virtual {v13, v11}, Lcom/duolingo/session/challenges/ElementFragment;->H(Lnha0;)Lcom/duolingo/core/session/FragmentGuess;\n\n    move-result-object v0'
assert submit_text.count(submit_anchor)==1
submit_hook=submit_anchor+'\n\n    invoke-static {v13, v0}, Lcom/duoaero/nativebase/NativeCourseBridge;->formulaHintGuess(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;\n\n    move-result-object v0\n\n    check-cast v0, Lcom/duolingo/core/session/FragmentGuess;'
try:
 tip_source.write_text(tip_text.replace(tip_anchor,'    invoke-static {}, Lcom/duoaero/nativebase/NativeCourseBridge;->formulaTipOpened()V\n\n'+tip_anchor),encoding='utf-8')
 submit_source.write_text(submit_text.replace(submit_anchor,submit_hook),encoding='utf-8')
 unit_header_source.write_text(unit_header_text.replace(unit_header_anchor,unit_header_hook+unit_header_anchor),encoding='utf-8')
 profile_inputs_source.write_text(profile_inputs_text.replace(profile_inputs_anchor,'    invoke-static {v0}, Lcom/duoaero/nativebase/NativeCourseBridge;->recordProfileInputs([Ljava/lang/Object;)V\n\n'+profile_inputs_anchor),encoding='utf-8')
 resume_source.write_text(resume_text.replace(resume_anchor,resume_hook+resume_anchor),encoding='utf-8')
 figure_view_source.write_text(figure_view_text.replace(figure_view_anchor,figure_view_anchor+figure_view_hook),encoding='utf-8')
 launch_source.write_text(launch_text.replace(launch_anchor,launch_replacement),encoding='utf-8')
 # The original home independently requests Math onboarding at zero course XP.
 # Aerospace enrollment already supplies its path; no math placement survey is needed.
 welcome_source.write_text(welcome_text.replace(welcome_anchor,welcome_anchor+welcome_hook),encoding='utf-8')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali_classes3',WORK/'classes3.dex')
finally:
 tip_source.write_bytes(tip_original)
 submit_source.write_bytes(submit_original)
 unit_header_source.write_bytes(unit_header_original)
 profile_inputs_source.write_bytes(profile_inputs_original)
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
tabs_source=SMALI/'smali_classes6/qu80.smali'
tabs_original=tabs_source.read_bytes()
tabs_text=tabs_original.decode('utf-8').replace('\r\n','\n')
tabs_guard='    if-gt v3, v7, :cond_19\n\n    if-ge v7, v2, :cond_19'
assert tabs_text.count(tabs_guard)==1
# The original selector assumes every course has two or three tabs. This
# course currently has one real midterm; do not invent a second tab.
tabs_replacement='''    if-le v3, v7, :duoaero_tab_count_valid
    invoke-static {}, Lcom/duoaero/nativebase/NativeCourseBridge;->hasLocalCourse()Z
    move-result v8
    if-eqz v8, :cond_19
    if-ne v7, v15, :cond_19
    :duoaero_tab_count_valid
    if-ge v7, v2, :cond_19'''
picker_source=SMALI/'smali_classes6/com/duolingo/feature/math/section/MathSectionPickerView.smali'
picker_original=picker_source.read_bytes()
picker_text=picker_original.decode('utf-8').replace('\r\n','\n')
picker_anchor='.method public final setSectionPickerTitle(Ljava/lang/String;)V\n    .locals 0'
assert picker_text.count(picker_anchor)==1
picker_hook='''.method public final setSectionPickerTitle(Ljava/lang/String;)V
    .locals 1
    invoke-static {}, Lcom/duoaero/nativebase/NativeCourseBridge;->hasLocalCourse()Z
    move-result v0
    if-eqz v0, :duoaero_original_picker_title
    const-string p1, "DuoAero"
    :duoaero_original_picker_title'''
profile_image_source=SMALI/'smali_classes6/oup.smali'
profile_image_original=profile_image_source.read_bytes()
profile_image_text=profile_image_original.decode('utf-8').replace('\r\n','\n')
# This is the actual drawable passed to Compose's painterResource in the
# profile-completion card. The h4w score value is a count, not a resource ID.
profile_image_anchor='    const v4, 0x7f0826dc\n\n    invoke-static {v4, v10, v3}, Ly6o;->m(ILo18;I)La8t;'
assert profile_image_text.count(profile_image_anchor)==1
profile_image_hook='    const v4, 0x7f0826dc\n\n    invoke-static {v4}, Lcom/duoaero/nativebase/NativeProfileDrawable;->supported(I)I\n\n    move-result v4\n\n    invoke-static {v4, v10, v3}, Ly6o;->m(ILo18;I)La8t;'
token_touch_source=SMALI/'smali_classes6/kp3.smali'
token_touch_original=token_touch_source.read_bytes()
token_touch_text=token_touch_original.decode('utf-8').replace('\r\n','\n')
token_touch_anchor='    invoke-virtual {v0, v2}, Lcom/duolingo/feature/math/ui/figure/MathFigureView;->setFigure(Lcom/duolingo/core/math/models/figure/MathFigureUiState;)V'
assert token_touch_text.count(token_touch_anchor)==1
# The original token is an Android card containing a MathFigureView. Its
# embedded figure can consume a fast pointer sequence before the card sees
# it. The original figure supports touch passthrough; enable it only for this
# local course so both tapping and the parent drag controller receive input.
token_touch_hook=token_touch_anchor+'''

    invoke-static {}, Lcom/duoaero/nativebase/NativeCourseBridge;->hasLocalCourse()Z
    move-result v2
    if-eqz v2, :duoaero_token_touch_done
    invoke-virtual {v0}, Landroid/view/View;->getImportantForAccessibility()I
    move-result v3
    invoke-virtual {v0, v2}, Lcom/duolingo/feature/math/ui/figure/MathFigureView;->setTouchPassthrough(Z)V
    invoke-virtual {v0, v3}, Landroid/view/View;->setImportantForAccessibility(I)V
    :duoaero_token_touch_done'''
try:
 token_touch_source.write_text(token_touch_text.replace(token_touch_anchor,token_touch_hook),encoding='utf-8')
 profile_image_source.write_text(profile_image_text.replace(profile_image_anchor,profile_image_hook),encoding='utf-8')
 picker_source.write_text(picker_text.replace(picker_anchor,picker_hook),encoding='utf-8')
 tabs_source.write_text(tabs_text.replace(tabs_guard,tabs_replacement),encoding='utf-8')
 bank_source.write_text(bank_text.replace(bank_anchor,bank_hook+bank_anchor),encoding='utf-8')
 factory_source.write_text(factory_text.replace(factory_anchor,factory_hook).replace(factory_timeout,factory_timeout_hook),encoding='utf-8')
 retry_source.write_text(retry_text.replace(retry_anchor,retry_hook),encoding='utf-8')
 sandbox_source.write_text(sandbox_text.replace(sandbox_anchor,sandbox_hook),encoding='utf-8')
 accessibility_source.write_text(accessibility_text.replace(accessibility_anchor,accessibility_hook+accessibility_anchor),encoding='utf-8')
 prompt_source.write_text(prompt_text.replace(prompt_anchor,prompt_hook+prompt_anchor),encoding='utf-8')
 symbol_source.write_text(symbol_text.replace(symbol_anchor,symbol_hook+symbol_anchor),encoding='utf-8')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali_classes6',WORK/'classes6.dex')
finally:
 token_touch_source.write_bytes(token_touch_original)
 profile_image_source.write_bytes(profile_image_original)
 picker_source.write_bytes(picker_original)
 tabs_source.write_bytes(tabs_original)
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
settings_source=SMALI/'smali_classes7/com/duolingo/settings/main/c.smali'
settings_original=settings_source.read_bytes()
settings_text=settings_original.decode('utf-8').replace('\r\n','\n')
settings_start=settings_text.index('.method public static final j(Lc020;Lqqh;Lo18;I)V')
settings_end=settings_text.index('.end method',settings_start)
settings_method=settings_text[settings_start:settings_end]
settings_anchor='    invoke-static {}, Lt18;->d()Z'
assert settings_method.count(settings_anchor)==2
settings_position=settings_start+settings_method.rindex(settings_anchor)
settings_text=settings_text[:settings_position]+'    invoke-static {v14}, Lcom/duoaero/nativebase/NativeUpdateHost;->settingsRow(Ljava/lang/Object;)V\n\n'+settings_text[settings_position:]
logout_anchor='    const-string v8, "signOutButton"'
assert settings_text.count(logout_anchor)==1
settings_text=settings_text.replace(logout_anchor,logout_anchor+'\n\n    invoke-static {v9}, Lcom/duoaero/nativebase/NativeGoogleHost;->logoutHandler(Ljava/lang/Object;)Ljava/lang/Object;\n\n    move-result-object v9\n\n    check-cast v9, Lkotlin/jvm/functions/Function0;')
inline_source=SMALI/'smali_classes7/fyd.smali'
inline_original=inline_source.read_bytes()
inline_text=inline_original.decode('utf-8').replace('\r\n','\n')
inline_prompt='    invoke-static/range {v8 .. v20}, Ljvo;->a(Lcom/duolingo/core/math/models/figure/MathFigureUiState;Lz5q;Lcvo;Lkotlin/jvm/functions/Function0;Lqqh;Lqqh;Lkotlin/jvm/functions/Function0;Ljava/lang/Integer;Ls6p;Lcom/duolingo/feature/math/ui/figure/WebViewInteractionState;Lo18;II)V'
inline_slots='    invoke-static/range {v16 .. v26}, Lfz0;->d(Ljava/util/List;Lqqh;Lqqh;ZZLz5q;FZLs6p;Lo18;I)V'
assert inline_text.count(inline_prompt)==inline_text.count(inline_slots)==1
assert inline_text.count('    .locals 32')==1
inline_text=inline_text.replace('    .locals 32','    .locals 34')
inline_begin="""    move-object/from16 v33, v8
    invoke-static {v8}, Lcom/duoaero/nativebase/NativeInlineGap;->isGap(Ljava/lang/Object;)Z
    move-result v9
    if-eqz v9, :duoaero_not_gap
    const/16 v32, 0x2
    goto :duoaero_gap_figure_done
    :duoaero_not_gap
    move-object/from16 v9, v18
    invoke-static {v8, v9}, Lcom/duoaero/nativebase/NativeInlineFormula;->begin(Ljava/lang/Object;Ljava/lang/Object;)Z
    move-result v32
    const/4 v9, 0x0
"""
inline_text=inline_text.replace(inline_prompt,inline_begin+inline_prompt+"\n    :duoaero_gap_figure_done\n")
inline_slot_modifier="""    move/from16 v0, v32
    if-eqz v0, :duoaero_original_slot_width
    sget-object v0, Lw5q;->a:Lw5q;
    move-object/from16 v21, v0
    :duoaero_original_slot_width
"""
inline_gap="""    move/from16 v0, v32
    const/4 v1, 0x2
    if-ne v0, v1, :duoaero_regular_slots
    move-object/from16 v15, v33
    invoke-static/range {v15 .. v26}, Lcom/duoaero/nativebase/NativeInlineGap;->render(Ljava/lang/Object;Ljava/util/List;Ljava/lang/Object;Ljava/lang/Object;ZZLjava/lang/Object;FZLjava/lang/Object;Ljava/lang/Object;I)V
    goto :duoaero_slots_done
    :duoaero_regular_slots
"""
inline_text=inline_text.replace(inline_slots,inline_gap+inline_slot_modifier+inline_slots+"\n    move/from16 v0, v32\n    invoke-static {v0, v11}, Lcom/duoaero/nativebase/NativeInlineFormula;->end(ZLjava/lang/Object;)V\n    :duoaero_slots_done\n")
chest_source=SMALI/'smali_classes7/zit.smali'
chest_original=chest_source.read_bytes()
chest_text=chest_original.decode('utf-8').replace('\r\n','\n')
chest_anchor='.method public final G0(Lcom/duolingo/core/rewards/RewardsServiceReward;ZLtl8;)Ljava/lang/Object;\n    .locals 25'
assert chest_text.count(chest_anchor)==1
chest_hook="""
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    invoke-static {v0, v1}, Lcom/duoaero/nativebase/NativeChestRewards;->claim(Ljava/lang/Object;Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :duoaero_original_chest_claim
    sget-object v0, Lxv80;->a:Lxv80;
    return-object v0
    :duoaero_original_chest_claim
"""
chest_text=chest_text.replace(chest_anchor,chest_anchor+'\n'+chest_hook)
try:
 chest_source.write_text(chest_text,encoding='utf-8')
 inline_source.write_text(inline_text,encoding='utf-8')
 settings_source.write_text(settings_text,encoding='utf-8')
 grade_source.write_text(grade_text.replace(grade_anchor,grade_hook),encoding='utf-8')
 run(java('java'),'-Xmx3g','-cp',str(APKTOOL)+os.pathsep+str(WORK),'AssembleDex',SMALI/'smali_classes7',WORK/'classes7.dex')
finally:
 chest_source.write_bytes(chest_original)
 inline_source.write_bytes(inline_original)
 grade_source.write_bytes(grade_original)
 settings_source.write_bytes(settings_original)
run(sys.executable,ROOT/'native-base/extend_math_fonts.py')
run(sys.executable,ROOT/'native-base/path_adapter.py')
run(sys.executable,ROOT/'native-base/formula_exercises.py')
with zipfile.ZipFile(WORK/'resources.apk') as res,zipfile.ZipFile(APK) as base,zipfile.ZipFile(WORK/'unsigned.apk','w') as out:
 animation_files,animation_report=animation_overlays(base,(ROOT/'app/assets/mascot/welcome.png').read_bytes())
 (WORK/'mascot-report.json').write_text(json.dumps(animation_report,indent=2)+'\n')
 out.writestr('AndroidManifest.xml',res.read('AndroidManifest.xml'))
 for entry in base.infolist():
  n=entry.filename
  if n=='resources.arsc':
   table,resource_id=updater_paths(base.read(entry))
   table,scene_id=scene_mascot(table)
   table,mood_ids=mood_scenes(table)
   assert resource_id==0x7f160016
   branded,branding_report=rebrand_table(launcher_mascot(table),mascot_paths)
   (WORK/'branding-report.json').write_text(json.dumps(branding_report,indent=2)+'\n')
   out.writestr(entry,branded)
  elif n in animation_files:out.writestr(entry,animation_files[n])
  elif n=='res/mipmap-anydpi-v21/ic_launcher.xml':out.writestr(entry,launcher_xml)
  elif n.startswith('res/font/duolingosansmath_') and n.endswith('.ttf'):out.writestr(entry,(WORK/'font-overlays'/Path(n).name).read_bytes())
  elif n=='classes.dex':out.writestr(entry,(WORK/'classes.dex').read_bytes())
  elif n=='classes3.dex':out.writestr(entry,(WORK/'classes3.dex').read_bytes())
  elif n=='classes4.dex':out.writestr(entry,(WORK/'classes4.dex').read_bytes())
  elif n=='classes6.dex':out.writestr(entry,(WORK/'classes6.dex').read_bytes())
  elif n=='classes7.dex':out.writestr(entry,(WORK/'classes7.dex').read_bytes())
  elif n!='AndroidManifest.xml' and not n.startswith('META-INF/'):out.writestr(entry,base.read(entry))
 out.write(WORK/'dex/classes.dex','classes12.dex')
 out.write(updater/'dex/classes.dex','classes13.dex')
 out.write(updater/'inhouse_update_paths.xml','res/xml/inhouse_update_paths.xml')
 out.write(ROOT/'app/assets/mascot/launcher.png',MASCOT_PATH)
 out.write(ROOT/'app/assets/mascot/welcome.png',SCENE_MASCOT_PATH)
 for mood,source in MOOD_SCENES.items():out.write(ROOT/'app/assets/mascot'/source,'res/drawable/duoaero_scene_'+mood+'.png')
 out.writestr(LOGO_PATH,wordmark_xml_bytes)
 for path,xml in mascot_xml_bytes.items():out.writestr(path,xml)
 for asset in (ROOT/'app/assets/updates').iterdir():
  if asset.is_file() and asset.name!='config.json':out.write(asset,'assets/updates/'+asset.name)
 update_config=json.loads((ROOT/'app/assets/updates/config.json').read_text())
 update_config.pop('installedVersion',None)
 update_config.pop('installedVersionCode',None)
 out.writestr('assets/updates/config.json',json.dumps(update_config))
 if production or os.environ.get('DUOAERO_STANDALONE')=='1':out.writestr('assets/duoaero/standalone-bootstrap','1')
 if production or os.environ.get('DUOAERO_GOOGLE_GATE')=='1':out.writestr('assets/duoaero/google-required','1')
 for shared in (ROOT/'shared').rglob('*'):
  if shared.is_file():out.write(shared,'assets/shared/'+shared.relative_to(ROOT/'shared').as_posix())
 out.write(ROOT/'native-base/vendor/notosansmath/OFL.txt','assets/duoaero/licenses/NotoSansMath-OFL.txt')
 # A separate input for the original hardcoded-session loader. The original
 # math reference asset remains unchanged for baseline comparisons.
 lesson=ROOT/'native-base/tests/fixtures/aerospace_lesson.json'
 out.write(lesson,'assets/hardcoded_sessions/duoaero/aerospace_lesson.json')
 out.write(ROOT/'native-base/tests/fixtures/aerospace_formula_lesson.json','assets/hardcoded_sessions/duoaero/aerospace_formula_lesson.json')
 bank=json.loads((ROOT/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
 by_id={question['id']:question for question in bank}
 # Exercise word gaps first, so their native interaction and screenshots are
 # observed even if an unrelated matching-card regression aborts the probe.
 mixed=[q for q in bank if q['type']=='gap']
 mixed.extend(next(q for q in bank if q['type']==kind) for kind in ('multi','matching'))
 mixed.extend(q for q in bank if q['type']=='order')
 mixed.append(next(q for q in bank if q['type']=='matching' and q['id'].startswith('BOOK-V6')))
 # Exercise the actual alternating formula/choice sequence in the original
 # controller, not just the separately serialized challenge models.
 if os.environ.get('DUOAERO_WIND_DIAGNOSTIC')=='1' and not production:
  # Exercise the new wind formula blocks and their two one-calculation steps
  # in the original controller; model conversion alone is not UI acceptance.
  mixed.extend(lesson_questions([by_id['TA1-0012-F1'],by_id['TA1-0092-D2']]))
  inequality=dict(by_id['TA1-0012-F1'],id='diagnostic_inequality',
   stem='For TAS>=1.3Vs and M<=0.75, what is 2 + 2?',
   options=['4','3','5','6'],answer=0,explanation='2 + 2 = 4.')
  inequality.pop('lesson_steps',None);inequality.pop('formula_hint',None)
  mixed.append(inequality)
  mixed.extend(lesson_questions([by_id['TA1-0041-F1']]))
 else:
  mixed.extend(lesson_questions([by_id['TA1-0107-D2']]))
  mixed.extend(lesson_questions([by_id['TA1-0078-D2']]))
 if os.environ.get('DUOAERO_WORD_TOUCH_DIAGNOSTIC')=='1' and not production:
  # Exercise word and named slots before both symbolic and fractional
  # formulas, including an exponent whose base must remain visible.
  mixed=lesson_questions([by_id['BOOK-V6-01-D1']],teach_words=True)
  mixed.extend(lesson_questions([by_id['TA1-0012-F1']],teach_words=True)[:3])
  mixed.extend(lesson_questions([by_id['TA1-0041-F1']],teach_words=True)[:3])
  sound=lesson_questions([by_id['TA1-0107-D2']],teach_words=True)
  mixed.extend(q for q in sound if q['id'].startswith('TA1-0107-D2-F3'))
 if os.environ.get('DUOAERO_ISA_DIAGNOSTIC')=='1' and not production:
  # Real native rendering/grading of the newly divided pressure calculation.
  mixed=lesson_questions([by_id['TA1-0463-D2']],teach_words=True)
 if os.environ.get('DUOAERO_SQRT_DIAGNOSTIC')=='1' and not production:
  # Original question with a square root, a nested physical fraction and units.
  mixed=[by_id['TA1-0006-F1']]
 out.writestr('assets/hardcoded_sessions/duoaero/aerospace_mixed_lesson.json',json.dumps(native_session(mixed,'duoaero_mixed_diagnostic'),ensure_ascii=False))
 mixed_driver=copy.deepcopy(mixed)
 for question in mixed_driver:
  if question['type']=='matching':
   question['pairs']=[[content(None,value) if any('latex' in p for p in notation_parts(value)) else value for value in pair] for pair in question['pairs']]
  elif question['type']=='choice':
   option=question['answer'];rich=question.get('rich_text',{}).get('options',[None]*len(question['options']))
   question['selection']=content(rich[option],question['options'][option])
 out.writestr('assets/duoaero/mixed-source.json',json.dumps(mixed_driver,ensure_ascii=False))
 plain_sample=[by_id[c['id']] for c in json.loads(lesson.read_text())['challenges'][:12]]
 # Exercise the reported unformatted density fraction on the actual original
 # select-one screen, in addition to authored rich-text samples.
 sample=lesson_questions(plain_sample[:1]+[by_id['TA1-0148'],by_id['TA1-0078-D2'],by_id['TA1-0132-D2'],by_id['TA1-0154-D2'],by_id['TA1-0081-D2'],by_id['TA1-0397-D2'],by_id['TA1-0107-D2']]+[q for q in bank if q.get('rich_text')])
 # The select-one driver handles only cards; the separate formula driver
 # exercises native expression-building questions, including inserted steps.
 sample=[q for q in sample if q['type']=='choice']
 sample_ids={q['id'] for q in sample}
 sample.extend(q for q in plain_sample[1:] if q['id'] not in sample_ids)
 sample=sample[:20]
 assert all(q['type']=='choice' for q in sample) and 10<=len(sample)<=20
 # MathSessionCoordinator starts the original JS sandbox only when the
 # original session type supplies a skill ID (Session.Type.F1). A language
 # GLOBAL_PRACTICE session can render blobs but skips their grader startup.
 rich_session={'id':'duoaero_native_rich_diagnostic','type':'MATH_LESSON','fromLanguage':'en',
  'skillId':'duoaero_aerospace_diagnostic','levelIndex':0,'levelSessionIndex':0,
  'metadata':{'id':'duoaero_native_rich_diagnostic','type':'math_lesson'},
  'challenges':[choice_blob(q,include_formula_hint=True) for q in sample]}
 out.writestr('assets/hardcoded_sessions/duoaero/aerospace_rich_lesson.json',json.dumps(rich_session,ensure_ascii=False))
 catalog={};legacy_catalog={}
 lesson_total=0
 for node in json.loads((ROOT/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig')):
  from path_adapter import stable_id
  lesson_total+=len(node['lessons'])
  for position,entry in enumerate(node['lessons']):
   selected=[by_id[i] for i in entry['ids']]
   try: adapted=native_session(selected,entry['id'],stable_id('skill',node['id']),teach_words=True)
   except NotImplementedError: continue
   adapted['levelSessionIndex']=position
   catalog[entry['id']]=adapted
   if any(question.get('lesson_steps') for question in selected):
    legacy=native_session(selected,entry['id'],stable_id('skill',node['id']),expand_steps=False)
    legacy['levelSessionIndex']=position
    legacy_catalog[entry['id']]=legacy
 # Preserve earned chests from every node in 1.3.3 after regrouping.
 legacy_chests, prerequisites = {}, []
 for node in json.loads((ROOT/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig')):
  prerequisites.extend(lesson['id'] for lesson in node['lessons'])
  legacy_chests[stable_id('chest', node['id'])] = list(prerequisites)
 out.writestr('assets/duoaero/course/legacy-chest-requirements.json',json.dumps(legacy_chests))
 out.writestr('assets/duoaero/course/session-catalog.json',json.dumps(catalog,ensure_ascii=False))
 out.writestr('assets/duoaero/course/legacy-session-catalog.json',json.dumps(legacy_catalog,ensure_ascii=False))
 # Keep exact published question sets for old on-device and Drive proofs;
 # later lesson expansions must not invalidate previously completed lessons.
 for history_version in ('1.3.0','1.3.5','1.3.6','1.3.7'):
  out.write(ROOT/('native-base/session-history/'+history_version+'.json'),
            'assets/duoaero/course/history-'+history_version+'.json')
 print('Local original session catalog:',len(catalog),'of',lesson_total,'lessons; runtime navigation and completion require separate acceptance.')
 for source_name,target_name in [('native_course_path_info','path-info'),('native_course_section','section'),('native_lesson_index','lesson-index')]:
  out.write(ROOT/('native-base/tests/fixtures/'+source_name+'.json'),'assets/duoaero/course/'+target_name+'.json')
run(tool('zipalign'),'-f','-p','4',WORK/'unsigned.apk',WORK/'aligned.apk')
if production:
 target=WORK/('DuoAero-'+version+'-unsigned.apk');shutil.copyfile(WORK/'aligned.apk',target)
 print('Original runtime unsigned production candidate (requires acceptance and permanent signing):',target)
else:
 run(java('java'),'-jar',BT/'lib/apksigner.jar','sign','--ks',KEY,'--ks-pass','pass:android','--out',WORK/'DuoAero-native-base-test.apk',WORK/'aligned.apk')
 print('Original runtime test APK:',WORK/'DuoAero-native-base-test.apk')
