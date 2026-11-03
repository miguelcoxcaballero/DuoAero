package com.duoaero.nativebase;
import android.app.Instrumentation;
import android.app.Activity;
import java.util.concurrent.atomic.AtomicReference;
/** Observe synthetic fixed-screen capture cost without changing app state. */
final class ScreenshotMemoryProbe {
 static String run(Instrumentation test,AtomicReference<Activity> resumed)throws Exception {
  for(int i=0;i<300 && (resumed.get()==null || !SessionInteraction.hasControl(test,"com.duolingo:id/primaryCardView"));i++)Thread.sleep(200);
  Activity home=resumed.get();
  if(home==null || !SessionInteraction.hasControl(test,"com.duolingo:id/primaryCardView"))throw new IllegalStateException("Original home did not become visible");
  for(int i=0;i<4;i++){SessionScreen.sampleMemory(test,"idle-control-"+i);Thread.sleep(500);}
  for(int i=0;i<20;i++){
   if(resumed.get()!=home)throw new IllegalStateException("Foreground activity changed during memory control");
   SessionScreen.capture(test,"memory-fixed-screen","memory-fixed-tree");
   Thread.sleep(200);
  }
  SessionScreen.sampleMemory(test,"fixed-screen-complete");
  return "PASS: sampled 20 captures on the same home activity without changing lesson state. Inspect per-phase memory values; this is not a leak diagnosis.\n";
 }
}
