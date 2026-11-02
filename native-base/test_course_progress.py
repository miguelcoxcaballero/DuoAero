"""Test real completion validation and path projection; not a persistence/UI claim."""
import os
import subprocess
from runtime_config import WORK, JAR, java

# Use the pinned host JSON dependency verified by test_profile_response.
import test_profile_response

source = WORK / 'CourseProgressCheck.java'
source.write_text('''
import org.json.*;
import java.util.*;
import com.duoaero.nativebase.NativeCourseProgress;
import com.duoaero.nativebase.NativeQuestionLedger;
public class CourseProgressCheck {
 static int checks;
 static void check(boolean value){if(!value)throw new AssertionError("case "+checks);checks++;}
 static JSONObject copy(JSONObject o){return new JSONObject(o.toString());}
 static JSONObject level(JSONObject section,int unit)throws Exception{return section.getJSONArray("units").getJSONObject(unit).getJSONArray("levels").getJSONObject(0);}
 public static void main(String[] args)throws Exception{
  JSONObject lesson=new JSONObject("{id:'lesson-1',challenges:[{id:'q1'},{id:'q2'}]}");
  JSONObject good=new JSONObject("{id:'lesson-1',type:'MATH_LESSON',failed:false,shouldLearnThings:true,startTime:1,endTime:2,challenges:[{id:'q1'},{id:'q2'}]}");
  check(NativeCourseProgress.isCompleted(good,lesson));
  for(String field:new String[]{"id","type","failed","shouldLearnThings","startTime","endTime","challenges"}){
   JSONObject bad=copy(good);bad.remove(field);check(!NativeCourseProgress.isCompleted(bad,lesson));
  }
  check(!NativeCourseProgress.isCompleted(copy(good).put("failed",true),lesson));
  check(!NativeCourseProgress.isCompleted(copy(good).put("shouldLearnThings",false),lesson));
  check(NativeCourseProgress.reviewCompletionIssue(copy(good).put("shouldLearnThings",false),lesson)==null);
  JSONObject missingReviewFlag=copy(good);missingReviewFlag.remove("shouldLearnThings");
  check(NativeCourseProgress.reviewCompletionIssue(missingReviewFlag,lesson)!=null);
  check(NativeCourseProgress.reviewCompletionIssue(copy(good).put("failed",true),lesson)!=null);
  check(NativeCourseProgress.reviewCompletionIssue(copy(good).put("challenges",new JSONArray("[{id:'q1'}]")),lesson)!=null);
  check(!NativeCourseProgress.isCompleted(copy(good).put("id","other"),lesson));
  check(!NativeCourseProgress.isCompleted(copy(good).put("endTime",0),lesson));
  check(!NativeCourseProgress.isCompleted(copy(good).put("challenges",new JSONArray("[{id:'q1'},{id:'q1'}]")),lesson));
  check(!NativeCourseProgress.isCompleted(copy(good).put("challenges",new JSONArray("[{id:'q1'},{id:'foreign'}]")),lesson));
  check(NativeCourseProgress.isCompleted(copy(good).put("challenges",new JSONArray("[{id:'q1'},{id:'q1'},{id:'q2'}]")),lesson));
  JSONObject expanded=new JSONObject("{id:'lesson-1',challenges:[{id:'q1'},{id:'q2'},{id:'q3'}]}");
  check(!NativeCourseProgress.isCompleted(good,expanded));
  check(NativeCourseProgress.isRecordedCompletion(good,expanded,lesson));
  check(!NativeCourseProgress.isRecordedCompletion(copy(good).put("failed",true),expanded,lesson));
  check(!NativeCourseProgress.isRecordedCompletion(good,expanded,copy(lesson).put("id","other")));
  check(!NativeCourseProgress.isRecordedCompletion(good,expanded,null));
  JSONArray history=new JSONArray().put(lesson);
  check(NativeCourseProgress.isRecordedCompletion(good,expanded,null,history));
  check(!NativeCourseProgress.isRecordedCompletion(copy(good).put("challenges",new JSONArray("[{id:'q1'}]")),expanded,null,history));
  check(!NativeCourseProgress.isRecordedCompletion(copy(good).put("challenges",new JSONArray("[{id:'q1'},{id:'q2'},{id:'foreign'}]")),expanded,null,history));
  check(!NativeCourseProgress.isRecordedCompletion(good,expanded,null,new JSONArray().put(copy(lesson).put("id","other"))));
  JSONObject migrations=new JSONObject("{newLesson:{sourceLesson:'lesson-1',requiredQuestions:['q1','q2']}}");
  Set<String> real=new HashSet<>(Collections.singleton("lesson-1"));
  Map<String,Set<String>> verified=new HashMap<>();verified.put("lesson-1",new HashSet<>(Arrays.asList("q1","q2")));
  check(NativeCourseProgress.projectedCompletions(real,migrations,verified).contains("newLesson"));
  check(!real.contains("newLesson")); // projection did not create a submission
  verified.put("lesson-1",Collections.singleton("q1"));
  check(!NativeCourseProgress.projectedCompletions(real,migrations,verified).contains("newLesson"));
  verified.put("lesson-1",new HashSet<>(Arrays.asList("q1","q2")));
  check(!NativeCourseProgress.projectedCompletions(Collections.emptySet(),migrations,verified).contains("newLesson"));
  check(!NativeCourseProgress.projectedCompletions(real,migrations,Collections.emptyMap()).contains("newLesson"));
  JSONObject duplicate=new JSONObject("{newLesson:{sourceLesson:'lesson-1',requiredQuestions:['q1','q1']}}");
  check(!NativeCourseProgress.projectedCompletions(real,duplicate,verified).contains("newLesson"));
  JSONObject course=new JSONObject("{pathSectionsSummary:[{id:'section'}]}");
  JSONObject section=new JSONObject("{id:'section',units:[{levels:[{pathLevelClientData:{sessionMetadatas:[{id:'a'},{id:'b'}]}}]},{levels:[{pathLevelClientData:{sessionMetadatas:[{id:'c'}]}}]}]}");
  NativeCourseProgress.project(course,section,Collections.emptySet());
  check(level(section,0).getString("state").equals("active")&&level(section,1).getString("state").equals("locked"));
  NativeCourseProgress.project(course,section,new HashSet<>(Arrays.asList("a","foreign")));
  check(level(section,0).getInt("finishedSessions")==1&&level(section,0).getString("state").equals("active"));
  check(level(section,1).getString("state").equals("locked"));
  NativeCourseProgress.project(course,section,new HashSet<>(Arrays.asList("a","b")));
  check(level(section,0).getString("state").equals("passed")&&level(section,1).getString("state").equals("active"));
  check(course.getJSONArray("pathSectionsSummary").getJSONObject(0).getInt("completedUnits")==1);
  NativeCourseProgress.project(course,section,new HashSet<>(Arrays.asList("a","b","c")));
  check(level(section,1).getString("state").equals("passed"));
  check(course.getJSONArray("pathSectionsSummary").getJSONObject(0).getJSONArray("completedLevelsPerUnit").toString().equals("[1,1]"));
  String snapshot=section.toString();NativeCourseProgress.project(course,section,new HashSet<>(Arrays.asList("a","b","c")));
  check(snapshot.equals(section.toString()));
  JSONObject chest=new JSONObject("{id:'chest1',type:'chest',pathLevelClientData:{}}");
  section.getJSONArray("units").getJSONObject(0).getJSONArray("levels").put(chest);
  NativeCourseProgress.project(course,section,Collections.emptySet(),Collections.emptySet());
  check(chest.getString("state").equals("locked"));
  NativeCourseProgress.project(course,section,new HashSet<>(Arrays.asList("a","b")),Collections.emptySet());
  check(chest.getString("state").equals("active")&&chest.getInt("finishedSessions")==0);
  check(level(section,1).getString("state").equals("locked"));
  NativeCourseProgress.project(course,section,new HashSet<>(Arrays.asList("a","b")),Collections.singleton("chest1"));
  check(chest.getString("state").equals("passed")&&chest.getInt("finishedSessions")==1);
  check(level(section,1).getString("state").equals("active"));
  check(course.getJSONArray("pathSectionsSummary").getJSONObject(0).getInt("completedUnits")==1);
  JSONObject twoCourse=new JSONObject("{pathSectionsSummary:[{id:'first'},{id:'second'}]}");
  JSONObject firstSection=new JSONObject("{id:'first',units:[{levels:[{pathLevelClientData:{sessionMetadatas:[{id:'first-lesson'}]}}]}]}");
  JSONObject secondSection=new JSONObject("{id:'second',units:[{levels:[{pathLevelClientData:{sessionMetadatas:[{id:'second-a'}]}}]},{levels:[{pathLevelClientData:{sessionMetadatas:[{id:'second-b'}]}}]}]}");
  Set<String> done=new HashSet<>(Arrays.asList("first-lesson","second-a"));
  NativeCourseProgress.project(twoCourse,firstSection,done);
  NativeCourseProgress.project(twoCourse,secondSection,done);
  check(level(firstSection,0).getString("state").equals("passed"));
  check(level(secondSection,0).getString("state").equals("passed")&&level(secondSection,1).getString("state").equals("active"));
  check(twoCourse.getJSONArray("pathSectionsSummary").getJSONObject(0).getInt("completedUnits")==1);
  check(twoCourse.getJSONArray("pathSectionsSummary").getJSONObject(1).getInt("completedUnits")==1);
  JSONObject records=new JSONObject();
  NativeQuestionLedger.record(records,"q1",false,100,"lesson1");
  NativeQuestionLedger.record(records,"q2",false,200,"lesson2");
  check(NativeQuestionLedger.unresolved(records).equals(Arrays.asList("q1","q2")));
  NativeQuestionLedger.record(records,"q1",true,300,"review1");
  check(NativeQuestionLedger.unresolved(records).equals(Arrays.asList("q2")));
  check(records.getJSONObject("q1").getInt("misses")==1);
  NativeQuestionLedger.record(records,"q1",false,150,"older-device");
  check(records.getJSONObject("q1").getBoolean("correct"));
  NativeQuestionLedger.record(records,"q1",false,400,"lesson3");
  check(NativeQuestionLedger.unresolved(records).equals(Arrays.asList("q2","q1")));
  check(records.getJSONObject("q1").getInt("misses")==2);
  NativeQuestionLedger.record(records,"q2",true,500,"review2");
  NativeQuestionLedger.record(records,"q1",true,600,"review2");
  check(NativeQuestionLedger.unresolved(records).isEmpty());
  System.out.println("PASS: "+checks+" native completion/projection boundary checks; actual submission schema and restart persistence require device acceptance");
 }
}
''', encoding='utf-8')
classpath = os.pathsep.join(map(str, [WORK / 'json-20250517.jar', WORK / 'classes', JAR]))
subprocess.run([java('javac'), '-cp', classpath, '-d', WORK / 'classes', source], check=True)
subprocess.run([java('java'), '-cp', classpath, 'CourseProgressCheck'], check=True)
