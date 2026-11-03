package com.duoaero.nativebase;

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
  CountDownLatch entered=new CountDownLatch(1);
  AtomicReference<Throwable> error=new AtomicReference<>();
  AtomicReference<View> overlay=new AtomicReference<>();
  AtomicReference<Object> animation=new AtomicReference<>();
  test.runOnMainSync(()->{
   try{
    ClassLoader loader=activity.getClassLoader();
    Class<?> holeClass=Class.forName("com.duolingo.core.ui.CharacterInHoleAnimationView",true,loader);
    View hole=(View)holeClass.getConstructor(android.content.Context.class).newInstance(activity);
    Object binding=holeClass.getField("s").get(hole);
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
    Class<?> function=Class.forName("kotlin.jvm.functions.Function0",true,loader);
    Object onEntrance=java.lang.reflect.Proxy.newProxyInstance(loader,new Class<?>[]{function},(proxy,method,args)->{
     if(method.getName().equals("invoke")){
      try{
       Object manager=lottie.getClass().getMethod("getBasePerformanceModeManager").invoke(lottie);
       Object mode=manager.getClass().getMethod("a").invoke(manager);
       Object motionDisabled=manager.getClass().getMethod("b").invoke(manager);
       float animatorScale=android.provider.Settings.Global.getFloat(activity.getContentResolver(), "animator_duration_scale", 1f);
       boolean loaded=lottie.getClass().getMethod("getComposition").invoke(lottie)!=null;
       android.util.Log.i("DuoAeroWaveProbe", "mode="+mode+" motionDisabled="+motionDisabled+" animatorScale="+animatorScale+" attached="+lottie.isAttachedToWindow()+" shown="+lottie.isShown()+" compositionAtEntrance="+loaded);
       lottie.getClass().getMethod("u").invoke(lottie);entered.countDown();
      }
      catch(Throwable problem){error.set(problem);entered.countDown();}
      return Class.forName("xv80",true,loader).getField("a").get(null);
     }
     if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
     if(method.getName().equals("equals"))return proxy==args[0];
     if(method.getName().equals("toString"))return "DuoAero wave entrance probe";
     return null;
    });
    // Same 500 ms entrance and start callback as setAndPlayHoleAnimation.
    holeClass.getMethod("u",View.class,float.class,function).invoke(null,lottie,110f,onEntrance);
   }catch(Throwable failure){error.set(failure);entered.countDown();}
  });
  if(!entered.await(15,TimeUnit.SECONDS))throw new IllegalStateException("Original hole entrance callback missing");
  if(error.get()!=null)throw new IllegalStateException("Cannot start original wave view",error.get());
  android.os.ParcelFileDescriptor video=test.getUiAutomation().executeShellCommand("screenrecord --time-limit 12 /sdcard/duoaero-wave-preview.mp4");
  float min=1f,max=0f;
  for(int i=0;i<20;i++){
   Thread.sleep(300);SessionScreen.capture(test,"wave-lottie-"+i,"wave-lottie-"+i);
   final int sampleIndex=i;final float[] progress={0f};
   test.runOnMainSync(()->{
    try{
     View sample=(View)animation.get();Object drawable=sample.getClass().getField("e").get(sample);
     android.animation.Animator animator=(android.animation.Animator)drawable.getClass().getField("b").get(drawable);
     Object composition=sample.getClass().getMethod("getComposition").invoke(sample);
     progress[0]=((Number)sample.getClass().getMethod("getProgress").invoke(sample)).floatValue();
     android.util.Log.i("DuoAeroWaveProbe","sample="+sampleIndex+" progress="+progress[0]+" frame="+sample.getClass().getMethod("getFrame").invoke(sample)+" duration="+sample.getClass().getMethod("getDuration").invoke(sample)+" composition="+(composition!=null)+" running="+animator.isRunning()+" attached="+sample.isAttachedToWindow()+" shown="+sample.isShown());
    }catch(Throwable failure){error.set(failure);}
   });
   if(error.get()!=null)throw new IllegalStateException("Cannot observe original wave animator",error.get());
   min=Math.min(min,progress[0]);max=Math.max(max,progress[0]);
  }
  if(video!=null)try(java.io.InputStream stream=new android.os.ParcelFileDescriptor.AutoCloseInputStream(video)){while(stream.read()!=-1){}}
  if(max-min<.05f)throw new IllegalStateException("Original looping wave did not advance");
  test.runOnMainSync(()->{View view=overlay.get();if(view!=null&&view.getParent() instanceof ViewGroup)((ViewGroup)view.getParent()).removeView(view);});
  return "Original hole entrance callback delivered and looping wave advanced; inspect captured frames.\n";
 }
}

