package com.duoaero.nativebase;

import android.app.Application;
import android.util.AtomicFile;
import org.json.JSONObject;
import java.io.*;
import java.util.*;

/** Atomic native submissions and monotonic completion, isolated to local test identity. */
public final class NativeSessionStore {
 private NativeSessionStore(){}
 static synchronized void record(Application app,String sessionId,JSONObject submission)throws Exception {
  if(!NativeCourseBridge.hasLocalCourse()||!sessionId.matches("[A-Za-z0-9_-]{1,160}"))throw new IllegalArgumentException("Invalid local course session");
  File folder=new File(NativeAccountStore.root(app),"submissions");
  if(!folder.isDirectory()&&!folder.mkdirs())throw new IOException("Cannot create native session store");
  AtomicFile file=new AtomicFile(new File(folder,sessionId+".json"));
  JSONObject catalog=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/session-catalog.json"));
  JSONObject lesson=catalog.getJSONObject(sessionId);
  boolean completed=NativeCourseProgress.isCompleted(submission,lesson);
  JSONObject proof=completed?submission:null;
  org.json.JSONArray days=new org.json.JSONArray();
  if(completed)days.put(java.time.LocalDate.now().toString());
  try{
   JSONObject previous=read(file);
   days=NativeRewards.mergeDays(days,previous.optJSONArray("studyDays"));
   if(!sessionId.equals(previous.getString("sessionId")))throw new IOException("Stored lesson identity mismatch");
   completed|=previous.optBoolean("completedOnce")||NativeCourseProgress.isCompleted(previous.getJSONObject("nativeSubmission"),lesson);
   if(proof==null){
    JSONObject prior=previous.optJSONObject("completionSubmission");
    if(prior==null)prior=previous.optJSONObject("nativeSubmission");
    if(prior!=null&&NativeCourseProgress.isCompleted(prior,lesson))proof=prior;
   }
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
  if(completed)NativeSessionResume.completed(app,sessionId);
  android.util.Log.i("DuoAeroNative","Durable lesson completion "+sessionId+": "+completed+"; latest submission issue="+NativeCourseProgress.completionIssue(submission,lesson));
  // The original home may keep its path resource cached when SessionActivity
  // closes. Publish the committed local progress instead of relying on a
  // subsequent native network refresh or an app restart.
  if(completed)NativeRewards.refresh(app,true);
  NativeGoogleHost.changed(app);
 }
 static synchronized Set<String> completedLessons(Application app)throws Exception {
  Set<String> completed=new HashSet<>();
  File folder=new File(NativeAccountStore.root(app),"submissions");
  File[] files=folder.listFiles((dir,name)->name.matches("[A-Za-z0-9_-]{1,160}\\.json(?:\\.bak)?"));
  if(files==null)return completed;
  JSONObject catalog=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/session-catalog.json"));
  Set<String> bases=new HashSet<>();for(File path:files)bases.add(path.getName().replaceFirst("\\.bak$",""));
  for(String name:bases){
   JSONObject record=read(new AtomicFile(new File(folder,name)));
   String id=record.getString("sessionId");
   if(!name.equals(id+".json")||!catalog.has(id))throw new IOException("Invalid saved lesson identity");
   if(record.optBoolean("completedOnce")||NativeCourseProgress.isCompleted(record.getJSONObject("nativeSubmission"),catalog.getJSONObject(id)))completed.add(id);
  }
  return completed;
 }
 static synchronized JSONObject exportCompletions(Application app)throws Exception {
  JSONObject result=new JSONObject(),catalog=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/session-catalog.json"));
  File folder=new File(NativeAccountStore.root(app),"submissions");
  for(String id:completedLessons(app)){
   JSONObject stored=read(new AtomicFile(new File(folder,id+".json")));
   JSONObject proof=stored.optJSONObject("completionSubmission");if(proof==null)proof=stored.optJSONObject("nativeSubmission");
   if(proof==null||!NativeCourseProgress.isCompleted(proof,catalog.getJSONObject(id)))continue;
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
   if(proof==null||!NativeCourseProgress.isCompleted(proof,catalog.getJSONObject(id)))continue;
   AtomicFile file=new AtomicFile(new File(folder,id+".json"));JSONObject stored;
   try{stored=read(file);}
   catch(FileNotFoundException absent){stored=new JSONObject().put("schema",1).put("sessionId",id).put("nativeSubmission",proof);}
   stored.put("studyDays",NativeRewards.mergeDays(stored.optJSONArray("studyDays"),remote.optJSONArray("studyDays")));
   if(stored.optBoolean("completedOnce")){
    JSONObject localProof=stored.optJSONObject("completionSubmission");
    if(localProof!=null)proof=localProof;
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
