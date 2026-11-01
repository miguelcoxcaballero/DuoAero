package com.duoaero.nativebase;
import android.app.Instrumentation;
import android.content.Intent;
import android.os.Bundle;
import java.lang.reflect.*;

/** Offline-only integration probe: never sends the synthetic profile to a service. */
public final class UserSessionProbe extends Instrumentation {
 private String courseId="DUOAERO_AEROSPACE_MIDTERM1";
 private boolean defaultExperiments=false;
 private boolean earlySetup=false;
 private boolean nativeCourseCache=false;
 private boolean fullCoursePath=false;
 private boolean captureHome=false;
 private boolean seedConfig=false;
 private String lesson="math";
 private String interaction="none";
 private Throwable setupError;
 public void onCreate(Bundle args){
  if(args!=null){courseId=args.getString("course_id",courseId);defaultExperiments="native-defaults".equals(args.getString("experiments"));earlySetup="early".equals(args.getString("bootstrap"));}
  fullCoursePath=args!=null&&"native-full".equals(args.getString("course_cache"));
  nativeCourseCache=fullCoursePath||(args!=null&&"native-minimal".equals(args.getString("course_cache")));
  captureHome=args!=null&&"true".equals(args.getString("capture_home"));
  seedConfig=args!=null&&"native-default".equals(args.getString("config_cache"));
  if(args!=null)lesson=args.getString("lesson",lesson);
  if(args!=null)interaction=args.getString("interact",interaction);
  if(earlySetup)try{LocalProfileSetup.install(getTargetContext(),courseId,defaultExperiments);}catch(Throwable error){setupError=error;}
  start();
 }
 public void onStart(){Bundle output=new Bundle();StringBuilder report=new StringBuilder();boolean completed=false;try{
  ClassLoader loader=getTargetContext().getClassLoader();
  if(!lesson.equals("math")&&!lesson.equals("aerospace")&&!lesson.equals("aerospace-rich"))throw new IllegalArgumentException("Unsupported diagnostic lesson");
  if(!java.util.Arrays.asList("none","first-assist","math-correct","math-wrong","math-all").contains(interaction))throw new IllegalArgumentException("Unsupported interaction");
  if(interaction.equals("first-assist")&&!lesson.equals("aerospace"))throw new IllegalArgumentException("Interaction requires the assist fixture");
  if(interaction.startsWith("math-")&&!lesson.equals("aerospace-rich"))throw new IllegalArgumentException("Math interaction requires rich fixture");
  if(nativeCourseCache&&!courseId.equals("MATH_BT"))throw new IllegalArgumentException("Minimal cache requires original MATH_BT diagnostic profile");
  if(setupError!=null)throw new IllegalStateException("Early diagnostic profile setup failed",setupError);
  if(!earlySetup)LocalProfileSetup.install(getTargetContext(),courseId,defaultExperiments);
  if(seedConfig&&!captureHome)report.append(LocalConfigCache.install(getTargetContext()));
  report.append("Diagnostic course variant: ").append(courseId).append("\n");
  report.append("Diagnostic setup phase: ").append(earlySetup?"before Application.onCreate":"instrumentation onStart").append('\n');
  if(defaultExperiments)report.append("Experiment input: original empty/default entries for synthetic user.\n");
  Object app=getTargetContext().getApplicationContext();
  final java.util.concurrent.atomic.AtomicReference<android.app.Activity> resumed=new java.util.concurrent.atomic.AtomicReference<>();
  ((android.app.Application)app).registerActivityLifecycleCallbacks(new android.app.Application.ActivityLifecycleCallbacks(){
   public void onActivityCreated(android.app.Activity a,Bundle b){android.util.Log.i("DuoAeroProbe","created "+a.getClass().getName());}
   public void onActivityResumed(android.app.Activity a){resumed.set(a);android.util.Log.i("DuoAeroProbe","resumed "+a.getClass().getName());}
   public void onActivityStarted(android.app.Activity a){}
   public void onActivityPaused(android.app.Activity a){}
   public void onActivityStopped(android.app.Activity a){}
   public void onActivitySaveInstanceState(android.app.Activity a,Bundle b){}
   public void onActivityDestroyed(android.app.Activity a){}
  });
  // Exercise the real startup path before opening a session. Directly launching
  // SessionActivity skips application initialization performed by LaunchActivity.
  Intent launch=getTargetContext().getPackageManager().getLaunchIntentForPackage(getTargetContext().getPackageName());
  if(launch==null)throw new IllegalStateException("Missing original launcher");
  getTargetContext().startActivity(launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
  Thread.sleep(6000);
  Class<?> activity=Class.forName("com.duolingo.session.SessionActivity",true,loader);
  String lessonAsset=lesson.equals("math")?"hardcoded_sessions/math/math_lesson.json":lesson.equals("aerospace")?"hardcoded_sessions/duoaero/aerospace_lesson.json":"hardcoded_sessions/duoaero/aerospace_rich_lesson.json";
  report.append("Lesson input: ").append(lessonAsset).append('\n');
  Object params=Class.forName("com.duolingo.data.session.start.SessionStartParams$Hardcoded",true,loader)
   .getConstructor(String.class,boolean.class).newInstance(lessonAsset,false);
  Object via=Class.forName("com.duolingo.data.onboarding.OnboardingVia",true,loader).getField("HOME").get(null);
  for(Method method:activity.getDeclaredMethods())if(method.getName().equals("L")&&method.getParameterTypes().length==13){
   Intent intent=(Intent)method.invoke(null,getTargetContext(),params,false,via,false,false,null,null,null,true,false,null,activity);
   getTargetContext().startActivity(intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
   report.append("Original SessionActivity requested with isolated local profile. Network blocked.\n");
   break;
  }
  Thread.sleep(12000);
  android.app.Activity current=resumed.get();
  report.append("Resumed: ").append(current==null?"none":current.getClass().getName()).append('\n');
  if(current==null || !activity.isInstance(current))throw new IllegalStateException("SessionActivity did not resume");
  Object observedVm=activity.getMethod("J").invoke(current);
  if(nativeCourseCache){report.append(LocalCourseCache.install(getTargetContext(),observedVm,fullCoursePath));Thread.sleep(12000);}
  try(SessionDependencies dependencies=new SessionDependencies(observedVm)){
   Thread.sleep(5000);
   report.append(dependencies.report());
  }
  final java.util.concurrent.atomic.AtomicReference<Throwable> snapshotError=new java.util.concurrent.atomic.AtomicReference<>();
  runOnMainSync(()->{
   try {
    Object vm=activity.getMethod("J").invoke(current);
    for(String name:new String[]{"s2","t2","u2","v2","l4"}){
     Object value=vm.getClass().getField(name).get(vm);
     report.append(name).append('=').append(value==null?"null":value.getClass().getName()).append('\n');
    }
    Object engine=vm.getClass().getField("t2").get(vm);
    Object engineFlow=engine.getClass().getField("k").get(engine);
    Object engineState=engineFlow.getClass().getMethod("getValue").invoke(engineFlow);
    report.append("Engine state: ").append(engineState==null?"null":engineState.getClass().getName()).append('\n');
    if(engineState!=null && engineState.getClass().getName().equals("eo10")){
     Object loadedSession=engineState.getClass().getField("e").get(engineState);
     report.append("Loaded original Session model: ").append(loadedSession.getClass().getName()).append('\n');
     report.append("Loaded challenge count: ").append(loadedSession.getClass().getMethod("g").invoke(loadedSession)).append('\n');
    }
    Object init=vm.getClass().getField("x1").get(vm);
    for(String name:new String[]{"a","b","c","d","e","f","g","h","i"}){
     Object subject=init.getClass().getField(name).get(init);
     if(subject.getClass().getName().equals("f2z")){
      subject=subject.getClass().getField("a").get(subject);
      subject=subject.getClass().getField("b").get(subject);
     }
     Object value=subject.getClass().getMethod("y0").invoke(subject);
     report.append("Initialization ").append(name).append('=').append(value instanceof Boolean?value:value==null?"null":value.getClass().getName()).append('\n');
    }
   }catch(Throwable e){snapshotError.set(e);}
  });
  if(snapshotError.get()!=null)throw new IllegalStateException("Cannot inspect original session state",snapshotError.get());
  android.util.Log.i("DuoAeroProbe",report.toString());
  Object sessionLoader=observedVm.getClass().getField("j").get(observedVm);
  Object javascript=sessionLoader.getClass().getField("k").get(sessionLoader);
  Object sandboxFactory=javascript.getClass().getField("c").get(javascript);
  Object sandbox=sandboxFactory.getClass().getField("f").get(sandboxFactory);
  java.util.Map<?,?> executionContexts=(java.util.Map<?,?>)javascript.getClass().getField("f").get(javascript);
  report.append("Native JavaScript sandbox present: ").append(sandbox!=null).append("; execution contexts: ").append(executionContexts.keySet()).append('\n');
  SessionScreen.capture(this);
  if(interaction.equals("first-assist"))report.append(SessionInteraction.firstAssistAnswer(this));
  if(interaction.equals("math-all"))report.append(SessionInteraction.allMathAnswers(this,current));
  else if(interaction.startsWith("math-"))report.append(SessionInteraction.firstMathAnswer(this,current,interaction.equals("math-wrong")));
  if(interaction.equals("math-all")){
   Object engine=observedVm.getClass().getField("t2").get(observedVm);
   Object flow=engine.getClass().getField("k").get(engine);
   Object state=flow.getClass().getMethod("getValue").invoke(flow);
   report.append("Engine after all answers: ").append(state==null?"null":state.getClass().getName()).append('\n');
   if(state!=null)for(Field field:state.getClass().getFields()){
    if(Modifier.isStatic(field.getModifiers()))continue;
    Object value=field.get(state);
    report.append("End-state field ").append(field.getName()).append(": ").append(value==null?"null":value.getClass().getName()).append('\n');
   }
  }
  if(interaction.equals("math-all")){
   try(SessionDependencies dependencies=SessionDependencies.end(this,current)){
    Thread.sleep(5000);report.append(dependencies.report());
   }
  }
  if(captureHome){
   runOnMainSync(current::finish);
   Thread.sleep(12000);
   android.app.Activity home=resumed.get();
   report.append("After finishing diagnostic session activity, resumed: ").append(home==null?"none":home.getClass().getName()).append('\n');
   if(home!=null&&home.getClass().getName().equals("com.duolingo.splash.LaunchActivity")){
    try(SessionDependencies dependencies=SessionDependencies.home(home)){
     Thread.sleep(5000);report.append(dependencies.report());
     if(seedConfig){
      SessionScreen.capture(this,"home-before-config","home-before-config");
      report.append(LocalConfigCache.install(getTargetContext()));
      Thread.sleep(12000);
      report.append("After native Config input:\n").append(dependencies.report());
     }
    }
   }
   SessionScreen.capture(this,"home-diagnostic","home-view-tree");
  }
  completed=true;
  report.append("Isolated request counts (no query, headers or body): ")
   .append(Class.forName("com.duoaero.nativebase.NativeCourseBridge",true,loader).getMethod("diagnosticRequests").invoke(null)).append('\n');
  report.append("DIAGNOSTIC_COLLECTION_COMPLETED=true. This does not assert lesson rendering or grading.\n");
 }catch(Throwable error){if(error instanceof InvocationTargetException)error=error.getCause();report.append(android.util.Log.getStackTraceString(error));}
 output.putString("stream",report.toString());output.putBoolean("diagnostic_completed",completed);finish(completed?-1:0,output);}
}
