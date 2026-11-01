package com.duoaero.nativebase;

import android.app.Instrumentation;
import android.view.accessibility.AccessibilityNodeInfo;

/** Drives actual native controls. No answer, grading or engine state injection. */
final class SessionInteraction {
 static String firstAssistAnswer(Instrumentation test)throws Exception {
  String stem="Which one from the following characteristics does not define the aerospace industry?";
  String next="Regarding the navigation aids:";
  if(!contains(test,stem))throw new IllegalStateException("Expected first Aerospace question is not visible");
  click(test,"com.duolingo:id/optionText","Low delivery times.");
  Thread.sleep(1000);
  SessionScreen.capture(test,"interaction-selected","interaction-selected");
  if(hasContinue(test))click(test,null,"CONTINUE");
  else click(test,"com.duolingo:id/submitButton",null);
  Thread.sleep(1500);
  SessionScreen.capture(test,"interaction-submitted","interaction-submitted");
  // Some native challenge types separate Check and Continue. Only click
  // Continue if the same question is still present; never skip a new question.
  if(contains(test,stem)&&hasContinue(test)){
   click(test,null,"CONTINUE");
   Thread.sleep(1500);
   SessionScreen.capture(test,"interaction-continued","interaction-continued");
  }
  boolean advanced=contains(test,next);
  return "UI interaction: selected the first question's correct option through native accessibility controls; submitted through original button.\n"
   +"Second Aerospace question visible: "+advanced+". Grading feedback must be checked in screenshots; this does not verify session completion or persistence.\n";
 }
 static String firstMathAnswer(Instrumentation test,android.app.Activity activity,boolean wrong)throws Exception {
  String answer=wrong?"\\text{Difficult automation.}":"\\text{Low delivery times.}";
  click(test,"com.duolingo:id/mathCard",answer);
  Thread.sleep(800);
  SessionScreen.capture(test,"interaction-selected","interaction-selected");
  click(test,"com.duolingo:id/submitButton",null);
  Thread.sleep(1200);
  SessionScreen.capture(test,"interaction-submitted","interaction-submitted");
  if(contains(test,"Something went wrong")||contains(test,"skip this exercise"))
   throw new IllegalStateException("Native Math grading failed; error-and-skip must not count as answer acceptance");
  NativeMathGrade.require(test,activity,wrong?"INCORRECT":"CORRECT");
  String footer=wrong?"GOT IT":"CONTINUE";
  click(test,null,footer);
  Thread.sleep(1500);
  SessionScreen.capture(test,"interaction-continued","interaction-continued");
  String payload;
  try(java.io.InputStream stream=test.getTargetContext().getAssets().open("hardcoded_sessions/duoaero/aerospace_rich_lesson.json")){
   java.io.ByteArrayOutputStream bytes=new java.io.ByteArrayOutputStream();byte[] buffer=new byte[8192];int n;
   while((n=stream.read(buffer))!=-1)bytes.write(buffer,0,n);
   payload=new String(bytes.toByteArray(),"UTF-8");
  }
  org.json.JSONObject session=new org.json.JSONObject(payload);
  org.json.JSONObject next=new org.json.JSONObject(session.getJSONArray("challenges").getJSONObject(1).getString("challengeBlob"));
  String nextOption=next.getJSONArray("pants").getJSONObject(0).getJSONObject("child").getString("value");
  return "UI interaction: original Math card selected; native FragmentGuess confirmed "+(wrong?"INCORRECT":"CORRECT")+"; original Check and "+footer+" clicked.\n"
   +"Next formula question option visible: "+contains(test,nextOption)+". Inspect grading and formula screenshots; no session completion or persistence asserted.\n";
 }
 static String allMathAnswers(Instrumentation test,android.app.Activity activity)throws Exception {
  String payload;
  try(java.io.InputStream input=test.getContext().getAssets().open("rich-session-selections.json")){
   java.io.ByteArrayOutputStream bytes=new java.io.ByteArrayOutputStream();byte[] buffer=new byte[4096];int n;
   while((n=input.read(buffer))!=-1)bytes.write(buffer,0,n);
   payload=new String(bytes.toByteArray(),"UTF-8");
  }
  org.json.JSONArray selections=new org.json.JSONArray(payload);
  for(int i=0;i<selections.length();i++){
   org.json.JSONObject question=selections.getJSONObject(i);
   String answer=question.getString("answer");
   // Native streak animations may expose an extra Continue between questions.
   for(int attempt=0;attempt<30&&!contains(test,answer);attempt++){
    if(attempt%10==9&&hasContinue(test))click(test,null,"CONTINUE");
    Thread.sleep(200);
   }
   if(i>=1&&i<=3)SessionScreen.capture(test,"lesson-prompt-"+i,"lesson-prompt-"+i);
   click(test,"com.duolingo:id/mathCard",answer);
   Thread.sleep(250);
   click(test,"com.duolingo:id/submitButton",null);
   Thread.sleep(1000);
   SessionScreen.capture(test,"lesson-answer-"+i,"lesson-answer-"+i);
   NativeMathGrade.require(test,activity,"CORRECT");
   android.util.Log.i("DuoAeroProbe","Native correct answer "+(i+1)+"/"+selections.length()+": "+question.getString("id"));
   if(!hasContinue(test))throw new IllegalStateException("Missing graded Continue at "+question.getString("id"));
   click(test,null,"CONTINUE");
   Thread.sleep(1000);
  }
  Thread.sleep(8000);
  SessionScreen.capture(test,"lesson-after-last-answer","lesson-after-last-answer");
  return "All "+selections.length()+" diagnostic selections graded CORRECT by original visible fragments. Last Continue clicked. Inspect final screen: this alone does not assert session completion, saved progress or resume.\n";
 }
 static String claimXp(Instrumentation test)throws Exception {
  if(!contains(test,"CLAIM XP"))throw new IllegalStateException("Original Claim XP is not visible");
  click(test,"com.duolingo:id/continueButtonView","CLAIM XP");
  Thread.sleep(6000);
  SessionScreen.capture(test,"lesson-after-claim-xp","lesson-after-claim-xp");
  return "Clicked original Claim XP through accessibility; captured the resulting screen. Persistence is not asserted.\n";
 }
 private static boolean contains(Instrumentation test,String text){
  AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();
  if(root==null)return false;
  try{return contains(root,text,0);}finally{root.recycle();}
 }
 private static boolean contains(AccessibilityNodeInfo node,String text,int depth){
  if(depth>50||!own(node))return false;
  if(node.isVisibleToUser()&&((node.getText()!=null&&node.getText().toString().contains(text))||(node.getContentDescription()!=null&&node.getContentDescription().toString().contains(text))))return true;
  for(int i=0;i<node.getChildCount();i++){
   AccessibilityNodeInfo child=node.getChild(i);
   if(child!=null)try{if(contains(child,text,depth+1))return true;}finally{child.recycle();}
  }
  return false;
 }
 private static boolean hasContinue(Instrumentation test){
  AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();
  if(root==null)return false;
  try{
   AccessibilityNodeInfo button=find(root,null,"CONTINUE",0);
   if(button==null)return false;
   try{return button.isEnabled()&&button.getText()!=null&&button.getText().toString().equalsIgnoreCase("CONTINUE");}finally{button.recycle();}
  }finally{root.recycle();}
 }
 private static void click(Instrumentation test,String id,String text){
  AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();
  if(root==null)throw new IllegalStateException("No active native window");
  AccessibilityNodeInfo node;
  try{node=find(root,id,text,0);}finally{root.recycle();}
  if(node==null)throw new IllegalStateException("Native control not visible: "+id);
  try{
   for(int parents=0;parents<8&&!node.isClickable();parents++){
    AccessibilityNodeInfo parent=node.getParent();
    if(parent==null)break;
    node.recycle();node=parent;
   }
   if(!own(node)||!node.isEnabled()||!node.isClickable()||!node.performAction(AccessibilityNodeInfo.ACTION_CLICK))
    throw new IllegalStateException("Native control did not accept click: "+id);
  }finally{node.recycle();}
 }
 private static boolean own(AccessibilityNodeInfo node){return "com.duoaero.nativebase".contentEquals(node.getPackageName()==null?"":node.getPackageName());}
 private static AccessibilityNodeInfo find(AccessibilityNodeInfo node,String id,String text,int depth){
  if(depth>50||!own(node))return null;
  // Preserve source-bank answer matching while allowing the native inline
  // fraction presentation command in card accessibility descriptions.
  CharSequence description=node.getContentDescription()==null?"":node.getContentDescription();
  if(node.isVisibleToUser()&&(id==null||id.equals(node.getViewIdResourceName()))&&(text==null||text.contentEquals(node.getText()==null?"":node.getText())||text.contentEquals(description)||("\\textstyle "+text).contentEquals(description)))return AccessibilityNodeInfo.obtain(node);
  for(int i=0;i<node.getChildCount();i++){
   AccessibilityNodeInfo child=node.getChild(i);
   if(child!=null)try{AccessibilityNodeInfo found=find(child,id,text,depth+1);if(found!=null)return found;}finally{child.recycle();}
  }
  return null;
 }
}
