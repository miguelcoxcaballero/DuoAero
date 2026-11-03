package com.duoaero.nativebase;

import android.app.Activity;
import android.app.Instrumentation;
import java.util.concurrent.atomic.AtomicReference;

/** Read the original visible challenge identity without changing session state. */
final class NativeChallengeIdentity {
 static String read(Instrumentation test,Activity activity)throws Exception {
  AtomicReference<String> result=new AtomicReference<>();AtomicReference<Exception> error=new AtomicReference<>();
  test.runOnMainSync(()->{
   try{
    Object vm=activity.getClass().getMethod("J").invoke(activity);
    if(vm==null)return;
    Object engine=vm.getClass().getField("t2").get(vm);if(engine==null)return;
    Object flow=engine.getClass().getField("k").get(engine);if(flow==null)return;
    Object state=flow.getClass().getMethod("getValue").invoke(flow);
    if(state==null||!state.getClass().getName().equals("eo10"))return;
    Object persisted=state.getClass().getField("a").get(state);if(persisted==null)return;
    Object visual=persisted.getClass().getField("c").get(persisted);
    if(visual==null||!visual.getClass().getName().equals("com.duolingo.data.session.state.SessionVisualState$Challenge"))return;
    Object index=visual.getClass().getField("a").get(visual),session=state.getClass().getField("e").get(state);
    ClassLoader loader=activity.getClassLoader();
    Object challenge=Class.forName("com.duolingo.core.session.v2",true,loader).getMethod("b",session.getClass(),Class.forName("com.duolingo.core.session.api.SessionChallengeIndex",true,loader)).invoke(null,session,index);
    if(challenge==null)return;
    Object id=challenge.getClass().getMethod("getId").invoke(challenge);
    result.set((String)id.getClass().getField("a").get(id));
   }catch(Exception failure){error.set(failure);}
  });
  if(error.get()!=null)throw error.get();return result.get();
 }
 static String gradingState(Instrumentation test,Activity activity)throws Exception {
  AtomicReference<String> result=new AtomicReference<>();AtomicReference<Exception> error=new AtomicReference<>();
  test.runOnMainSync(()->{
   try{
    Object vm=activity.getClass().getMethod("J").invoke(activity);if(vm==null)return;
    Object engine=vm.getClass().getField("t2").get(vm);if(engine==null)return;
    Object flow=engine.getClass().getField("k").get(engine);if(flow==null)return;
    Object state=flow.getClass().getMethod("getValue").invoke(flow);
    if(state==null||!state.getClass().getName().equals("eo10"))return;
    Object persisted=state.getClass().getField("a").get(state);if(persisted==null)return;
    Object visual=persisted.getClass().getField("c").get(persisted);
    if(visual==null||!visual.getClass().getName().equals("com.duolingo.data.session.state.SessionVisualState$Challenge"))return;
    Object grading=visual.getClass().getField("b").get(visual);
    if(grading!=null)result.set(grading.getClass().getName());
   }catch(Exception failure){error.set(failure);}
  });
  if(error.get()!=null)throw error.get();return result.get();
 }

}
