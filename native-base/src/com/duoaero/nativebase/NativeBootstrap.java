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
  if(prepared)return;
  if(NativeAccountStore.required(app)&&NativeAccountStore.current(app).isEmpty()){
   NativeCourseBridge.localOnly=true;return;
  }
  if(NativeCourseBridge.localOnly&&!NativeAccountStore.required(app))return;
  try{
   // Seed the real login/user cache before DuoApp captures its startup state.
   // Late input was verified to leave a cold launcher on the welcome screen.
   NativeLocalProfile.install(app,"MATH_BT",true);
   prepared=true;
   Log.i("DuoAeroNative","Standalone profile prepared before original application startup");
  }catch(Exception error){throw new IllegalStateException("Cannot prepare local course identity",error);}
 }
 public static synchronized void start(Application app){
  NativeUpdateHost.install(app);
  NativeRewards.observe(app);
  if(NativeAccountStore.required(app))NativeGoogleHost.install(app);
  if(!prepared&&NativeAccountStore.required(app)){
   try{NativeLocalConfig.install(app);}catch(Exception error){throw new IllegalStateException("Cannot initialize original welcome configuration",error);}
  }
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
    // Social cache input is independent of the goals scope. A cold launcher
    // may take longer than one observation window to publish that scope.
    try{NativeLocalFeatures.social(app);}
    catch(Exception error){Log.e("DuoAeroNative","Standalone social initialization failed",error);}
    try{NativeLocalFeatures.avatar(app);}
    catch(Exception error){Log.e("DuoAeroNative","Standalone avatar configuration failed",error);}
    for(int attempt=1;attempt<=3;attempt++){
     try{NativeLocalFeatures.goals(app);Log.i("DuoAeroNative","Standalone goals cache ready on attempt "+attempt);break;}
     catch(Exception error){
      if(attempt==3)Log.e("DuoAeroNative","Standalone goals initialization failed",error);
      else Log.w("DuoAeroNative","Original goals scope not ready; retrying native cache initialization");
     }
    }
   },"duoaero-native-features").start();
  }catch(Exception error){
   Log.e("DuoAeroNative","Standalone native initialization failed",error);
   throw new IllegalStateException("Cannot initialize local Aerospace course",error);
  }
 }
 static synchronized void accountChanged(Application app,boolean signedIn)throws Exception {
  prepared=false;finished=false;
  NativeSessionResume.accountChanged();
  NativeCourseBridge.localCourseInstalled=false;
  NativeCourseBridge.serveLocalCourse=false;
  if(signedIn){
   // The private Google identity owns the store. The original local course
   // profile remains an adapter and is never sent to Duolingo's service.
   NativeLocalProfile.install(app,"MATH_BT",true);prepared=true;start(app);
  }else NativeLocalProfile.clearLogin(app);
 }
}
