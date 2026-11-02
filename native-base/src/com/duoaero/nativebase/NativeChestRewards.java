package com.duoaero.nativebase;

import android.app.Application;
import android.util.AtomicFile;
import java.io.*;
import java.util.*;
import org.json.*;

/** Account-owned, idempotent path chest claims behind the original reward UI. */
public final class NativeChestRewards {
 static final int GEMS=25;
 private NativeChestRewards(){}
 static synchronized JSONObject snapshot(Application app)throws Exception {
  AtomicFile file=new AtomicFile(new File(NativeAccountStore.root(app),"chests.json"));
  try(FileInputStream input=file.openRead()){
   ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buffer=new byte[4096];int n;
   while((n=input.read(buffer))!=-1)bytes.write(buffer,0,n);
   return new JSONObject(bytes.toString("UTF-8"));
  }catch(FileNotFoundException absent){return new JSONObject();}
 }
 static Set<String> ids(JSONObject records){Set<String> result=new HashSet<>();for(Iterator<String> i=records.keys();i.hasNext();)result.add(i.next());return result;}
 static Set<String> eligible(Application app)throws Exception {
  JSONObject section=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/section.json"));
  Set<String> complete=NativeSessionStore.projectedCompletedLessons(app),eligible=new HashSet<>();
  boolean prerequisites=true;
  JSONArray units=section.getJSONArray("units");
  for(int i=0;i<units.length();i++){
   JSONArray levels=units.getJSONObject(i).getJSONArray("levels");
   for(int j=0;j<levels.length();j++){
    JSONObject level=levels.getJSONObject(j);
    if("chest".equals(level.optString("type"))){if(prerequisites)eligible.add(level.getString("id"));continue;}
    JSONArray lessons=level.getJSONObject("pathLevelClientData").getJSONArray("sessionMetadatas");
    for(int k=0;k<lessons.length();k++)prerequisites&=complete.contains(lessons.getJSONObject(k).getString("id"));
   }
  }
  // A previous release placed a chest after every node. Existing claims
  // remain eligible and count toward the balance after regrouping.
  JSONObject legacy=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/legacy-chest-requirements.json"));
  for(Iterator<String> keys=legacy.keys();keys.hasNext();){
   String id=keys.next();JSONArray required=legacy.getJSONArray(id);boolean valid=true;
   for(int k=0;k<required.length();k++)if(!complete.contains(required.getString(k))){valid=false;break;}
   if(valid)eligible.add(id);
  }
  return eligible;
 }
 static synchronized boolean merge(Application app,JSONObject incoming)throws Exception {
  JSONObject records=snapshot(app);Set<String> allowed=eligible(app);boolean changed=false;
  for(Iterator<String> i=incoming.keys();i.hasNext();){String id=i.next();
   if(allowed.contains(id)&&!records.has(id)&&incoming.optLong(id,0)>0){records.put(id,incoming.getLong(id));changed=true;}
  }
  if(!changed)return false;
  File root=NativeAccountStore.root(app);if(!root.isDirectory()&&!root.mkdirs())throw new IOException("Cannot create reward store");
  AtomicFile file=new AtomicFile(new File(root,"chests.json"));FileOutputStream output=null;
  try{output=file.startWrite();output.write(records.toString().getBytes("UTF-8"));file.finishWrite(output);}
  catch(Exception error){if(output!=null)file.failWrite(output);throw error;}
  return true;
 }
 public static boolean claim(Object viewModel,Object reward){
  if(!NativeCourseBridge.hasLocalCourse())return false;
  try{
   Application app=(Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
   synchronized(NativeAccountStore.LOCK){
    Object config=viewModel.getClass().getField("b").get(viewModel);
    String id=(String)config.getClass().getField("a").get(config);
    if(!eligible(app).contains(id))throw new IllegalStateException("Chest is still locked");
    if(!reward.getClass().getName().endsWith("RewardsServiceReward$CurrencyReward")||reward.getClass().getField("e").getInt(reward)!=GEMS)
     throw new IllegalStateException("Unexpected path chest reward");
    merge(app,new JSONObject().put(id,System.currentTimeMillis()));
    NativeGoogleHost.changed(app);
    // No cache waits on the UI/coroutine thread. Return only after durable claim.
    NativeRewards.refresh(app,true);
    return true;
   }
  }catch(Exception error){throw new IllegalStateException("Cannot claim local path chest",error);}
 }
 static JSONArray bundles(){
  try{return new JSONArray().put(new JSONObject().put("id","duoaero-path-chest").put("rewardBundleType","PATH_CHEST")
   .put("rewards",new JSONArray().put(new JSONObject().put("id","duoaero-path-gems").put("currency","GEMS").put("amount",GEMS).put("consumed",false))));}
  catch(JSONException error){throw new IllegalStateException(error);}
 }
}
