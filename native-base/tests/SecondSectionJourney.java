package com.duoaero.nativebase;

import android.app.Activity;
import android.app.Instrumentation;
import android.graphics.Rect;
import android.view.accessibility.AccessibilityNodeInfo;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.concurrent.atomic.AtomicReference;
import org.json.JSONArray;
import org.json.JSONObject;

/** Synthetic account, original path and controls; never writes a completion. */
final class SecondSectionJourney {
 private SecondSectionJourney(){}
 private static final String ID="com.duolingo:id/";
 private static void await(Instrumentation test,String description,java.util.concurrent.Callable<Boolean> condition,long timeout)throws Exception {
  long until=android.os.SystemClock.uptimeMillis()+timeout;
  while(android.os.SystemClock.uptimeMillis()<until){test.getUiAutomation().clearCache();if(condition.call())return;Thread.sleep(500);}
  throw new IllegalStateException("Not observed: "+description);
 }
 private static void collect(AccessibilityNodeInfo node,String id,ArrayList<AccessibilityNodeInfo> found){
  if(node==null)return;
  if(id.equals(node.getViewIdResourceName())&&node.isVisibleToUser())found.add(AccessibilityNodeInfo.obtain(node));
  for(int i=0;i<node.getChildCount();i++){AccessibilityNodeInfo child=node.getChild(i);if(child!=null)try{collect(child,id,found);}finally{child.recycle();}}
 }
 private static int exactTextCount(AccessibilityNodeInfo node,String text){
  if(node==null)return 0;int n=node.isVisibleToUser()&&node.getText()!=null&&text.equalsIgnoreCase(node.getText().toString())?1:0;
  for(int i=0;i<node.getChildCount();i++){AccessibilityNodeInfo child=node.getChild(i);if(child!=null)try{n+=exactTextCount(child,text);}finally{child.recycle();}}
  return n;
 }
 private static boolean topicPopup(Instrumentation test,String title){
  AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();if(root==null)return false;
  ArrayList<AccessibilityNodeInfo> titles=new ArrayList<>(),buttons=new ArrayList<>();
  try{collect(root,ID+"titleText",titles);collect(root,ID+"learnButton",buttons);
   boolean match=false,enabled=false;
   for(AccessibilityNodeInfo n:titles)if(n.getText()!=null&&title.equalsIgnoreCase(n.getText().toString()))match=true;
   for(AccessibilityNodeInfo n:buttons)if(n.isEnabled())enabled=true;
   return match&&enabled;
  }finally{for(AccessibilityNodeInfo n:titles)n.recycle();for(AccessibilityNodeInfo n:buttons)n.recycle();root.recycle();}
 }
 private static void openTopic(Instrumentation test,String topic,String title)throws Exception {
  for(int attempt=0;attempt<12;attempt++){
   AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();
   if(root!=null){
    ArrayList<AccessibilityNodeInfo> headers=new ArrayList<>(),ovals=new ArrayList<>();
    try{
     collect(root,ID+"headerText",headers);collect(root,ID+"oval",ovals);
     int top=-1,bottom=Integer.MAX_VALUE;
     for(AccessibilityNodeInfo h:headers){CharSequence t=h.getText();if(t!=null&&t.toString().startsWith(topic+" ·")){Rect r=new Rect();h.getBoundsInScreen(r);top=r.bottom;break;}}
     if(top>=0){
      for(AccessibilityNodeInfo h:headers){Rect r=new Rect();h.getBoundsInScreen(r);if(r.top>top)bottom=Math.min(bottom,r.top);}
      for(AccessibilityNodeInfo oval:ovals){Rect r=new Rect();oval.getBoundsInScreen(r);if(r.top>top&&r.top<bottom){
       if(!oval.performAction(AccessibilityNodeInfo.ACTION_CLICK))throw new IllegalStateException("Cannot open native path node");
       await(test,"topic popup",()->topicPopup(test,title),30000);
       SessionInteraction.click(test,ID+"learnButton",null);return;
      }}
     }
    }finally{for(AccessibilityNodeInfo h:headers)h.recycle();for(AccessibilityNodeInfo o:ovals)o.recycle();root.recycle();}
   }
   android.util.DisplayMetrics metrics=test.getTargetContext().getResources().getDisplayMetrics();
   int x=metrics.widthPixels/2, start=(int)(metrics.heightPixels*.75), end=(int)(metrics.heightPixels*.30);
   android.os.ParcelFileDescriptor fd=test.getUiAutomation().executeShellCommand("input swipe "+x+" "+start+" "+x+" "+end+" 500");
   if(fd!=null)try(InputStream in=new android.os.ParcelFileDescriptor.AutoCloseInputStream(fd)){while(in.read()!=-1){}}
   Thread.sleep(800);
  }
  throw new IllegalStateException("Native topic not visible: "+topic);
 }
 private static JSONObject proof(File folder,String id)throws Exception {
  File file=new File(folder,id+".json");if(!file.isFile())return null;
  try(InputStream in=new FileInputStream(file)){ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] b=new byte[4096];int n;while((n=in.read(b))!=-1)bytes.write(b,0,n);return new JSONObject(bytes.toString("UTF-8"));}
 }
 static String run(Instrumentation test,AtomicReference<Activity> resumed)throws Exception {
  JSONObject answers;
  try(InputStream in=test.getTargetContext().getAssets().open("duoaero/journey-diagnostic-answers.json")){ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1)bytes.write(b,0,n);answers=new JSONObject(bytes.toString("UTF-8"));}
  StringBuilder report=new StringBuilder();
  String[] topics={"3.1","3.1","3.1","3.2","3.2","3.3","3.3"};
  String[] titles={"Launch vehicles","Launch vehicles","Launch vehicles","Space flight environment","Space flight environment","Spacecraft","Spacecraft"};
  int[] indices={0,1,2,0,1,0,1};
  File folder=new File(test.getTargetContext().getFilesDir(),"duoaero-course/local-test/submissions");
  for(int i=0;i<topics.length;i++)if(proof(folder,"second-partial-"+topics[i]+"-lesson-"+indices[i])!=null)throw new IllegalStateException("Unexpected pre-existing completion");
  await(test,"course home",()->SessionInteraction.hasControl(test,ID+"primaryCardView"),120000);
  SessionInteraction.click(test,ID+"primaryCardView",null);
  await(test,"second section picker",()->SessionInteraction.contains(test,"Midterm 2"),60000);
  SessionInteraction.clickLast(test,"Midterm 2");Thread.sleep(1000);
  await(test,"expanded second section",()->{AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();if(root==null)return false;try{return exactTextCount(root,"Midterm 2")>=2;}finally{root.recycle();}},60000);
  SessionInteraction.clickLast(test,"Midterm 2");
  await(test,"second section path",()->SessionInteraction.contains(test,"Launch vehicles")&&SessionInteraction.hasControl(test,ID+"oval"),120000);
  for(int i=0;i<topics.length;i++){
   final int step=i;String id="second-partial-"+topics[i]+"-lesson-"+indices[i];
   resumed.set(null);openTopic(test,topics[i],titles[i]);
   await(test,"original lesson activity",()->{Activity a=resumed.get();return a!=null&&a.getClass().getName().equals("com.duolingo.session.SessionActivity");},90000);
   Activity current=resumed.get();JSONArray questions=answers.getJSONArray(id);
   report.append("SESSION ").append(id).append("\n");
   report.append(SessionInteraction.mixedAnswers(test,current,false,true,false,questions));
   report.append(SessionInteraction.claimXp(test));
   await(test,"saved original completion "+id,()->{JSONObject saved=proof(folder,id);return saved!=null&&saved.optBoolean("completedOnce");},120000);
   for(int j=step+1;j<topics.length;j++)if(proof(folder,"second-partial-"+topics[j]+"-lesson-"+indices[j])!=null)throw new IllegalStateException("Future lesson received unearned completion");
   SessionScreen.capture(test,"journey-after-"+i,"journey-after-"+i);
   android.util.Log.i("DuoAeroProbe","JOURNEY_LESSON_SAVED="+id);
   if(i+1<topics.length)await(test,"next original path",()->SessionInteraction.hasControl(test,ID+"oval"),120000);
  }
  return report.append("PASS: seven native path sessions graded and saved in order without seeded completion; process-restart verification remains separate.\n").toString();
 }
}
