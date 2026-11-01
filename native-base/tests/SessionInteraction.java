package com.duoaero.nativebase;

import android.app.Instrumentation;
import android.view.accessibility.AccessibilityNodeInfo;

/** Drives actual native controls. No answer, grading or engine state injection. */
final class SessionInteraction {
 static String firstPathNode(Instrumentation test)throws Exception {
  for(int i=0;i<150&&!hasControl(test,"com.duolingo:id/oval");i++)Thread.sleep(200);
  for(int i=0;i<150&&!contains(test,"Aeronautical organizations");i++){test.getUiAutomation().clearCache();Thread.sleep(200);}
  SessionScreen.capture(test,"path-topic-headers","path-topic-headers");
  if(!contains(test,"Aeronautical organizations"))throw new IllegalStateException("Original inline path header did not expose its Aerospace topic");
  click(test,"com.duolingo:id/oval",null);
  for(int i=0;i<150&&!hasControl(test,"com.duolingo:id/learnButton")&&!contains(test,"Low delivery times.");i++)Thread.sleep(200);
  SessionScreen.capture(test,"path-node-opened","path-node-opened");
  if(hasControl(test,"com.duolingo:id/learnButton"))click(test,"com.duolingo:id/learnButton",null);
  for(int i=0;i<225&&!contains(test,"Low delivery times.");i++)Thread.sleep(200);
  SessionScreen.capture(test,"path-session","path-session");
  if(!contains(test,"Low delivery times."))throw new IllegalStateException("First course question not visible after original path node");
  return "Original home node opened its first Aerospace question through the original remote-session loader.\n";
 }
 private static boolean hasControl(Instrumentation test,String id){
  AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();
  if(root==null)return false;
  try{AccessibilityNodeInfo node=find(root,id,null,0);if(node==null)return false;node.recycle();return true;}
  finally{root.recycle();}
 }
 static String mixedAnswers(Instrumentation test)throws Exception {
  java.io.ByteArrayOutputStream bytes=new java.io.ByteArrayOutputStream();
  try(java.io.InputStream input=test.getTargetContext().getAssets().open("duoaero/mixed-source.json")){
   byte[] buffer=new byte[8192];int n;while((n=input.read(buffer))!=-1)bytes.write(buffer,0,n);
  }
  org.json.JSONArray questions=new org.json.JSONArray(bytes.toString("UTF-8"));
  String[] positive={"Amazing!","Awesome!","Correct!","Excellent!","Good job!","Great!","Great job!","Nice job!","Nice!","Nicely done!","Wow!"};
  for(int i=0;i<questions.length();i++){
   org.json.JSONObject q=questions.getJSONObject(i);String kind=q.getString("type");
   Thread.sleep(1800);SessionScreen.capture(test,"mixed-prompt-"+i,"mixed-prompt-"+i);
   if(kind.equals("multi")){
    org.json.JSONArray answer=q.getJSONArray("answer"),options=q.getJSONArray("options");
    for(int j=0;j<answer.length();j++){click(test,null,options.getString(answer.getInt(j)));Thread.sleep(300);}
   }else if(kind.equals("matching")){
    org.json.JSONArray pairs=q.getJSONArray("pairs");
    for(int j=0;j<pairs.length();j++){
     org.json.JSONArray pair=pairs.getJSONArray(j);
     click(test,null,pair.getString(0));Thread.sleep(300);
     click(test,null,pair.getString(1));Thread.sleep(700);
    }
   }else if(kind.equals("gap"))clickLast(test,q.getJSONArray("answer").getString(0));
   else if(kind.equals("order")){
    org.json.JSONArray sequence=q.getJSONArray("answer"),items=q.getJSONArray("items");
    for(int j=0;j<sequence.length();j++){clickLast(test,items.getString(sequence.getInt(j)));Thread.sleep(300);}
   }else throw new IllegalStateException("No mixed driver for "+kind);
   SessionScreen.capture(test,"mixed-selected-"+i,"mixed-selected-"+i);
   // Matching can grade automatically after the final pair. Other native
   // controllers use their original Check action.
   boolean correct=hasContinue(test)&&!contains(test,"GOT IT");
   for(String label:positive)if(contains(test,label))correct=true;
   if(!correct)click(test,"com.duolingo:id/submitButton",null);
   for(int attempt=0;attempt<150&&!correct;attempt++){
    correct=hasContinue(test)&&!contains(test,"GOT IT");
    for(String label:positive)if(contains(test,label))correct=true;
    if(!correct)Thread.sleep(200);
   }
   SessionScreen.capture(test,"mixed-graded-"+i,"mixed-graded-"+i);
   if(!correct)throw new IllegalStateException("No original correct feedback for "+q.getString("id"));
   android.util.Log.i("DuoAeroProbe","Native mixed feedback CORRECT: "+q.getString("id")+" type="+kind);
   click(test,null,"CONTINUE");
  }
  return "All "+questions.length()+" mixed source exercises produced original visible correct feedback through native controls. No course completion or overflow acceptance asserted.\n";
 }
 static String formulaAnswers(Instrumentation test,android.app.Activity activity,boolean wrong)throws Exception {
  // Select through the original token controls; no model/grade injection.
  org.json.JSONArray answers;
  try(java.io.InputStream input=test.getContext().getAssets().open("formula-selections.json")){
   java.io.ByteArrayOutputStream bytes=new java.io.ByteArrayOutputStream();byte[] buffer=new byte[4096];int n;while((n=input.read(buffer))!=-1)bytes.write(buffer,0,n);
   answers=new org.json.JSONArray(bytes.toString("UTF-8"));
  }
  for(int i=0;i<(wrong?1:answers.length());i++){
   test.getUiAutomation().clearCache();
   SessionScreen.capture(test,"formula-prompt-"+i,"formula-prompt-"+i);
   org.json.JSONArray tokens=wrong?new org.json.JSONArray().put("V"):answers.getJSONObject(i).getJSONArray("tokens");
   for(int j=0;j<tokens.length();j++){clickLast(test,tokens.getString(j));Thread.sleep(500);}
   SessionScreen.capture(test,"formula-selected-"+i,"formula-selected-"+i);
   click(test,"com.duolingo:id/submitButton",null);
   Thread.sleep(1500);
   SessionScreen.capture(test,"formula-graded-"+i,"formula-graded-"+i);
   NativeMathGrade.require(test,activity,wrong?"INCORRECT":"CORRECT");
   if(wrong){
    boolean rendered=false;
    for(int attempt=0;attempt<30&&!rendered;attempt++){
     final boolean[] result={false};
     test.runOnMainSync(()->result[0]=hasFormulaFeedback(activity.getWindow().getDecorView()));
     rendered=result[0];if(!rendered)Thread.sleep(200);
    }
    if(!rendered)throw new IllegalStateException("Incorrect feedback did not render the native LaTeX view");
    SessionScreen.capture(test,"formula-feedback-rendered","formula-feedback-rendered");
   }
   android.util.Log.i("DuoAeroProbe","Native formula controller with Aerospace symbolic comparison: "+(wrong?"INCORRECT":"CORRECT")+" at "+i+" source="+answers.getJSONObject(i).getString("id"));
   String action=wrong?"GOT IT":"CONTINUE";
   for(int attempt=0;attempt<150&&!contains(test,action);attempt++)Thread.sleep(200);
   click(test,null,action);Thread.sleep(1200);
  }
  return (wrong?1:answers.length())+" formula selections submitted through native controls; Aerospace symbolic comparison checked against visible original fragment result. No full course acceptance.\n";
 }
 private static boolean hasFormulaFeedback(android.view.View view){
  if(view.getClass().getName().equals("com.duolingo.feature.math.ui.figure.MathLatexView"))try{
   Object latex=view.getClass().getMethod("getLatexString").invoke(view);
   if(latex!=null&&latex.toString().contains("q=\\frac{1}{2}"))return view.isShown();
  }catch(Exception ignored){}
  if(view instanceof android.view.ViewGroup){android.view.ViewGroup group=(android.view.ViewGroup)view;
   for(int i=0;i<group.getChildCount();i++)if(hasFormulaFeedback(group.getChildAt(i)))return true;}
  return false;
 }
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
  return allMathAnswers(test,activity,"rich-session-selections.json",true);
 }
 static String allPathAnswers(Instrumentation test,android.app.Activity activity)throws Exception {
  return allMathAnswers(test,activity,"path-session-selections.json",false);
 }
 private static String allMathAnswers(Instrumentation test,android.app.Activity activity,String selectionAsset,boolean checkRichLayout)throws Exception {
  String payload;
  try(java.io.InputStream input=test.getContext().getAssets().open(selectionAsset)){
   java.io.ByteArrayOutputStream bytes=new java.io.ByteArrayOutputStream();byte[] buffer=new byte[4096];int n;
   while((n=input.read(buffer))!=-1)bytes.write(buffer,0,n);
   payload=new String(bytes.toByteArray(),"UTF-8");
  }
  org.json.JSONArray selections=new org.json.JSONArray(payload);
  long finalContinueAt=0;
  for(int i=0;i<selections.length();i++){
   org.json.JSONObject question=selections.getJSONObject(i);
   String answer=question.getString("answer");
   // Native streak animations may expose an extra Continue between questions.
   for(int attempt=0;attempt<30&&!contains(test,answer);attempt++){
    if(attempt%10==9&&hasContinue(test))click(test,null,"CONTINUE");
    Thread.sleep(200);
   }
   if(checkRichLayout&&(question.getString("id").matches("TA1-(0148|0397-D2(-S1)?|0182-F1|0232|0753-D3|0832-D3)")||question.getString("id").equals("TH-2026-OTHER-1")))SessionScreen.capture(test,"lesson-prompt-"+i,"lesson-prompt-"+i);
   if(checkRichLayout&&question.getString("id").equals("TA1-0753-D3")){
    AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();
    boolean scrolled=false;
    if(root!=null)try{scrolled=scrollForward(root,0);}finally{root.recycle();}
    if(!scrolled)throw new IllegalStateException("Long Aerospace prompt does not expose working native scrolling");
    Thread.sleep(700);
    SessionScreen.capture(test,"lesson-prompt-scrolled","lesson-prompt-scrolled");
   }
   click(test,"com.duolingo:id/mathCard",answer);
   // Blob selection evaluates asynchronously. Observe that original result
   // before pressing Check; checking during evaluation can be ignored.
   NativeMathGrade.awaitSelection(test,activity,"CORRECT");
   test.waitForIdleSync();Thread.sleep(600);
   click(test,"com.duolingo:id/submitButton",null);
   Thread.sleep(1000);
   SessionScreen.capture(test,"lesson-answer-"+i,"lesson-answer-"+i);
   NativeMathGrade.require(test,activity,"CORRECT");
   android.util.Log.i("DuoAeroProbe","Native correct answer "+(i+1)+"/"+selections.length()+": "+question.getString("id"));
   for(int attempt=0;attempt<150&&!hasContinue(test);attempt++)Thread.sleep(200);
   if(!hasContinue(test))throw new IllegalStateException("Missing graded Continue at "+question.getString("id"));
   if(i==selections.length()-1)finalContinueAt=android.os.SystemClock.elapsedRealtime();
   click(test,null,"CONTINUE");
   if(i<selections.length()-1)Thread.sleep(1000);
  }
  for(int attempt=0;attempt<100&&!contains(test,"CLAIM XP");attempt++)Thread.sleep(200);
  boolean summaryVisible=contains(test,"CLAIM XP");
  long summaryWait=android.os.SystemClock.elapsedRealtime()-finalContinueAt;
  android.util.Log.i("DuoAeroProbe","Final Continue to observed Claim XP: "+summaryWait+" ms; visible="+summaryVisible);
  SessionScreen.capture(test,"lesson-after-last-answer","lesson-after-last-answer");
  return "Final Continue to observed Claim XP: "+summaryWait+" ms; visible="+summaryVisible+".\nAll "+selections.length()+" diagnostic selections graded CORRECT by original visible fragments. Last Continue clicked. Inspect final screen: this alone does not assert session completion, saved progress or resume.\n";
 }
 static String claimXp(Instrumentation test)throws Exception {
  for(int attempt=0;attempt<60;attempt++){
   test.getUiAutomation().clearCache();
   if(contains(test,"CLAIM XP"))break;
   Thread.sleep(1000);
  }
  if(!contains(test,"CLAIM XP"))throw new IllegalStateException("Original Claim XP is not visible");
  click(test,"com.duolingo:id/continueButtonView","CLAIM XP");
  Thread.sleep(12000);
  SessionScreen.capture(test,"lesson-after-claim-xp","lesson-after-claim-xp");
  return "Clicked original Claim XP through accessibility; captured the resulting screen. Persistence is not asserted.\n";
 }
 private static boolean scrollForward(AccessibilityNodeInfo node,int depth){
  if(depth>50||!own(node))return false;
  if(node.isVisibleToUser()&&node.isScrollable()&&node.performAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD))return true;
  for(int i=0;i<node.getChildCount();i++){
   AccessibilityNodeInfo child=node.getChild(i);
   if(child!=null)try{if(scrollForward(child,depth+1))return true;}finally{child.recycle();}
  }
  return false;
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
 // The same label may already be in an answer slot. The bank is the last
 // matching native control in traversal order; select it rather than removing
 // a previously selected token. This only performs native accessibility taps.
 private static void clickLast(Instrumentation test,String text)throws Exception {
  AccessibilityNodeInfo node=null;
  for(int attempt=0;attempt<18&&node==null;attempt++){
   AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();
   if(root!=null)try{
    node=findLast(root,text,0);
    if(node==null)scrollBank(root,attempt<9?AccessibilityNodeInfo.ACTION_SCROLL_FORWARD:AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD,0);
   }finally{root.recycle();}
   if(node==null)Thread.sleep(300);
  }
  if(node==null)throw new IllegalStateException("Native bank token not visible: "+text);
  try{for(int i=0;i<8&&!node.isClickable();i++){AccessibilityNodeInfo parent=node.getParent();if(parent==null)break;node.recycle();node=parent;}
   if(!own(node)||!node.isEnabled()||!node.performAction(AccessibilityNodeInfo.ACTION_CLICK))throw new IllegalStateException("Native bank token did not accept click: "+text);
  }finally{node.recycle();}
 }
 private static boolean scrollBank(AccessibilityNodeInfo node,int action,int depth){
  if(depth>50||!own(node))return false;
  // The bank is the last scrollable native region, below the prompt/slots.
  for(int i=node.getChildCount()-1;i>=0;i--){AccessibilityNodeInfo child=node.getChild(i);if(child!=null)try{if(scrollBank(child,action,depth+1))return true;}finally{child.recycle();}}
  return node.isVisibleToUser()&&node.isScrollable()&&node.performAction(action);
 }
 private static AccessibilityNodeInfo findLast(AccessibilityNodeInfo node,String text,int depth){
  if(depth>50||!own(node))return null;
  for(int i=node.getChildCount()-1;i>=0;i--){AccessibilityNodeInfo child=node.getChild(i);if(child!=null)try{AccessibilityNodeInfo found=findLast(child,text,depth+1);if(found!=null)return found;}finally{child.recycle();}}
  if(node.isVisibleToUser()&&(text.contentEquals(node.getText()==null?"":node.getText())||text.contentEquals(node.getContentDescription()==null?"":node.getContentDescription())))return AccessibilityNodeInfo.obtain(node);
  return null;
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
