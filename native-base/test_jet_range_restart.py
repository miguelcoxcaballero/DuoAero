"""Restart a seeded synthetic account after native range-lesson completion."""
import json,os,re,subprocess,time,zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from runtime_config import WORK
PACKAGE='com.duoaero.nativebase';TARGET='2.2-range-draft-formula-lesson-0';NEXT='2.2-range-draft-formula-lesson-1'
OUT=Path(os.environ['DUOAERO_EVIDENCE'])
def adb(*args):return subprocess.check_output(['adb',*args],timeout=45)
def tree():
 try:
  adb('shell','timeout','15','uiautomator','dump','/sdcard/range-restart.xml')
  return ET.fromstring(adb('exec-out','cat','/sdcard/range-restart.xml'))
 except (ET.ParseError,subprocess.SubprocessError):return None
def screenshot(name):
 (OUT/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'))
 t=tree()
 if t is not None:(OUT/(name+'.xml')).write_bytes(ET.tostring(t))
def wait(predicate,timeout=120):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  t=tree()
  if t is not None and predicate(t):return t
  time.sleep(1)
 raise AssertionError('Native range path state was not observed')
def tap(n):
 bounds=n.get('bounds','');values=re.findall(r'\d+',bounds);assert len(values)==4,bounds
 l,t,r,b=map(int,values);adb('shell','input','tap',str((l+r)//2),str((t+b)//2))
def has(t,text):return any(text.casefold() in (n.get('text','')+' '+n.get('content-desc','')).casefold() for n in t.iter('node'))
def open_target():
 for page in range(18):
  t=tree()
  if t is not None:
   ovals=[n for n in t.iter('node') if n.get('resource-id')=='com.duolingo:id/oval' and n.get('visible-to-user','true')=='true']
   for oval in ovals:
    tap(oval);time.sleep(.5);dialog=tree()
    if dialog is not None and any(n.get('resource-id')=='com.duolingo:id/titleText' and n.get('text','').casefold()=='range formulas' for n in dialog.iter('node')):
     buttons=[n for n in dialog.iter('node') if n.get('resource-id')=='com.duolingo:id/learnButton' and n.get('enabled')=='true']
     if buttons:tap(buttons[-1]);return
    # A missed tap must not send Back from the path and leave the app.
    if dialog is not None and any(n.get('resource-id')=='com.duolingo:id/learnButton' for n in dialog.iter('node')) and any(n.get('resource-id')=='com.duolingo:id/titleText' for n in dialog.iter('node')):
     dimensions=re.findall(r'(\d+)x(\d+)',adb('shell','wm','size').decode())
     assert dimensions,'No emulator display dimensions'
     width,height=map(int,dimensions[-1])
     adb('shell','input','tap',str(max(3,int(width*.01))),str(int(height*.5)))
     wait(lambda t:not (any(n.get('resource-id')=='com.duolingo:id/learnButton' for n in t.iter('node')) and any(n.get('resource-id')=='com.duolingo:id/titleText' for n in t.iter('node'))),timeout=15)
  adb('shell','input','swipe','700','2300','700','900','500');time.sleep(.5)
 raise AssertionError('Range formulas node unavailable after restart')
assert adb('shell','getprop','ro.kernel.qemu').strip()==b'1'
with zipfile.ZipFile(WORK/'DuoAero-native-base-test.apk') as apk:
 expected=json.loads(apk.read('assets/duoaero/jet-range-path-answers.json'))
 catalog=json.loads(apk.read('assets/duoaero/course/session-catalog.json'))
 assert NEXT in catalog
path='files/duoaero-course/local-test/submissions/'+TARGET+'.json'
def proof():return json.loads(adb('exec-out','run-as',PACKAGE,'cat',path))
before=proof();assert before.get('completedOnce') is True
ids=Counter(x['id'] for x in expected);assert Counter(x['id'] for x in before['completionSubmission']['challenges'])==ids
adb('logcat','-c');adb('shell','am','force-stop',PACKAGE);adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
wait(lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')))
screenshot('range-restart-path');open_target()
end=time.monotonic()+120;selected=None
while time.monotonic()<end:
 log=adb('logcat','-d','-s','DuoAeroNative:I').decode(errors='replace')
 routes=re.findall(r'Local original session selected: ([A-Za-z0-9_.-]+)',log)
 if routes:selected=routes[-1];break
 time.sleep(1)
assert selected==NEXT,('Unexpected lesson after restart',selected)
after=proof();assert after.get('completedOnce') is True
assert Counter(x['id'] for x in after['completionSubmission']['challenges'])==ids
wait(lambda t: has(t,'Complete the formula in words') and has(t,'burn') and has(t,'CHECK'),timeout=120)
screenshot('range-restart-next')
(OUT/'range-restart-result.txt').write_text('PASS: seeded synthetic account retained the exact completion challenge IDs and displayed the next native range lesson question after restart; real accounts and remaining lessons not tested.\n')
