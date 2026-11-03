"""Reach and grade the diagnostic second section's final draft topic.

Earlier five topics are synthetically seeded, so this is not course traversal.
"""
import json,os,re,subprocess,time,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from runtime_config import WORK
from feedback_checks import assert_native_correct, feedback_terminal
from visual_controls import native_positive_banner
PACKAGE='com.duoaero.nativebase';OUT=Path(os.environ['DUOAERO_EVIDENCE'])
def adb(*a):return subprocess.check_output(['adb',*a],timeout=30)
def capture(name):
 try:
  adb('shell','timeout','15','uiautomator','dump','/sdcard/section-tail.xml');raw=adb('exec-out','cat','/sdcard/section-tail.xml');tree=ET.fromstring(raw);(OUT/(name+'.xml')).write_bytes(raw)
 except (ET.ParseError,subprocess.SubprocessError):tree=None
 (OUT/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'));return tree
def has(t,s):return any(s.casefold() in (n.get('text','')+' '+n.get('content-desc','')).casefold() for n in t.iter('node'))
def wait(name,pred,seconds=90):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  t=capture(name)
  if t is not None and pred(t):return t
  time.sleep(2)
 raise AssertionError('Not observed: '+name)
def tap(n):
 a,b,c,d=map(int,re.findall(r'\d+',n.get('bounds')));x,y=str((a+c)//2),str((b+d)//2);adb('shell','input','swipe',x,y,x,y,'100')
def write_private(path,data):
 assert re.fullmatch(r'[A-Za-z0-9_./-]+',path)
 subprocess.run(['adb','shell','run-as',PACKAGE,'sh','-c',"'cat > "+path+"'"],input=json.dumps(data).encode(),check=True,timeout=30)
try:
 adb('shell','am','force-stop',PACKAGE);assert b'Success' in adb('shell','pm','clear',PACKAGE)
 with zipfile.ZipFile(WORK/'DuoAero-native-base-test.apk') as apk:
  section=json.loads(apk.read('assets/duoaero/course/section-2.json'));catalog=json.loads(apk.read('assets/duoaero/course/session-catalog.json'))
 assert [u['teachingObjective'].split(' · ')[0] for u in section['units']]==['3.1','3.2','3.3','4','5.1','5.2']
 folder='files/duoaero-course/local-test/submissions';adb('shell','run-as',PACKAGE,'mkdir','-p',folder)
 for unit in section['units'][:5]:
  for session in unit['levels'][0]['pathLevelClientData']['sessionMetadatas']:
   id=session['id'];lesson=catalog[id];now=time.time();proof={'id':id,'type':'MATH_LESSON','failed':False,'shouldLearnThings':True,'startTime':now-120,'endTime':now,'challenges':[{'id':q['id']} for q in lesson['challenges']]};write_private(folder+'/'+id+'.json',{'schema':1,'sessionId':id,'savedAt':int(now*1000),'nativeSubmission':proof,'completionSubmission':proof,'completedOnce':True})
 adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
 home=wait('section-tail-home',lambda t:any(n.get('resource-id')=='com.duolingo:id/path' for n in t.iter('node')) and any(n.get('resource-id')=='com.duolingo:id/primaryCardView' for n in t.iter('node')))
 if not has(home,'MIDTERM 2'):
  tap(next(n for n in home.iter('node') if n.get('resource-id')=='com.duolingo:id/primaryCardView'))
  picker=wait('section-tail-picker',lambda t:has(t,'Midterm 2') and not any(n.get('resource-id')=='com.duolingo:id/path' for n in t.iter('node')))
  tap([n for n in picker.iter('node') if n.get('text','').casefold()=='midterm 2'][-1]);expanded=wait('section-tail-expanded',lambda t:len([n for n in t.iter('node') if n.get('text','').casefold()=='midterm 2'])>=2);tap([n for n in expanded.iter('node') if n.get('text','').casefold()=='midterm 2'][-1])
 for attempt in range(8):
  path=capture('section-tail-path-'+str(attempt))
  if path is not None and has(path,'5.2 · Rotorcraft'):
   ovals=[n for n in path.iter('node') if n.get('resource-id')=='com.duolingo:id/oval']
   for oval in reversed(ovals):
    tap(oval);time.sleep(1);dialog=capture('section-tail-node')
    if dialog is not None and has(dialog,'Rotorcraft') and any(n.get('resource-id')=='com.duolingo:id/learnButton' for n in dialog.iter('node')):
     tap(next(n for n in dialog.iter('node') if n.get('resource-id')=='com.duolingo:id/learnButton'));break
    adb('shell','input','keyevent','4')
   else:continue
   break
  adb('shell','input','swipe','700','2200','700','700','500');time.sleep(1)
 else:raise AssertionError('Final seeded diagnostic topic not opened')
 answer='The pitch of the rotor blades together';question=wait('section-tail-question',lambda t:has(t,answer));tap(next(n for n in question.iter('node') if answer in n.get('content-desc','') and n.get('resource-id')=='com.duolingo:id/mathCard'))
 ready=wait('section-tail-ready',lambda t:any(n.get('text')=='CHECK' and n.get('enabled')=='true' for n in t.iter('node')));tap(next(n for n in ready.iter('node') if n.get('text')=='CHECK' and n.get('enabled')=='true'))
 end=time.monotonic()+60
 while time.monotonic()<end:
  feedback=capture('section-tail-feedback')
  if feedback is None:time.sleep(2);continue
  if feedback_terminal(feedback):
   assert_native_correct(feedback,'first rotorcraft question');break
  if any(n.get('text')=='CONTINUE' and n.get('enabled')=='true' for n in feedback.iter('node')):
   if native_positive_banner(OUT/'section-tail-feedback.png',OUT/'section-tail-feedback-banner.png'):
    assert_native_correct(feedback,'first rotorcraft question',visual_positive=True);break
  time.sleep(2)
 else:raise AssertionError('No original positive rotorcraft feedback')
 (OUT/'section-tail-result.txt').write_text('PASS: five earlier diagnostic topics seeded; final rotorcraft node opened and its first answer graded. Full course, real progress and Drive remain unverified.\n')
finally:(OUT/'section-tail-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroNative:I','AndroidRuntime:E'))
