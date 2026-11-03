"""Seed prior diagnostic sessions, then finish a later second-midterm base lesson on the native path.

This uses a synthetic local account. It does not establish real Drive or
Google migration, editorial acceptance, or production second-midterm coverage.
"""
import json, os, re, subprocess, time, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from runtime_config import WORK
from visual_controls import claim_xp, native_positive_banner

OUT=Path(os.environ['DUOAERO_EVIDENCE']); PACKAGE='com.duoaero.nativebase'
TOPIC=os.environ['DUOAERO_LATER_BASE_TOPIC']; assert TOPIC in ('4','5.1','5.2')
TITLE={'4':'Missiles','5.1':'Diverse aircraft','5.2':'Rotorcraft'}[TOPIC]
def adb(*args): return subprocess.check_output(['adb',*args],timeout=35)
def capture(name):
    try:
        adb('shell','timeout','15','uiautomator','dump','/sdcard/extra-section.xml')
        raw=adb('exec-out','cat','/sdcard/extra-section.xml'); tree=ET.fromstring(raw)
        (OUT/(name+'.xml')).write_bytes(raw)
    except (ET.ParseError,subprocess.SubprocessError): tree=None
    (OUT/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'))
    return tree

def has(tree,value):
    return any(value.casefold() in (n.get('text','')+' '+n.get('content-desc','')).casefold() for n in tree.iter('node'))
from feedback_checks import assert_native_correct, feedback_terminal

def wait(name,predicate,seconds=90):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        tree=capture(name)
        if tree is not None and predicate(tree):return tree
        time.sleep(2)
    raise AssertionError('Not observed: '+name)
def wait_correct(name, context, seconds=60):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        tree=capture(name)
        if tree is None:
            time.sleep(2);continue
        if feedback_terminal(tree):
            assert_native_correct(tree, context)
            return tree
        # The original final-question celebration is drawn, but absent from the
        # accessibility dump. Verify its actual positive banner via OCR only
        # when an enabled Continue is present, and still reject error/skip.
        if any(n.get('text','')=='CONTINUE' and n.get('enabled')=='true' for n in tree.iter('node')):
            visual=native_positive_banner(OUT/(name+'.png'), OUT/(name+'-banner.png'))
            if visual:
                assert_native_correct(tree, context, visual_positive=True)
                return tree
        time.sleep(2)
    raise AssertionError('Positive native feedback not observed: '+context)

def tap(node):
    a,b,c,d=map(int,re.findall(r'\d+',node.get('bounds')))
    x=str((a+c)//2);y=str((b+d)//2)
    adb('shell','input','swipe',x,y,x,y,'100')
def write_private(path,data):
    assert re.fullmatch(r'[A-Za-z0-9_./-]+',path)
    subprocess.run(['adb','shell','run-as',PACKAGE,'sh','-c',"'cat > "+path+"'"],input=json.dumps(data).encode(),check=True,timeout=30)

def open_second_section(prefix):
    home=wait(prefix+'-home',lambda t:any(n.get('resource-id')=='com.duolingo:id/primaryCardView' for n in t.iter('node')) or (has(t,'Midterm 2') and any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node'))),120)
    if has(home,'Midterm 2') and any(n.get('resource-id')=='com.duolingo:id/oval' for n in home.iter('node')):
        return home
    tap(next(n for n in home.iter('node') if n.get('resource-id')=='com.duolingo:id/primaryCardView'))
    picker=wait(prefix+'-picker',lambda t:has(t,'Midterm 2') and not any(n.get('resource-id')=='com.duolingo:id/path' for n in t.iter('node')))
    labels=[n for n in picker.iter('node') if 'midterm 2' in n.get('text','').casefold()];assert labels;tap(labels[-1])
    expanded=wait(prefix+'-expanded',lambda t:len([n for n in t.iter('node') if n.get('text','').casefold()=='midterm 2'])>=2)
    tap([n for n in expanded.iter('node') if n.get('text','').casefold()=='midterm 2'][-1])
    return wait(prefix+'-path',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')),120)

def open_topic(topic,title,prefix):
    for attempt in range(10):
        path=capture(prefix+'-path-'+str(attempt))
        if path is not None:
            headers=[n for n in path.iter('node') if n.get('resource-id')=='com.duolingo:id/headerText']
            target=next((n for n in headers if n.get('text','').casefold().startswith(topic.casefold()+' ·')),None)
            if target is not None:
                top=int(re.findall(r'\d+',target.get('bounds'))[3])
                later=[int(re.findall(r'\d+',n.get('bounds'))[1]) for n in headers if int(re.findall(r'\d+',n.get('bounds'))[1])>top]
                end=min(later) if later else 99999
                levels=[n for n in path.iter('node') if n.get('resource-id')=='com.duolingo:id/oval' and top<int(re.findall(r'\d+',n.get('bounds'))[1])<end]
                if levels:
                    tap(levels[0])
                    popup=wait(prefix+'-node',lambda t:any(n.get('resource-id')=='com.duolingo:id/titleText' for n in t.iter('node')),30)
                    assert any(n.get('resource-id')=='com.duolingo:id/titleText' and n.get('text','').casefold()==title.casefold() for n in popup.iter('node')), 'Wrong node opened: '+topic
                    buttons=[n for n in popup.iter('node') if n.get('resource-id')=='com.duolingo:id/learnButton' and n.get('enabled')=='true']
                    assert buttons,'Target node is locked: '+topic
                    tap(buttons[0]);return
        adb('shell','input','swipe','700','2200','700','700','500');time.sleep(1)
    raise AssertionError('Diagnostic node not visible: '+topic)

try:
    adb('shell','am','force-stop',PACKAGE);assert b'Success' in adb('shell','pm','clear',PACKAGE)
    with zipfile.ZipFile(WORK/'DuoAero-native-base-test.apk') as apk:
        catalog=json.loads(apk.read('assets/duoaero/course/session-catalog.json'))
        section=json.loads(apk.read('assets/duoaero/course/section-2.json'))
    for topic in ('4','5.1','5.2'):
        expected=['second-partial-'+topic+'-lesson-'+str(i) for i in (range(1) if topic=='4' else range(2))]
        assert all(k in catalog for k in expected)
        assert any([x['id'] for x in level['pathLevelClientData'].get('sessionMetadatas',[])]==expected
                   for unit in section['units'] for level in unit['levels'])
    folder='files/duoaero-course/local-test/submissions';adb('shell','run-as',PACKAGE,'mkdir','-p',folder)
    identifiers=[entry['id'] for unit in section['units'][:{'4':3,'5.1':4,'5.2':5}[TOPIC]] for entry in unit['levels'][0]['pathLevelClientData']['sessionMetadatas']]
    for identifier in identifiers:
        lesson=catalog[identifier];now=time.time()
        proof={'id':identifier,'type':'MATH_LESSON','failed':False,'shouldLearnThings':True,
               'startTime':now-120,'endTime':now,'challenges':[{'id':q['id']} for q in lesson['challenges']]}
        write_private(folder+'/'+identifier+'.json',{'schema':1,'sessionId':identifier,'savedAt':int(now*1000),
                      'nativeSubmission':proof,'completionSubmission':proof,'completedOnce':True})
    adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    path=open_second_section('extra-section')
    open_topic(TOPIC,TITLE,'base-space')
    questions=[q for q in json.loads((Path(__file__).resolve().parents[1]/'research/midterm2_concepts.json').read_text())['questions'] if q['topic']==TOPIC]; assert len(questions)==10
    for index,q in enumerate(questions):
        answer=q['options'][q['answer']]
        question=wait('extra-section-question-'+str(index),lambda t:has(t,answer),90)
        choices=[n for n in question.iter('node') if answer in (n.get('text','')+' '+n.get('content-desc','')) and n.get('resource-id')=='com.duolingo:id/mathCard']
        assert choices,'Expected draft answer card '+q['id'];tap(choices[-1])
        ready=wait('extra-section-ready-'+str(index),lambda t:any(n.get('text','')=='CHECK' and n.get('enabled')=='true' for n in t.iter('node')),30)
        tap(next(n for n in ready.iter('node') if n.get('text','')=='CHECK' and n.get('enabled')=='true'))
        feedback=wait_correct('extra-section-feedback-'+str(index), 'Question '+q['id'])
        tap(next(n for n in feedback.iter('node') if n.get('text','')=='CONTINUE' and n.get('enabled')=='true'))
    end=time.monotonic()+100
    while time.monotonic()<end:
        complete=capture('extra-section-complete')
        buttons=[] if complete is None else [n for n in complete.iter('node') if n.get('text','')=='CLAIM XP']
        if buttons:tap(buttons[-1]);break
        point=claim_xp(OUT/'extra-section-complete.png',OUT/'extra-section-claim-ocr.png')
        if point:adb('shell','input','tap',str(point[0]),str(point[1]));break
        time.sleep(2)
    else:raise AssertionError('Claim XP missing')
    wait('extra-section-after',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')),120)
    saved=json.loads(adb('exec-out','run-as',PACKAGE,'cat',folder+'/second-partial-'+TOPIC+'-lesson-0.json'))
    assert saved.get('completedOnce') is True
    adb('shell','am','force-stop',PACKAGE);adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    open_second_section('extra-section-restart')
    reloaded=json.loads(adb('exec-out','run-as',PACKAGE,'cat',folder+'/second-partial-'+TOPIC+'-lesson-0.json'))
    assert reloaded.get('completedOnce') is True
    (OUT/('later-base-'+TOPIC+'-result.txt')).write_text('PASS: seeded earlier diagnostic topics, completed base '+TOPIC+' lesson and verified its original saved submission after restart; real accounts and remaining course unverified.\n')
finally:
    (OUT/'extra-section-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroNative:I','AndroidRuntime:E'))
