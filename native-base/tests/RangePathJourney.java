package com.duoaero.nativebase;
import android.app.Activity;
import android.app.Instrumentation;
import android.graphics.Rect;
import android.view.accessibility.AccessibilityNodeInfo;
import java.io.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;
import org.json.*;

/** Seeded synthetic-account path probe. No completion is written by this test. */
final class RangePathJourney {
 private static final String TARGET="2.2-range-draft-formula-lesson-0",ID="com.duolingo:id/";
 private static void collect(AccessibilityNodeInfo n,String id,List<AccessibilityNodeInfo> out){
  if(n==null)return;
  if(id.equals(n.getViewIdResourceName())&&n.isVisibleToUser())out.add(AccessibilityNodeInfo.obtain(n));
  for(int i=0;i<n.getChildCount();i++){AccessibilityNodeInfo child=n.getChild(i);if(child!=null)try{collect(child,id,out);}finally{child.recycle();}}
 }
 private static void touch(Instrumentation test,AccessibilityNodeInfo node)throws Exception{
  Rect r=new Rect();node.getBoundsInScreen(r);if(r.isEmpty())throw new IllegalStateException("Empty path control");
  long now=android.os.SystemClock.uptimeMillis();
  android.view.MotionEvent a=android.view.MotionEvent.obtain(now,now,android.view.MotionEvent.ACTION_DOWN,r.exactCenterX(),r.exactCenterY(),0);
  android.view.MotionEvent b=android.view.MotionEvent.obtain(now,now+40,android.view.MotionEvent.ACTION_UP,r.exactCenterX(),r.exactCenterY(),0);
  a.setSource(android.view.InputDevice.SOURCE_TOUCHSCREEN);b.setSource(android.view.InputDevice.SOURCE_TOUCHSCREEN);
  try{if(!test.getUiAutomation().injectInputEvent(a,true))throw new IllegalStateException("Path down failed");Thread.sleep(40);if(!test.getUiAutomation().injectInputEvent(b,true))throw new IllegalStateException("Path up failed");}finally{a.recycle();b.recycle();}
 }
 private static boolean popup(Instrumentation test,String title){
  AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();if(root==null)return false;
  List<AccessibilityNodeInfo> titles=new ArrayList<>(),buttons=new ArrayList<>();
  try{collect(root,ID+"titleText",titles);collect(root,ID+"learnButton",buttons);
   boolean matches=false,enabled=false;
   for(AccessibilityNodeInfo n:titles)if(n.getText()!=null&&title.equalsIgnoreCase(n.getText().toString()))matches=true;
   for(AccessibilityNodeInfo n:buttons)if(n.isEnabled())enabled=true;
   return matches&&enabled;
  }finally{for(AccessibilityNodeInfo n:titles)n.recycle();for(AccessibilityNodeInfo n:buttons)n.recycle();root.recycle();}
 }
 private static void openTarget(Instrumentation test)throws Exception{
  for(int page=0;page<18;page++){
   AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();if(root==null){Thread.sleep(500);continue;}
   List<AccessibilityNodeInfo> ovals=new ArrayList<>();try{collect(root,ID+"oval",ovals);}finally{root.recycle();}
   int count=ovals.size();for(AccessibilityNodeInfo n:ovals)n.recycle();
   for(int i=0;i<count;i++){
    root=test.getUiAutomation().getRootInActiveWindow();if(root==null)continue;
    ovals=new ArrayList<>();try{collect(root,ID+"oval",ovals);if(i<ovals.size())touch(test,ovals.get(i));}
    finally{for(AccessibilityNodeInfo n:ovals)n.recycle();root.recycle();}
    for(int j=0;j<20&&!popup(test,"Range formulas")&&!SessionInteraction.hasControl(test,ID+"learnButton");j++)Thread.sleep(150);
    if(popup(test,"Range formulas")){SessionInteraction.click(test,ID+"learnButton",null);return;}
    // A tap can miss or land on a noninteractive path decoration. Back is
    // only safe after a path popup actually appeared; otherwise it exits Home.
    if(SessionInteraction.hasControl(test,ID+"learnButton")){
     test.getUiAutomation().performGlobalAction(android.accessibilityservice.AccessibilityService.GLOBAL_ACTION_BACK);Thread.sleep(300);
    }
   }
   android.util.DisplayMetrics dm=test.getTargetContext().getResources().getDisplayMetrics();
   android.os.ParcelFileDescriptor fd=test.getUiAutomation().executeShellCommand("input swipe "+(dm.widthPixels/2)+" "+(int)(dm.heightPixels*.75)+" "+(dm.widthPixels/2)+" "+(int)(dm.heightPixels*.30)+" 500");
   if(fd!=null)try(InputStream in=new android.os.ParcelFileDescriptor.AutoCloseInputStream(fd)){while(in.read()!=-1){}}
   Thread.sleep(500);
  }
  throw new IllegalStateException("Range formulas node not reached");
 }
 private static JSONObject read(File file)throws Exception{
  if(!file.isFile())return null;
  try(InputStream in=new FileInputStream(file)){ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] b=new byte[4096];int n;while((n=in.read(b))!=-1)out.write(b,0,n);return new JSONObject(out.toString("UTF-8"));}
 }
 static String run(Instrumentation test,AtomicReference<Activity> resumed)throws Exception{
  File folder=new File(test.getTargetContext().getFilesDir(),"duoaero-course/local-test/submissions");
  File file=new File(folder,TARGET+".json");if(file.exists())throw new IllegalStateException("Target already completed before probe");
  JSONArray questions;
  try(InputStream in=test.getTargetContext().getAssets().open("duoaero/jet-range-path-answers.json")){
   ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1)out.write(b,0,n);questions=new JSONArray(out.toString("UTF-8"));
  }
  if(questions.length()!=12)throw new IllegalStateException("Unexpected lesson size");
  for(int i=0;i<240&&!SessionInteraction.hasControl(test,ID+"oval");i++)Thread.sleep(500);
  if(!SessionInteraction.hasControl(test,ID+"oval"))throw new IllegalStateException("Original path unavailable");
  SessionScreen.capture(test,"range-path-before","range-path-before");resumed.set(null);openTarget(test);
  Activity activity=null;for(int i=0;i<180;i++){activity=resumed.get();if(activity!=null&&activity.getClass().getName().equals("com.duolingo.session.SessionActivity"))break;Thread.sleep(500);}
  if(activity==null||!activity.getClass().getName().equals("com.duolingo.session.SessionActivity"))throw new IllegalStateException("Original session activity unavailable");
  for(int i=0;i<240;i++){if("JET-DRY-WORDS".equals(NativeChallengeIdentity.read(test,activity))&&SessionInteraction.contains(test,"payload"))break;Thread.sleep(500);}
  if(!"JET-DRY-WORDS".equals(NativeChallengeIdentity.read(test,activity)))throw new IllegalStateException("Wrong first challenge in path lesson");
  String result=SessionInteraction.mixedAnswers(test,activity,false,true,false,questions);
  result+=SessionInteraction.claimXp(test);
  JSONObject saved=null;for(int i=0;i<240;i++){saved=read(file);if(saved!=null&&saved.optBoolean("completedOnce"))break;Thread.sleep(500);}
  if(saved==null||!saved.optBoolean("completedOnce"))throw new IllegalStateException("Path completion not saved");
  JSONObject proof=saved.optJSONObject("completionSubmission");if(proof==null)throw new IllegalStateException("Native completion proof missing");
  Set<String> expected=new HashSet<>(),actual=new HashSet<>();for(int i=0;i<questions.length();i++)expected.add(questions.getJSONObject(i).getString("id"));
  JSONArray answered=proof.getJSONArray("challenges");for(int i=0;i<answered.length();i++)actual.add(answered.getJSONObject(i).getString("id"));
  if(!expected.equals(actual))throw new IllegalStateException("Saved proof does not cover exact path challenges");
  SessionScreen.capture(test,"range-path-after","range-path-after");
  return result+"PASS: seeded synthetic prior history, opened the original range path and saved all 12 native controls; restart and real accounts remain unverified.\n";
 }
}
