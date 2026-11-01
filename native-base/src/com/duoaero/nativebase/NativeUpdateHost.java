package com.duoaero.nativebase;

import android.app.Activity;
import android.app.Application;
import android.content.Intent;
import android.os.Bundle;
import com.inhouse.services.updater.NativeUpdates;
import com.inhouse.services.updater.UpdateActivity;

/** Host wiring only. The canonical updater owns channels, consent and install. */
public final class NativeUpdateHost implements Application.ActivityLifecycleCallbacks {
 private static NativeUpdateHost instance;
 private static java.lang.ref.WeakReference<Activity> foreground=new java.lang.ref.WeakReference<>(null);
 private static Object updateClick;
 private static java.lang.reflect.Method originalButton;
 private final NativeUpdates updates;
 private NativeUpdateHost(Application app){updates=new NativeUpdates(app);}
 public static synchronized void install(Application app){
  if(instance!=null)return;
  instance=new NativeUpdateHost(app);
  app.registerActivityLifecycleCallbacks(instance);
 }
 public static void open(Activity activity){
  activity.startActivity(new Intent(activity,UpdateActivity.class).putExtra("settings",true));
 }
 public void onActivityResumed(Activity activity){
  foreground=new java.lang.ref.WeakReference<>(activity);
  // Diagnostic packages must not offer production-package APKs automatically.
  // Manual settings still exercise the same canonical UI and installer checks.
  if("com.duoaero".equals(activity.getPackageName()))updates.onResumed(activity);
 }
 /** Add the original settings text-button component to its existing section. */
 public static void settingsRow(Object composer){
  if(!NativeCourseBridge.hasLocalCourse())return;
  try{
   ClassLoader loader=composer.getClass().getClassLoader();
   if(originalButton==null){
    Class<?> function=Class.forName("kotlin.jvm.functions.Function0",true,loader);
    originalButton=Class.forName("oup",true,loader).getMethod("E",int.class,
     Class.forName("o18",true,loader),Class.forName("z5q",true,loader),String.class,String.class,function);
    updateClick=java.lang.reflect.Proxy.newProxyInstance(loader,new Class<?>[]{function},(proxy,method,args)->{
     if(method.getName().equals("invoke")){
      Activity activity=foreground.get();if(activity!=null&&!activity.isFinishing())open(activity);
      return Class.forName("xv80",true,loader).getField("a").get(null);
     }
     if(method.getName().equals("equals"))return proxy==args[0];
     if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
     return "DuoAero update settings";
    });
   }
   originalButton.invoke(null,384,composer,null,"App updates","duoaeroUpdatesButton",updateClick);
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot attach original update settings control",error);}
 }
 public void onActivityPaused(Activity activity){updates.onPaused(activity);}
 public void onActivityDestroyed(Activity activity){updates.onDestroyed(activity);}
 public void onActivityCreated(Activity activity,Bundle state){}
 public void onActivityStarted(Activity activity){}
 public void onActivityStopped(Activity activity){}
 public void onActivitySaveInstanceState(Activity activity,Bundle state){}
}
