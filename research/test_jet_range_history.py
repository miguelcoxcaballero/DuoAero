"""Exercise exact published proofs against the isolated candidate plan."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'native-base'))
from runtime_config import WORK,java
from jet_range_path_draft import candidate
from course_adapter import session
bank=json.loads((root/'app/assets/questions.json').read_text(encoding='utf-8-sig'))
plan=json.loads((root/'app/assets/lesson_plan.json').read_text(encoding='utf-8-sig'))
cb,cp=candidate(bank,plan);by={q['id']:q for q in cb}
old={l['id']:l for n in plan for l in n['lessons']}
new={l['id']:l for n in cp for l in n['lessons']}
changed=[k for k,v in old.items() if v['ids']!=new[k]['ids']]
target=[k for k in new if k.startswith('2.2-range-draft')]
assert len(changed)==3 and len(target)==13
jar=WORK/'json-20250517.jar';assert jar.is_file()
with tempfile.TemporaryDirectory() as tmp:
 tmp=Path(tmp);src=tmp/'RangeHistory.java'
 src.write_text('''import org.json.*; import java.nio.file.*;
import com.duoaero.nativebase.NativeCourseProgress;
public class RangeHistory {
 public static void main(String[] a)throws Exception {
  JSONObject old=new JSONObject(Files.readString(Path.of(a[0])));
  JSONObject current=new JSONObject(Files.readString(Path.of(a[1])));
  JSONObject target=new JSONObject(Files.readString(Path.of(a[2])));
  JSONArray responses=new JSONArray(); JSONArray questions=old.getJSONArray("challenges");
  for(int i=0;i<questions.length();i++) responses.put(new JSONObject().put("id",questions.getJSONObject(i).getString("id")));
  JSONObject proof=new JSONObject().put("id",old.getString("id")).put("type","MATH_LESSON").put("failed",false).put("shouldLearnThings",true).put("startTime",1).put("endTime",2).put("challenges",responses);
  if(!NativeCourseProgress.isRecordedCompletion(proof,current,null,new JSONArray().put(old))) throw new AssertionError("Historic proof lost");
  if(NativeCourseProgress.isRecordedCompletion(proof,target,null,new JSONArray().put(old))) throw new AssertionError("New lesson credited");
 }
}''')
 subprocess.run([str(java('javac')),'-cp',str(jar),'-d',str(tmp),str(root/'native-base/src/com/duoaero/nativebase/NativeCourseProgress.java'),str(src)],check=True)
 for version in ('1.3.0','1.3.5','1.3.6','1.3.7'):
  history=json.loads((root/'native-base/session-history'/f'{version}.json').read_text())
  for name in changed:
   source=history[name];current=session([by[x] for x in new[name]['ids']],name,teach_words=True)
   for target_id in target:
    dest=session([by[x] for x in new[target_id]['ids']],target_id,teach_words=True)
    files=[]
    for i,obj in enumerate((source,current,dest)):
     path=tmp/f'{i}.json';path.write_text(json.dumps(obj));files.append(str(path))
    subprocess.run([str(java('java')),'-cp',os.pathsep.join((str(jar),str(tmp))),'RangeHistory',*files],check=True)
print('PASS: exact historical proofs retained for three original lessons and do not complete 13 new lesson IDs; Android persistence pending.')
