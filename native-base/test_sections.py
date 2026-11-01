"""Exercise the original section picker; only first midterm has authored data."""
import os,re,subprocess,time
from pathlib import Path
from xml.etree import ElementTree as ET
PACKAGE='com.duoaero.nativebase';OUT=Path(os.environ['DUOAERO_EVIDENCE'])
def adb(*args):return subprocess.check_output(['adb',*args],timeout=30)
def capture(name):
 try:
  adb('shell','timeout','15','uiautomator','dump','/sdcard/section-test.xml')
  data=adb('exec-out','cat','/sdcard/section-test.xml'); tree=ET.fromstring(data)
  (OUT/(name+'.xml')).write_bytes(data)
 except (ET.ParseError,subprocess.SubprocessError):tree=None
 (OUT/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'));return tree
def wait(name,predicate):
 end=time.monotonic()+90
 while time.monotonic()<end:
  tree=capture(name)
  if tree is not None and predicate(tree):return tree
  time.sleep(2)
 raise AssertionError('Original section screen not observed: '+name)
def has(tree,value):return any(value.casefold() in (n.get('text','')+' '+n.get('content-desc','')).casefold() for n in tree.iter('node'))
def tap(n):
 a,b,c,d=map(int,re.findall(r'\d+',n.get('bounds')));adb('shell','input','tap',str((a+c)//2),str((b+d)//2))
try:
 adb('shell','am','force-stop',PACKAGE);assert b'Success' in adb('shell','pm','clear',PACKAGE)
 adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
 home=wait('sections-home',lambda t:has(t,'1 · Aerospace industry') and any(n.get('resource-id')=='com.duolingo:id/primaryCardView' for n in t.iter('node')))
 tap(next(n for n in home.iter('node') if n.get('resource-id')=='com.duolingo:id/primaryCardView'))
 # The home header already says Midterm 1. Require the home path to be gone,
 # otherwise a transition frame falsely passes without opening the selector.
 picker=wait('sections-picker',lambda t:has(t,'Midterm 1') and not any(n.get('resource-id')=='com.duolingo:id/path' for n in t.iter('node')))
 assert has(picker,'DuoAero'),'Picker retained the original Math heading'
 assert any(n.get('text','').strip()=='1' for n in picker.iter('node')),'First midterm has the wrong section icon'
 labels=[n for n in picker.iter('node') if 'midterm 1' in n.get('text','').casefold()]
 assert len(labels)>=2,'Missing original midterm navigation row'
 tap(labels[-1])
 wait('sections-returned',lambda t:has(t,'1 · Aerospace industry') and any(n.get('resource-id')=='com.duolingo:id/path' for n in t.iter('node')))
 (OUT/'sections-result.txt').write_text('PASS: first midterm appears in the original section picker and its row returns to the original path; no unprovided partials asserted.\n')
finally:
 (OUT/'sections-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroNative:I','AndroidRuntime:E'))
