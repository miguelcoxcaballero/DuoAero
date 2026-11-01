package com.duoaero.nativebase;

import android.app.Activity;
import android.app.Instrumentation;
import android.view.View;
import android.view.ViewGroup;

/** Reads already attached original renderers; never changes animation state. */
final class SessionRendering {
 static String inspect(Instrumentation test,Activity activity){
  StringBuilder report=new StringBuilder();
  test.runOnMainSync(()->visit(activity.getWindow().getDecorView(),report,0));
  return report.toString();
 }
 private static void visit(View view,StringBuilder report,int depth){
  if(depth>40)return;
  for(Class<?> type=view.getClass();type!=null;type=type.getSuperclass()){
   if(!type.getName().equals("app.rive.runtime.kotlin.RiveAnimationView"))continue;
   report.append("Attached native Rive: ");
   try{
    Object file=type.getMethod("getFile").invoke(view);
    Object controller=type.getMethod("getController").invoke(view);
    Object renderer=type.getMethod("getArtboardRenderer").invoke(view);
    report.append("file=").append(file!=null)
     .append(" playing=").append(type.getMethod("isPlaying").invoke(view))
     .append(" autoplay=").append(type.getMethod("getAutoplay").invoke(view))
     .append(" artboard=").append(type.getMethod("getArtboardName").invoke(view));
    for(String getter:new String[]{"isActive","getArtboardBounds"})report.append(' ').append(getter).append('=').append(controller.getClass().getMethod(getter).invoke(controller));
    for(String getter:new String[]{"getType","getWidth","getHeight","getHasCppObject"})report.append(' ').append(getter).append('=').append(renderer.getClass().getMethod(getter).invoke(renderer));
   }catch(Exception error){report.append("inspection-error=").append(error.getClass().getSimpleName());}
   report.append('\n');break;
  }
  if(view instanceof ViewGroup){ViewGroup group=(ViewGroup)view;for(int i=0;i<group.getChildCount();i++)visit(group.getChildAt(i),report,depth+1);}
 }
}
