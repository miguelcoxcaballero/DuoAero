package com.duoaero.nativebase;

import android.app.Activity;
import android.os.SystemClock;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewTreeObserver;
import android.view.Window;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

/** Synthetic build only: observe the real input and the original summary draw. */
public final class NativeCompletionTiming {
 private static volatile long lastTouchUptime;
 private static final class Observer implements InvocationHandler {
  final Window.Callback original;
  Observer(Window.Callback original){this.original=original;}
  public Object invoke(Object proxy,Method method,Object[] args)throws Throwable {
   if("dispatchTouchEvent".equals(method.getName()) && args!=null && args.length==1 && args[0] instanceof MotionEvent){
    MotionEvent event=(MotionEvent)args[0];
    if(event.getActionMasked()==MotionEvent.ACTION_UP)lastTouchUptime=event.getEventTime();
   }
   try{return method.invoke(original,args);}catch(InvocationTargetException error){throw error.getCause();}
  }
 }
 public static void attach(Activity activity){
  Window window=activity.getWindow();Window.Callback callback=window.getCallback();
  if(callback==null || Proxy.isProxyClass(callback.getClass()) && Proxy.getInvocationHandler(callback) instanceof Observer)return;
  window.setCallback((Window.Callback)Proxy.newProxyInstance(Window.Callback.class.getClassLoader(),new Class<?>[]{Window.Callback.class},new Observer(callback)));
 }
 public static void observeSummary(View root,View button){
  if(root==null||button==null)return;
  final long touch=lastTouchUptime;
  Log.i("DuoAeroCompletionTiming","summary_view_created_after_last_touch_ms="+(touch>0?SystemClock.uptimeMillis()-touch:-1));
  root.getViewTreeObserver().addOnPreDrawListener(new ViewTreeObserver.OnPreDrawListener(){
   public boolean onPreDraw(){
    if(!root.isShown()||!button.isShown())return true;
    android.graphics.Rect visible=new android.graphics.Rect();
    if(!button.getGlobalVisibleRect(visible)||visible.width()<1||visible.height()<1)return true;
    for(View current=button;current!=null;){
     if(current.getAlpha()<0.5f)return true;
     android.view.ViewParent parent=current.getParent();
     current=parent instanceof View?(View)parent:null;
    }
    root.getViewTreeObserver().removeOnPreDrawListener(this);
    long now=SystemClock.uptimeMillis();
    Log.i("DuoAeroCompletionTiming","summary_predraw_after_last_touch_ms="+(touch>0?now-touch:-1)+" button_enabled="+button.isEnabled());
    return true;
   }
  });
 }
}
