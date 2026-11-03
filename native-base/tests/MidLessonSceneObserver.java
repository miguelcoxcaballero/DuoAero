package com.duoaero.nativebase;

import android.app.Activity;
import android.app.Instrumentation;
import android.graphics.Rect;
import android.view.View;
import android.view.ViewGroup;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

/** Observe only naturally reached original mid-lesson views; never create one. */
final class MidLessonSceneObserver implements AutoCloseable {
 private final Instrumentation test;
 private final AtomicReference<Activity> resumed;
 private final AtomicBoolean active=new AtomicBoolean(true),seen=new AtomicBoolean(false);
 private volatile String geometry="not observed",failure="none";
 private final Thread observer;
 MidLessonSceneObserver(Instrumentation test,AtomicReference<Activity> resumed){
  this.test=test;this.resumed=resumed;
  observer=new Thread(()->{
   try{
    while(active.get()&&!seen.get()){
     final Rect bounds=new Rect();final boolean[] visible={false};
     test.runOnMainSync(()->{
      Activity activity=resumed.get();
      if(activity==null||activity.getWindow()==null)return;
      View scene=find(activity.getWindow().getDecorView());
      if(scene!=null&&scene.isShown()&&scene.getGlobalVisibleRect(bounds)&&bounds.width()>0&&bounds.height()>0)visible[0]=true;
     });
     if(visible[0]){
      geometry=bounds.toShortString();seen.set(true);
      for(int i=0;i<3&&active.get();i++){
       SessionScreen.capture(test,"journey-midlesson-"+i,"journey-midlesson-"+i);
       Thread.sleep(350);
      }
      break;
     }
     Thread.sleep(350);
    }
   }catch(Throwable error){failure=error.getClass().getSimpleName();}
  },"DuoAero-midlesson-observer");
  observer.setDaemon(true);observer.start();
 }
 private static View find(View view){
  if(view.getClass().getName().equals("com.duolingo.core.ui.MidLessonAnimationView"))return view;
  if(view instanceof ViewGroup){ViewGroup group=(ViewGroup)view;for(int i=0;i<group.getChildCount();i++){View found=find(group.getChildAt(i));if(found!=null)return found;}}
  return null;
 }
 public void close(){active.set(false);try{observer.join(3000);}catch(InterruptedException e){Thread.currentThread().interrupt();}}
 String report(){return "Original mid-lesson scene observed="+seen.get()+" visibleBounds="+geometry+" observerFailure="+failure+"; inspect captures and normal continuation separately.\n";}
}
