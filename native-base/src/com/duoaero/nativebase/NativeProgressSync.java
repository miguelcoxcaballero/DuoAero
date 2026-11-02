package com.duoaero.nativebase;

import android.app.Application;
import java.util.*;
import org.json.*;

/** Account-bound bridge payload; no tokens, original telemetry or resume parcel. */
final class NativeProgressSync {
 private NativeProgressSync(){}
 static String read(Application app,String account)throws Exception {
  synchronized(NativeAccountStore.LOCK){
   NativeAccountStore.require(app,account);
   JSONObject records=NativeMistakeStore.snapshot(app),lessons=NativeSessionStore.exportCompletions(app);
   JSONObject chests=NativeChestRewards.snapshot(app);
   long updated=0;
   for(Iterator<String> keys=chests.keys();keys.hasNext();)updated=Math.max(updated,chests.optLong(keys.next()));
   for(Iterator<String> keys=records.keys();keys.hasNext();)updated=Math.max(updated,records.getJSONObject(keys.next()).optLong("at"));
   for(Iterator<String> keys=lessons.keys();keys.hasNext();)updated=Math.max(updated,lessons.getJSONObject(keys.next()).optLong("at"));
   return new JSONObject().put("nativeSchema",1).put("records",records).put("completedLessons",lessons).put("chests",chests).put("updatedAt",updated).toString();
  }
 }
 static boolean apply(Application app,String account,String raw)throws Exception {
  if(raw==null||raw.length()>4*1024*1024)throw new IllegalArgumentException("Invalid Drive progress size");
  synchronized(NativeAccountStore.LOCK){
   NativeAccountStore.require(app,account);
   String before=NativeSessionStore.exportCompletions(app).toString();
   JSONObject incoming=new JSONObject(raw);
   if(incoming.optInt("nativeSchema")!=1)throw new IllegalArgumentException("Unsupported native Drive progress schema");
   JSONObject catalog=NativeCourseBridge.sessionCatalog(app);
   Set<String> known=new HashSet<>();
   for(Iterator<String> keys=catalog.keys();keys.hasNext();){JSONArray challenges=catalog.getJSONObject(keys.next()).getJSONArray("challenges");for(int i=0;i<challenges.length();i++)known.add(challenges.getJSONObject(i).getString("id"));}
   JSONObject records=incoming.optJSONObject("records"),lessons=incoming.optJSONObject("completedLessons");
   if(records!=null)NativeMistakeStore.merge(app,records,known);
   if(lessons!=null)NativeSessionStore.importCompletions(app,lessons);
   JSONObject chests=incoming.optJSONObject("chests");
   boolean claimed=chests!=null&&NativeChestRewards.merge(app,chests);
   return claimed||!before.equals(NativeSessionStore.exportCompletions(app).toString());
  }
 }
}
