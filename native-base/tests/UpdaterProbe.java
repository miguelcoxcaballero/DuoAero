package com.duoaero.nativebase;

import android.app.*;
import android.content.*;
import android.net.Uri;
import android.os.Bundle;
import android.view.accessibility.AccessibilityNodeInfo;
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import org.json.JSONObject;

/** Exercises the host's original settings control and canonical updater. */
public final class UpdaterProbe extends Instrumentation {
 public void onCreate(Bundle args){
  try{Class.forName("com.duoaero.nativebase.NativeCourseBridge",true,getTargetContext().getClassLoader()).getField("captureNativeFlows").setBoolean(null,true);}
  catch(Exception error){throw new IllegalStateException(error);}
  start();
 }
 public void onStart(){
  Bundle result=new Bundle();StringBuilder report=new StringBuilder();
  try{
   Context context=getTargetContext();ClassLoader loader=context.getClassLoader();
   // LaunchActivity performs original process/home initialization that a
   // direct internal SettingsActivity intent does not perform.
   Activity homeActivity=startActivitySync(new Intent().setClassName(context.getPackageName(),"com.duolingo.splash.LaunchActivity").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
   boolean home=false;
   for(int attempt=0;attempt<90;attempt++){
    AccessibilityNodeInfo root=getUiAutomation().getRootInActiveWindow();
    if(root!=null)try{home=contains(root,"Aerospace activities / Aerospace infrastructure");}finally{root.recycle();}
    if(home)break;Thread.sleep(1000);
   }
   if(!home)throw new IllegalStateException("Original home did not initialize before settings");
   runOnMainSync(()->{
    android.view.View tab=homeActivity.findViewById(homeActivity.getResources().getIdentifier("tabProfile","id","com.duolingo"));
    if(tab==null||!tab.performClick())throw new IllegalStateException("Original profile tab missing");
   });
   Thread.sleep(10000);
   SessionScreen.capture(this,"profile-observation","profile-observation");
   try(SessionDependencies dependencies=SessionDependencies.profile(homeActivity)){Thread.sleep(5000);report.append(dependencies.report());}
   catch(Exception observation){report.append("Profile observation unavailable: ").append(observation.getClass().getSimpleName()).append('\n');}
   Activity settings=startActivitySync(new Intent().setClassName(context.getPackageName(),"com.duolingo.settings.SettingsActivity").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
   ActivityMonitor updaterMonitor=addMonitor("com.inhouse.services.updater.UpdateActivity",null,false);
   boolean found=false;
   for(int attempt=0;attempt<60;attempt++){
    AccessibilityNodeInfo root=getUiAutomation().getRootInActiveWindow();
    if(root!=null)try{found=click(root,"App updates");if(!found&&attempt>10)scroll(root);}finally{root.recycle();}
    if(found)break;Thread.sleep(1000);
   }
   if(!found){
    SessionScreen.capture(this,"updater-settings","updater-settings");
    try(SessionDependencies dependencies=SessionDependencies.named(settings)){Thread.sleep(5000);report.append(dependencies.report());}
    catch(Exception observation){report.append("Optional dependency observation unavailable: ").append(observation.getClass().getSimpleName()).append('\n');}
    throw new IllegalStateException("Original settings did not expose App updates");
   }
   Thread.sleep(6000);
   SessionScreen.capture(this,"updater-settings","updater-settings");
   Activity canonical=waitForMonitorWithTimeout(updaterMonitor,10000);removeMonitor(updaterMonitor);
   if(canonical==null)throw new IllegalStateException("Canonical updater activity not observed");
   Field webField=canonical.getClass().getDeclaredField("web");webField.setAccessible(true);
   android.webkit.WebView web=(android.webkit.WebView)webField.get(canonical);
   java.util.concurrent.CountDownLatch bridgeDone=new java.util.concurrent.CountDownLatch(1);
   java.util.concurrent.atomic.AtomicReference<String> bridgeValue=new java.util.concurrent.atomic.AtomicReference<>();
   runOnMainSync(()->web.evaluateJavascript("JSON.stringify({visible:document.body.innerText,version:InhouseNative.getAppVersion(),code:InhouseNative.getAppVersionCode(),state:JSON.parse(InhouseNative.getUpdateState())})",value->{bridgeValue.set(value);bridgeDone.countDown();}));
   if(!bridgeDone.await(10,java.util.concurrent.TimeUnit.SECONDS))throw new IllegalStateException("Canonical JavaScript bridge timed out");
   String decoded=(String)new org.json.JSONTokener(bridgeValue.get()).nextValue();JSONObject bridgeState=new JSONObject(decoded);
   String visible=bridgeState.getString("visible");
   if(!visible.contains("Updates")||!visible.contains("Version B")||!visible.contains("Check for updates"))throw new IllegalStateException("Canonical updater visible DOM missing settings");
   android.content.pm.PackageInfo installed=context.getPackageManager().getPackageInfo(context.getPackageName(),0);
   if(!installed.versionName.equals(bridgeState.getString("version"))||installed.getLongVersionCode()!=bridgeState.getLong("code")||!"B".equals(bridgeState.getJSONObject("state").getString("channel")))throw new IllegalStateException("Canonical bridge did not expose actual installed identity/policy");
   Class<?> state=Class.forName("com.inhouse.services.updater.UpdateState",true,loader);
   JSONObject policy=new JSONObject((String)state.getMethod("read",Context.class).invoke(null,context));
   if(!"B".equals(policy.getString("channel"))||policy.getInt("developmentConsent")!=0)throw new IllegalStateException("Unexpected initial channel policy");
   File directory=new File(context.getCacheDir(),"updates");directory.mkdirs();
   File sample=new File(directory,"provider-probe.txt");byte[] expected="DuoAero provider smoke test".getBytes(StandardCharsets.UTF_8);
   try(FileOutputStream output=new FileOutputStream(sample)){output.write(expected);}
   Class<?> provider=Class.forName("com.inhouse.services.updater.UpdateFileProvider",true,loader);
   Uri uri=(Uri)provider.getMethod("getUriForFile",Context.class,String.class,File.class).invoke(null,context,context.getPackageName()+".update-provider",sample);
   try(InputStream input=context.getContentResolver().openInputStream(uri)){
    ByteArrayOutputStream bytes=new ByteArrayOutputStream();int b;while((b=input.read())!=-1)bytes.write(b);
    if(!java.util.Arrays.equals(expected,bytes.toByteArray()))throw new IllegalStateException("Own provider returned wrong content");
   }finally{sample.delete();}
   report.append("PASS: original settings App updates control opens canonical settings; default B without A consent; own update-provider resolves canonical cache paths and reads exact bytes. No update installation asserted.\n");
   result.putBoolean("UPDATER_HOST_VERIFIED",true);
   report.append("UPDATER_HOST_VERIFIED=true\n");
  }catch(Throwable error){if(error instanceof InvocationTargetException)error=error.getCause();report.append(android.util.Log.getStackTraceString(error));}
  result.putString("stream",report.toString());finish(-1,result);
 }
 private static boolean contains(AccessibilityNodeInfo n,String label){
  if(String.valueOf(n.getText()).contains(label)||String.valueOf(n.getContentDescription()).contains(label))return true;
  for(int i=0;i<n.getChildCount();i++){AccessibilityNodeInfo c=n.getChild(i);if(c!=null)try{if(contains(c,label))return true;}finally{c.recycle();}}
  return false;
 }
 private static boolean click(AccessibilityNodeInfo n,String label){
  if(label.equalsIgnoreCase(String.valueOf(n.getText()))){
   if(n.performAction(AccessibilityNodeInfo.ACTION_CLICK))return true;
   AccessibilityNodeInfo p=n.getParent();if(p!=null)try{return p.performAction(AccessibilityNodeInfo.ACTION_CLICK);}finally{p.recycle();}
  }
  for(int i=0;i<n.getChildCount();i++){AccessibilityNodeInfo c=n.getChild(i);if(c!=null)try{if(click(c,label))return true;}finally{c.recycle();}}
  return false;
 }
 private static boolean scroll(AccessibilityNodeInfo n){
  if(n.isScrollable()&&n.performAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD))return true;
  for(int i=0;i<n.getChildCount();i++){AccessibilityNodeInfo c=n.getChild(i);if(c!=null)try{if(scroll(c))return true;}finally{c.recycle();}}
  return false;
 }
}
