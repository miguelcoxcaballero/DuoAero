package com.duoaero.nativebase;
import android.app.Instrumentation;
import android.content.Intent;
import android.os.Bundle;
import java.lang.reflect.*;

/** Offline-only integration probe: never sends the synthetic profile to a service. */
public final class UserSessionProbe extends Instrumentation {
 private String courseId="DUOAERO_AEROSPACE_MIDTERM1";
 private boolean defaultExperiments=false;
 public void onCreate(Bundle args){if(args!=null){courseId=args.getString("course_id",courseId);defaultExperiments="native-defaults".equals(args.getString("experiments"));}start();}
 public void onStart(){Bundle output=new Bundle();StringBuilder report=new StringBuilder();boolean completed=false;try{
  ClassLoader loader=getTargetContext().getClassLoader();
  Class<?> bridge=Class.forName("com.duoaero.nativebase.NativeCourseBridge",true,loader);
  bridge.getField("localOnly").setBoolean(null,true);
  Object user=UserModelProbe.makeLocalUser(getTargetContext(),courseId);
  report.append("Diagnostic course variant: ").append(courseId).append("\n");
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
  Object component=app.getClass().getMethod("generatedComponent").invoke(app);
  Object provider=component.getClass().getField("q2").get(component);
  Method provide=provider.getClass().getMethod("get");provide.setAccessible(true);
  Object repository=provide.invoke(provider);
  Class<?> flow=Class.forName("if40",true,loader);
  Object state=Class.forName("wd90",true,loader).getConstructor(user.getClass()).newInstance(user);
  Object stateFlow=flow.getConstructor(Object.class).newInstance(state);
  Object userFlow=flow.getConstructor(Object.class).newInstance(user);
  Object offlineRepositoryMode=flow.getConstructor(Object.class).newInstance(Boolean.FALSE);
  Class<?> lazy=Class.forName("qvl",true,loader);
  for(String fieldName:new String[]{"t","u","v","w"}){
   final Object value=fieldName.equals("w")?offlineRepositoryMode:fieldName.equals("v")?userFlow:stateFlow;
   Object holder=Proxy.newProxyInstance(loader,new Class[]{lazy},(proxy,method,args)->{
    if(method.getName().equals("getValue"))return value;
    if(method.getName().equals("isInitialized"))return true;
    if(method.getName().equals("toString"))return "Offline synthetic course state";
    if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
    if(method.getName().equals("equals"))return proxy==args[0];
    throw new UnsupportedOperationException(method.getName());
   });
   Field field=repository.getClass().getField(fieldName);field.setAccessible(true);field.set(repository,holder);
  }
  Object loginRepository=repository.getClass().getField("l").get(repository);
  Object userId=user.getClass().getField("b").get(user);
  Class<?> loginMethod=Class.forName("com.duolingo.core.signuplogin.LoginState$LoginMethod",true,loader);
  Object loginState=Class.forName("qwn",true,loader).getConstructor(userId.getClass(),loginMethod).newInstance(userId,loginMethod.getField("UNKNOWN").get(null));
  final Object loginFlow=flow.getConstructor(Object.class).newInstance(loginState);
  Object loginHolder=Proxy.newProxyInstance(loader,new Class[]{lazy},(proxy,method,args)->method.getName().equals("getValue")?loginFlow:method.getName().equals("isInitialized")?true:"Offline local identity");
  Field loginField=loginRepository.getClass().getField("c");loginField.setAccessible(true);loginField.set(loginRepository,loginHolder);
  if(defaultExperiments){
   LocalExperimentProfile.install(component,userId,loader);
   report.append("Experiment input: original empty/default entries for synthetic user.\n");
  }
  // Exercise the real startup path before opening a session. Directly launching
  // SessionActivity skips application initialization performed by LaunchActivity.
  Intent launch=getTargetContext().getPackageManager().getLaunchIntentForPackage(getTargetContext().getPackageName());
  if(launch==null)throw new IllegalStateException("Missing original launcher");
  getTargetContext().startActivity(launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
  Thread.sleep(6000);
  Class<?> activity=Class.forName("com.duolingo.session.SessionActivity",true,loader);
  Object params=Class.forName("com.duolingo.data.session.start.SessionStartParams$Hardcoded",true,loader)
   .getConstructor(String.class,boolean.class).newInstance("hardcoded_sessions/math/math_lesson.json",false);
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
  android.graphics.Bitmap screenshot=getUiAutomation().takeScreenshot();
  if(screenshot==null)throw new IllegalStateException("Cannot capture session screen");
  java.io.File screenshotFile=new java.io.File(getTargetContext().getExternalFilesDir(null),"session-diagnostic.png");
  try(java.io.FileOutputStream file=new java.io.FileOutputStream(screenshotFile)){screenshot.compress(android.graphics.Bitmap.CompressFormat.PNG,100,file);}
  screenshot.recycle();
  completed=true;
  report.append("DIAGNOSTIC_COLLECTION_COMPLETED=true. This does not assert lesson rendering or grading.\n");
 }catch(Throwable error){if(error instanceof InvocationTargetException)error=error.getCause();report.append(android.util.Log.getStackTraceString(error));}
 output.putString("stream",report.toString());output.putBoolean("diagnostic_completed",completed);finish(completed?-1:0,output);}
}
