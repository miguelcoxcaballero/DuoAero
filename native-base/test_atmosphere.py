"""Seed prior lessons only, then really complete the first Atmosphere lesson."""
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
    final_continue_at=None
    adb('shell','am','force-stop',PACKAGE);assert b'Success' in adb('shell','pm','clear',PACKAGE)
    with zipfile.ZipFile(WORK/'DuoAero-native-base-test.apk') as apk:
        section=json.loads(apk.read('assets/duoaero/course/section.json'))
        catalog=json.loads(apk.read('assets/duoaero/course/session-catalog.json'))
    units=section['units'];assert units[1]['teachingObjective'].startswith('2.1')
    target=units[1]['levels'][0];meta=target['pathLevelClientData']['sessionMetadatas']
    first,second=meta[0]['id'],meta[1]['id']
    assert first=='2.1-5-point-0-lesson-0'
    root='files/duoaero-course/local-test';folder=root+'/submissions'
    adb('shell','run-as',PACKAGE,'mkdir','-p',folder)
    claims={}
    for level in units[0]['levels']:
        if level['type']=='chest':claims[level['id']]=int(time.time()*1000);continue
        for entry in level['pathLevelClientData']['sessionMetadatas']:
            lesson=catalog[entry['id']];now=time.time()
            proof={'id':lesson['id'],'type':'MATH_LESSON','failed':False,'shouldLearnThings':True,
                   'startTime':now-120,'endTime':now,'challenges':[{'id':q['id']} for q in lesson['challenges']]}
            write_private(folder+'/'+lesson['id']+'.json',{'schema':1,'sessionId':lesson['id'],'savedAt':int(now*1000),'nativeSubmission':proof,'completionSubmission':proof,'completedOnce':True})
    write_private(root+'/chests.json',claims)
    bank={q['id']:q for q in json.loads((ROOT/'app/assets/questions.json').read_text())}
    plan=json.loads((ROOT/'app/assets/lesson_plan.json').read_text())
    source=next(lesson for node in plan for lesson in node['lessons'] if lesson['id']==first)
    expanded=lesson_questions([bank[qid] for qid in source['ids']],teach_words=True)
    bank.update({question['id']:question for question in expanded})
    adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    tree=wait('atmosphere-home',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')))
    open_atmosphere('atmosphere-initial')
    # Reproduce a mistake and its native retry: the reported lesson includes
    # formula/gap controllers and the user's screenshot shows wrong feedback.
    sequence=[(expanded[0]['id'],True,False)]+[(q['id'],False,HINT_TEST and q['id']==HINT_ID) for q in expanded[1:]]+[(expanded[0]['id'],False,False)]
    if HINT_TEST:sequence.append((HINT_ID,False,False))
    for index,(qid,wrong,hinted) in enumerate(sequence):
        q=bank[qid];kind=q['type']
        if kind=='choice':
            answer=(q['answer']+1)%len(q['options']) if wrong else q['answer']
            parts=q.get('rich_text',{}).get('options',[None]*len(q['options']))
            needle=content(parts[answer],q['options'][answer]);resource='com.duolingo:id/mathCard'
        elif kind=='gap':needle=q['answer'][0];resource=None
        elif kind in ('formula_blocks','formula_named'):
            assert q['answer_blocks']
            needle=q['answer_blocks'][0];resource=None
        else:raise AssertionError('Unsupported atmosphere question '+kind)
        tree=wait('atmosphere-question-'+str(index),lambda t:bool(matching(t,needle,resource)),60,True)
        if hinted:
            containers=[n for n in tree.iter('node') if n.get('resource-id')=='com.duolingo:id/calculatorAndTipContainer']
            assert len(containers)==1,'Expected native formula-hint button'
            left,top,right,bottom=map(int,re.findall(r'\d+',containers[0].get('bounds')))
            adb('shell','input','tap',str((left+3*right)//4),str((top+bottom)//2))
            hint=wait('atmosphere-hint-open',lambda t:bool(matching(t,'a tip') and matching(t,'GOT IT')),30)
            tap_node(matching(hint,'GOT IT')[-1])
            tree=wait('atmosphere-hint-dismissed',lambda t:bool(matching(t,needle,resource)),30)
            assert not matching(tree,'Oops'),'The hint graded before Check'
        candidates=matching(tree,needle,resource)
        if kind!='choice':
            # Compose often exposes the label on a non-clickable child of the
            # actual card. A touch at the label's bounds still hits the card.
            candidates=[n for n in candidates if n.get('text','')==needle or n.get('content-desc','')==needle]
            clickable=[n for n in candidates if n.get('clickable')=='true']
            if clickable:candidates=clickable
        assert candidates,'No selectable answer for '+qid
        # The card can become visible during the native page transition before
        # it accepts input. Let the transition settle, then retry the actual
        # touch only while the Check action remains disabled.
        time.sleep(1)
        choose(candidates[-1],kind,needle)
        if kind in ('formula_blocks','formula_named'):
            for next_needle in q['answer_blocks'][1:]:
                tree=wait('atmosphere-next-token-'+str(index),lambda t:bool(matching(t,next_needle)),30)
                candidates=[n for n in matching(tree,next_needle) if n.get('text','')==next_needle or n.get('content-desc','')==next_needle]
                clickable=[n for n in candidates if n.get('clickable')=='true']
                if clickable:candidates=clickable
                assert candidates,'No selectable formula token '+next_needle
                choose(candidates[-1],kind,next_needle)
        for retry in range(3):
            try:
                tree=wait('atmosphere-selected-'+str(index),lambda t:any(n.get('resource-id')=='com.duolingo:id/submitButton' and n.get('enabled')=='true' for n in t.iter('node')),10)
                break
            except AssertionError:
                if retry==2:raise
                tree=wait('atmosphere-retry-'+str(index),lambda t:bool(matching(t,needle,resource)),10)
                candidates=matching(tree,needle,resource)
                if kind!='choice':
                    candidates=[n for n in candidates if n.get('text','')==needle or n.get('content-desc','')==needle]
                    clickable=[n for n in candidates if n.get('clickable')=='true']
                    if clickable:candidates=clickable
                assert candidates,'Answer disappeared while waiting: '+qid
                choose(candidates[-1],kind,needle)
        if kind=='choice':time.sleep(1.5)  # Original asynchronous JS grading.
        tap_node(next(n for n in tree.iter('node') if n.get('resource-id')=='com.duolingo:id/submitButton' and n.get('enabled')=='true'))
        tree=wait('atmosphere-graded-'+str(index),lambda t:bool(matching(t,'CONTINUE') or matching(t,'GOT IT')),45)
        if wrong or hinted:
            assert matching(tree,'GOT IT'),'Expected incorrect feedback for '+qid
            tap_node(matching(tree,'GOT IT')[-1])
        else:
            assert not matching(tree,'GOT IT'),'Answer graded incorrectly for '+qid
            recorder=None
            if index == len(sequence)-1 and os.environ.get('DUOAERO_CAPTURE_COMPLETION')=='1':
                # Start before the final transition so the recording includes
                # the native celebration rather than just its final frame.
                recorder=subprocess.Popen(['adb','shell','screenrecord','--time-limit','60',
                                           '/sdcard/duoaero-lesson-completion.mp4'],
                                          stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                time.sleep(.8)
            if index == len(sequence)-1:
                final_continue_at=time.monotonic()
            tap_node(matching(tree,'CONTINUE')[-1])
    deadline=time.monotonic()+90
    while time.monotonic()<deadline:
        tree=capture('atmosphere-complete')
        if tree is not None and matching(tree,'CLAIM XP'):
            claim_seen_at=time.monotonic()
            tap_node(matching(tree,'CLAIM XP')[-1]);break
        # Some original Rive summaries expose neither text nor a special ID.
        # OCR verifies the visible button before tapping it.
        point=claim_xp(OUT/'atmosphere-complete.png',OUT/'atmosphere-claim-ocr.png')
        if point:
            claim_seen_at=time.monotonic()
            adb('shell','input','tap',str(point[0]),str(point[1]));break
        time.sleep(2)
    else:raise AssertionError('Claim XP missing')
    if os.environ.get('DUOAERO_CAPTURE_COMPLETION')=='1' and recorder is not None:
        # Stop only once Claim XP is observed. Waiting synchronously for a
        # fixed recording length distorted timing and could miss the end.
        subprocess.run(['adb','shell','kill -INT $(pidof screenrecord)'],check=False,
                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=10)
        try:recorder.wait(timeout=10)
        except subprocess.TimeoutExpired:recorder.kill();recorder.wait()
        subprocess.run(['adb','pull','/sdcard/duoaero-lesson-completion.mp4',str(OUT/'lesson-completion.mp4')],
                       check=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30)
    if final_continue_at is not None and os.environ.get('DUOAERO_CAPTURE_COMPLETION')!='1':
        (OUT/'atmosphere-latency.txt').write_text(
            'Elapsed from initiating final Continue to observing Claim XP: '
            +str(round(claim_seen_at-final_continue_at,2))+' s. Includes adb and screenshot/OCR detection overhead; emulator only.\n')
    tree=wait('atmosphere-returned-home',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')),90)
    saved=json.loads(adb('exec-out','run-as',PACKAGE,'cat',folder+'/'+first+'.json'))
    assert saved.get('completedOnce') is True,'Atmosphere completion was not accepted and stored'
    # Observe the exact original session selected after returning, before any restart.
    routes=adb('logcat','-d','-s','DuoAeroNative:I').decode()
    assert 'Durable lesson completion '+first+': true' in routes,'No confirmed native completion'
    next_source=next(lesson for node in plan for lesson in node['lessons'] if lesson['id']==second)
    next_q=bank[next_source['ids'][0]];assert next_q['type']=='choice'
    next_index=next_q['answer'];next_parts=next_q.get('rich_text',{}).get('options',[None]*len(next_q['options']))
    next_answer=content(next_parts[next_index],next_q['options'][next_index])
    for phase in ('live','restart'):
        if phase=='restart':
            adb('shell','am','force-stop',PACKAGE)
            adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
            wait('atmosphere-restarted-home',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')))
        open_atmosphere('atmosphere-'+phase)
        wait('atmosphere-next-'+phase,lambda t:bool(matching(t,next_answer,'com.duolingo:id/mathCard')),60)
        routes=adb('logcat','-d','-s','DuoAeroNative:I').decode()
        selected=re.findall(r'Local original session selected: ([A-Za-z0-9_.-]+)',routes)
        assert selected and selected[-1]==second,'First Atmosphere node reopened the wrong lesson: '+phase
    (OUT/'atmosphere-result.txt').write_text('PASS: seeded earlier nodes; completed all real Atmosphere questions'+(' with a formula hint and end-of-lesson retry' if HINT_TEST else '')+', claimed XP, observed durable completion and opened its next lesson before and after restart. Earlier lessons and real Google/Drive are not tested.\n')
finally:
    (OUT/'atmosphere-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroNative:I','AndroidRuntime:E'))
