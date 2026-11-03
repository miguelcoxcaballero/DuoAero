"""Check isolated range-path APK data; does not exercise Android navigation."""
import json,sys,zipfile
from pathlib import Path
from runtime_config import ROOT,WORK
sys.path.insert(0,str(ROOT/'research'))
from jet_range_path_draft import candidate
from path_adapter import build_path,stable_id
from course_adapter import session
bank=json.loads((ROOT/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
original=json.loads((ROOT/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
cb,cp=candidate(bank,original);by={q['id']:q for q in cb}
_,_,expected=build_path(cp,cb)
with zipfile.ZipFile(WORK/'DuoAero-native-base-test.apk') as apk:
 def load(name):return json.loads(apk.read('assets/duoaero/course/'+name+'.json'))
 index,catalog,migrations,chests=(load(n) for n in ('lesson-index','session-catalog','lesson-migrations','legacy-chest-requirements'))
 assert index==expected
 new={name for name in index if name.startswith('2.2-range-draft')}
 assert len(new)==13 and not new.intersection(migrations)
 for node in cp:
  for pos,lesson in enumerate(node['lessons']):
   if lesson['id'] in new:
    expected_session=session([by[x] for x in lesson['ids']],lesson['id'],stable_id('skill',node['id']),teach_words=True)
    assert [q['id'] for q in catalog[lesson['id']]['challenges']]==[q['id'] for q in expected_session['challenges']]
 history_lessons=[]
 for node in original:
  history_lessons.extend(q['id'] for q in node['lessons'])
  assert chests[stable_id('chest',node['id'])]==history_lessons
 for version in ('1.3.0','1.3.5','1.3.6','1.3.7'):
  old=load('history-'+version)
  assert not new.intersection(old)
print('PASS: packaged diagnostic range path, 13 uncredited sessions and historical chest requirements; Android navigation not asserted.')
