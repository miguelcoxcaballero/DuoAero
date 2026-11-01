package com.duoaero.nativebase;

import android.app.Application;
import android.os.Parcel;
import android.os.Parcelable;
import android.util.AtomicFile;
import android.util.Base64;
import android.util.Log;
import java.io.*;
import java.security.MessageDigest;
import java.util.*;
import org.json.*;

/** Restores the original runtime's Parcelable, without editing its fields. */
public final class NativeSessionResume {
 private NativeSessionResume(){}
 private static final String FORMAT="duolingo-6.103.5-persisted-state-v1";
 private static final Map<Object,Boolean> observed=new WeakHashMap<>();
 private static final Set<String> finished=new HashSet<>();
 private static JSONObject catalog;
 private static Application application()throws Exception {
  return (Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
 }
 private static AtomicFile file(Application app,String id)throws IOException {
  File folder=new File(app.getFilesDir(),"duoaero-course/local-test/resume");
  if(!folder.isDirectory()&&!folder.mkdirs())throw new IOException("Cannot create native resume store");
  return new AtomicFile(new File(folder,id+".json"));
 }
 public static synchronized Object stateForSession(Object state,Object session){
  if(!NativeCourseBridge.hasLocalCourse())return state;
  try{
   Object header=session.getClass().getField("a").get(session);
   String id=(String)header.getClass().getMethod("C").invoke(header);
   Application app=application();
   if(catalog==null)catalog=new JSONObject(NativeCourseBridge.asset(app,"duoaero/course/session-catalog.json"));
   if(!catalog.has(id)||!id.matches("[A-Za-z0-9_-]{1,160}")||finished.contains(id))return state;
   String revision=Base64.encodeToString(MessageDigest.getInstance("SHA-256").digest(catalog.getJSONObject(id).toString().getBytes("UTF-8")),Base64.NO_WRAP);
   AtomicFile file=file(app,id);
   if(!observed.containsKey(session)){
    observed.put(session,Boolean.TRUE);
    if(((List<?>)state.getClass().getField("b").get(state)).isEmpty()){
     try(FileInputStream input=file.openRead()){
      ByteArrayOutputStream data=new ByteArrayOutputStream();byte[] buffer=new byte[8192];int n;
      while((n=input.read(buffer))!=-1){data.write(buffer,0,n);if(data.size()>8*1024*1024)throw new IOException("Native resume record too large");}
      JSONObject saved=new JSONObject(data.toString("UTF-8"));
      if(!FORMAT.equals(saved.getString("format"))||!id.equals(saved.getString("id"))||!revision.equals(saved.getString("revision")))throw new IOException("Native resume content changed");
      byte[] bytes=Base64.decode(saved.getString("parcel"),Base64.NO_WRAP);
      Parcel parcel=Parcel.obtain();
      try{
       parcel.unmarshall(bytes,0,bytes.length);parcel.setDataPosition(0);
       Object restored=((Parcelable.Creator<?>)state.getClass().getField("CREATOR").get(null)).createFromParcel(parcel);
       if(!state.getClass().equals(restored.getClass())||parcel.dataAvail()!=0)throw new IOException("Invalid native resume parcel");
       state=restored;
      }finally{parcel.recycle();}
      Log.i("DuoAeroNative","Original session state restored: "+id+"; completed challenge records="+((List<?>)state.getClass().getField("b").get(state)).size());
     }catch(FileNotFoundException absent){}
     catch(Exception invalid){file.delete();Log.w("DuoAeroNative","Native resume record could not be restored; starting this lesson again",invalid);}
    }
   }
   if(((List<?>)state.getClass().getField("b").get(state)).isEmpty())return state;
   Parcel parcel=Parcel.obtain();byte[] bytes;
   try{((Parcelable)state).writeToParcel(parcel,0);bytes=parcel.marshall();}finally{parcel.recycle();}
   if(bytes.length>4*1024*1024)throw new IOException("Native session state too large");
   JSONObject record=new JSONObject().put("format",FORMAT).put("id",id).put("revision",revision).put("parcel",Base64.encodeToString(bytes,Base64.NO_WRAP));
   FileOutputStream output=null;
   try{output=file.startWrite();output.write(record.toString().getBytes("UTF-8"));file.finishWrite(output);}
   catch(Exception error){if(output!=null)file.failWrite(output);throw error;}
   return state;
  }catch(Exception error){throw new IllegalStateException("Cannot preserve original local lesson state",error);}
 }
 static synchronized void completed(Application app,String id)throws Exception {
  finished.add(id);file(app,id).delete();
 }
}
