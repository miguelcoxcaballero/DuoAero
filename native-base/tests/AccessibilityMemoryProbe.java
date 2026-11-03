package com.duoaero.nativebase;
import android.app.Activity;
import android.app.Instrumentation;

/** Synthetic fixed-question control: reads accessibility only, never answers. */
final class AccessibilityMemoryProbe {
 static String run(Instrumentation test,Activity activity)throws Exception {
  String initial=NativeChallengeIdentity.read(test,activity);
  if(initial==null)throw new IllegalStateException("No native question for accessibility control");
  SessionScreen.sampleMemory(test,"accessibility-fixed-start");
  for(int i=1;i<=300;i++){
   if(!SessionInteraction.hasControl(test,"com.duolingo:id/mathCard"))
    throw new IllegalStateException("Original choice card disappeared during accessibility control");
   SessionInteraction.contains(test,"not-a-visible-control");
   if(i%50==0){
    if(!initial.equals(NativeChallengeIdentity.read(test,activity)))throw new IllegalStateException("Question changed during fixed control");
    SessionScreen.sampleMemory(test,"accessibility-fixed-"+i);
   }
  }
  return "PASS: 300 repeated accessibility searches on one original question without answering; compare memory samples, not device acceptance.\n";
 }
}
