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

OUT=Path(os.environ.get('DUOAERO_EVIDENCE','/tmp/duoaero-evidence'))
OUT.mkdir(parents=True,exist_ok=True)
PACKAGE='com.duoaero.nativebase'

def adb(*args):
    return subprocess.check_output(['adb',*args],timeout=30)

def capture(name):
    (OUT/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'))
    adb('shell','rm','-f','/sdcard/duoaero-standalone.xml')
    dump=adb('shell','uiautomator','dump','/sdcard/duoaero-standalone.xml')
    result=subprocess.run(['adb','exec-out','cat','/sdcard/duoaero-standalone.xml'],capture_output=True,timeout=30)
    xml=result.stdout
    try:
        tree=ET.fromstring(xml)
    except ET.ParseError:
        # Android can temporarily expose no root during a real screen change.
        # Preserve that observation and keep waiting; never treat it as a pass.
        with (OUT/'standalone-capture-retries.txt').open('ab') as log:log.write(dump+b'\n'+xml+b'\n')
        return None
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

try:
    adb('shell','am','force-stop',PACKAGE)
    assert b'Success' in adb('shell','pm','clear',PACKAGE)
    adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    tree=wait_for('standalone-home',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')) and any('Midterm 1' in n.get('text','') for n in t.iter('node')))
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
    # Exact original grade_correct_* strings, including randomized variants.
    positive={'Amazing!','Awesome!','Correct!','Excellent!','Good job!','Great!','Great job!','Nice job!','Nice!','Nicely done!','Wow!'}
    question_ids=list(plan[0]['lessons'][0]['ids'])
    if os.environ.get('DUOAERO_TEST_MISTAKES')=='1':
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
        # The final correct ribbon renders its lettering inside Rive, which
        # exposes no text node. Its original graded action is CONTINUE; a wrong
        # answer exposes GOT IT. Require the current answer card as well so a
        # between-question celebration cannot satisfy this observation.
        def correct_feedback(t):
            labels={n.get('text','').strip().casefold() for n in t.iter('node')}
            current=any(answer in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node'))
            return current and 'continue' in labels and 'got it' not in labels
        tree=wait_for('standalone-graded-'+str(i),correct_feedback,30)
        tap(tree,text='CONTINUE')
    tree=wait_for('standalone-complete',lambda t:any(n.get('text','').strip()=='CLAIM XP' for n in t.iter('node')),60)
    tap(tree,text='CLAIM XP')
    tree=wait_for('standalone-returned-home',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')),60)
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
    (OUT/'standalone-before-restart-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroNative:I','AndroidRuntime:E'))
    adb('shell','am','force-stop',PACKAGE)
    adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    tree=wait_for('standalone-restored-home',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')))
    restored=json.loads(adb('exec-out','run-as',PACKAGE,'cat',store))
    assert restored['sessionId']==first_id and restored['completedOnce'] is True, 'Completion lost after process restart'
    tap(tree,'com.duolingo:id/oval')
    second_id=plan[0]['lessons'][1]['id']
    second=bank[plan[0]['lessons'][1]['ids'][0]]
    assert second['type']=='choice' and not second.get('rich_text')
    second_answer=second['options'][second['answer']]
    tree=wait_for('standalone-restored-node',lambda t:any(n.get('resource-id')=='com.duolingo:id/learnButton' or second_answer in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),60)
    if any(n.get('resource-id')=='com.duolingo:id/learnButton' for n in tree.iter('node')):tap(tree,'com.duolingo:id/learnButton')
    wait_for('standalone-next-lesson',lambda t:any(second_answer in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),60)
    routes=adb('logcat','-d','-s','DuoAeroNative:I').decode()
    selected=re.findall(r'Local original session selected: ([A-Za-z0-9_-]+)',routes)
    assert selected and selected[-1]==second_id, 'Restored path did not select its next lesson'
    (OUT/'standalone-result.txt').write_text('PASS: cold start, 19 correct native answers, Claim XP, return to path, committed completion after process restart, and next lesson selected through the original node. This does not establish the entire course or account/Drive behavior.\n')
finally:
    (OUT/'standalone-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroNative:I','AndroidRuntime:E','chromium:E'))
    (OUT/'standalone-anr.txt').write_bytes(adb('shell','dumpsys','activity','lastanr'))
