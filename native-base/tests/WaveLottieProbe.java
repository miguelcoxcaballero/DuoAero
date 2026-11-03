package com.duoaero.nativebase;

import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.app.Activity;
import android.app.Instrumentation;
import android.graphics.Color;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

/** Exercises the original in-lesson hole view; not a lesson-navigation test. */
public final class WaveLottieProbe {
 private WaveLottieProbe(){}
 public static String run(Instrumentation test,Activity activity)throws Exception{
  CountDownLatch ended=new CountDownLatch(1);
  AtomicReference<Throwable> error=new AtomicReference<>();
  AtomicReference<View> overlay=new AtomicReference<>();
  AtomicReference<Object> animation=new AtomicReference<>();
  test.runOnMainSync(()->{
   try{
    ClassLoader loader=activity.getClassLoader();
    Class<?> cls=Class.forName("com.duolingo.core.ui.CharacterInHoleAnimationView",true,loader);
    View hole=(View)cls.getConstructor(android.content.Context.class).newInstance(activity);
    Object binding=cls.getField("s").get(hole);
    View lottie=(View)binding.getClass().getField("c").get(binding);
    View alternate=(View)binding.getClass().getField("d").get(binding);
    alternate.setVisibility(View.GONE);lottie.setVisibility(View.VISIBLE);
    FrameLayout host=new FrameLayout(activity);host.setBackgroundColor(Color.rgb(18,31,36));
    host.addView(hole,new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.MATCH_PARENT));
    activity.addContentView(host,new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.MATCH_PARENT));
    overlay.set(host);animation.set(lottie);
    int id=activity.getResources().getIdentifier("duo_waving","raw","com.duolingo");
    if(id==0)throw new IllegalStateException("Original wave resource missing");
    lottie.getClass().getMethod("setAnimation",int.class).invoke(lottie,id);
    lottie.getClass().getMethod("m",AnimatorListenerAdapter.class).invoke(lottie,new AnimatorListenerAdapter(){
      @Override public void onAnimationEnd(Animator a){ended.countDown();}
    });
    lottie.getClass().getMethod("i").invoke(lottie);
   }catch(Throwable failure){error.set(failure);}
  });
  if(error.get()!=null)throw new IllegalStateException("Cannot start original wave view",error.get());
  android.os.ParcelFileDescriptor video=test.getUiAutomation().executeShellCommand("screenrecord --time-limit 12 /sdcard/duoaero-wave-preview.mp4");
  for(int i=0;i<20;i++){
   Thread.sleep(300);SessionScreen.capture(test,"wave-lottie-"+i,"wave-lottie-"+i);
  }
  if(video!=null)try(java.io.InputStream stream=new android.os.ParcelFileDescriptor.AutoCloseInputStream(video)){while(stream.read()!=-1){}}
  if(!ended.await(8,TimeUnit.SECONDS))throw new IllegalStateException("Original Lottie completion callback missing");
  test.runOnMainSync(()->{View view=overlay.get();if(view!=null&&view.getParent() instanceof ViewGroup)((ViewGroup)view.getParent()).removeView(view);});
  return "Original character-in-hole view played waving resource and delivered completion callback; assess captured frames visually.\n";
 }
}
