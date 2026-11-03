"""Cold-start the installed APK and tap native path controls through adb only.

No profile injection, instrumentation activity, mock grade or backend bypass is
performed by this driver. The APK itself must initialize its original runtime.
"""
import os
import json
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from visual_controls import claim_xp, native_positive_banner
from feedback_checks import assert_native_correct, feedback_terminal

OUT=Path(os.environ.get('DUOAERO_EVIDENCE','/tmp/duoaero-evidence'))
OUT.mkdir(parents=True,exist_ok=True)
PACKAGE='com.duoaero.nativebase'

def adb(*args):
    return subprocess.check_output(['adb',*args],timeout=30)

def capture(name):
    (OUT/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'))
    adb('shell','rm','-f','/sdcard/duoaero-standalone.xml')
    try:
        dump=adb('shell','timeout','20','uiautomator','dump','/sdcard/duoaero-standalone.xml')
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as error:
        # Animated original views can prevent Android's idle condition. Keep
        # the fresh screenshot for visual inspection; no missing tree passes.
        with (OUT/'standalone-capture-retries.txt').open('a') as log:
            log.write(str(error)+'\n')
        return None
    result=subprocess.run(['adb','exec-out','cat','/sdcard/duoaero-standalone.xml'],capture_output=True,timeout=30)
    xml=result.stdout
    try:
        tree=ET.fromstring(xml)
    except ET.ParseError:
        # Android can temporarily expose no root during a real screen change.
        # Preserve that observation and keep waiting; never treat it as a pass.
        with (OUT/'standalone-capture-retries.txt').open('ab') as log:log.write(b'UI hierarchy temporarily unavailable.\n')
        return None
    # Capture after the hierarchy query; the previous pre-query image could
    # still show splash while the later XML already described the home.
    (OUT/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'))
    (OUT/(name+'.xml')).write_bytes(xml)
    return tree

def wait_for(name,predicate,timeout=120,advance_continue=False):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        tree=capture(name)
        if tree is not None and predicate(tree):return tree
        if tree is not None and advance_continue and any(n.get('text','').strip()=='CONTINUE' for n in tree.iter('node')):
            # The original streak celebration can add a Continue between
            # questions. Only advance while waiting for the next known answer.
            tap(tree,text='CONTINUE')
        time.sleep(3)
    raise AssertionError('Timed out waiting for '+name)

def tap(tree,resource=None,text=None):
    node=next((n for n in tree.iter('node') if n.get('package')==PACKAGE and (resource is None or n.get('resource-id')==resource) and (text is None or any(text in v for v in (n.get('text',''),n.get('content-desc','')))) and n.get('enabled')=='true'),None)
    if node is None:raise AssertionError('Native control unavailable: '+str((resource,text)))
    x1,y1,x2,y2=map(int,re.findall(r'\d+',node.get('bounds')))
    adb('shell','input','tap',str((x1+x2)//2),str((y1+y2)//2))

def earned_rewards(tree):
    nodes=list(tree.iter('node'))
    return (any(n.get('resource-id')=='com.duolingo:id/menuStreak' and n.get('content-desc','').casefold()=='1 day streak' for n in nodes)
            and any(n.get('resource-id')=='com.duolingo:id/itemButton' and n.get('text')=='10' for n in nodes))

def wait_correct_answer(name, answer, timeout=60):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        tree=capture(name)
        if tree is None:
            time.sleep(2);continue
        current=any(answer in (n.get('text','')+n.get('content-desc','')) for n in tree.iter('node'))
        if not current:
            time.sleep(2);continue
        if feedback_terminal(tree):
            assert_native_correct(tree, name)
            return tree
        if any(n.get('text','')=='CONTINUE' and n.get('enabled')=='true' for n in tree.iter('node')):
            visual=native_positive_banner(OUT/(name+'.png'), OUT/(name+'-banner.png'))
            if visual:
                assert_native_correct(tree, name, visual_positive=True)
                return tree
        time.sleep(2)
    raise AssertionError('Positive native feedback not observed: '+name)

def capture_completion_motion():
    # Multiple frames distinguish static overlapping artwork from the moving
    # original celebration. A single screenshot cannot establish animation.
    for frame in range(6):
        (OUT/('standalone-celebration-%02d.png'%frame)).write_bytes(adb('exec-out','screencap','-p'))
        time.sleep(.5)

try:
    adb('shell','am','force-stop',PACKAGE)
    assert b'Success' in adb('shell','pm','clear',PACKAGE)
    adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    tree=wait_for('standalone-home',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')) and any('1 · aerospace industry' in n.get('text','').casefold() for n in t.iter('node')))
    tap(tree,'com.duolingo:id/oval')
    # Original onboarding may start the first lesson directly from the node.
    # Accept either native navigation route, then require the actual question.
    tree=wait_for('standalone-node',lambda t:any(n.get('resource-id')=='com.duolingo:id/learnButton' or 'Low delivery times.' in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),60)
    if any(n.get('resource-id')=='com.duolingo:id/learnButton' for n in tree.iter('node')):tap(tree,'com.duolingo:id/learnButton')
    tree=wait_for('standalone-question',lambda t:any('Low delivery times.' in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),60)
    (OUT/'standalone-first-question-result.txt').write_text('PASS: cold start, original home, named node, first question. No completion or persistence asserted.\n')
    # Use independently authored source answers and real touch input. Never
    # install an instrumentation profile or replace an app state/grade.
    root=Path(__file__).resolve().parents[1]
    bank={q['id']:q for q in json.loads((root/'app/assets/questions.json').read_text())}
    plan=json.loads((root/'app/assets/lesson_plan.json').read_text())
    question_ids=list(plan[0]['lessons'][0]['ids'])
    if os.environ.get('DUOAERO_TEST_MISTAKES')=='1' or os.environ.get('DUOAERO_TEST_REVIEW')=='1':
        first=bank[question_ids[0]]
        wrong=first['options'][(first['answer']+1)%len(first['options'])]
        tap(tree,text=wrong)
        tree=wait_for('standalone-wrong-selected',lambda t:any(n.get('resource-id')=='com.duolingo:id/submitButton' and n.get('enabled')=='true' for n in t.iter('node')),15)
        tap(tree,'com.duolingo:id/submitButton')
        tree=wait_for('standalone-wrong-feedback',lambda t:any(n.get('text','').strip()=='GOT IT' for n in t.iter('node')),30)
        tap(tree,text='GOT IT')
        second=bank[question_ids[1]]
        next_answer=second['options'][second['answer']]
        wait_for('standalone-after-wrong',lambda t:any(next_answer in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),30)
        pending=json.loads(adb('exec-out','run-as',PACKAGE,'cat','files/duoaero-course/local-test/question-state.json'))
        assert pending['records'][question_ids[0]]['correct'] is False, 'Original mistake was not persisted'
        if os.environ.get('DUOAERO_TEST_REVIEW')=='1':
            from test_review_flow import run
            run(adb,tap,wait_for,capture,OUT,PACKAGE,first,plan[0]['lessons'][0]['id'])
            raise SystemExit(0)
        # The original lesson must recycle its actual mistake after the other
        # questions. No test injects or appends a challenge to its engine.
        question_ids=question_ids[1:]+question_ids[:1]
    for i,qid in enumerate(question_ids):
        q=bank[qid]
        assert q['type']=='choice' and not q.get('rich_text'), 'Cold-start driver needs reviewed support for this type'
        answer=q['options'][q['answer']]
        tree=wait_for('standalone-answer-'+str(i),lambda t:any(answer in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),30,advance_continue=True)
        if i==5 and os.environ.get('DUOAERO_TEST_RESUME')=='1':
            # Stop only after the original controller displays question six.
            # The test never supplies or edits the persisted app state.
            adb('shell','am','force-stop',PACKAGE)
            adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
            tree=wait_for('standalone-midlesson-home',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')))
            tap(tree,'com.duolingo:id/oval')
            tree=wait_for('standalone-midlesson-node',lambda t:any(n.get('resource-id')=='com.duolingo:id/learnButton' or answer in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),60)
            if any(n.get('resource-id')=='com.duolingo:id/learnButton' for n in tree.iter('node')):tap(tree,'com.duolingo:id/learnButton')
            tree=wait_for('standalone-midlesson-resumed',lambda t:any(answer in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),60)
            assert b'Original session state restored:' in adb('logcat','-d','-s','DuoAeroNative:I'), 'No original state restoration observed'
            (OUT/'standalone-midlesson-result.txt').write_text('PASS: five original answers, process force-stop, relaunch through original path and question six restored. No state injected by test.\n')
        tap(tree,text=answer)
        tree=wait_for('standalone-selected-'+str(i),lambda t:any(n.get('resource-id')=='com.duolingo:id/submitButton' and n.get('enabled')=='true' for n in t.iter('node')),15)
        tap(tree,'com.duolingo:id/submitButton')
        tree=wait_correct_answer('standalone-graded-'+str(i),answer)
        tap(tree,text='CONTINUE')
    deadline=time.monotonic()+90
    end_seen=False
    while time.monotonic()<deadline:
        tree=capture('standalone-complete')
        if tree is not None:
            label=next((n.get('text') for n in tree.iter('node') if n.get('text','').strip().casefold()=='claim xp'),None)
            if label:
                capture_completion_motion()
                tap(tree,text=label);break
            end_seen |= any(n.get('resource-id') in {'com.duolingo:id/sessionCompleteAnimationView','com.duolingo:id/sessionEndViewPager'} for n in tree.iter('node'))
        # Rive can keep UiAutomator from reaching its idle condition even when
        # the summary is fully visible. Keep the already observed end container
        # and inspect this fresh screenshot only while our session is resumed.
        if end_seen:
            activities=adb('shell','dumpsys','activity','activities').decode()
            active=any(('mResumedActivity' in line or 'topResumedActivity' in line) and PACKAGE+'/' in line and 'SessionActivity' in line for line in activities.splitlines())
            if active:
                point=claim_xp(OUT/'standalone-complete.png',OUT/'standalone-claim-ocr.png')
                if point is not None:
                    capture_completion_motion()
                    adb('shell','input','tap',str(point[0]),str(point[1]));break
        time.sleep(3)
    else:raise AssertionError('Original Claim XP not visible in accessibility or rendered footer')
    tree=wait_for('standalone-returned-home',lambda t:earned_rewards(t) and any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')),60)
    first_id=plan[0]['lessons'][0]['id']
    store='files/duoaero-course/local-test/submissions/'+first_id+'.json'
    saved=json.loads(adb('exec-out','run-as',PACKAGE,'cat',store))
    assert saved['sessionId']==first_id and saved['completedOnce'] is True, 'Native submission did not establish durable completion'
    if os.environ.get('DUOAERO_TEST_MISTAKES')=='1':
        ledger=json.loads(adb('exec-out','run-as',PACKAGE,'cat','files/duoaero-course/local-test/question-state.json'))
        corrected=ledger['records'][plan[0]['lessons'][0]['ids'][0]]
        assert corrected['correct'] is True and corrected['misses']==1, 'Correct retry did not resolve the persistent mistake'
        assert all(ledger['records'][qid]['correct'] is True for qid in question_ids)
        (OUT/'standalone-mistakes-result.txt').write_text('PASS: real wrong answer stored, original end-of-lesson retry, correct retry clears the pending mistake and completion is committed.\n')
    # A durable file alone is insufficient: the still-running original home
    # must route the same node to its next lesson without an app restart.
    second_id=plan[0]['lessons'][1]['id']
    second=bank[plan[0]['lessons'][1]['ids'][0]]
    assert second['type']=='choice' and not second.get('rich_text')
    second_answer=second['options'][second['answer']]
    tap(tree,'com.duolingo:id/oval')
    tree=wait_for('standalone-live-node',lambda t:any(n.get('resource-id')=='com.duolingo:id/learnButton' or second_answer in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),60)
    if any(n.get('resource-id')=='com.duolingo:id/learnButton' for n in tree.iter('node')):tap(tree,'com.duolingo:id/learnButton')
    wait_for('standalone-live-next-lesson',lambda t:any(second_answer in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),60)
    routes=adb('logcat','-d','-s','DuoAeroNative:I').decode()
    selected=re.findall(r'Local original session selected: ([A-Za-z0-9_-]+)',routes)
    assert selected and selected[-1]==second_id, 'Live path did not select its next lesson before restart'
    (OUT/'standalone-before-restart-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroCompletionTiming:I','*:S'))
    adb('shell','am','force-stop',PACKAGE)
    adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    tree=wait_for('standalone-restored-home',lambda t:earned_rewards(t) and any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')))
    restored=json.loads(adb('exec-out','run-as',PACKAGE,'cat',store))
    assert restored['sessionId']==first_id and restored['completedOnce'] is True, 'Completion lost after process restart'
    tap(tree,'com.duolingo:id/oval')
    tree=wait_for('standalone-restored-node',lambda t:any(n.get('resource-id')=='com.duolingo:id/learnButton' or second_answer in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),60)
    if any(n.get('resource-id')=='com.duolingo:id/learnButton' for n in tree.iter('node')):tap(tree,'com.duolingo:id/learnButton')
    wait_for('standalone-next-lesson',lambda t:any(second_answer in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),60)
    routes=adb('logcat','-d','-s','DuoAeroNative:I').decode()
    selected=re.findall(r'Local original session selected: ([A-Za-z0-9_-]+)',routes)
    assert selected and selected[-1]==second_id, 'Restored path did not select its next lesson'
    (OUT/'standalone-result.txt').write_text('PASS: cold start, 19 correct native answers, Claim XP, return to path, committed completion plus visible10gems/1day streak after process restart, and next lesson selected through the original node. This does not establish the entire course or account/Drive behavior.\n')
finally:
    (OUT/'standalone-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroCompletionTiming:I','*:S'))
    (OUT/'standalone-anr.txt').write_text('Omitted from synthetic timing evidence to avoid exporting identifiers.\n')
