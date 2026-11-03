"""Prepare an isolated emulator account for a *seeded* range-path probe.

Old proofs use exact published 1.3.7 challenge sets. The one prior TSFC lesson
without a historical version is explicitly simulated from its current test
catalog. This is not a continuous-journey or real-account test.
"""
import json,re,subprocess,time,zipfile
from pathlib import Path
from runtime_config import WORK
PACKAGE='com.duoaero.nativebase'; TARGET='2.2-range-draft-formula-lesson-0'
def adb(*args):return subprocess.check_output(['adb',*args],timeout=45)
def write(path,data):
 assert re.fullmatch(r'[A-Za-z0-9_./-]+',path)
 subprocess.run(['adb','shell','run-as',PACKAGE,'sh','-c',"'cat > "+path+"'"],input=json.dumps(data).encode(),check=True,timeout=30)
assert adb('shell','getprop','ro.kernel.qemu').strip()==b'1', 'Only the isolated emulator is supported'
with zipfile.ZipFile(WORK/'DuoAero-native-base-test.apk') as apk:
 def read(name):return json.loads(apk.read('assets/duoaero/course/'+name+'.json'))
 section,catalog,history,migrations=(read(n) for n in ('section','session-catalog','history-1.3.7','lesson-migrations'))
prior=[];claims={};found=False
for unit in section['units']:
 for level in unit['levels']:
  if level['type']=='chest':claims[level['id']]=int(time.time()*1000);continue
  ids=[e['id'] for e in level['pathLevelClientData']['sessionMetadatas']]
  if TARGET in ids:found=True;break
  prior.extend(ids)
 if found:break
assert found and TARGET not in history and TARGET not in migrations
explicit=[x for x in prior if x not in history and x not in migrations]
assert explicit==['2.2-3-point-1-lesson-3'],explicit
for target in prior:
 if target not in history and target in migrations:
  migration=migrations[target];source=migration['sourceLesson']
  assert source in prior and source in history
  assert set(migration['requiredQuestions']) <= {x['id'] for x in history[source]['challenges']}
adb('shell','am','force-stop',PACKAGE);assert b'Success' in adb('shell','pm','clear',PACKAGE)
root='files/duoaero-course/local-test';folder=root+'/submissions'
adb('shell','run-as',PACKAGE,'mkdir','-p',folder)
for identifier in prior:
 if identifier not in history and identifier not in explicit:continue
 lesson=history[identifier] if identifier in history else catalog[identifier]
 now=time.time();proof={'id':identifier,'type':'MATH_LESSON','failed':False,'shouldLearnThings':True,
  'startTime':now-120,'endTime':now,'challenges':[{'id':q['id']} for q in lesson['challenges']]}
 write(folder+'/'+identifier+'.json',{'schema':1,'sessionId':identifier,'savedAt':int(now*1000),
   'nativeSubmission':proof,'completionSubmission':proof,'completedOnce':True})
write(root+'/chests.json',claims)
print('Prepared isolated account with exact historic proofs, synthetic TSFC prior proof and synthetic chest claims; target remains uncompleted.')
