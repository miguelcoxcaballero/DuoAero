"""Seed first three sessions, then complete the fourth through the original path."""
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

def active_oval(tree):
    # Only tap the original active level: hidden older ovals may be underneath
    # the sticky section header and clicking them can leave the application.
    matches=[]
    for parent in tree.iter('node'):
        children=list(parent)
        if any(n.get('resource-id')=='com.duolingo:id/progressRing' for n in children):
            matches.extend(n for n in children if n.get('resource-id')=='com.duolingo:id/oval')
    return matches[0] if len(matches)==1 else None

def open_active_node(prefix, expected_title):
    tree=wait(prefix+'-path',lambda t:active_oval(t) is not None,90)
    tap_node(active_oval(tree))
    dialog=wait(prefix+'-node',lambda t:bool(matching(t,expected_title)
                    and any(n.get('resource-id')=='com.duolingo:id/learnButton' for n in t.iter('node'))),60)
    tap_node(next(n for n in dialog.iter('node') if n.get('resource-id')=='com.duolingo:id/learnButton'))

try:
    adb('shell','am','force-stop',PACKAGE)
    assert b'Success' in adb('shell','pm','clear',PACKAGE)
    with zipfile.ZipFile(WORK/'DuoAero-native-base-test.apk') as apk:
        section=json.loads(apk.read('assets/duoaero/course/section.json'))
        catalog=json.loads(apk.read('assets/duoaero/course/session-catalog.json'))
    fourth='2.3-3-point-0-lesson-3';root='files/duoaero-course/local-test';folder=root+'/submissions'
    adb('shell','run-as',PACKAGE,'mkdir','-p',folder)
    claims={};found=False
    def seed(identifier):
        lesson=catalog[identifier];now=time.time()
        proof={'id':identifier,'type':'MATH_LESSON','failed':False,'shouldLearnThings':True,
               'startTime':now-120,'endTime':now,'challenges':[{'id':q['id']} for q in lesson['challenges']]}
        write_private(folder+'/'+identifier+'.json',{'schema':1,'sessionId':identifier,'savedAt':int(now*1000),
          'nativeSubmission':proof,'completionSubmission':proof,'completedOnce':True})
    for unit in section['units']:
        for level in unit['levels']:
            if level['type']=='chest':claims[level['id']]=int(time.time()*1000);continue
            ids=[x['id'] for x in level['pathLevelClientData']['sessionMetadatas']]
            if fourth in ids:
                assert len(ids)==4 and ids[-1]==fourth
                for identifier in ids[:-1]:seed(identifier)
                found=True;break
            for identifier in ids:seed(identifier)
        if found:break
    assert found
    write_private(root+'/chests.json',claims)
    bank={q['id']:q for q in json.loads((ROOT/'app/assets/questions.json').read_text())}
    plan=json.loads((ROOT/'app/assets/lesson_plan.json').read_text())
    source=next(lesson for node in plan for lesson in node['lessons'] if lesson['id']==fourth)
    node_index=next(i for i,node in enumerate(plan) if node['id']=='2.3-3-point-0')
    next_node=plan[node_index+1];next_source=next_node['lessons'][0]
    next_question=lesson_questions([bank[qid] for qid in next_source['ids']],teach_words=True)[0]
    assert next_question['type']=='choice'
    next_parts=next_question.get('rich_text',{}).get('options',[None]*len(next_question['options']))
    next_needle=content(next_parts[next_question['answer']],next_question['options'][next_question['answer']])
    expanded=lesson_questions([bank[qid] for qid in source['ids']],teach_words=True)
    assert len(expanded)==20 and all(q['type']=='choice' for q in expanded)
    adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    wait('four-session-home',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')))
    open_active_node('four-session','Wing structural components')
    for index,q in enumerate(expanded):
        parts=q.get('rich_text',{}).get('options',[None]*len(q['options']))
        needle=content(parts[q['answer']],q['options'][q['answer']])
        tree=wait('four-session-question-'+str(index),lambda t:bool(matching(t,needle,'com.duolingo:id/mathCard')),60,True)
        time.sleep(1);tap_node(matching(tree,needle,'com.duolingo:id/mathCard')[-1])
        tree=wait('four-session-selected-'+str(index),lambda t:any(n.get('resource-id')=='com.duolingo:id/submitButton' and n.get('enabled')=='true' for n in t.iter('node')),20)
        time.sleep(1.5);tap_node(next(n for n in tree.iter('node') if n.get('resource-id')=='com.duolingo:id/submitButton' and n.get('enabled')=='true'))
        tree=wait('four-session-graded-'+str(index),lambda t:bool(matching(t,'CONTINUE') or matching(t,'GOT IT')),45)
        assert not matching(tree,'GOT IT'),'Unexpected wrong result for '+q['id']
        tap_node(matching(tree,'CONTINUE')[-1])
    deadline=time.monotonic()+90
    while time.monotonic()<deadline:
        tree=capture('four-session-complete')
        if tree is not None and matching(tree,'CLAIM XP'):
            tap_node(matching(tree,'CLAIM XP')[-1]);break
        point=claim_xp(OUT/'four-session-complete.png',OUT/'four-session-claim-ocr.png')
        if point:adb('shell','input','tap',str(point[0]),str(point[1]));break
        time.sleep(2)
    else:raise AssertionError('Claim XP missing')
    wait('four-session-returned',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')),90)
    saved=json.loads(adb('exec-out','run-as',PACKAGE,'cat',folder+'/'+fourth+'.json'))
    assert saved.get('completedOnce') is True,'Fourth session was not durably saved'
    routes=adb('logcat','-d','-s','DuoAeroNative:I').decode()
    assert 'Local original session selected: '+fourth in routes
    assert 'Durable lesson completion '+fourth+': true' in routes
    adb('shell','am','force-stop',PACKAGE);adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    wait('four-session-restarted',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')),90)
    saved=json.loads(adb('exec-out','run-as',PACKAGE,'cat',folder+'/'+fourth+'.json'))
    assert saved.get('completedOnce') is True
    open_active_node('four-session-next',next_node['name'])
    wait('four-session-next-question',lambda t:bool(matching(t,next_needle,'com.duolingo:id/mathCard')),60)
    routes=adb('logcat','-d','-s','DuoAeroNative:I').decode()
    selected=re.findall(r'Local original session selected: ([A-Za-z0-9_.-]+)',routes)
    assert selected and selected[-1]==next_source['id'],'The next node opened the wrong session'
    (OUT/'four-session-result.txt').write_text('PASS: prior path and three sessions seeded; fourth native session selected, 20 answers graded, completion saved, and next node opened after restart. Earlier progress and real Drive are not tested.\n')
finally:
    (OUT/'four-session-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroNative:I','AndroidRuntime:E'))
