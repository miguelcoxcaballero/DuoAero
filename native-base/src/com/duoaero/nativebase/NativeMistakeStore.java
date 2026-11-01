package com.duoaero.nativebase;

import android.app.Application;
import android.util.AtomicFile;
import java.io.*;
import java.util.*;
import org.json.*;

/** Persist actual original graded outcomes; never evaluates or changes an answer. */
final class NativeMistakeStore {
 private NativeMistakeStore(){}
 static synchronized JSONObject snapshot(Application app)throws Exception {
  return new JSONObject(readLedger(app).getJSONObject("records").toString());
 }
 static synchronized void merge(Application app,JSONObject incoming,Set<String> known)throws Exception {
  JSONObject ledger=readLedger(app),records=ledger.getJSONObject("records");
  boolean changed=false;
  for(Iterator<String> keys=incoming.keys();keys.hasNext();){
   String id=keys.next();if(!known.contains(id))continue;
   JSONObject value=incoming.optJSONObject(id);if(value==null||!(value.opt("correct") instanceof Boolean)||value.optLong("at")<=0)continue;
   JSONObject prior=records.optJSONObject(id);
   if(prior!=null&&prior.optLong("at")>=value.getLong("at"))continue;
   String session=value.optString("session","");if(!session.matches("[A-Za-z0-9_-]{1,160}"))continue;
   int misses=Math.max(prior==null?0:prior.optInt("misses"),Math.max(0,value.optInt("misses")));
   records.put(id,new JSONObject().put("correct",value.getBoolean("correct")).put("at",value.getLong("at")).put("misses",misses).put("session",session));changed=true;
  }
  if(!changed)return;
  File folder=NativeAccountStore.root(app);if(!folder.isDirectory()&&!folder.mkdirs())throw new IOException("Cannot create question store");
  AtomicFile file=new AtomicFile(new File(folder,"question-state.json"));FileOutputStream output=null;
  try{output=file.startWrite();output.write(ledger.toString().getBytes("UTF-8"));file.finishWrite(output);}
  catch(Exception error){if(output!=null)file.failWrite(output);throw error;}
 }
 private static JSONObject readLedger(Application app)throws Exception {
  AtomicFile file=new AtomicFile(new File(NativeAccountStore.root(app),"question-state.json"));
  try(FileInputStream input=file.openRead()){
   ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buffer=new byte[8192];int n;
   while((n=input.read(buffer))!=-1){bytes.write(buffer,0,n);if(bytes.size()>4*1024*1024)throw new IOException("Question store too large");}
   JSONObject ledger=new JSONObject(bytes.toString("UTF-8"));
   if(ledger.getInt("schema")!=1)throw new IOException("Unsupported question store");
   return ledger;
  }catch(FileNotFoundException absent){return new JSONObject().put("schema",1).put("records",new JSONObject()).put("cursors",new JSONObject());}
 }
 static synchronized void observe(Application app,Object session,Object state,JSONObject lesson)throws Exception {
  List<?> completed=(List<?>)state.getClass().getField("b").get(state);
  if(completed.isEmpty())return;
  File directory=NativeAccountStore.root(app);
  if(!directory.isDirectory()&&!directory.mkdirs())throw new IOException("Cannot create local question store");
  AtomicFile file=new AtomicFile(new File(directory,"question-state.json"));
  JSONObject ledger;
  try(FileInputStream input=file.openRead()){
   ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buffer=new byte[8192];int n;
   while((n=input.read(buffer))!=-1){bytes.write(buffer,0,n);if(bytes.size()>4*1024*1024)throw new IOException("Question store too large");}
   ledger=new JSONObject(bytes.toString("UTF-8"));
  }catch(FileNotFoundException absent){ledger=new JSONObject().put("schema",1).put("records",new JSONObject()).put("cursors",new JSONObject());}
  if(ledger.getInt("schema")!=1)throw new IOException("Unsupported question store");
  JSONObject records=ledger.getJSONObject("records"),cursors=ledger.getJSONObject("cursors");
  String id=lesson.getString("id");
  String run=id+":"+state.getClass().getField("q").get(state).toString();
  int cursor=cursors.optInt(run),next=cursor;
  if(cursor>=completed.size())return;
  Set<String> known=new HashSet<>();JSONArray expected=lesson.getJSONArray("challenges");
  for(int i=0;i<expected.length();i++)known.add(expected.getJSONObject(i).getString("id"));
  ClassLoader loader=session.getClass().getClassLoader();
  java.lang.reflect.Method resolve=Class.forName("com.duolingo.core.session.v2",true,loader)
   .getMethod("b",session.getClass(),Class.forName("com.duolingo.core.session.api.SessionChallengeIndex",true,loader));
  for(int i=cursor;i<completed.size();i++){
   Object info=completed.get(i),grade=info.getClass().getField("b").get(info);
   if(grade==null)break;
   Object challenge=resolve.invoke(null,session,info.getClass().getField("a").get(info));
   if(challenge==null)throw new IOException("Original completed challenge cannot be resolved");
   Object identity=challenge.getClass().getMethod("getId").invoke(challenge);
   String qid=(String)identity.getClass().getField("a").get(identity);
   if(!known.contains(qid))throw new IOException("Completed question outside local lesson");
   boolean correct=(Boolean)grade.getClass().getMethod("e").invoke(grade);
   NativeQuestionLedger.record(records,qid,correct,System.currentTimeMillis(),id);
   next=i+1;
  }
  if(next==cursor)return;
  cursors.put(run,next);
  FileOutputStream output=null;
  try{output=file.startWrite();output.write(ledger.toString().getBytes("UTF-8"));file.finishWrite(output);}
  catch(Exception error){if(output!=null)file.failWrite(output);throw error;}
  android.util.Log.i("DuoAeroNative","Original question outcomes committed: "+id+"; attempts="+next+"; unresolved="+NativeQuestionLedger.unresolved(records).size());
  NativeGoogleHost.changed(app);
 }
}
