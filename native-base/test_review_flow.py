"""Real UI continuation after the caller has made and persisted one mistake."""
import json
import re
import time
from visual_controls import claim_xp


def run(adb, tap, wait_for, capture, out, package, question, first_lesson):
    adb('shell','am','force-stop',package)
    adb('shell','am','start','-W','-n',package+'/com.duolingo.splash.LaunchActivity')
    tree=wait_for('review-home',lambda t:any(n.get('resource-id')=='com.duolingo:id/tabProfile' for n in t.iter('node')))
    tap(tree,'com.duolingo:id/tabProfile')
    settings_ids={'com.duolingo:id/settingsButton','com.duolingo:id/menuSettings'}
    tree=wait_for('review-profile',lambda t:any(n.get('resource-id') in settings_ids for n in t.iter('node')),60)
    control=next(n.get('resource-id') for n in tree.iter('node') if n.get('resource-id') in settings_ids)
    tap(tree,control)
    for attempt in range(35):
        tree=capture('review-settings')
        if tree is not None and any(n.get('text')=='Review mistakes' for n in tree.iter('node')):
            tap(tree,text='Review mistakes')
            break
        if tree is not None:
            scroll=next((n for n in tree.iter('node') if n.get('scrollable')=='true'),None)
            if scroll is not None:
                x1,y1,x2,y2=map(int,re.findall(r'\d+',scroll.get('bounds')))
                adb('shell','input','swipe',str((x1+x2)//2),str(y1+(y2-y1)*3//4),str((x1+x2)//2),str(y1+(y2-y1)//4),'450')
        time.sleep(2)
    else:
        raise AssertionError('Original settings did not expose Review mistakes')
    answer=question['options'][question['answer']]
    tree=wait_for('review-question',lambda t:any(answer in (n.get('text','')+n.get('content-desc','')) for n in t.iter('node')),60)
    routes=adb('logcat','-d','-s','DuoAeroNative:I').decode()
    selected=re.findall(r'Local original mistake review selected: (review_[a-f0-9]{32})',routes)
    assert selected, 'Original loader did not select the saved mistake review'
    review_id=selected[-1]
    tap(tree,text=answer)
    tree=wait_for('review-selected',lambda t:any(n.get('resource-id')=='com.duolingo:id/submitButton' and n.get('enabled')=='true' for n in t.iter('node')),15)
    tap(tree,'com.duolingo:id/submitButton')
    tree=wait_for('review-graded',lambda t:any(n.get('text','').strip()=='CONTINUE' for n in t.iter('node')) and not any(n.get('text','').strip()=='GOT IT' for n in t.iter('node')),30)
    tap(tree,text='CONTINUE')
    for attempt in range(35):
        tree=capture('review-complete')
        if tree is not None:
            if any(n.get('text','').strip().casefold()=='claim xp' for n in tree.iter('node')):
                node=next(n for n in tree.iter('node') if n.get('text','').strip().casefold()=='claim xp')
                tap(tree,text=node.get('text'));break
            if any(n.get('resource-id')=='com.duolingo:id/sessionCompleteAnimationView' for n in tree.iter('node')):
                point=claim_xp(out/'review-complete.png',out/'review-claim-ocr.png')
                if point:
                    adb('shell','input','tap',str(point[0]),str(point[1]));break
            if any(n.get('text','').strip()=='CONTINUE' for n in tree.iter('node')):
                tap(tree,text='CONTINUE')
        time.sleep(3)
    else:raise AssertionError('Original review Claim XP was not rendered')
    wait_for('review-return',lambda t:any(n.get('resource-id')=='com.duolingo:id/tabProfile' or n.get('text')=='Review mistakes' for n in t.iter('node')),60)
    base='files/duoaero-course/local-test/'
    saved=json.loads(adb('exec-out','run-as',package,'cat',base+'reviews/'+review_id+'-submission.json'))
    assert saved['sessionId']==review_id and saved['completed'] is True
    ledger=json.loads(adb('exec-out','run-as',package,'cat',base+'question-state.json'))
    record=ledger['records'][question['id']]
    assert record['correct'] is True and record['misses']==1 and record['session']==review_id
    # A short review must never complete the original unfinished course lesson.
    raw=adb('exec-out','run-as',package,'sh','-c',"cat '"+base+'submissions/'+first_lesson+".json' 2>/dev/null || true")
    assert not raw.strip() or json.loads(raw)['completedOnce'] is False
    adb('shell','am','force-stop',package)
    adb('shell','am','start','-W','-n',package+'/com.duolingo.splash.LaunchActivity')
    wait_for('review-restarted',lambda t:any(n.get('resource-id')=='com.duolingo:id/oval' for n in t.iter('node')))
    restored=json.loads(adb('exec-out','run-as',package,'cat',base+'question-state.json'))
    assert restored['records'][question['id']]['correct'] is True
    (out/'review-result.txt').write_text('PASS: actual wrong answer, process restart, original settings review entry, original question/grade/completion, persistent correction after restart, no course lesson falsely completed.\n')
