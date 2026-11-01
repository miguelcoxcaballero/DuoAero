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
  check(!NativeCourseProgress.isCompleted(copy(good).put("id","other"),lesson));
  check(!NativeCourseProgress.isCompleted(copy(good).put("endTime",0),lesson));
  check(!NativeCourseProgress.isCompleted(copy(good).put("challenges",new JSONArray("[{id:'q1'},{id:'q1'}]")),lesson));
  check(!NativeCourseProgress.isCompleted(copy(good).put("challenges",new JSONArray("[{id:'q1'},{id:'foreign'}]")),lesson));
  check(NativeCourseProgress.isCompleted(copy(good).put("challenges",new JSONArray("[{id:'q1'},{id:'q1'},{id:'q2'}]")),lesson));
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
  System.out.println("PASS: "+checks+" native completion/projection boundary checks; actual submission schema and restart persistence require device acceptance");
 }
}
''', encoding='utf-8')
classpath = os.pathsep.join(map(str, [WORK / 'json-20250517.jar', WORK / 'classes', JAR]))
subprocess.run([java('javac'), '-cp', classpath, '-d', WORK / 'classes', source], check=True)
subprocess.run([java('java'), '-cp', classpath, 'CourseProgressCheck'], check=True)
