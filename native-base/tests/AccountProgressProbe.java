package com.duoaero.nativebase;

import android.app.*;
import android.content.*;
import android.os.Bundle;
import java.io.*;
import java.lang.reflect.*;
import org.json.*;

/** Synthetic storage-boundary test. This does not authenticate with Google. */
public final class AccountProgressProbe extends Instrumentation {
 private int checks;
 private void check(boolean valid)throws Exception{if(!valid)throw new IllegalStateException("Account storage check "+checks);checks++;}
 public void onCreate(Bundle args){start();}
 public void onStart(){
  Bundle result=new Bundle();StringBuilder report=new StringBuilder();
  SharedPreferences prefs=getTargetContext().getSharedPreferences("duoaero-google",0);
  try{
   Application app=(Application)getTargetContext().getApplicationContext();ClassLoader loader=app.getClassLoader();
   Class<?> sync=Class.forName("com.duoaero.nativebase.NativeProgressSync",true,loader);
   Method read=sync.getDeclaredMethod("read",Application.class,String.class),apply=sync.getDeclaredMethod("apply",Application.class,String.class,String.class);
   read.setAccessible(true);apply.setAccessible(true);
   JSONObject catalog;
   try(InputStream input=app.getAssets().open("duoaero/course/session-catalog.json")){
    ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] block=new byte[8192];int n;while((n=input.read(block))!=-1)bytes.write(block,0,n);
    catalog=new JSONObject(bytes.toString("UTF-8"));
   }
   String lessonId=catalog.keys().next();JSONObject lesson=catalog.getJSONObject(lessonId);
   JSONArray source=lesson.getJSONArray("challenges"),questions=new JSONArray();
   for(int i=0;i<source.length();i++)questions.put(new JSONObject().put("id",source.getJSONObject(i).getString("id")));
   String qid=source.getJSONObject(0).getString("id");
   JSONObject proof=new JSONObject().put("id",lessonId).put("type","MATH_LESSON").put("failed",false)
    .put("shouldLearnThings",true).put("startTime",1).put("endTime",2).put("challenges",questions)
    .put("trackingProperties",new JSONObject().put("testOnly","must-not-export"));
   JSONObject payload=new JSONObject().put("nativeSchema",1)
    .put("records",new JSONObject().put(qid,new JSONObject().put("correct",false).put("at",10).put("session",lessonId).put("misses",1)))
    .put("completedLessons",new JSONObject().put(lessonId,new JSONObject().put("at",20).put("nativeCompletion",proof)));
   check(prefs.edit().putString("account","synthetic-account-a").commit());
   check(new JSONObject((String)read.invoke(null,app,"synthetic-account-a")).getJSONObject("records").length()==0);
   check(Boolean.TRUE.equals(apply.invoke(null,app,"synthetic-account-a",payload.toString())));
   check(Boolean.FALSE.equals(apply.invoke(null,app,"synthetic-account-a",payload.toString())));
   JSONObject first=new JSONObject((String)read.invoke(null,app,"synthetic-account-a"));
   check(first.getJSONObject("completedLessons").has(lessonId));
   check(!first.getJSONObject("records").getJSONObject(qid).getBoolean("correct"));
   check(!first.toString().contains("must-not-export")&&!first.toString().contains("trackingProperties"));
   check(!first.has("session")&&!first.has("cursors"));
   Class<?> review=Class.forName("com.duoaero.nativebase.NativeReviewStore",true,loader);
   Method create=review.getDeclaredMethod("create",Application.class);create.setAccessible(true);
   JSONObject initialReview=(JSONObject)create.invoke(null,app);
   check(initialReview.getJSONArray("challenges").length()==1);
   check(initialReview.getString("id").equals(((JSONObject)create.invoke(null,app)).getString("id")));
   check(prefs.edit().putString("account","synthetic-account-b").commit());
   JSONObject other=new JSONObject((String)read.invoke(null,app,"synthetic-account-b"));
   check(other.getJSONObject("records").length()==0&&other.getJSONObject("completedLessons").length()==0);
   check(create.invoke(null,app)==null);
   boolean denied=false;
   try{read.invoke(null,app,"synthetic-account-a");}catch(InvocationTargetException error){denied=error.getCause() instanceof SecurityException;}
   check(denied);
   denied=false;try{apply.invoke(null,app,"synthetic-account-a",payload.toString());}catch(InvocationTargetException error){denied=error.getCause() instanceof SecurityException;}
   check(denied);
   JSONObject invalid=new JSONObject(payload.toString());
   invalid.getJSONObject("completedLessons").getJSONObject(lessonId).getJSONObject("nativeCompletion").put("challenges",new JSONArray());
   apply.invoke(null,app,"synthetic-account-b",invalid.toString());
   other=new JSONObject((String)read.invoke(null,app,"synthetic-account-b"));
   check(other.getJSONObject("completedLessons").length()==0);
   check(prefs.edit().putString("account","synthetic-account-a").commit());
   JSONObject correction=new JSONObject(payload.toString());correction.getJSONObject("records").getJSONObject(qid).put("correct",true).put("at",30);
   apply.invoke(null,app,"synthetic-account-a",correction.toString());
   apply.invoke(null,app,"synthetic-account-a",payload.toString());
   JSONObject restored=new JSONObject((String)read.invoke(null,app,"synthetic-account-a"));
   check(restored.getJSONObject("records").getJSONObject(qid).getBoolean("correct"));
   check(restored.getJSONObject("records").getJSONObject(qid).getInt("misses")==1);
   check(restored.getJSONObject("completedLessons").has(lessonId));
   report.append("PASS: ").append(checks).append(" synthetic account storage, cross-account rejection, completion validation and minimized export checks. No Google login, network Drive sync or lesson UI acceptance asserted.\n");
   result.putBoolean("ACCOUNT_STORAGE_VERIFIED",true);
   report.append("ACCOUNT_STORAGE_VERIFIED=true\n");
  }catch(Throwable error){if(error instanceof InvocationTargetException)error=error.getCause();report.append(android.util.Log.getStackTraceString(error));}
  finally{prefs.edit().remove("account").commit();}
  result.putString("stream",report.toString());finish(-1,result);
 }
}
