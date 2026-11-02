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
   Class<?> catalogBridge=Class.forName("com.duoaero.nativebase.NativeCourseBridge",true,loader);
   Method cachedCatalog=catalogBridge.getDeclaredMethod("sessionCatalog",Application.class);cachedCatalog.setAccessible(true);
   JSONObject sharedCatalog=(JSONObject)cachedCatalog.invoke(null,app);
   String originalCatalog=sharedCatalog.toString();
   check(sharedCatalog==cachedCatalog.invoke(null,app));
   Class<?> sync=Class.forName("com.duoaero.nativebase.NativeProgressSync",true,loader);
   Method read=sync.getDeclaredMethod("read",Application.class,String.class),apply=sync.getDeclaredMethod("apply",Application.class,String.class,String.class);
   read.setAccessible(true);apply.setAccessible(true);
   JSONObject catalog;
   try(InputStream input=app.getAssets().open("duoaero/course/session-catalog.json")){
    ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] block=new byte[8192];int n;while((n=input.read(block))!=-1)bytes.write(block,0,n);
    catalog=new JSONObject(bytes.toString("UTF-8"));
   }
   // Exercise dotted Atmosphere IDs through completion and mistake export.
   String lessonId="2.1-5-point-0-lesson-0";JSONObject lesson=catalog.getJSONObject(lessonId);
   Class<?> idValidator=Class.forName("com.duoaero.nativebase.NativeSessionId",true,loader);
   Method validId=idValidator.getDeclaredMethod("valid",String.class);validId.setAccessible(true);
   check(Boolean.TRUE.equals(validId.invoke(null,lessonId)));
   check(Boolean.FALSE.equals(validId.invoke(null,"../escape")));
   check(Boolean.FALSE.equals(validId.invoke(null,"a..b")));
   check(Boolean.FALSE.equals(validId.invoke(null,".hidden")));
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
   Class<?> rewards=Class.forName("com.duoaero.nativebase.NativeRewards",true,loader);
   Method rewardProfile=rewards.getDeclaredMethod("profile",Application.class,JSONObject.class);rewardProfile.setAccessible(true);
   JSONObject earned=(JSONObject)rewardProfile.invoke(null,app,new JSONObject());
   check(earned.getJSONObject("gemsConfig").getInt("gems")==10);
   check(earned.getJSONObject("streakData").getInt("length")==0);
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
   check(((JSONObject)rewardProfile.invoke(null,app,new JSONObject())).getJSONObject("gemsConfig").getInt("gems")==0);
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
   check(((JSONObject)rewardProfile.invoke(null,app,new JSONObject())).getJSONObject("gemsConfig").getInt("gems")==10);
   // Isolated synthetic prerequisites verify claim durability and Drive union.
   check(prefs.edit().putString("account","synthetic-chests").commit());
   JSONObject section;
   try(InputStream input=app.getAssets().open("duoaero/course/section.json")){
    ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] block=new byte[8192];int n;while((n=input.read(block))!=-1)bytes.write(block,0,n);
    section=new JSONObject(bytes.toString("UTF-8"));
   }
   JSONArray levels=section.getJSONArray("units").getJSONObject(0).getJSONArray("levels");
   String chestId=levels.getJSONObject(levels.length()-1).getString("id");
   Class<?> chest=Class.forName("com.duoaero.nativebase.NativeChestRewards",true,loader);
   Method mergeChest=chest.getDeclaredMethod("merge",Application.class,JSONObject.class);mergeChest.setAccessible(true);
   JSONObject claim=new JSONObject().put(chestId,100);
   check(Boolean.FALSE.equals(mergeChest.invoke(null,app,claim)));
   JSONArray metadata=new JSONArray();
   for(int k=0;k<levels.length();k++){
    JSONObject level=levels.getJSONObject(k);if("chest".equals(level.optString("type")))continue;
    JSONArray entries=level.getJSONObject("pathLevelClientData").getJSONArray("sessionMetadatas");
    for(int j=0;j<entries.length();j++)metadata.put(entries.getJSONObject(j));
   }
   JSONObject completionSet=new JSONObject();
   for(int i=0;i<metadata.length();i++){
    String id=metadata.getJSONObject(i).getString("id");JSONArray sourceQuestions=catalog.getJSONObject(id).getJSONArray("challenges"),submitted=new JSONArray();
    for(int j=0;j<sourceQuestions.length();j++)submitted.put(new JSONObject().put("id",sourceQuestions.getJSONObject(j).getString("id")));
    completionSet.put(id,new JSONObject().put("at",20).put("nativeCompletion",new JSONObject().put("id",id).put("type","MATH_LESSON")
     .put("failed",false).put("shouldLearnThings",true).put("startTime",1).put("endTime",2).put("challenges",submitted)));
   }
   apply.invoke(null,app,"synthetic-chests",new JSONObject().put("nativeSchema",1).put("completedLessons",completionSet).toString());
   check(Boolean.TRUE.equals(mergeChest.invoke(null,app,claim)));
   check(Boolean.FALSE.equals(mergeChest.invoke(null,app,claim)));
   check(Boolean.FALSE.equals(mergeChest.invoke(null,app,new JSONObject().put("unknown",200))));
   check(((JSONObject)rewardProfile.invoke(null,app,new JSONObject())).getJSONObject("gemsConfig").getInt("gems")==metadata.length()*10+25);
   JSONObject legacy;
   try(InputStream input=app.getAssets().open("duoaero/course/legacy-chest-requirements.json")){
    ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] block=new byte[4096];int n;while((n=input.read(block))!=-1)bytes.write(block,0,n);
    legacy=new JSONObject(bytes.toString("UTF-8"));
   }
   String oldChest=null;int firstCount=levels.getJSONObject(0).getJSONObject("pathLevelClientData").getJSONArray("sessionMetadatas").length();
   for(java.util.Iterator<String> ids=legacy.keys();ids.hasNext();){String id=ids.next();if(!id.equals(chestId)&&legacy.getJSONArray(id).length()==firstCount){oldChest=id;break;}}
   check(oldChest!=null);
   check(Boolean.TRUE.equals(mergeChest.invoke(null,app,new JSONObject().put(oldChest,80))));
   check(Boolean.FALSE.equals(mergeChest.invoke(null,app,new JSONObject().put(oldChest,80))));
   check(((JSONObject)rewardProfile.invoke(null,app,new JSONObject())).getJSONObject("gemsConfig").getInt("gems")==metadata.length()*10+50);
   String chestExport=(String)read.invoke(null,app,"synthetic-chests");
   check(new JSONObject(chestExport).getJSONObject("chests").has(chestId));
   check(prefs.edit().putString("account","synthetic-chests-restored").commit());
   apply.invoke(null,app,"synthetic-chests-restored",chestExport);
   check(Boolean.FALSE.equals(apply.invoke(null,app,"synthetic-chests-restored",chestExport)));
   check(((JSONObject)rewardProfile.invoke(null,app,new JSONObject())).getJSONObject("gemsConfig").getInt("gems")==metadata.length()*10+50);
   Class<?> userFactory=Class.forName("com.duoaero.nativebase.NativeLocalUser",true,loader);
   Method make=userFactory.getDeclaredMethod("makeLocalUser",Context.class,String.class);make.setAccessible(true);
   Object nativeUser=make.invoke(null,app,"MATH_BT");
   check(nativeUser.getClass().getName().equals("com.duolingo.data.user.User"));
   java.util.List<?> bundles=(java.util.List<?>)nativeUser.getClass().getField("g0").get(nativeUser);
   check(bundles.size()==1);
   Object bundle=bundles.get(0);
   check(bundle.getClass().getField("b").get(bundle).toString().equals("PATH_CHEST"));
   java.util.List<?> rewardsList=(java.util.List<?>)bundle.getClass().getField("c").get(bundle);
   check(rewardsList.size()==1 && rewardsList.get(0).getClass().getName().endsWith("CurrencyReward"));
   // A previously completed lesson remains exportable/importable after its
   // current question set changes. Use the exact published 1.3.7 snapshot.
   JSONObject legacyCatalog;
   try(InputStream input=app.getAssets().open("duoaero/course/history-1.3.7.json")){
    ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] block=new byte[8192];int n;
    while((n=input.read(block))!=-1)bytes.write(block,0,n);
    legacyCatalog=new JSONObject(bytes.toString("UTF-8"));
   }
   String revisedId="2.1-5-point-0-lesson-1";
   JSONArray oldQuestions=legacyCatalog.getJSONObject(revisedId).getJSONArray("challenges"),oldIds=new JSONArray();
   for(int i=0;i<oldQuestions.length();i++)oldIds.put(new JSONObject().put("id",oldQuestions.getJSONObject(i).getString("id")));
   JSONObject oldProof=new JSONObject().put("id",revisedId).put("type","MATH_LESSON").put("failed",false)
    .put("shouldLearnThings",true).put("startTime",1).put("endTime",2).put("challenges",oldIds);
   Class<?> progress=Class.forName("com.duoaero.nativebase.NativeCourseProgress",true,loader);
   Method completed=progress.getDeclaredMethod("isCompleted",JSONObject.class,JSONObject.class);
   check(Boolean.FALSE.equals(completed.invoke(null,oldProof,catalog.getJSONObject(revisedId))));
   check(prefs.edit().putString("account","synthetic-legacy").commit());
   JSONObject legacyPayload=new JSONObject().put("nativeSchema",1).put("completedLessons",new JSONObject()
    .put(revisedId,new JSONObject().put("at",20).put("nativeCompletion",oldProof)));
   check(Boolean.TRUE.equals(apply.invoke(null,app,"synthetic-legacy",legacyPayload.toString())));
   check(new JSONObject((String)read.invoke(null,app,"synthetic-legacy")).getJSONObject("completedLessons").has(revisedId));
   // Check published snapshots against a hypothetical later lesson. A
   // future split must not break a complete historical proof or accept a
   // partial/foreign proof. These are synthetic records, not a Drive roundtrip.
   String[] versions={"1.3.0","1.3.5","1.3.6","1.3.7"};JSONObject[] histories=new JSONObject[versions.length];
   for(int i=0;i<versions.length;i++){
    try(InputStream input=app.getAssets().open("duoaero/course/history-"+versions[i]+".json")){
     ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] block=new byte[8192];int n;
     while((n=input.read(block))!=-1)bytes.write(block,0,n);
     histories[i]=new JSONObject(bytes.toString("UTF-8"));
    }
   }
   String evolvedId="2.1-0-point-0-lesson-0";
   JSONObject hypothetical=new JSONObject(catalog.getJSONObject(evolvedId).toString());
   hypothetical.getJSONArray("challenges").put(new JSONObject().put("id","future-added-challenge"));
   JSONArray historicalLessons=new JSONArray();for(JSONObject history:histories)historicalLessons.put(history.getJSONObject(evolvedId));
   Method recorded=progress.getDeclaredMethod("isRecordedCompletion",JSONObject.class,JSONObject.class,JSONObject.class,JSONArray.class);
   Class<?> sessionStore=Class.forName("com.duoaero.nativebase.NativeSessionStore",true,loader);
   Method storedProof=sessionStore.getDeclaredMethod("validStoredProof",android.app.Application.class,JSONObject.class,JSONObject.class);
   storedProof.setAccessible(true);
   for(JSONObject history:histories){
    JSONArray ids=new JSONArray(),historicalQuestions=history.getJSONObject(evolvedId).getJSONArray("challenges");
    for(int i=0;i<historicalQuestions.length();i++)ids.put(new JSONObject().put("id",historicalQuestions.getJSONObject(i).getString("id")));
    JSONObject historicalProof=new JSONObject().put("id",evolvedId).put("type","MATH_LESSON").put("failed",false)
     .put("shouldLearnThings",true).put("startTime",1).put("endTime",2).put("challenges",ids);
    check(Boolean.TRUE.equals(recorded.invoke(null,historicalProof,hypothetical,null,historicalLessons)));
    // Exercise the packaged historical assets and cache used by import/export,
    // not only the pure comparison helper.
    check(Boolean.TRUE.equals(storedProof.invoke(null,app,historicalProof,hypothetical)));
    check(Boolean.TRUE.equals(storedProof.invoke(null,app,historicalProof,hypothetical)));
    JSONObject broken=new JSONObject(historicalProof.toString());broken.getJSONArray("challenges").put(new JSONObject().put("id","foreign"));
    check(Boolean.FALSE.equals(recorded.invoke(null,broken,hypothetical,null,historicalLessons)));
    check(Boolean.FALSE.equals(storedProof.invoke(null,app,broken,hypothetical)));
   }
   // The 1.3.0 second Atmosphere lesson predates a split challenge and has a
   // genuinely different set from 1.3.5. Require its exact historical proof.
   String oldId="2.1-5-point-0-lesson-1";
   JSONArray published130Questions=histories[0].getJSONObject(oldId).getJSONArray("challenges");
   check(published130Questions.length()+1==histories[1].getJSONObject(oldId).getJSONArray("challenges").length());
   JSONObject published130Proof=new JSONObject().put("id",oldId).put("type","MATH_LESSON").put("failed",false)
    .put("shouldLearnThings",true).put("startTime",1).put("endTime",2).put("challenges",new JSONArray(published130Questions.toString()));
   JSONObject currentLesson=catalog.getJSONObject(oldId);
   check(Boolean.FALSE.equals(recorded.invoke(null,published130Proof,currentLesson,null,new JSONArray())));
   check(Boolean.TRUE.equals(recorded.invoke(null,published130Proof,currentLesson,null,new JSONArray().put(histories[0].getJSONObject(oldId)))));
   check(Boolean.TRUE.equals(storedProof.invoke(null,app,published130Proof,currentLesson)));
   // 1.3.7 added named and word-formula challenges to the first Atmosphere
   // lesson. Its exact completion must remain valid after future expansion,
   // while older snapshots cannot accidentally validate that distinct proof.
   String published137Id="2.1-5-point-0-lesson-0";
   JSONObject published137=histories[3].getJSONObject(published137Id);
   JSONArray published137Questions=published137.getJSONArray("challenges");
   JSONObject published137Proof=new JSONObject().put("id",published137Id).put("type","MATH_LESSON").put("failed",false)
    .put("shouldLearnThings",true).put("startTime",1).put("endTime",2).put("challenges",new JSONArray(published137Questions.toString()));
   JSONObject future137=new JSONObject(catalog.getJSONObject(published137Id).toString());
   future137.getJSONArray("challenges").put(new JSONObject().put("id","future-formula-question"));
   JSONArray pre137=new JSONArray();for(int i=0;i<3;i++)pre137.put(histories[i].getJSONObject(published137Id));
   check(Boolean.FALSE.equals(recorded.invoke(null,published137Proof,future137,null,pre137)));
   check(Boolean.TRUE.equals(recorded.invoke(null,published137Proof,future137,null,new JSONArray().put(published137))));
   check(Boolean.TRUE.equals(storedProof.invoke(null,app,published137Proof,future137)));
   JSONObject partial137=new JSONObject(published137Proof.toString());partial137.getJSONArray("challenges").remove(0);
   check(Boolean.FALSE.equals(storedProof.invoke(null,app,partial137,future137)));
   // Validate exact published 1.3.7 proofs on both sides of each rebalance,
   // including the two original ISA levels whose prerequisites changed.
   for(String node:new String[]{"2.1-5-point-0","2.1-5-point-1","2.1-0-point-0","2.3-6-point-0","2.3-5-point-0","2.5-5-point-0"}){
    for(int index=0;index<2;index++){
     String id=node+"-lesson-"+index;
     JSONArray old=histories[3].getJSONObject(id).getJSONArray("challenges");
     JSONObject movedProof=new JSONObject().put("id",id).put("type","MATH_LESSON").put("failed",false)
      .put("shouldLearnThings",true).put("startTime",1).put("endTime",2).put("challenges",new JSONArray(old.toString()));
     JSONObject revised=catalog.getJSONObject(id);
     check(Boolean.FALSE.equals(completed.invoke(null,movedProof,revised)));
     check(Boolean.TRUE.equals(storedProof.invoke(null,app,movedProof,revised)));
     JSONObject partial=new JSONObject(movedProof.toString());partial.getJSONArray("challenges").remove(0);
     check(Boolean.FALSE.equals(storedProof.invoke(null,app,partial,revised)));
    }
   }
   // Split sessions get path-only credit only when an exact historical proof
   // actually contains all of the questions moved to the new session.
   JSONObject migrations;
   try(InputStream input=app.getAssets().open("duoaero/course/lesson-migrations.json")){
    ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] block=new byte[4096];int n;
    while((n=input.read(block))!=-1)bytes.write(block,0,n);migrations=new JSONObject(bytes.toString("UTF-8"));
   }
   Method actualMethod=sessionStore.getDeclaredMethod("completedLessons",Application.class);actualMethod.setAccessible(true);
   Method projectedMethod=sessionStore.getDeclaredMethod("projectedCompletedLessons",Application.class);projectedMethod.setAccessible(true);
   JSONObject oldCompletions=new JSONObject(),newCompletions=new JSONObject();
   for(java.util.Iterator<String> it=migrations.keys();it.hasNext();){
    String target=it.next(),sourceId=migrations.getJSONObject(target).getString("sourceLesson");
    JSONArray old=histories[3].getJSONObject(sourceId).getJSONArray("challenges"),now=catalog.getJSONObject(sourceId).getJSONArray("challenges");
    for(int mode=0;mode<2;mode++){
     JSONArray ids=new JSONArray(mode==0?old.toString():now.toString());
     JSONObject completedProof=new JSONObject().put("id",sourceId).put("type","MATH_LESSON").put("failed",false)
      .put("shouldLearnThings",true).put("startTime",1).put("endTime",2).put("challenges",ids);
     (mode==0?oldCompletions:newCompletions).put(sourceId,new JSONObject().put("at",20).put("nativeCompletion",completedProof));
    }
   }
   check(prefs.edit().putString("account","synthetic-split-old").commit());
   check(Boolean.TRUE.equals(apply.invoke(null,app,"synthetic-split-old",new JSONObject().put("nativeSchema",1).put("completedLessons",oldCompletions).toString())));
   java.util.Set<?> actual=(java.util.Set<?>)actualMethod.invoke(null,app),projected=(java.util.Set<?>)projectedMethod.invoke(null,app);
   JSONObject oldExport=new JSONObject((String)read.invoke(null,app,"synthetic-split-old")).getJSONObject("completedLessons");
   for(java.util.Iterator<String> it=migrations.keys();it.hasNext();){String target=it.next();check(!actual.contains(target)&&projected.contains(target)&&!oldExport.has(target));}
   check(((JSONObject)rewardProfile.invoke(null,app,new JSONObject())).getJSONObject("gemsConfig").getInt("gems")==oldCompletions.length()*10);
   // Replaying the shortened source must not discard the historical proof
   // needed for path credit, nor award gems for the derived lesson.
   String firstTarget=migrations.keys().next(),firstSource=migrations.getJSONObject(firstTarget).getString("sourceLesson");
   Method recordMethod=sessionStore.getDeclaredMethod("record",Application.class,String.class,JSONObject.class);recordMethod.setAccessible(true);
   Class<?> bridge=Class.forName("com.duoaero.nativebase.NativeCourseBridge",true,loader);
   Field localOnly=bridge.getField("localOnly"),installed=bridge.getField("localCourseInstalled");
   boolean oldLocal=localOnly.getBoolean(null),oldInstalled=installed.getBoolean(null);
   try{
    // Unlike a real lesson, this storage-only instrumentation has not
    // launched the standalone course bootstrap. Enable its normal guard for
    // the actual record call, then restore the process state immediately.
    localOnly.setBoolean(null,true);installed.setBoolean(null,true);
    recordMethod.invoke(null,app,firstSource,newCompletions.getJSONObject(firstSource).getJSONObject("nativeCompletion"));
   }finally{localOnly.setBoolean(null,oldLocal);installed.setBoolean(null,oldInstalled);}
   check(((java.util.Set<?>)projectedMethod.invoke(null,app)).contains(firstTarget));
   check(!new JSONObject((String)read.invoke(null,app,"synthetic-split-old")).getJSONObject("completedLessons").has(firstTarget));
   check(((JSONObject)rewardProfile.invoke(null,app,new JSONObject())).getJSONObject("gemsConfig").getInt("gems")==oldCompletions.length()*10);
   // A real old-version lesson can finish after the update, rather than
   // already being present in the store before migration.
   check(prefs.edit().putString("account","synthetic-split-inflight").commit());
   try{
    localOnly.setBoolean(null,true);installed.setBoolean(null,true);
    recordMethod.invoke(null,app,firstSource,oldCompletions.getJSONObject(firstSource).getJSONObject("nativeCompletion"));
   }finally{localOnly.setBoolean(null,oldLocal);installed.setBoolean(null,oldInstalled);}
   check(((java.util.Set<?>)actualMethod.invoke(null,app)).contains(firstSource));
   check(((java.util.Set<?>)projectedMethod.invoke(null,app)).contains(firstTarget));
   check(((JSONObject)rewardProfile.invoke(null,app,new JSONObject())).getJSONObject("gemsConfig").getInt("gems")==10);
   check(prefs.edit().putString("account","synthetic-split-current").commit());
   check(Boolean.TRUE.equals(apply.invoke(null,app,"synthetic-split-current",new JSONObject().put("nativeSchema",1).put("completedLessons",newCompletions).toString())));
   java.util.Set<?> newProjected=(java.util.Set<?>)projectedMethod.invoke(null,app);
   for(java.util.Iterator<String> it=migrations.keys();it.hasNext();)check(!newProjected.contains(it.next()));
   check(((JSONObject)rewardProfile.invoke(null,app,new JSONObject())).getJSONObject("gemsConfig").getInt("gems")==newCompletions.length()*10);
   // Importing the old proof after a shorter current completion must upgrade
   // the retained evidence without duplicating rewards or fake submissions.
   apply.invoke(null,app,"synthetic-split-current",new JSONObject().put("nativeSchema",1).put("completedLessons",oldCompletions).toString());
   newProjected=(java.util.Set<?>)projectedMethod.invoke(null,app);
   for(java.util.Iterator<String> it=migrations.keys();it.hasNext();)check(newProjected.contains(it.next()));
   check(((JSONObject)rewardProfile.invoke(null,app,new JSONObject())).getJSONObject("gemsConfig").getInt("gems")==newCompletions.length()*10);
   check(prefs.edit().putString("account","synthetic-split-partial").commit());
   JSONObject partialCompletions=new JSONObject(oldCompletions.toString());
   for(java.util.Iterator<String> it=migrations.keys();it.hasNext();){
    JSONObject migration=migrations.getJSONObject(it.next());String sourceId=migration.getString("sourceLesson");
    String missing=migration.getJSONArray("requiredQuestions").getString(0);
    JSONArray ids=partialCompletions.getJSONObject(sourceId).getJSONObject("nativeCompletion").getJSONArray("challenges");
    boolean removed=false;for(int i=0;i<ids.length();i++)if(missing.equals(ids.getJSONObject(i).getString("id"))){ids.remove(i);removed=true;break;}
    check(removed);
   }
   apply.invoke(null,app,"synthetic-split-partial",new JSONObject().put("nativeSchema",1).put("completedLessons",partialCompletions).toString());
   java.util.Set<?> partialProjected=(java.util.Set<?>)projectedMethod.invoke(null,app);
   for(java.util.Iterator<String> it=migrations.keys();it.hasNext();)check(!partialProjected.contains(it.next()));
   check(((JSONObject)rewardProfile.invoke(null,app,new JSONObject())).getJSONObject("gemsConfig").getInt("gems")==0);
   // A previously completed topic can still unlock its existing chest after
   // two of its levels gain derived third lessons; claiming remains idempotent.
   check(prefs.edit().putString("account","synthetic-split-chest").commit());
   JSONObject oldTopic=new JSONObject();JSONArray topicUnits=section.getJSONArray("units");String topicChest=null;
   for(int unit=0;unit<=1;unit++){
    JSONArray path=topicUnits.getJSONObject(unit).getJSONArray("levels");
    for(int i=0;i<path.length();i++){
     JSONObject level=path.getJSONObject(i);
     if("chest".equals(level.optString("type"))){if(unit==1)topicChest=level.getString("id");continue;}
     JSONArray entries=level.getJSONObject("pathLevelClientData").getJSONArray("sessionMetadatas");
     for(int j=0;j<entries.length();j++){
      String id=entries.getJSONObject(j).getString("id");JSONObject historical=histories[3].optJSONObject(id);
      if(historical==null)continue;
      JSONObject historicalProof=new JSONObject().put("id",id).put("type","MATH_LESSON").put("failed",false)
       .put("shouldLearnThings",true).put("startTime",1).put("endTime",2).put("challenges",new JSONArray(historical.getJSONArray("challenges").toString()));
      oldTopic.put(id,new JSONObject().put("at",20).put("nativeCompletion",historicalProof));
     }
    }
   }
   check(topicChest!=null);
   apply.invoke(null,app,"synthetic-split-chest",new JSONObject().put("nativeSchema",1).put("completedLessons",oldTopic).toString());
   check(Boolean.TRUE.equals(mergeChest.invoke(null,app,new JSONObject().put(topicChest,100))));
   check(Boolean.FALSE.equals(mergeChest.invoke(null,app,new JSONObject().put(topicChest,100))));
   check(((JSONObject)rewardProfile.invoke(null,app,new JSONObject())).getJSONObject("gemsConfig").getInt("gems")==oldTopic.length()*10+25);
   check(sharedCatalog==cachedCatalog.invoke(null,app));
   check(originalCatalog.equals(sharedCatalog.toString()));
   report.append("PASS: ").append(checks).append(" synthetic account storage, cross-account rejection, completion validation, immutable shared catalog and minimized export checks. No Google login, network Drive sync or lesson UI acceptance asserted.\n");
   result.putBoolean("ACCOUNT_STORAGE_VERIFIED",true);
   report.append("ACCOUNT_STORAGE_VERIFIED=true\n");
  }catch(Throwable error){if(error instanceof InvocationTargetException)error=error.getCause();report.append(android.util.Log.getStackTraceString(error));}
  finally{prefs.edit().remove("account").commit();}
  result.putString("stream",report.toString());finish(-1,result);
 }
}
