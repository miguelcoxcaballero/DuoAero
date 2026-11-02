"""Exercise a diagnostic-only second section in the original picker.

This does not add second-midterm educational content to production.
"""
import json,os,re,subprocess,time
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image
from visual_controls import claim_xp
PACKAGE='com.duoaero.nativebase';OUT=Path(os.environ['DUOAERO_EVIDENCE'])
def adb(*args):return subprocess.check_output(['adb',*args],timeout=30)
def capture(name):
 try:
  adb('shell','timeout','15','uiautomator','dump','/sdcard/two-sections.xml')
  data=adb('exec-out','cat','/sdcard/two-sections.xml');tree=ET.fromstring(data)
  (OUT/(name+'.xml')).write_bytes(data)
 except (ET.ParseError,subprocess.SubprocessError):tree=None
 (OUT/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'));return tree
def wait(name,predicate,seconds=90):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  tree=capture(name)
  if tree is not None and predicate(tree):return tree
  time.sleep(2)
 raise AssertionError('Not observed: '+name)
def has(tree,value):return any(value.casefold() in (n.get('text','')+' '+n.get('content-desc','')).casefold() for n in tree.iter('node'))
def tap(n):
 a,b,c,d=map(int,re.findall(r'\d+',n.get('bounds')));x=str((a+c)//2);y=str((b+d)//2);adb('shell','input','swipe',x,y,x,y,'100')
def second_active(tree,capture_name):
 if not has(tree,'3.2 · Space flight environment'):return False
 ovals=[n for n in tree.iter('node') if n.get('resource-id')=='com.duolingo:id/oval']
 if len(ovals)<2:return False
 a,b,c,d=map(int,re.findall(r'\d+',ovals[-1].get('bounds')))
 with Image.open(OUT/(capture_name+'.png')) as image:
  red,green,blue=image.convert('RGB').getpixel(((a+c)//2,b+(d-b)//5))
  return green>120 and green>red*1.2 and green>blue*1.2
try:
 adb('shell','am','force-stop',PACKAGE);assert b'Success' in adb('shell','pm','clear',PACKAGE)
 adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
 home=wait('two-sections-home',lambda t:has(t,'1 · Aerospace industry') and any(n.get('resource-id')=='com.duolingo:id/primaryCardView' for n in t.iter('node')))
 tap(next(n for n in home.iter('node') if n.get('resource-id')=='com.duolingo:id/primaryCardView'))
 picker=wait('two-sections-picker',lambda t:has(t,'Midterm 2') and not any(n.get('resource-id')=='com.duolingo:id/path' for n in t.iter('node')))
 labels=[n for n in picker.iter('node') if 'midterm 2' in n.get('text','').casefold()]
 assert labels,'Second section row was not found'
 tap(labels[-1])
 # A first tap expands the section card; the original picker requires a
 # second tap on its child row to navigate to that section's path.
 expanded=wait('two-sections-expanded',lambda t:len([n for n in t.iter('node') if n.get('text','').casefold()=='midterm 2'])>=2)
 rows=[n for n in expanded.iter('node') if n.get('text','').casefold()=='midterm 2']
 tap(rows[-1])
 second=wait('two-sections-returned',lambda t:has(t,'3.1 · Launch vehicles') and any(n.get('resource-id')=='com.duolingo:id/path' for n in t.iter('node')),90)
 oval=next(n for n in second.iter('node') if n.get('resource-id')=='com.duolingo:id/oval')
 tap(oval)
 popup=wait('two-sections-node',lambda t:any(n.get('resource-id')=='com.duolingo:id/learnButton' for n in t.iter('node')))
 tap(next(n for n in popup.iter('node') if n.get('resource-id')=='com.duolingo:id/learnButton'))
 draft=json.loads((Path(__file__).resolve().parents[1]/'research/midterm2_concepts.json').read_text())
 questions=[q for q in draft['questions'] if q['topic']=='3.1'];assert len(questions)==10
 for index,q in enumerate(questions):
  answer=q['options'][q['answer']]
  question=wait('two-sections-exercise-'+str(index),lambda t:has(t,answer),90)
  choices=[n for n in question.iter('node') if answer in (n.get('text','')+' '+n.get('content-desc','')) and n.get('resource-id')=='com.duolingo:id/mathCard']
  assert choices,'Missing original answer card '+q['id'];tap(choices[-1])
  ready=wait('two-sections-ready-'+str(index),lambda t:any(n.get('text','')=='CHECK' and n.get('enabled')=='true' for n in t.iter('node')),30)
  tap(next(n for n in ready.iter('node') if n.get('text','')=='CHECK' and n.get('enabled')=='true'))
  feedback=wait('two-sections-feedback-'+str(index),lambda t:has(t,'CONTINUE') or has(t,'GOT IT'),60)
  assert not has(feedback,'GOT IT'),'Correct answer rejected: '+q['id']
  tap(next(n for n in feedback.iter('node') if n.get('text','')=='CONTINUE' and n.get('enabled')=='true'))
 end=time.monotonic()+90
 while time.monotonic()<end:
  complete=capture('two-sections-complete')
  buttons=[] if complete is None else [n for n in complete.iter('node') if n.get('text','')=='CLAIM XP']
  if buttons:tap(buttons[-1]);break
  point=claim_xp(OUT/'two-sections-complete.png',OUT/'two-sections-claim-ocr.png')
  if point:adb('shell','input','tap',str(point[0]),str(point[1]));break
  time.sleep(2)
 else:raise AssertionError('Second-section Claim XP missing')
 # A saved JSON file alone is insufficient: the original path must actually
 # expose the next node, both before and after a process restart.
 wait('two-sections-after-completion',lambda t:second_active(t,'two-sections-after-completion'),120)
 saved=json.loads(adb('exec-out','run-as',PACKAGE,'cat','files/duoaero-course/local-test/submissions/second-partial-3.1-lesson-0.json'))
 assert saved.get('completedOnce') is True,'Second-section completion not durably recorded'
 adb('shell','am','force-stop',PACKAGE)
 adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
 restarted=wait('two-sections-restarted',lambda t:any(n.get('resource-id')=='com.duolingo:id/path' for n in t.iter('node')),90)
 if not has(restarted,'MIDTERM 2'):
  card=next(n for n in restarted.iter('node') if n.get('resource-id')=='com.duolingo:id/primaryCardView');tap(card)
  picker=wait('two-sections-restart-picker',lambda t:has(t,'Midterm 2') and not any(n.get('resource-id')=='com.duolingo:id/path' for n in t.iter('node')))
  labels=[n for n in picker.iter('node') if n.get('text','').casefold()=='midterm 2'];tap(labels[-1])
  expanded=wait('two-sections-restart-expanded',lambda t:len([n for n in t.iter('node') if n.get('text','').casefold()=='midterm 2'])>=2)
  tap([n for n in expanded.iter('node') if n.get('text','').casefold()=='midterm 2'][-1])
 path=wait('two-sections-restart-path',lambda t:second_active(t,'two-sections-restart-path'),120)
 tap([n for n in path.iter('node') if n.get('resource-id')=='com.duolingo:id/oval'][-1])
 next_node=wait('two-sections-next-node',lambda t:any(n.get('resource-id')=='com.duolingo:id/learnButton' for n in t.iter('node')),45)
 tap(next(n for n in next_node.iter('node') if n.get('resource-id')=='com.duolingo:id/learnButton'))
 # The original math renderer draws its question body in a web view without
 # accessibility text. The answer cards do expose their content, so identify
 # the expected first exercise through its unique correct answer.
 answer='Spacecraft and occupants are continually falling around Earth together.'
 exercise=wait('two-sections-next-question',lambda t:has(t,answer),90)
 cards=[n for n in exercise.iter('node') if answer in n.get('content-desc','') and n.get('resource-id')=='com.duolingo:id/mathCard']
 assert cards,'The expected original answer card is missing';tap(cards[-1])
 ready=wait('two-sections-next-ready',lambda t:any(n.get('text','')=='CHECK' and n.get('enabled')=='true' for n in t.iter('node')),30)
 tap(next(n for n in ready.iter('node') if n.get('text','')=='CHECK' and n.get('enabled')=='true'))
 feedback=wait('two-sections-next-feedback',lambda t:has(t,'CONTINUE') or has(t,'GOT IT'),60)
 assert not has(feedback,'GOT IT'),'The correct second-topic answer was rejected'
 (OUT/'two-sections-result.txt').write_text('PASS: 10 drafted questions graded, first second-section lesson saved, next node unlocked and its first answer graded after restart. Full course, rewards and Drive remain unverified.\n')
finally:
 (OUT/'two-sections-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroNative:I','AndroidRuntime:E'))
