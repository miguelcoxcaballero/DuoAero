package com.duoaero.nativebase;

import org.json.*;
import java.util.*;

/** Pure projection of acknowledged lesson completions onto original path data. */
public final class NativeCourseProgress {
 private NativeCourseProgress(){}
 public static boolean isCompleted(JSONObject submission,JSONObject lesson)throws JSONException {
  return completionIssue(submission,lesson)==null;
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
  JSONArray units=section.getJSONArray("units"),completedPerUnit=new JSONArray();
  boolean activeAssigned=false;
  int completedUnits=0;
  for(int i=0;i<units.length();i++){
   JSONArray levels=units.getJSONObject(i).getJSONArray("levels");int passed=0;
   for(int j=0;j<levels.length();j++){
    JSONObject level=levels.getJSONObject(j);
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
  JSONArray summaries=course.getJSONArray("pathSectionsSummary");
  for(int i=0;i<summaries.length();i++){
   JSONObject summary=summaries.getJSONObject(i);
   if(section.getString("id").equals(summary.getString("id")))summary.put("completedUnits",completedUnits).put("completedLevelsPerUnit",completedPerUnit);
  }
 }
}
