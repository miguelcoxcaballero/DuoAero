"""Original chest UI with explicitly seeded lesson prerequisites, not traversal proof."""
import json, os, re, subprocess, time, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from runtime_config import WORK

OUT=Path(os.environ['DUOAERO_EVIDENCE']); PACKAGE='com.duoaero.nativebase'
def adb(*args):return subprocess.check_output(['adb',*args],timeout=35)
def capture(name):
    try:
        adb('shell','timeout','15','uiautomator','dump','/sdcard/chest-test.xml')
        tree=ET.fromstring(adb('exec-out','cat','/sdcard/chest-test.xml'))
        (OUT/(name+'.xml')).write_bytes(ET.tostring(tree))
    except (ET.ParseError,subprocess.SubprocessError):tree=None
    (OUT/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'))
    return tree

def wait(name,condition):
    deadline=time.monotonic()+90
    while time.monotonic()<deadline:
        tree=capture(name)
        if tree is not None and condition(tree):return tree
        time.sleep(2)
    raise AssertionError('Original chest UI timed out: '+name)

def counter(tree,value):
    return any(n.get('resource-id')=='com.duolingo:id/itemButton' and n.get('text')==str(value) for n in tree.iter('node'))

def chest_nodes(tree):
    return [n for n in tree.iter('node') if n.get('resource-id') in {'com.duolingo:id/chest','com.duolingo:id/chestView','com.duolingo:id/chestImage','com.duolingo:id/chestAnimationView'}]

def tap(node):
    x1,y1,x2,y2=map(int,re.findall(r'\d+',node.get('bounds')))
    adb('shell','input','tap',str((x1+x2)//2),str((y1+y2)//2))

try:
    adb('shell','am','force-stop',PACKAGE);assert b'Success' in adb('shell','pm','clear',PACKAGE)
    with zipfile.ZipFile(WORK/'DuoAero-native-base-test.apk') as apk:
        section=json.loads(apk.read('assets/duoaero/course/section.json'))
        catalog=json.loads(apk.read('assets/duoaero/course/session-catalog.json'))
    levels=section['units'][0]['levels']; chest=levels[1]['id']
    folder='files/duoaero-course/local-test/submissions'
    adb('shell','run-as',PACKAGE,'mkdir','-p',folder)
    for metadata in levels[0]['pathLevelClientData']['sessionMetadatas']:
        lesson=catalog[metadata['id']];now=time.time()
        proof={'id':lesson['id'],'type':'MATH_LESSON','failed':False,'shouldLearnThings':True,
               'startTime':now-120,'endTime':now,'challenges':[{'id':q['id']} for q in lesson['challenges']]}
        record={'schema':1,'sessionId':lesson['id'],'savedAt':int(now*1000),'nativeSubmission':proof,'completionSubmission':proof,'completedOnce':True}
        destination=folder+'/'+lesson['id']+'.json'
        assert re.fullmatch(r'[A-Za-z0-9_./-]+',destination)
        subprocess.run(['adb','shell','run-as',PACKAGE,'sh','-c',"'cat > "+destination+"'"],input=json.dumps(record).encode(),check=True,timeout=30)
    initial=len(levels[0]['pathLevelClientData']['sessionMetadatas'])*10
    adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    tree=wait('chest-home',lambda t:counter(t,initial) and chest_nodes(t))
    tap(chest_nodes(tree)[0])
    deadline=time.monotonic()+90;opened=False
    while time.monotonic()<deadline:
        tree=capture('chest-open')
        if tree is not None:
            buttons=[n for n in tree.iter('node') if n.get('text','').strip().upper() in {'OPEN','OPEN CHEST','CLAIM','CONTINUE','CLAIM REWARD'} and n.get('enabled')=='true']
            if buttons:tap(buttons[0])
        result=subprocess.run(['adb','exec-out','run-as',PACKAGE,'cat','files/duoaero-course/local-test/chests.json'],capture_output=True,timeout=30)
        if result.returncode==0:
            try: opened=chest in json.loads(result.stdout)
            except (ValueError,UnicodeDecodeError): pass  # run-as may print a transient missing-file error
            if opened:break
        time.sleep(2)
    assert opened,'Original chest interaction did not durably award gems'
    # Return through the original reward activity's footer if still present.
    for _ in range(5):
        tree=capture('chest-reward')
        if tree is not None and counter(tree,initial+25):break
        if tree is not None:
            buttons=[n for n in tree.iter('node') if n.get('text','').strip().upper() in {'CONTINUE','NO THANKS','DONE'} and n.get('enabled')=='true']
            if buttons:tap(buttons[0])
        time.sleep(2)
    wait('chest-awarded-home',lambda t:counter(t,initial+25))
    adb('shell','am','force-stop',PACKAGE)
    adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    wait('chest-restored-home',lambda t:counter(t,initial+25))
    claims=json.loads(adb('exec-out','run-as',PACKAGE,'cat','files/duoaero-course/local-test/chests.json'))
    assert set(claims)=={chest}
    (OUT/'chests-result.txt').write_text('PASS: seeded prerequisites, original visible chest tap/reward, durable25gems, visible balance after restart. This does not prove lesson traversal or real Drive synchronization.\n')
finally:
    (OUT/'chests-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroNative:I','AndroidRuntime:E'))
    (OUT/'chests-anr.txt').write_bytes(adb('shell','dumpsys','activity','lastanr'))
