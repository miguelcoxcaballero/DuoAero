"""Exact published-proof regression for a newly added TSFC lesson."""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from runtime_config import ROOT, WORK, java

source_id='2.2-3-point-0-lesson-0'
target_id='2.2-3-point-1-lesson-3'
plan=json.loads((ROOT/'app/assets/lesson_plan.json').read_text())
source=next(l for n in plan for l in n['lessons'] if l['id']==source_id)
target=next(l for n in plan for l in n['lessons'] if l['id']==target_id)
assert target['ids']==['TA1-0173-F1'] and 'TA1-0173-F1' not in source['ids']
assert target_id not in json.loads((ROOT/'native-base/lesson-migrations.json').read_text())
jar=WORK/'json-20250517.jar'
assert jar.is_file(), 'Set DUOAERO_WORK to the verified host dependency directory'
with tempfile.TemporaryDirectory() as folder:
    folder=Path(folder)
    java_source=folder/'TsfcHistoryCheck.java'
    java_source.write_text('''import org.json.*;
import java.nio.file.*;
import com.duoaero.nativebase.NativeCourseProgress;
public class TsfcHistoryCheck {
 public static void main(String[] args)throws Exception {
  JSONObject old=new JSONObject(Files.readString(Path.of(args[0])));
  JSONObject current=new JSONObject(Files.readString(Path.of(args[1])));
  JSONObject fresh=new JSONObject().put("id",args[2]).put("challenges",new JSONArray().put(new JSONObject().put("id","TA1-0173-F1")));
  JSONArray responses=new JSONArray();JSONArray expected=old.getJSONArray("challenges");
  for(int i=0;i<expected.length();i++)responses.put(new JSONObject().put("id",expected.getJSONObject(i).getString("id")));
  JSONObject proof=new JSONObject().put("id",old.getString("id")).put("type","MATH_LESSON").put("failed",false).put("shouldLearnThings",true).put("startTime",1).put("endTime",2).put("challenges",responses);
  if(!NativeCourseProgress.isRecordedCompletion(proof,current,null,new JSONArray().put(old)))throw new AssertionError("Exact historic proof lost");
  if(NativeCourseProgress.isRecordedCompletion(proof,fresh,null,new JSONArray().put(old)))throw new AssertionError("Historic proof credited a different lesson");
 }
}''')
    subprocess.run([str(java('javac')),'-cp',str(jar),'-d',str(folder),str(ROOT/'native-base/src/com/duoaero/nativebase/NativeCourseProgress.java'),str(java_source)],check=True)
    current={'id':source_id,'challenges':[{'id':qid} for qid in source['ids']]}
    current_path=folder/'current.json';current_path.write_text(json.dumps(current))
    for version in ('1.3.0','1.3.5','1.3.6','1.3.7'):
        snapshot=json.loads((ROOT/'native-base/session-history'/f'{version}.json').read_text())
        assert target_id not in snapshot
        old=snapshot[source_id]
        assert any(q['id']=='TA1-0173-F1' for q in old['challenges'])
        old_path=folder/'old.json';old_path.write_text(json.dumps(old))
        subprocess.run([str(java('java')),'-cp',os.pathsep.join((str(jar),str(folder))),'TsfcHistoryCheck',str(old_path),str(current_path),target_id],check=True)
print('PASS: exact four published source proofs remain valid and cannot complete the new lesson; Android/account persistence pending.')
