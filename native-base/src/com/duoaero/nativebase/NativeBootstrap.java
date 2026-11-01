package com.duoaero.nativebase;

import android.app.Application;
import android.os.SystemClock;
import android.util.Log;

/** Standalone integration of the native repositories. No replacement screens. */
public final class NativeBootstrap {
 private static boolean prepared,finished;
 public static synchronized void prepare(Application app){
  try(java.io.InputStream marker=app.getAssets().open("duoaero/standalone-bootstrap")){}
  catch(java.io.IOException disabled){return;}
  if(prepared||NativeCourseBridge.localOnly)return;
  try{
   // Seed the real login/user cache before DuoApp captures its startup state.
   // Late input was verified to leave a cold launcher on the welcome screen.
   NativeLocalProfile.install(app,"MATH_BT",true);
   prepared=true;
   Log.i("DuoAeroNative","Standalone profile prepared before original application startup");
  }catch(Exception error){throw new IllegalStateException("Cannot prepare local course identity",error);}
 }
 public static synchronized void start(Application app){
  if(!prepared||finished)return;
  finished=true;
  long begin=SystemClock.elapsedRealtime();
  try{
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
