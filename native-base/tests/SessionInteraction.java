package com.duoaero.nativebase;

import android.app.Instrumentation;
import android.view.accessibility.AccessibilityNodeInfo;

/** Drives actual native controls. No answer, grading or engine state injection. */
final class SessionInteraction {
 private static boolean actualTouch;
 static String quitPreview(Instrumentation test)throws Exception {
  for(int i=0;i<150&&!hasControl(test,"com.duolingo:id/challengeInstruction");i++)Thread.sleep(200);
  // A brand-new session may exit immediately without a confirmation sheet.
  // Complete its first real question to exercise the in-progress quit dialog.
  org.json.JSONObject first;
  try(java.io.InputStream input=test.getTargetContext().getAssets().open("duoaero/mixed-source.json")){
   java.io.ByteArrayOutputStream bytes=new java.io.ByteArrayOutputStream();byte[] buffer=new byte[4096];int n;
   while((n=input.read(buffer))!=-1)bytes.write(buffer,0,n);
   first=new org.json.JSONArray(bytes.toString("UTF-8")).getJSONObject(0);
  }
  if(!first.getString("type").equals("gap"))throw new IllegalStateException("Quit diagnostic expects the original first word gap");
  Thread.sleep(1500);clickLast(test,first.getJSONArray("answer").getString(0));Thread.sleep(500);
  click(test,"com.duolingo:id/submitButton",null);
  for(int i=0;i<150&&!hasContinue(test);i++)Thread.sleep(200);
  if(!hasContinue(test)||contains(test,"GOT IT"))throw new IllegalStateException("Quit diagnostic first answer did not grade correctly");
  click(test,null,"CONTINUE");Thread.sleep(1500);
  for(int i=0;i<150&&!hasControl(test,"com.duolingo:id/quitButton");i++)Thread.sleep(200);
  click(test,"com.duolingo:id/quitButton",null);
  SessionScreen.capture(test,"static-quit-after-tap","static-quit-after-tap");
  for(int i=0;i<150&&!hasControl(test,"com.duolingo:id/primaryButton");i++)Thread.sleep(200);
  if(!hasControl(test,"com.duolingo:id/primaryButton"))
   throw new IllegalStateException("Original quit keep-going control missing");
  Class<?> mascot=Class.forName("com.duoaero.nativebase.NativeMascotView",true,test.getTargetContext().getClassLoader());
  if(!Boolean.TRUE.equals(mascot.getMethod("quitAnimationAttached").invoke(null)))
   throw new IllegalStateException("Original quit sheet opened without its animated mascot");
  SessionScreen.capture(test,"static-quit-dialog","static-quit-dialog");
  // Record the attached original sheet, rather than treating two isolated
  // drawable frames as proof of smooth animation in the real view.
  try(android.os.ParcelFileDescriptor.AutoCloseInputStream stream=
      new android.os.ParcelFileDescriptor.AutoCloseInputStream(test.getUiAutomation().executeShellCommand(
       "screenrecord --time-limit 4 /sdcard/duoaero-sad-quit.mp4"))){
   byte[] buffer=new byte[1024];while(stream.read(buffer)!=-1){}
  }
  click(test,"com.duolingo:id/primaryButton",null);
  for(int i=0;i<150&&!hasControl(test,"com.duolingo:id/challengeInstruction");i++)Thread.sleep(200);
  if(!hasControl(test,"com.duolingo:id/challengeInstruction"))throw new IllegalStateException("Did not return to original lesson");
  return "STATIC_QUIT_SCREEN_VERIFIED=true; original quit sheet opened and returned to lesson; inspect image for clipping.\n";
 }
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
 static boolean hasControl(Instrumentation test,String id){
  AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();
  if(root==null)return false;
  try{AccessibilityNodeInfo node=find(root,id,null,0);if(node==null)return false;node.recycle();return true;}
  finally{root.recycle();}
 }
 static String mixedAnswers(Instrumentation test,android.app.Activity activity,boolean hintRetry,boolean touch,boolean fractionWrong)throws Exception {
  java.io.ByteArrayOutputStream bytes=new java.io.ByteArrayOutputStream();
  try(java.io.InputStream input=test.getTargetContext().getAssets().open("duoaero/mixed-source.json")){
   byte[] buffer=new byte[8192];int n;while((n=input.read(buffer))!=-1)bytes.write(buffer,0,n);
  }
  org.json.JSONArray questions=new org.json.JSONArray(bytes.toString("UTF-8"));
  return mixedAnswers(test,activity,hintRetry,touch,fractionWrong,questions);
 }
 static String mixedAnswers(Instrumentation test,android.app.Activity activity,boolean hintRetry,boolean touch,boolean fractionWrong,org.json.JSONArray questions)throws Exception {
  actualTouch=touch;
  boolean windScenario=false,directHintScenario=false,rocketScenario=false,payloadScenario=false;
  for(int i=0;i<questions.length();i++){String id=questions.getJSONObject(i).getString("id");if(id.equals("TA1-0092-D2-S1"))windScenario=true;if(id.equals("TA1-0106-F1"))directHintScenario=true;if(id.equals("M2-ROCKET-DELTA-CALC"))rocketScenario=true;if(id.equals("TA1-0083-D2"))payloadScenario=true;}
  String hintId=payloadScenario?"TA1-0083-D2":rocketScenario?"M2-ROCKET-DELTA-CALC":directHintScenario?"TA1-0106-F1":windScenario?"TA1-0092-D2-S1":"TA1-0107-D2-S1";
  org.json.JSONObject hintedQuestion=null;
  String[] positive={"Amazing!","Awesome!","Correct!","Excellent!","Good job!","Great!","Great job!","Nice job!","Nice!","Nicely done!","Wow!"};
  for(int i=0;i<questions.length();i++){
   org.json.JSONObject q=questions.getJSONObject(i);String kind=q.getString("type");
   Thread.sleep(1800);dismissPixelLauncherAnr(test);SessionScreen.capture(test,"mixed-prompt-"+i,"mixed-prompt-"+i);
   boolean hinted=hintRetry&&q.getString("id").equals(hintId);
   boolean wrongFraction=fractionWrong&&q.getString("id").equals("COLUMN-FACTOR-FORMULA-NAMED-ALL");
   if(hinted){
    hintedQuestion=q;
    clickTip(test);Thread.sleep(800);
    if(!contains(test,"a tip")||contains(test,"GOT IT")&&contains(test,"Incorrect"))throw new IllegalStateException("Hint sheet failed or graded before Check");
    SessionScreen.capture(test,"mixed-mach-hint","mixed-mach-hint");
    test.sendKeyDownUpSync(android.view.KeyEvent.KEYCODE_BACK);Thread.sleep(700);
   }
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
   else if(kind.equals("formula_blocks")||kind.equals("formula_named")){
    org.json.JSONArray tokens=q.getJSONArray("answer_blocks");
    for(int j=0;j<tokens.length();j++){clickLast(test,wrongFraction&&j==0?"area":tokens.getString(j));Thread.sleep(500);}
   }else if(kind.equals("choice")){
    click(test,"com.duolingo:id/mathCard",q.getString("selection"));
    Thread.sleep(1500); // Original JS grading completes asynchronously.
   }
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
   if(hinted||wrongFraction){
    for(int attempt=0;attempt<150&&!contains(test,"GOT IT");attempt++)Thread.sleep(200);
    if(!contains(test,"GOT IT"))throw new IllegalStateException("Expected incorrect feedback after Check");
    SessionScreen.capture(test,wrongFraction?"mixed-fraction-wrong":"mixed-mach-hinted-feedback",wrongFraction?"mixed-fraction-wrong":"mixed-mach-hinted-feedback");
    click(test,null,"GOT IT");continue;
   }
   for(int attempt=0;attempt<150&&!correct;attempt++){
    correct=hasContinue(test)&&!contains(test,"GOT IT");
    for(String label:positive)if(contains(test,label))correct=true;
    if(!correct)Thread.sleep(200);
   }
   SessionScreen.capture(test,"mixed-graded-"+i,"mixed-graded-"+i);
   if(!correct)throw new IllegalStateException("No original correct feedback for "+q.getString("id"));
   if(contains(test,"Something went wrong")||contains(test,"skip this exercise")||contains(test,"GOT IT"))
    throw new IllegalStateException("Original controller reported an error or incorrect answer for "+q.getString("id"));
   if(kind.equals("matching")){
    boolean positiveFeedback=false;
    for(String label:positive)if(contains(test,label))positiveFeedback=true;
    if(!positiveFeedback)throw new IllegalStateException("Matching feedback lacks an explicit positive signal for "+q.getString("id"));
   }else NativeMathGrade.require(test,activity,"CORRECT");
   android.util.Log.i("DuoAeroProbe","Native mixed feedback CORRECT: "+q.getString("id")+" type="+kind);
   click(test,null,"CONTINUE");
  }
  if(fractionWrong){
   org.json.JSONObject retry=null;
   for(int i=0;i<questions.length();i++)if(questions.getJSONObject(i).getString("id").equals("COLUMN-FACTOR-FORMULA-NAMED-ALL"))retry=questions.getJSONObject(i);
   if(retry==null)throw new IllegalStateException("Fraction retry question missing");
   for(int attempt=0;attempt<150&&!(contains(test,"Complete the formula with quantities")&&contains(test,"capacity")&&contains(test,"force"));attempt++){
    if(contains(test,"you missed")&&hasContinue(test))click(test,null,"CONTINUE");
    Thread.sleep(200);
   }
   if(!(contains(test,"Complete the formula with quantities")&&contains(test,"capacity")&&contains(test,"force")))throw new IllegalStateException("Wrong fraction did not retry at lesson end");
   SessionScreen.capture(test,"mixed-fraction-retry","mixed-fraction-retry");
   org.json.JSONArray tokens=retry.getJSONArray("answer_blocks");
   for(int i=0;i<tokens.length();i++){clickLast(test,tokens.getString(i));Thread.sleep(500);}
   click(test,"com.duolingo:id/submitButton",null);
   for(int attempt=0;attempt<150&&!hasContinue(test);attempt++)Thread.sleep(200);
   if(!hasContinue(test)||contains(test,"GOT IT"))throw new IllegalStateException("Fraction retry did not grade correctly");
   if(contains(test,"Something went wrong")||contains(test,"skip this exercise"))throw new IllegalStateException("Fraction retry was skipped after a controller error");
   NativeMathGrade.require(test,activity,"CORRECT");
   click(test,null,"CONTINUE");
   for(int attempt=0;attempt<150&&!contains(test,"CLAIM XP");attempt++)Thread.sleep(200);
   if(!contains(test,"CLAIM XP"))throw new IllegalStateException("Fraction retry did not reach completion");
   return "PASS: wrong native fraction graded at Check and retried at lesson end, then Claim XP appeared. Course persistence not tested.\n";
  }
  if(hintRetry){
   String retryNeedle=payloadScenario?"10100":rocketScenario?"3297":directHintScenario?"1.0 mm":windScenario?"1.4583":"17.97";
   for(int attempt=0;attempt<150&&(contains(test,"GOT IT")||!contains(test,retryNeedle)||!hasControl(test,"com.duolingo:id/mathCard"));attempt++){
    if(contains(test,"you missed")&&hasContinue(test))click(test,null,"CONTINUE");
    Thread.sleep(200);
   }
   if(contains(test,"GOT IT")||!contains(test,retryNeedle)||!hasControl(test,"com.duolingo:id/mathCard")||hintedQuestion==null)throw new IllegalStateException("Hinted calculation did not retry at lesson end");
   SessionScreen.capture(test,"mixed-mach-retry","mixed-mach-retry");
   click(test,"com.duolingo:id/mathCard",hintedQuestion.getString("selection"));Thread.sleep(1500);
   click(test,"com.duolingo:id/submitButton",null);
   for(int attempt=0;attempt<150&&!hasContinue(test);attempt++)Thread.sleep(200);
   if(!hasContinue(test)||contains(test,"GOT IT"))throw new IllegalStateException("Correct hinted retry did not grade correctly");
   if(contains(test,"Something went wrong")||contains(test,"skip this exercise"))throw new IllegalStateException("Hinted retry was skipped after a controller error");
   NativeMathGrade.require(test,activity,"CORRECT");
   click(test,null,"CONTINUE");
   for(int attempt=0;attempt<150&&!contains(test,"CLAIM XP");attempt++)Thread.sleep(200);
   if(!contains(test,"CLAIM XP"))throw new IllegalStateException("Hinted retry did not reach lesson completion");
   if(directHintScenario)return "PASS: native axial extension hint was graded only at Check and retried at lesson end, then Claim XP appeared. Course persistence was not tested.\n";
   if(rocketScenario)return "PASS: native rocket hint was graded only at Check and retried at lesson end, then Claim XP appeared. Course persistence was not tested.\n";
   if(payloadScenario)return "PASS: native payload hint was graded only at Check and retried at lesson end, then Claim XP appeared. Course persistence was not tested.\n";
   return "PASS: native "+(windScenario?"wind":"Mach")+" formula practice preceded each calculation; a viewed hint was graded only at Check and retried at lesson end, then Claim XP appeared. Course persistence was not tested.\n";
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
  return allMathAnswers(test,activity,"rich-session-selections.json",true,false);
 }
 static String allMathHintRetry(Instrumentation test,android.app.Activity activity)throws Exception {
  return allMathAnswers(test,activity,"rich-session-selections.json",true,true);
 }
 static String allPathAnswers(Instrumentation test,android.app.Activity activity)throws Exception {
  return allMathAnswers(test,activity,"path-session-selections.json",false,false);
 }
 private static String allMathAnswers(Instrumentation test,android.app.Activity activity,String selectionAsset,boolean checkRichLayout,boolean hintRetry)throws Exception {
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
   if(checkRichLayout&&(question.getString("id").matches("TA1-(0148|0397-D2(-S1)?|0107-D2|0182-F1|0232|0753-D3|0832-D3)")||question.getString("id").equals("TH-2026-OTHER-1")))SessionScreen.capture(test,"lesson-prompt-"+i,"lesson-prompt-"+i);
   if(checkRichLayout&&question.getString("id").equals("TA1-0148")){
    // This fixture alone carries the experimental native hint. Capture the
    // opened sheet before Check; the production bank does not enable it yet.
    clickTip(test);Thread.sleep(1000);
    SessionScreen.capture(test,"lesson-hint-open","lesson-hint-open");
    if(contains(test,"INCORRECT"))throw new IllegalStateException("Hint graded before Check");
    test.sendKeyDownUpSync(android.view.KeyEvent.KEYCODE_BACK);Thread.sleep(700);
   }
   if(checkRichLayout&&!hintRetry&&question.getString("id").matches("TA1-(0078|0132|0154|0081)-D2")){
    clickTip(test);Thread.sleep(1000);
    if(!contains(test,"a tip"))throw new IllegalStateException("Native formula hint did not open: "+question.getString("id"));
    SessionScreen.capture(test,"lesson-hint-"+question.getString("id"),"lesson-hint-"+question.getString("id"));
    test.sendKeyDownUpSync(android.view.KeyEvent.KEYCODE_BACK);Thread.sleep(700);
   }
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
   if(hintRetry&&question.getString("id").equals("TA1-0148")){
    for(int attempt=0;attempt<100&&!contains(test,"GOT IT");attempt++)Thread.sleep(200);
    if(!contains(test,"GOT IT"))throw new IllegalStateException("Hint did not mark answer for retry at Check");
    SessionScreen.capture(test,"lesson-hint-graded","lesson-hint-graded");
    click(test,null,"GOT IT");Thread.sleep(1000);continue;
   }
   NativeMathGrade.require(test,activity,"CORRECT");
   android.util.Log.i("DuoAeroProbe","Native correct answer "+(i+1)+"/"+selections.length()+": "+question.getString("id"));
   for(int attempt=0;attempt<150&&!hasContinue(test);attempt++)Thread.sleep(200);
   if(!hasContinue(test))throw new IllegalStateException("Missing graded Continue at "+question.getString("id"));
   if(i==selections.length()-1)finalContinueAt=android.os.SystemClock.elapsedRealtime();
   click(test,null,"CONTINUE");
   if(i<selections.length()-1)Thread.sleep(1000);
  }
  if(hintRetry){
   for(int attempt=0;attempt<150&&!contains(test,"Density");attempt++){
    if(contains(test,"you missed")&&hasContinue(test))click(test,null,"CONTINUE");
    Thread.sleep(200);
   }
   if(!contains(test,"Density"))throw new IllegalStateException("Hinted question did not reappear at the end");
   SessionScreen.capture(test,"lesson-hint-retry","lesson-hint-retry");
   click(test,"com.duolingo:id/mathCard","\\textstyle "+contentDensity());
   NativeMathGrade.awaitSelection(test,activity,"CORRECT");
   click(test,"com.duolingo:id/submitButton",null);
   for(int attempt=0;attempt<150&&!hasContinue(test);attempt++)Thread.sleep(200);
   if(!hasContinue(test))throw new IllegalStateException("Correct hint retry did not complete");
   click(test,null,"CONTINUE");
  }
  for(int attempt=0;attempt<100&&!contains(test,"CLAIM XP");attempt++)Thread.sleep(200);
  boolean summaryVisible=contains(test,"CLAIM XP");
  long summaryWait=android.os.SystemClock.elapsedRealtime()-finalContinueAt;
  android.util.Log.i("DuoAeroProbe","Final Continue to observed Claim XP: "+summaryWait+" ms; visible="+summaryVisible);
  SessionScreen.capture(test,"lesson-after-last-answer","lesson-after-last-answer");
  if(hintRetry&&!summaryVisible)throw new IllegalStateException("Claim XP did not appear after successful hint retry");
  if(hintRetry)return "PASS: formula hint stayed ungraded until Check, was marked incorrect on Check, and was retried after the remaining questions. Correct retry reached Claim XP. Persistence is not asserted.\n";
  return "Final Continue to observed Claim XP: "+summaryWait+" ms; visible="+summaryVisible+".\nAll "+selections.length()+" diagnostic selections graded CORRECT by original visible fragments. Last Continue clicked. Inspect final screen: this alone does not assert session completion, saved progress or resume.\n";
 }
 private static String contentDensity(){return "\\text{Density}";}
 private static void clickTip(Instrumentation test){
  AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();
  if(root==null)throw new IllegalStateException("No active native hint window");
  try{
   java.util.List<AccessibilityNodeInfo> containers=root.findAccessibilityNodeInfosByViewId("com.duolingo:id/calculatorAndTipContainer");
   if(containers.size()!=1)throw new IllegalStateException("No unique native calculator and hint container");
   AccessibilityNodeInfo best=rightmostClickable(containers.get(0),0);
   containers.get(0).recycle();
   if(best==null)throw new IllegalStateException("Native hint button not visible");
   try{if(!best.performAction(AccessibilityNodeInfo.ACTION_CLICK))throw new IllegalStateException("Native hint did not open");}
   finally{best.recycle();}
  }finally{root.recycle();}
 }
 private static AccessibilityNodeInfo rightmostClickable(AccessibilityNodeInfo node,int depth){
  if(depth>30||!own(node)||!node.isVisibleToUser())return null;
  AccessibilityNodeInfo best=node.isClickable()?AccessibilityNodeInfo.obtain(node):null;
  android.graphics.Rect b=new android.graphics.Rect(),r=new android.graphics.Rect();
  for(int i=0;i<node.getChildCount();i++){
   AccessibilityNodeInfo child=node.getChild(i);if(child==null)continue;
   try{
    AccessibilityNodeInfo candidate=rightmostClickable(child,depth+1);
    if(candidate!=null){
     candidate.getBoundsInScreen(r);
     if(best!=null)best.getBoundsInScreen(b);
     if(best==null||r.centerX()>b.centerX()){if(best!=null)best.recycle();best=candidate;}
     else candidate.recycle();
    }
   }finally{child.recycle();}
  }
  return best;
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
 static boolean contains(Instrumentation test,String text){
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
 static void clickLast(Instrumentation test,String text)throws Exception {
  AccessibilityNodeInfo node=null;
  for(int attempt=0;attempt<18&&node==null;attempt++){
   dismissPixelLauncherAnr(test);
   AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();
   if(root!=null)try{
    node=findLast(root,text,0);
    if(node==null)scrollBank(root,attempt<9?AccessibilityNodeInfo.ACTION_SCROLL_FORWARD:AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD,0);
   }finally{root.recycle();}
   if(node==null)Thread.sleep(300);
  }
  if(node==null)throw new IllegalStateException("Native bank token not visible: "+text);
  try{for(int i=0;i<8&&!node.isClickable();i++){AccessibilityNodeInfo parent=node.getParent();if(parent==null)break;node.recycle();node=parent;}
   if(!own(node)||!node.isEnabled())throw new IllegalStateException("Native bank token unavailable: "+text);
   if(actualTouch){
    android.graphics.Rect rect=new android.graphics.Rect();node.getBoundsInScreen(rect);
    if(rect.isEmpty())throw new IllegalStateException("Empty native token touch bounds: "+text);
    long down=android.os.SystemClock.uptimeMillis();
    android.view.MotionEvent first=android.view.MotionEvent.obtain(down,down,android.view.MotionEvent.ACTION_DOWN,rect.exactCenterX(),rect.exactCenterY(),0);
    android.view.MotionEvent last=android.view.MotionEvent.obtain(down,down+30,android.view.MotionEvent.ACTION_UP,rect.exactCenterX(),rect.exactCenterY(),0);
    first.setSource(android.view.InputDevice.SOURCE_TOUCHSCREEN);
    last.setSource(android.view.InputDevice.SOURCE_TOUCHSCREEN);
    try{
     if(!test.getUiAutomation().injectInputEvent(first,true))throw new IllegalStateException("Token down event not injected: "+text);
     Thread.sleep(30);
     if(!test.getUiAutomation().injectInputEvent(last,true))throw new IllegalStateException("Token up event not injected: "+text);
    }finally{first.recycle();last.recycle();}
   }else if(!node.performAction(AccessibilityNodeInfo.ACTION_CLICK))throw new IllegalStateException("Native bank token did not accept click: "+text);
  }finally{node.recycle();}
 }
 /** The hosted emulator occasionally shows an ANR for its Pixel Launcher
  * over the test app after a resolution change. Dismiss only that exact
  * system dialog; never dismiss an ANR belonging to DuoAero. */
 private static void dismissPixelLauncherAnr(Instrumentation test)throws Exception {
  AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();
  if(root==null)return;
  try{
   java.util.List<AccessibilityNodeInfo> labels=root.findAccessibilityNodeInfosByText("Pixel Launcher isn't responding");
   boolean launcher=false;
   for(AccessibilityNodeInfo label:labels){
    if("Pixel Launcher isn't responding".contentEquals(label.getText()==null?"":label.getText()))launcher=true;
    label.recycle();
   }
   if(!launcher)return;
   java.util.List<AccessibilityNodeInfo> buttons=root.findAccessibilityNodeInfosByText("Close app");
   for(AccessibilityNodeInfo button:buttons){
    try{
     if(!"Close app".contentEquals(button.getText()==null?"":button.getText()))continue;
     AccessibilityNodeInfo current=AccessibilityNodeInfo.obtain(button);
     try{
      for(int depth=0;depth<5&&!current.isClickable();depth++){
       AccessibilityNodeInfo parent=current.getParent();if(parent==null)break;
       current.recycle();current=parent;
      }
      if(current.isClickable()&&current.performAction(AccessibilityNodeInfo.ACTION_CLICK)){
       android.util.Log.i("DuoAeroProbe","Dismissed emulator Pixel Launcher ANR");Thread.sleep(700);break;
      }
     }finally{current.recycle();}
    }finally{button.recycle();}
   }
  }finally{root.recycle();}
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
 static void click(Instrumentation test,String id,String text){
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
