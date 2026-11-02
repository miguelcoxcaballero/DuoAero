package com.duoaero.nativebase;

import android.app.Application;
import android.util.AtomicFile;
import org.json.JSONObject;
import java.io.*;
import java.util.*;

/** Atomic native submissions and monotonic completion, isolated to local test identity. */
public final class NativeSessionStore {
 private NativeSessionStore(){}
 private static JSONObject legacyCatalog;
 private static JSONObject[] historicalCatalogs;
 private static JSONObject migrations;
 private static JSONObject migrations(Application app)throws Exception {
  if(migrations==null)migrations=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/lesson-migrations.json"));
  return migrations;
 }
 private static boolean coversMigratedQuestions(Application app,String source,JSONObject proof)throws Exception {
  if(proof==null)return false;
  org.json.JSONArray challenges=proof.optJSONArray("challenges");if(challenges==null)return false;
  Set<String> ids=new HashSet<>();for(int i=0;i<challenges.length();i++)ids.add(challenges.getJSONObject(i).getString("id"));
  JSONObject mappings=migrations(app);
  for(Iterator<String> keys=mappings.keys();keys.hasNext();){
   JSONObject migration=mappings.getJSONObject(keys.next());if(!source.equals(migration.getString("sourceLesson")))continue;
   org.json.JSONArray required=migration.getJSONArray("requiredQuestions");if(required.length()==0)continue;
   boolean all=true;for(int i=0;i<required.length();i++)all&=ids.contains(required.getString(i));
   if(all)return true;
  }
  return false;
 }
 private static boolean validStoredProof(Application app,JSONObject proof,JSONObject lesson)throws Exception {
  if(proof==null)return false;
  // The normal current-version completion needs no historical catalog I/O.
  if(NativeCourseProgress.isCompleted(proof,lesson))return true;
  // Assets cannot change during the life of an installed app. Cache the
  // immutable catalog objects: rebuilding them for every lesson makes a
  // full progress refresh increasingly expensive as the course grows.
  if(legacyCatalog==null)legacyCatalog=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/legacy-session-catalog.json"));
  if(historicalCatalogs==null){
   String[] versions={"1.3.0","1.3.5","1.3.6","1.3.7"};JSONObject[] loaded=new JSONObject[versions.length];
   for(int i=0;i<versions.length;i++)loaded[i]=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/history-"+versions[i]+".json"));
   historicalCatalogs=loaded;
  }
  org.json.JSONArray history=new org.json.JSONArray();
  for(JSONObject old:historicalCatalogs){
   JSONObject previous=old.optJSONObject(lesson.getString("id"));
   if(previous!=null)history.put(previous);
  }
  return NativeCourseProgress.isRecordedCompletion(proof,lesson,legacyCatalog.optJSONObject(lesson.getString("id")),history);
 }
 static synchronized void record(Application app,String sessionId,JSONObject submission)throws Exception {
  long profileStart=android.os.SystemClock.elapsedRealtime();
  if(!NativeCourseBridge.hasLocalCourse()||!NativeSessionId.valid(sessionId))throw new IllegalArgumentException("Invalid local course session");
  File folder=new File(NativeAccountStore.root(app),"submissions");
  if(!folder.isDirectory()&&!folder.mkdirs())throw new IOException("Cannot create native session store");
  AtomicFile file=new AtomicFile(new File(folder,sessionId+".json"));
  JSONObject catalog=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/session-catalog.json"));
  JSONObject lesson=catalog.getJSONObject(sessionId);
  android.util.Log.i("DuoAeroNative","catalog_ms="+(android.os.SystemClock.elapsedRealtime()-profileStart));
  // An update can arrive while a published older lesson is in progress.
  // Accept its exact preserved historical question set on final submission;
  // a partial or foreign set still fails the same native completion checks.
  boolean submissionValid=validStoredProof(app,submission,lesson),completed=submissionValid;
  JSONObject proof=completed?submission:null;
  org.json.JSONArray days=new org.json.JSONArray();
  if(completed)days.put(java.time.LocalDate.now().toString());
  try{
   JSONObject previous=read(file);
   days=NativeRewards.mergeDays(days,previous.optJSONArray("studyDays"));
   if(!sessionId.equals(previous.getString("sessionId")))throw new IOException("Stored lesson identity mismatch");
   completed|=previous.optBoolean("completedOnce")||validStoredProof(app,previous.getJSONObject("nativeSubmission"),lesson);
   JSONObject prior=previous.optJSONObject("completionSubmission");
   if(prior==null)prior=previous.optJSONObject("nativeSubmission");
   if(proof==null){
    if(validStoredProof(app,prior,lesson))proof=prior;
   }
   else if(validStoredProof(app,prior,lesson)&&coversMigratedQuestions(app,sessionId,prior)
           &&!coversMigratedQuestions(app,sessionId,proof))proof=prior;
  }catch(FileNotFoundException absent){}
  JSONObject record=new JSONObject().put("schema",1).put("sessionId",sessionId)
   .put("savedAt",System.currentTimeMillis()).put("nativeSubmission",submission).put("completedOnce",completed).put("studyDays",days);
  if(proof!=null)record.put("completionSubmission",proof);
  FileOutputStream output=null;
  try{
   output=file.startWrite();output.write(record.toString().getBytes("UTF-8"));file.finishWrite(output);
  }catch(Exception failure){if(output!=null)file.failWrite(output);throw failure;}
  // Read back the committed bytes before acknowledging the original request.
  JSONObject saved=read(file);
  if(!sessionId.equals(saved.getString("sessionId"))||!saved.has("nativeSubmission")||saved.getBoolean("completedOnce")!=completed)throw new IOException("Invalid stored native session");
  android.util.Log.i("DuoAeroNative","durable_ms="+(android.os.SystemClock.elapsedRealtime()-profileStart));
  if(completed)NativeSessionResume.completed(app,sessionId);
  android.util.Log.i("DuoAeroNative","Durable lesson completion "+sessionId+": "+completed+"; latest submission issue="+(submissionValid?null:NativeCourseProgress.completionIssue(submission,lesson)));
  // The original home may keep its path resource cached when SessionActivity
  // closes. Publish the committed local progress instead of relying on a
  // subsequent native network refresh or an app restart.
  if(completed)NativeRewards.refresh(app,true);
  android.util.Log.i("DuoAeroNative","refresh_ms="+(android.os.SystemClock.elapsedRealtime()-profileStart));
  NativeGoogleHost.changed(app);
 }
 static synchronized Set<String> completedLessons(Application app)throws Exception {
  Set<String> completed=new HashSet<>();
  File folder=new File(NativeAccountStore.root(app),"submissions");
  File[] files=folder.listFiles((dir,name)->{
   String base=name.endsWith(".bak")?name.substring(0,name.length()-4):name;
   return base.endsWith(".json")&&NativeSessionId.valid(base.substring(0,base.length()-5));
  });
  if(files==null)return completed;
  JSONObject catalog=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/session-catalog.json"));
  Set<String> bases=new HashSet<>();for(File path:files)bases.add(path.getName().replaceFirst("\\.bak$",""));
  for(String name:bases){
   JSONObject record=read(new AtomicFile(new File(folder,name)));
   String id=record.getString("sessionId");
   if(!name.equals(id+".json")||!catalog.has(id))throw new IOException("Invalid saved lesson identity");
   if(record.optBoolean("completedOnce")||validStoredProof(app,record.getJSONObject("nativeSubmission"),catalog.getJSONObject(id)))completed.add(id);
  }
  return completed;
 }
 /** Derive path/chest eligibility only from verified stored historical proofs.
  * This never writes a synthetic submission or grants XP for a new lesson. */
 static synchronized Set<String> projectedCompletedLessons(Application app)throws Exception {
  Set<String> actual=completedLessons(app);
  JSONObject migrations=migrations(app);
  JSONObject catalog=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/session-catalog.json"));
  File folder=new File(NativeAccountStore.root(app),"submissions");
  Map<String,Set<String>> verified=new HashMap<>();
  for(Iterator<String> keys=migrations.keys();keys.hasNext();){
   JSONObject migration=migrations.getJSONObject(keys.next());String source=migration.getString("sourceLesson");
   if(verified.containsKey(source)||!actual.contains(source)||!catalog.has(source)||!NativeSessionId.valid(source))continue;
   JSONObject stored=read(new AtomicFile(new File(folder,source+".json")));
   JSONObject proof=stored.optJSONObject("completionSubmission");if(proof==null)proof=stored.optJSONObject("nativeSubmission");
   if(!validStoredProof(app,proof,catalog.getJSONObject(source)))continue;
   org.json.JSONArray challenges=proof.getJSONArray("challenges");Set<String> ids=new HashSet<>();
   for(int i=0;i<challenges.length();i++)ids.add(challenges.getJSONObject(i).getString("id"));
   verified.put(source,ids);
  }
  return NativeCourseProgress.projectedCompletions(actual,migrations,verified);
 }
 static synchronized JSONObject exportCompletions(Application app)throws Exception {
  JSONObject result=new JSONObject(),catalog=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/session-catalog.json"));
  File folder=new File(NativeAccountStore.root(app),"submissions");
  for(String id:completedLessons(app)){
   JSONObject stored=read(new AtomicFile(new File(folder,id+".json")));
   JSONObject proof=stored.optJSONObject("completionSubmission");if(proof==null)proof=stored.optJSONObject("nativeSubmission");
   if(!validStoredProof(app,proof,catalog.getJSONObject(id)))continue;
   JSONObject minimum=new JSONObject();
   for(String key:new String[]{"id","type","failed","shouldLearnThings","startTime","endTime"})minimum.put(key,proof.get(key));
   org.json.JSONArray ids=new org.json.JSONArray(),challenges=proof.getJSONArray("challenges");
   for(int i=0;i<challenges.length();i++)ids.put(new JSONObject().put("id",challenges.getJSONObject(i).getString("id")));
   minimum.put("challenges",ids);
   result.put(id,new JSONObject().put("at",stored.getLong("savedAt")).put("nativeCompletion",minimum).put("studyDays",stored.optJSONArray("studyDays")));
  }
  return result;
 }
 static synchronized void importCompletions(Application app,JSONObject incoming)throws Exception {
  JSONObject catalog=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/session-catalog.json"));
  File folder=new File(NativeAccountStore.root(app),"submissions");
  if(!folder.isDirectory()&&!folder.mkdirs())throw new IOException("Cannot create native session store");
  for(Iterator<String> keys=incoming.keys();keys.hasNext();){
   String id=keys.next();if(!catalog.has(id))continue;
   JSONObject remote=incoming.optJSONObject(id);if(remote==null)continue;
   JSONObject proof=remote.optJSONObject("nativeCompletion");
   if(!validStoredProof(app,proof,catalog.getJSONObject(id)))continue;
   AtomicFile file=new AtomicFile(new File(folder,id+".json"));JSONObject stored;
   try{stored=read(file);}
   catch(FileNotFoundException absent){stored=new JSONObject().put("schema",1).put("sessionId",id).put("nativeSubmission",proof);}
   stored.put("studyDays",NativeRewards.mergeDays(stored.optJSONArray("studyDays"),remote.optJSONArray("studyDays")));
   if(stored.optBoolean("completedOnce")){
    JSONObject localProof=stored.optJSONObject("completionSubmission");
    if(localProof!=null&&validStoredProof(app,localProof,catalog.getJSONObject(id))
       &&!(coversMigratedQuestions(app,id,proof)&&!coversMigratedQuestions(app,id,localProof)))proof=localProof;
   }
   stored.put("completionSubmission",proof).put("completedOnce",true).put("savedAt",Math.max(stored.optLong("savedAt",1),remote.optLong("at",1)));
   FileOutputStream output=null;
   try{output=file.startWrite();output.write(stored.toString().getBytes("UTF-8"));file.finishWrite(output);}
   catch(Exception error){if(output!=null)file.failWrite(output);throw error;}
   // A remote completion must not stop observation or delete the current
   // device's in-flight original session. Its local controller owns that.
  }
 }
 private static JSONObject read(AtomicFile file)throws Exception {
  try(FileInputStream input=file.openRead()){
   ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buffer=new byte[8192];int n;
   while((n=input.read(buffer))!=-1)bytes.write(buffer,0,n);
   return new JSONObject(bytes.toString("UTF-8"));
  }
 }
}
