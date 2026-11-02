package com.duoaero.nativebase;

import android.app.Activity;
import android.app.Application;
import android.content.Intent;
import android.util.AtomicFile;
import android.widget.Toast;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;
import org.json.*;

/** Local review data for the original lesson loader, renderer and grader. */
final class NativeReviewStore {
 private NativeReviewStore(){}
 static boolean isReview(String id){return id!=null&&id.matches("review_[a-f0-9]{32}");}
 private static File directory(Application app)throws IOException {
  File folder=new File(NativeAccountStore.root(app),"reviews");
  if(!folder.isDirectory()&&!folder.mkdirs())throw new IOException("Cannot create review store");
  return folder;
 }
 static JSONObject lookup(Application app,String id)throws Exception {
  if(!isReview(id))return null;
  try{return read(new AtomicFile(new File(directory(app),id+".json")));}
  catch(FileNotFoundException absent){return null;}
 }
 static JSONObject create(Application app)throws Exception {
  // Re-enter the same original session after process death so its saved
  // Parcelable restores the remaining review questions and answer history.
  AtomicFile active=new AtomicFile(new File(directory(app),"active.json"));
  try{
   String previous=read(active).getString("id");JSONObject existing=lookup(app,previous);
   if(existing!=null){
    boolean completed=false;
    try{completed=read(new AtomicFile(new File(directory(app),previous+"-submission.json"))).optBoolean("completed");}
    catch(FileNotFoundException notSubmitted){}
    if(!completed)return existing;
   }
  }catch(FileNotFoundException noActiveReview){}
  JSONObject state;
  try{state=read(new AtomicFile(new File(NativeAccountStore.root(app),"question-state.json")));}
  catch(FileNotFoundException empty){return null;}
  List<String> pending=NativeQuestionLedger.unresolved(state.getJSONObject("records"));
  if(pending.isEmpty())return null;
  JSONObject catalog=NativeCourseBridge.sessionCatalog(app);
  Map<String,JSONObject> questions=new HashMap<>();JSONObject template=null;
  for(Iterator<String> keys=catalog.keys();keys.hasNext();){
   JSONObject lesson=catalog.getJSONObject(keys.next());if(template==null)template=lesson;
   JSONArray items=lesson.getJSONArray("challenges");
   for(int i=0;i<items.length();i++)questions.put(items.getJSONObject(i).getString("id"),items.getJSONObject(i));
  }
  JSONArray selected=new JSONArray();
  for(String id:pending){if(questions.containsKey(id))selected.put(questions.get(id));if(selected.length()==20)break;}
  if(selected.length()==0)return null;
  String id="review_"+UUID.randomUUID().toString().replace("-","");
  JSONObject lesson=new JSONObject(template.toString()).put("id",id).put("levelSessionIndex",0)
   .put("metadata",new JSONObject().put("id",id).put("type","math_lesson")).put("challenges",selected);
  write(new AtomicFile(new File(directory(app),id+".json")),lesson);
  write(active,new JSONObject().put("id",id));
  return lesson;
 }
 static void record(Application app,String id,JSONObject submission)throws Exception {
  JSONObject lesson=lookup(app,id);if(lesson==null)throw new IOException("Unknown review session");
  String issue=NativeCourseProgress.reviewCompletionIssue(submission,lesson);
  JSONObject saved=new JSONObject().put("schema",1).put("sessionId",id).put("savedAt",System.currentTimeMillis())
   .put("nativeSubmission",submission).put("completed",issue==null);
  AtomicFile file=new AtomicFile(new File(directory(app),id+"-submission.json"));
  write(file,saved);
  if(!id.equals(read(file).getString("sessionId")))throw new IOException("Review commit failed");
  if(issue==null)NativeSessionResume.completed(app,id);
  android.util.Log.i("DuoAeroNative","Original mistake review submission stored: "+id+"; completed="+(issue==null));
 }
 static void open(Activity activity){
  try{
   Application app=activity.getApplication();JSONObject lesson=create(app);
   if(lesson==null){Toast.makeText(activity,"No mistakes to review. Keep learning!",Toast.LENGTH_LONG).show();return;}
   ClassLoader loader=activity.getClassLoader();
   Class<?> routeType=Class.forName("com.duolingo.data.session.SessionRouteParams",true,loader);
   Class<?> math=Class.forName("com.duolingo.data.session.SessionRouteParams$MathLesson",true,loader);
   Object streak=Class.forName("com.duolingo.data.session.SessionRouteParams$StreakEarnbackStatus$None",true,loader).getField("b").get(null);
   Object pathType=Class.forName("com.duolingo.data.path.common.PathLevelType",true,loader).getField("MATH_SKILL").get(null);
   Object rive=Class.forName("com.duolingo.core.math.models.config.MathRiveEligibility",true,loader).getField("ELIGIBLE").get(null);
   Constructor<?> constructor=null;
   for(Constructor<?> candidate:math.getConstructors())if(candidate.getParameterTypes().length==19)constructor=candidate;
   if(constructor==null)throw new NoSuchMethodException("Original MathLesson route");
   Object route=constructor.newInstance(lesson.getString("skillId"),0,true,false,false,false,false,streak,"en",lesson.getJSONObject("metadata").toString(),pathType,rive,true,false,false,null,false,null,false);
   Object params=Class.forName("com.duolingo.data.session.start.SessionStartParams$Remote",true,loader).getConstructor(routeType).newInstance(route);
   Object via=Class.forName("com.duolingo.data.onboarding.OnboardingVia",true,loader).getField("HOME").get(null);
   Class<?> sessionActivity=Class.forName("com.duolingo.session.SessionActivity",true,loader);
   for(Method method:sessionActivity.getDeclaredMethods())if(method.getName().equals("L")&&method.getParameterTypes().length==13){
    Intent intent=(Intent)method.invoke(null,activity,params,false,via,false,false,null,null,null,true,false,null,sessionActivity);
    activity.startActivity(intent);return;
   }
   throw new NoSuchMethodException("Original session navigation");
  }catch(Exception error){android.util.Log.e("DuoAeroNative","Unable to open mistake review",error);Toast.makeText(activity,"Could not open review. Your mistakes are still saved.",Toast.LENGTH_LONG).show();}
 }
 private static JSONObject read(AtomicFile file)throws Exception {
  try(InputStream input=file.openRead()){
   ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buffer=new byte[8192];int n;
   while((n=input.read(buffer))!=-1){bytes.write(buffer,0,n);if(bytes.size()>4*1024*1024)throw new IOException("Review record too large");}
   return new JSONObject(bytes.toString("UTF-8"));
  }
 }
 private static void write(AtomicFile file,JSONObject value)throws Exception {
  FileOutputStream output=null;
  try{output=file.startWrite();output.write(value.toString().getBytes("UTF-8"));file.finishWrite(output);}
  catch(Exception error){if(output!=null)file.failWrite(output);throw error;}
 }
}
