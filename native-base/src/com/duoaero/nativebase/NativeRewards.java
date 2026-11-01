package com.duoaero.nativebase;

import android.app.Application;
import org.json.*;
import java.time.*;
import java.util.*;

/** Reward projection from validated completion proofs; never an incrementing balance. */
final class NativeRewards {
 private NativeRewards(){}
 private static boolean observing;
 private static final java.util.concurrent.ExecutorService refresh=java.util.concurrent.Executors.newSingleThreadExecutor(r->new Thread(r,"duoaero-rewards"));
 static synchronized void observe(Application app){
  if(observing)return;observing=true;
  app.registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
   public void onActivityResumed(android.app.Activity activity){
    if(!NativeCourseBridge.hasLocalCourse()||activity.getClass().getName().contains("SessionActivity"))return;
    refresh(app,false);
   }
   public void onActivityCreated(android.app.Activity a,android.os.Bundle b){}
   public void onActivityStarted(android.app.Activity a){}
   public void onActivityPaused(android.app.Activity a){}
   public void onActivityStopped(android.app.Activity a){}
   public void onActivitySaveInstanceState(android.app.Activity a,android.os.Bundle b){}
   public void onActivityDestroyed(android.app.Activity a){}
  });
 }
 static void refresh(Application app,boolean path){
  String account=NativeAccountStore.current(app);
  refresh.execute(()->{synchronized(NativeAccountStore.LOCK){
   if(!account.equals(NativeAccountStore.current(app))||!NativeCourseBridge.hasLocalCourse())return;
   try{NativeLocalProfile.refreshRewards(app);if(path)NativeLocalCache.install(app,true);}
   catch(Exception error){android.util.Log.e("DuoAeroNative","Cannot refresh earned rewards",error);}
  }});
 }
 static JSONObject profile(Application app,JSONObject profile)throws Exception {
  ZoneId zone=ZoneId.systemDefault();
  project(NativeSessionStore.exportCompletions(app),profile,zone,LocalDate.now(zone));
  JSONObject gems=profile.getJSONObject("gemsConfig");
  Set<String> claimed=NativeChestRewards.ids(NativeChestRewards.snapshot(app));
  claimed.retainAll(NativeChestRewards.eligible(app));
  gems.put("gems",gems.getInt("gems")+claimed.size()*NativeChestRewards.GEMS);
  profile.put("rewardBundles",NativeChestRewards.bundles());
  return profile;
 }
 static JSONObject project(JSONObject lessons,JSONObject profile,ZoneId zone,LocalDate today)throws Exception {
  SortedSet<LocalDate> days=new TreeSet<>();
  for(Iterator<String> keys=lessons.keys();keys.hasNext();){
   JSONObject record=lessons.getJSONObject(keys.next());
   JSONArray studied=record.optJSONArray("studyDays");
   if(studied!=null)for(int i=0;i<studied.length();i++)days.add(LocalDate.parse(studied.getString(i)));
   // Migrate existing completions using their actual native end time, not
   // import time (which would falsely manufacture a streak today).
   long millis=(long)(record.getJSONObject("nativeCompletion").getDouble("endTime")*1000);
   if(millis>0)days.add(Instant.ofEpochMilli(millis).atZone(zone).toLocalDate());
  }
  days.removeIf(day->day.isAfter(today));
  int current=streak(days,today),longest=0,run=0;
  LocalDate previous=null,bestStart=null,bestEnd=null;
  for(LocalDate day:days){
   run=previous!=null&&previous.plusDays(1).equals(day)?run+1:1;
   if(run>longest){longest=run;bestEnd=day;bestStart=day.minusDays(run-1);}
   previous=day;
  }
  JSONObject lifetime=new JSONObject().put("length",longest);
  if(bestEnd!=null)lifetime.put("startDate",bestStart.toString()).put("endDate",bestEnd.toString()).put("achieveDate",bestEnd.toString());
  JSONObject streak=new JSONObject().put("length",current).put("updatedTimeZone",zone.getId())
   .put("updatedTimestamp",previous==null?0:previous.atStartOfDay(zone).toEpochSecond()).put("longestStreak",lifetime);
  if(previous!=null){
   JSONObject timeline=new JSONObject().put("length",current>0?current:run)
    .put("startDate",previous.minusDays((current>0?current:run)-1).toString())
    .put("endDate",previous.toString()).put("lastExtendedDate",previous.toString());
   // Original header observes UserStreak.currentStreak, not legacy length.
   streak.put(current>0?"currentStreak":"previousStreak",timeline);
  }
  if(current>0)streak.put("startTimestamp",previous.minusDays(current-1).atStartOfDay(zone).toEpochSecond());
  profile.put("streakData",streak).put("streak",current)
   .put("gemsConfig",new JSONObject().put("gems",lessons.length()*10).put("gemsPerSkill",10).put("useGems",true))
   .put("totalXp",lessons.length()*20);
  return profile;
 }
 static int streak(Set<LocalDate> days,LocalDate today){
  LocalDate cursor=days.contains(today)?today:today.minusDays(1);
  int length=0;while(days.contains(cursor)){length++;cursor=cursor.minusDays(1);}return length;
 }
 static JSONArray mergeDays(JSONArray left,JSONArray right){
  SortedSet<String> days=new TreeSet<>();LocalDate today=LocalDate.now();
  for(JSONArray values:new JSONArray[]{left,right})if(values!=null)for(int i=0;i<values.length();i++){
   try{LocalDate date=LocalDate.parse(values.optString(i));if(!date.isAfter(today))days.add(date.toString());}
   catch(java.time.format.DateTimeParseException invalid){}
  }
  return new JSONArray(days);
 }
}
