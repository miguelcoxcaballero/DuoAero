package com.duoaero.nativebase;

import org.json.*;
import java.util.*;

/** Pure projection of acknowledged lesson completions onto original path data. */
public final class NativeCourseProgress {
 private NativeCourseProgress(){}
 public static boolean isCompleted(JSONObject submission,JSONObject lesson)throws JSONException {
  return completionIssue(submission,lesson)==null;
 }
 /** Accept an already-recorded proof against its explicitly preserved old lesson. */
 public static boolean isRecordedCompletion(JSONObject submission,JSONObject lesson,JSONObject legacy)throws JSONException {
  return submission!=null&&(isCompleted(submission,lesson)
      ||(legacy!=null&&lesson.getString("id").equals(legacy.optString("id"))&&isCompleted(submission,legacy)));
 }
 /** Historical proofs are checked against the exact published question set,
  * never against an arbitrary subset of the current lesson. */
 public static boolean isRecordedCompletion(JSONObject submission,JSONObject lesson,JSONObject legacy,JSONArray history)throws JSONException {
  if(isRecordedCompletion(submission,lesson,legacy))return true;
  if(submission==null||history==null)return false;
  for(int i=0;i<history.length();i++){
   JSONObject previous=history.optJSONObject(i);
   if(previous!=null&&lesson.getString("id").equals(previous.optString("id"))&&isCompleted(submission,previous))return true;
  }
  return false;
 }
 public static String completionIssue(JSONObject submission,JSONObject lesson)throws JSONException {
  return completionIssue(submission,lesson,true);
 }
 public static String reviewCompletionIssue(JSONObject submission,JSONObject lesson)throws JSONException {
  return completionIssue(submission,lesson,false);
 }
 private static String completionIssue(JSONObject submission,JSONObject lesson,boolean requireLearning)throws JSONException {
  if(!lesson.getString("id").equals(submission.optString("id")))return "lesson identity mismatch";
  if(!"MATH_LESSON".equals(submission.optString("type")))return "unexpected session type";
  if(!Boolean.FALSE.equals(submission.opt("failed")))return "failed or missing success flag";
  if(!(submission.opt("shouldLearnThings") instanceof Boolean)||(requireLearning&&!Boolean.TRUE.equals(submission.opt("shouldLearnThings"))))return "missing native learning authorization";
  double start=submission.optDouble("startTime",Double.NaN),end=submission.optDouble("endTime",Double.NaN);
  if(!Double.isFinite(start)||!Double.isFinite(end)||start<0||end<start||end<=0)return "missing or invalid completion times";
  JSONArray expected=lesson.getJSONArray("challenges"),actual=submission.optJSONArray("challenges");
  if(expected.length()==0||actual==null)return "no submitted challenges";
  Set<String> wanted=new HashSet<>(),seen=new HashSet<>();
  for(int i=0;i<expected.length();i++)wanted.add(expected.getJSONObject(i).getString("id"));
  for(int i=0;i<actual.length();i++){
   JSONObject challenge=actual.optJSONObject(i);
   if(challenge==null||!wanted.contains(challenge.optString("id")))return "unknown submitted challenge";
   seen.add(challenge.getString("id"));
  }
  return wanted.equals(seen)?null:"incomplete lesson question coverage";
 }
 public static void project(JSONObject course,JSONObject section,Set<String> completed)throws JSONException {
  project(course,section,completed,Collections.emptySet());
 }
 public static void project(JSONObject course,JSONObject section,Set<String> completed,Set<String> chests)throws JSONException {
  JSONArray units=section.getJSONArray("units"),completedPerUnit=new JSONArray();
  boolean activeAssigned=false;
  int completedUnits=0;
  for(int i=0;i<units.length();i++){
   JSONArray levels=units.getJSONObject(i).getJSONArray("levels");int passed=0;
   for(int j=0;j<levels.length();j++){
    JSONObject level=levels.getJSONObject(j);
    if("chest".equals(level.optString("type"))){
     boolean claimed=chests.contains(level.getString("id"));
     level.put("finishedSessions",claimed?1:0);
     if(claimed){level.put("state","passed");passed++;}
     else if(!activeAssigned){level.put("state","active");activeAssigned=true;}
     else level.put("state","locked");
     continue;
    }
    JSONArray lessons=level.getJSONObject("pathLevelClientData").getJSONArray("sessionMetadatas");
    int count=0;for(int k=0;k<lessons.length();k++)if(completed.contains(lessons.getJSONObject(k).getString("id")))count++;
    level.put("finishedSessions",count);
    if(count==lessons.length()&&count>0){level.put("state","passed");passed++;}
    else if(!activeAssigned){level.put("state","active");activeAssigned=true;}
    else level.put("state","locked");
   }
   completedPerUnit.put(passed);
   if(levels.length()>0&&passed==levels.length())completedUnits++;
  }
  JSONArray tabs=course.optJSONArray("pathTabsSummary");
  if(tabs!=null)for(int i=0;i<tabs.length();i++){
   JSONArray groups=tabs.getJSONObject(i).getJSONArray("pathSectionGroups");
   for(int j=0;j<groups.length();j++){
    JSONObject group=groups.getJSONObject(j);JSONArray ids=group.getJSONArray("sectionIds");
    if(ids.length()==1&&section.getString("id").equals(ids.getString(0)))group.put("completedUnits",completedUnits);
   }
  }
  JSONArray summaries=course.getJSONArray("pathSectionsSummary");
  for(int i=0;i<summaries.length();i++){
   JSONObject summary=summaries.getJSONObject(i);
   if(section.getString("id").equals(summary.getString("id")))summary.put("completedUnits",completedUnits).put("completedLevelsPerUnit",completedPerUnit);
  }
 }
}
