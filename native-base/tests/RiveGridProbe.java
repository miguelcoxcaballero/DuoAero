package com.duoaero.nativebase;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.Intent;
import android.os.Bundle;
import android.util.AttributeSet;
import android.view.View;
import java.io.File;
import java.lang.reflect.Method;

/** Diagnostic: render the patched original grid in the app's own Rive view. */
public final class RiveGridProbe extends Instrumentation {
 public void onCreate(Bundle args){start();}
 public void onStart(){
  Bundle result=new Bundle();StringBuilder report=new StringBuilder();
  try {
   Activity activity=startActivitySync(new Intent().setClassName(getTargetContext().getPackageName(),"com.duolingo.splash.LaunchActivity").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
   ClassLoader loader=getTargetContext().getClassLoader();
   Class<?> rive=Class.forName("app.rive.runtime.kotlin.core.Rive",true,loader);
   Class<?> renderer=Class.forName("app.rive.runtime.kotlin.core.RendererType",true,loader);
   rive.getMethod("init$default",rive,android.content.Context.class,renderer,int.class,Object.class)
       .invoke(null,rive.getField("INSTANCE").get(null),activity,null,2,null);
   Class<?> type=Class.forName("app.rive.runtime.kotlin.RiveAnimationView",true,loader);
   final Object[] view={null};final Throwable[] error={null};
   runOnMainSync(()->{try{
    view[0]=type.getConstructor(android.content.Context.class,AttributeSet.class).newInstance(activity,null);
    activity.setContentView((View)view[0]);
    int resource=activity.getResources().getIdentifier("math_junior_grid","raw","com.duolingo");
    if(resource==0)throw new IllegalStateException("Original grid resource missing");
    Method load=null;for(Method m:type.getMethods())if(m.getName().equals("setRiveResource$default"))load=m;
    if(load==null)throw new IllegalStateException("Original Rive resource API missing");
    // Explicit original animation, autoplay; all other settings use Rive defaults.
    load.invoke(null,view[0],resource,null,"Timeline 1",null,true,false,null,null,null,490,null);
   }catch(Throwable t){error[0]=t;}});
   if(error[0]!=null)throw new IllegalStateException("Rive setup failed",error[0]);
   boolean ready=false;
   for(int i=0;i<40;i++){
    Thread.sleep(500);
    if(type.getMethod("getFile").invoke(view[0])!=null && (Boolean)type.getMethod("isPlaying").invoke(view[0])){ready=true;break;}
   }
   if(!ready)throw new IllegalStateException("Patched original Rive view did not start");
   File marker=new File(getTargetContext().getExternalFilesDir(null),"linus-rive-ready");
   if(!marker.createNewFile()&&!marker.exists())throw new IllegalStateException("Cannot signal readiness");
   Thread.sleep(18000);
   report.append("RIVE_GRID_READY=true; renderer started; visual playback requires video inspection.\n");
  }catch(Throwable t){report.append(android.util.Log.getStackTraceString(t));}
  result.putString(Instrumentation.REPORT_KEY_STREAMRESULT,report.toString());finish(0,result);
 }
}
