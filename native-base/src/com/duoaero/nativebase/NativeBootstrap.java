package com.duoaero.nativebase;

import android.app.Application;
import android.os.SystemClock;
import android.util.Log;

/** Standalone integration of the native repositories. No replacement screens. */
public final class NativeBootstrap {
 private static boolean started;
 public static synchronized void start(Application app){
  // Enabled only in an explicitly built standalone diagnostic until cold-start
  // and persistent-account acceptance passes. Ordinary probes stay isolated.
  try(java.io.InputStream marker=app.getAssets().open("duoaero/standalone-bootstrap")){}
  catch(java.io.IOException disabled){return;}
  if(started||NativeCourseBridge.localOnly)return;
  started=true;
  long begin=SystemClock.elapsedRealtime();
  try{
   NativeLocalProfile.install(app,"MATH_BT",true);
   NativeLocalConfig.install(app);
   NativeLocalCache.install(app,true);
   NativeCourseBridge.localCourseInstalled=true;
   NativeCourseBridge.serveLocalCourse=true;
   Log.i("DuoAeroNative","Standalone native profile/course initialized in "+(SystemClock.elapsedRealtime()-begin)+" ms");
   new Thread(()->{
    try{NativeLocalFeatures.goals(app);NativeLocalFeatures.social(app);Log.i("DuoAeroNative","Standalone optional feature caches ready");}
    catch(Exception error){Log.e("DuoAeroNative","Standalone feature initialization failed",error);}
   },"duoaero-native-features").start();
  }catch(Exception error){
   Log.e("DuoAeroNative","Standalone native initialization failed",error);
   throw new IllegalStateException("Cannot initialize local Aerospace course",error);
  }
 }
}
