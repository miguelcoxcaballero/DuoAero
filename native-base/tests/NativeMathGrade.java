package com.duoaero.nativebase;

import android.app.Activity;
import android.app.Instrumentation;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;

/** Reads the visible original fragment's result; never sets a grade or state. */
final class NativeMathGrade {
 static String read(Instrumentation test,Activity activity)throws Exception {
  AtomicReference<String> value=new AtomicReference<>();
  AtomicReference<Exception> error=new AtomicReference<>();
  test.runOnMainSync(()->{
   try{value.set(find(activity.getClass().getMethod("getSupportFragmentManager").invoke(activity),0));}
   catch(Exception e){error.set(e);}
  });
  if(error.get()!=null)throw error.get();
  return value.get();
 }
 private static String find(Object manager,int depth)throws Exception {
  if(depth>10)return null;
  Object store=manager.getClass().getField("c").get(manager);
  List<?> fragments=(List<?>)store.getClass().getMethod("f").invoke(store);
  for(Object fragment:fragments){
   if(!(Boolean)fragment.getClass().getMethod("isVisible").invoke(fragment))continue;
   if(fragment.getClass().getName().equals("com.duolingo.session.challenges.math.MathBlobSelectOneFragment")){
    Object guess=fragment.getClass().getField("E0").get(fragment);
    return guess==null?null:((Enum<?>)guess.getClass().getField("a").get(guess)).name();
   }
   if(fragment.getClass().getName().equals("com.duolingo.session.challenges.math.MathTokenDragFragment")||fragment.getClass().getName().equals("com.duolingo.session.challenges.math.MathExpressionBuildFragment")){
    Object guess=fragment.getClass().getField("E0").get(fragment);
    return guess==null?null:guess.getClass().getField("a").getBoolean(guess)?"CORRECT":"INCORRECT";
   }
   String result=find(fragment.getClass().getMethod("getChildFragmentManager").invoke(fragment),depth+1);
   if(result!=null)return result;
  }
  return null;
 }
 static void require(Instrumentation test,Activity activity,String expected)throws Exception {
  String actual=null;
  for(int attempt=0;attempt<300;attempt++){
   actual=read(test,activity);
   if(actual!=null)break;
   Thread.sleep(100);
  }
  if(!expected.equals(actual))throw new IllegalStateException("Original Math grade: expected "+expected+", got "+actual);
 }
}
