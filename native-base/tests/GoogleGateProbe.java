package com.duoaero.nativebase;

import android.app.*;
import android.content.*;
import android.os.Bundle;
import android.view.accessibility.AccessibilityNodeInfo;
import java.lang.reflect.*;

/** Original welcome/account routing only: synthetic identity, no OAuth claim. */
public final class GoogleGateProbe extends Instrumentation {
 public void onCreate(Bundle args){start();}
 public void onStart(){
  Bundle result=new Bundle();StringBuilder report=new StringBuilder();
  try{
   Context context=getTargetContext();ClassLoader loader=context.getClassLoader();
   context.startActivity(context.getPackageManager().getLaunchIntentForPackage(context.getPackageName()).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
   await("CONTINUE WITH GOOGLE");SessionScreen.capture(this,"google-welcome","google-welcome");
   Class<?> type=Class.forName("com.duoaero.nativebase.NativeGoogleHost",true,loader);
   Field field=type.getDeclaredField("instance");field.setAccessible(true);Object host=field.get(null);
   if(host==null)throw new IllegalStateException("Native Google host missing");
   type.getMethod("onAccount",String.class,String.class).invoke(host,"synthetic-routing-account","Synthetic routing probe");
   await("Midterm 1");SessionScreen.capture(this,"google-account-home","google-account-home");
   type.getMethod("onSignedOut").invoke(host);
   await("CONTINUE WITH GOOGLE");SessionScreen.capture(this,"google-signed-out","google-signed-out");
   if(!context.getSharedPreferences("duoaero-google",0).getString("account","").isEmpty())throw new IllegalStateException("Account retained after sign out");
   report.append("PASS: original Google-only welcome, synthetic identity activation reaches original course, sign out returns to original welcome. No real OAuth or Drive network acceptance asserted.\n");
   result.putBoolean("GOOGLE_GATE_VERIFIED",true);
   report.append("GOOGLE_GATE_VERIFIED=true\n");
  }catch(Throwable error){
   if(error instanceof InvocationTargetException)error=error.getCause();report.append(android.util.Log.getStackTraceString(error));
   try{SessionScreen.capture(this,"google-failure","google-failure");}catch(Throwable ignored){}
  }
  result.putString("stream",report.toString());finish(-1,result);
 }
 private void await(String text)throws Exception {
  for(int i=0;i<90;i++){
   AccessibilityNodeInfo root=getUiAutomation().getRootInActiveWindow();
   if(root!=null)try{if(contains(root,text))return;}finally{root.recycle();}
   Thread.sleep(1000);
  }
  throw new IllegalStateException("Original screen did not expose "+text);
 }
 private static boolean contains(AccessibilityNodeInfo node,String text){
  if(text.equalsIgnoreCase(String.valueOf(node.getText()))||text.equalsIgnoreCase(String.valueOf(node.getContentDescription())))return true;
  for(int i=0;i<node.getChildCount();i++){AccessibilityNodeInfo child=node.getChild(i);if(child!=null)try{if(contains(child,text))return true;}finally{child.recycle();}}
  return false;
 }
}
