"""Inspect the original path grid animation after replacing Junior with Linus."""
import json, os, re, shlex, subprocess, time, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from runtime_config import WORK
from rich_question import content
from course_adapter import lesson_questions
from visual_controls import claim_xp

OUT=Path(os.environ['DUOAERO_EVIDENCE']); PACKAGE='com.duoaero.nativebase'
HINT_TEST=os.environ.get('DUOAERO_TEST_FORMULA_HINT')=='1'
HINT_ID=os.environ.get('DUOAERO_HINT_QUESTION','TA1-0148')
ROOT=Path(__file__).resolve().parents[1]
def adb(*args):return subprocess.check_output(['adb',*args],timeout=35)
def capture(name):
    image=adb('exec-out','screencap','-p');(OUT/(name+'.png')).write_bytes(image)
    try:
        adb('shell','timeout','15','uiautomator','dump','/sdcard/atmosphere-test.xml')
        raw=adb('exec-out','cat','/sdcard/atmosphere-test.xml');tree=ET.fromstring(raw)
        (OUT/(name+'.xml')).write_bytes(raw)
        # The UI may advance during the dump; capture the same observed state.
        (OUT/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'))
        return tree
    except (ET.ParseError,subprocess.SubprocessError):return None

def wait(name,predicate,timeout=90,continue_interstitial=False):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        tree=capture(name)
        # The hosted emulator sometimes reports an ANR for its background
        # Pixel Launcher while DuoAero is already open. Dismiss only that
        # external system dialog; never hide an ANR from the app under test.
        if tree is not None and any("Pixel Launcher isn't responding" in n.get('text','') for n in tree.iter('node')):
            close=[n for n in tree.iter('node') if n.get('text','')=='Close app']
            if close:
                tap_node(close[0]);time.sleep(1);continue
        if tree is not None and predicate(tree):return tree
        if tree is not None and continue_interstitial:
            buttons=[n for n in tree.iter('node') if n.get('text','').strip()=='CONTINUE' and n.get('enabled')=='true']
            if buttons:tap_node(buttons[0])
        time.sleep(2)
    raise AssertionError('Timed out on '+name)

def tap_node(node):
    left,top,right,bottom=map(int,re.findall(r'\d+',node.get('bounds')))
    x,y=str((left+right)//2),str((top+bottom)//2)
    # A short real press gives the original draggable-token controller time to
    # observe its pointer-down before pointer-up; immediate tap can be lost.
    adb('shell','input','swipe',x,y,x,y,'100')
def matching(tree,needle,resource=None):
    return [n for n in tree.iter('node') if n.get('enabled')=='true'
            and (resource is None or n.get('resource-id')==resource)
            and needle in (n.get('text','')+' '+n.get('content-desc',''))]
def choose(node,kind,label):
    if kind=='formula_blocks':
        # Independent instrumentation targets the test APK, not the running
        # lesson process, and performs the visible original accessibility click.
        # adb passes a command string through the device shell. Formula labels
        # can contain spaces, braces or minus signs; preserve one literal extra.
        output=adb('shell','am','instrument','-w','-e','label',shlex.quote(label),
                   'com.duoaero.nativebase.tests/com.duoaero.nativebase.IndependentClickProbe')
        assert b'INDEPENDENT_CLICK_VERIFIED=true' in output,output.decode(errors='replace')
    else:tap_node(node)
def write_private(path,data):
    assert re.fullmatch(r'[A-Za-z0-9_./-]+',path)
    subprocess.run(['adb','shell','run-as',PACKAGE,'sh','-c',"'cat > "+path+"'"],input=json.dumps(data).encode(),check=True,timeout=30)

def open_atmosphere(prefix):
    for attempt in range(12):
        tree=capture(prefix+'-path-'+str(attempt))
        if tree is None:continue
        for oval in [n for n in tree.iter('node') if n.get('resource-id')=='com.duolingo:id/oval']:
            tap_node(oval);time.sleep(1)
            dialog=capture(prefix+'-node-'+str(attempt))
            if dialog is not None and matching(dialog,'International Standard Atmosphere'):
                buttons=[n for n in dialog.iter('node') if n.get('resource-id')=='com.duolingo:id/learnButton']
                if buttons:tap_node(buttons[0])
                return
            adb('shell','input','keyevent','4');time.sleep(.5)
        adb('shell','input','swipe','700','2200','700','700','500');time.sleep(1)
    raise AssertionError('Cannot open first Atmosphere path node')

try:
    adb('shell','am','force-stop',PACKAGE);assert b'Success' in adb('shell','pm','clear',PACKAGE)
    with zipfile.ZipFile(WORK/'DuoAero-native-base-test.apk') as apk:
        section=json.loads(apk.read('assets/duoaero/course/section.json'))
        catalog=json.loads(apk.read('assets/duoaero/course/session-catalog.json'))
        raw=apk.read('res/raw/math_junior_grid.riv')
        assert b'DuoAero Linus' in raw,'Patched grid resource missing from diagnostic APK'
        assert 'res/drawable/duoaero_scene_linus_grid_static.png' in apk.namelist(), 'Missing static path artwork'
    target='2.3-3-point-0-lesson-0';root='files/duoaero-course/local-test';folder=root+'/submissions'
    adb('shell','run-as',PACKAGE,'mkdir','-p',folder);claims={};found=False
    for unit in section['units']:
        for level in unit['levels']:
            if level['type']=='chest':claims[level['id']]=int(time.time()*1000);continue
            entries=level['pathLevelClientData']['sessionMetadatas']
            if any(x['id']==target for x in entries):found=True;break
            for entry in entries:
                lesson=catalog[entry['id']];now=time.time()
                proof={'id':lesson['id'],'type':'MATH_LESSON','failed':False,'shouldLearnThings':True,
                       'startTime':now-120,'endTime':now,'challenges':[{'id':q['id']} for q in lesson['challenges']]}
                write_private(folder+'/'+lesson['id']+'.json',{'schema':1,'sessionId':lesson['id'],'savedAt':int(now*1000),
                    'nativeSubmission':proof,'completionSubmission':proof,'completedOnce':True})
        if found:break
    assert found
    write_private(root+'/chests.json',claims)
    adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    tree=wait('linus-path-start',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')),90)
    assert matching(tree,'2.3 · Structures'),'Expected the seeded original Structures path'
    capture('linus-path-before-video')
    adb('shell','screenrecord','--bit-rate','1000000','--time-limit','12','/sdcard/linus-path.mp4')
    subprocess.run(['adb','pull','/sdcard/linus-path.mp4',str(OUT/'linus-path.mp4')],check=True,timeout=45,stdout=subprocess.DEVNULL)
    assert (OUT/'linus-path.mp4').stat().st_size>10000
    capture('linus-path-after-video')
    (OUT/'linus-path-result.txt').write_text('PASS: earlier nodes seeded; original Structures path opened with patched Rive and static resources and a 12-second recording. Actual appearance and animation require visual inspection; real progress not tested.\n')
finally:
    (OUT/'linus-path-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroNative:I','AndroidRuntime:E'))
