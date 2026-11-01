from pathlib import Path
import subprocess,zipfile,shutil
from runtime_config import ROOT as R, WORK as W, SDK, BT, JAR as platform, KEY, ADB, java, tool
import sys
import json
from rich_question import content
from formula_exercises import prototypes
def run(*args):subprocess.run([str(a) for a in args],check=True)
for folder in ['testclasses','testdex']:
 path=W/folder
 if path.exists():shutil.rmtree(path)
 path.mkdir(parents=True,exist_ok=True)
run(tool('aapt2'),'link','-o',W/'tests.apk','--manifest',R/'native-base/tests/AndroidManifest.xml','-I',platform)
run(java('javac'),'--release','8','-encoding','UTF-8','-classpath',platform,'-d',W/'testclasses',*list((R/'native-base/tests').glob('*.java')))
run(java('java'),'-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--lib',platform,'--min-api','29','--output',W/'testdex',*list((W/'testclasses').rglob('*.class')))
with zipfile.ZipFile(W/'tests.apk','a') as z:
 z.write(W/'testdex/classes.dex','classes.dex')
 for fixture in (R/'native-base/tests/fixtures').glob('*.json'):z.write(fixture,'assets/'+fixture.name)
 # Expected selections come from the source bank, independently of native JS
 # grading. The target APK supplies only the diagnostic question order.
 with zipfile.ZipFile(W/'DuoAero-native-base-test.apk') as target:
  lesson=json.loads(target.read('assets/hardcoded_sessions/duoaero/aerospace_rich_lesson.json'))
 bank={q['id']:q for q in json.loads((R/'app/assets/questions.json').read_text(encoding='utf-8-sig'))}
 from course_adapter import lesson_questions
 expanded_bank={part['id']:part for q in bank.values() for part in lesson_questions([q])}
 formula_questions=prototypes()+[q for q in bank.values() if q['type']=='formula_blocks']
 z.writestr('assets/formula-selections.json',json.dumps([{'id':q['id'],'tokens':q['answer_blocks']} for q in formula_questions]))
 selections=[]
 for challenge in lesson['challenges']:
  question=expanded_bank[challenge['id']];index=question['answer']
  rich=question.get('rich_text',{}).get('options',[None]*len(question['options']))
  selections.append({'id':question['id'],'answer':content(rich[index],question['options'][index])})
 z.writestr('assets/rich-session-selections.json',json.dumps(selections))
 plan=json.loads((R/'app/assets/lesson_plan.json').read_text())
 path_selections=[]
 for question_id in plan[0]['lessons'][0]['ids']:
  question=bank[question_id]
  assert question['type']=='choice', 'Path completion probe needs a reviewed driver for this question type'
  index=question['answer'];rich=question.get('rich_text',{}).get('options',[None]*len(question['options']))
  path_selections.append({'id':question_id,'answer':content(rich[index],question['options'][index])})
 z.writestr('assets/path-session-selections.json',json.dumps(path_selections))
run(java('java'),'-jar',BT/'lib/apksigner.jar','sign','--ks',KEY,'--ks-pass','pass:android','--out',W/'tests-signed.apk',W/'tests.apk')
if '--build-only' not in sys.argv:run(ADB,'install','-r',W/'tests-signed.apk')
