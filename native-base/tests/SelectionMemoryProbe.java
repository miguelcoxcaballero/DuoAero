package com.duoaero.nativebase;
import android.app.Activity;
import android.app.Instrumentation;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import org.json.JSONArray;
import org.json.JSONObject;

/** Alternate actual answer selections on a fixed question; never Check. */
final class SelectionMemoryProbe {
 static String run(Instrumentation test,Activity activity)throws Exception {
  JSONArray questions;
  try(InputStream in=test.getTargetContext().getAssets().open("duoaero/mixed-source.json")){
   ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buffer=new byte[8192];int n;
   while((n=in.read(buffer))!=-1)bytes.write(buffer,0,n);
   questions=new JSONArray(bytes.toString("UTF-8"));
  }
  JSONObject q=questions.getJSONObject(0);
  if(!"choice".equals(q.getString("type")))throw new IllegalStateException("Fixed selection fixture is not choice");
  String id=q.getString("id"),correct=q.getString("selection"),wrong=null;
  JSONArray options=q.getJSONArray("options");
  for(int i=0;i<options.length();i++)if(i!=q.getInt("answer")){
   String raw=options.getString(i);
   if(!raw.matches("[A-Za-z ]+"))throw new IllegalStateException("Unexpected diagnostic choice format");
   // Match the original adapter's native LaTeX accessibility description.
   wrong="\\text{"+raw+"}";break;
  }
  if(wrong==null||!id.equals(NativeChallengeIdentity.read(test,activity)))throw new IllegalStateException("Unexpected fixed question");
  for(int wait=0;wait<150;wait++){
   if(SessionInteraction.hasControl(test,"com.duolingo:id/mathCard")&&SessionInteraction.contains(test,correct)&&SessionInteraction.contains(test,wrong))break;
   Thread.sleep(200);
  }
  if(!SessionInteraction.hasControl(test,"com.duolingo:id/mathCard")||!SessionInteraction.contains(test,correct)||!SessionInteraction.contains(test,wrong)){
   SessionScreen.capture(test,"selection-memory-not-ready","selection-memory-not-ready");
   throw new IllegalStateException("Original selection controls not ready for fixed question");
  }
  SessionScreen.sampleMemory(test,"selection-fixed-start");
  for(int i=1;i<=20;i++){
   boolean chooseCorrect=i%2==1;
   SessionInteraction.click(test,"com.duolingo:id/mathCard",chooseCorrect?correct:wrong);
   NativeMathGrade.awaitSelection(test,activity,chooseCorrect?"CORRECT":"INCORRECT");
   if(!id.equals(NativeChallengeIdentity.read(test,activity)))throw new IllegalStateException("Question changed without Check");
   String state=NativeChallengeIdentity.gradingState(test,activity);
   if(state==null||!state.endsWith("GradingState$Input"))throw new IllegalStateException("Selection submitted before Check: "+state);
   if(i%2==0)SessionScreen.sampleMemory(test,"selection-fixed-"+i);
  }
  return "PASS: 20 alternating native answer selections on one question, no Check or advancement; inspect memory samples.\n";
 }
}
