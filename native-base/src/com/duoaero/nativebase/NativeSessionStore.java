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
  File folder=new File(app.getFilesDir(),"duoaero-course/local-test/submissions");
  if(!folder.isDirectory()&&!folder.mkdirs())throw new IOException("Cannot create native session store");
  AtomicFile file=new AtomicFile(new File(folder,sessionId+".json"));
  JSONObject catalog=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/session-catalog.json"));
  JSONObject lesson=catalog.getJSONObject(sessionId);
  boolean completed=NativeCourseProgress.isCompleted(submission,lesson);
  try{
   JSONObject previous=read(file);
   if(!sessionId.equals(previous.getString("sessionId")))throw new IOException("Stored lesson identity mismatch");
   completed|=previous.optBoolean("completedOnce")||NativeCourseProgress.isCompleted(previous.getJSONObject("nativeSubmission"),lesson);
  }catch(FileNotFoundException absent){}
  JSONObject record=new JSONObject().put("schema",1).put("sessionId",sessionId)
   .put("savedAt",System.currentTimeMillis()).put("nativeSubmission",submission).put("completedOnce",completed);
  FileOutputStream output=null;
  try{
   output=file.startWrite();output.write(record.toString().getBytes("UTF-8"));file.finishWrite(output);
  }catch(Exception failure){if(output!=null)file.failWrite(output);throw failure;}
  // Read back the committed bytes before acknowledging the original request.
  JSONObject saved=read(file);
  if(!sessionId.equals(saved.getString("sessionId"))||!saved.has("nativeSubmission")||saved.getBoolean("completedOnce")!=completed)throw new IOException("Invalid stored native session");
  if(completed)NativeSessionResume.completed(app,sessionId);
  android.util.Log.i("DuoAeroNative","Durable lesson completion "+sessionId+": "+completed+"; latest submission issue="+NativeCourseProgress.completionIssue(submission,lesson));
 }
 static synchronized Set<String> completedLessons(Application app)throws Exception {
  Set<String> completed=new HashSet<>();
  File folder=new File(app.getFilesDir(),"duoaero-course/local-test/submissions");
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
 private static JSONObject read(AtomicFile file)throws Exception {
  try(FileInputStream input=file.openRead()){
   ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buffer=new byte[8192];int n;
   while((n=input.read(buffer))!=-1)bytes.write(buffer,0,n);
   return new JSONObject(bytes.toString("UTF-8"));
  }
 }
}
