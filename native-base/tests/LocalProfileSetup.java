package com.duoaero.nativebase;
import android.content.Context;
import java.lang.reflect.*;

/** Installs only the isolated diagnostic identity and original default config. */
final class LocalProfileSetup {
 static void install(Context context,String courseId,boolean defaultExperiments)throws Exception {
  ClassLoader loader=context.getClassLoader();
  Class<?> bridge=Class.forName("com.duoaero.nativebase.NativeCourseBridge",true,loader);
  bridge.getField("localOnly").setBoolean(null,true);
  bridge.getField("captureLocalRequests").setBoolean(null,true);
  bridge.getField("captureNativeFlows").setBoolean(null,true);
  Object user=UserModelProbe.makeLocalUser(context,courseId);
  Object app=context.getApplicationContext();
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
  Object loginHolder=Proxy.newProxyInstance(loader,new Class[]{lazy},(proxy,method,args)->{
   if(method.getName().equals("getValue"))return loginFlow;
   if(method.getName().equals("isInitialized"))return true;
   if(method.getName().equals("toString"))return "Offline local identity";
   if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
   if(method.getName().equals("equals"))return proxy==args[0];
   throw new UnsupportedOperationException(method.getName());
  });
  Field loginField=loginRepository.getClass().getField("c");loginField.setAccessible(true);loginField.set(loginRepository,loginHolder);
  // Feed the original first-person cache too. Existing observers may have
  // captured repository flows before the diagnostic lazy holders were replaced.
  Object resourceFactory=repository.getClass().getField("r").get(repository);
  Class<?> category=Class.forName("com.duolingo.core.data.ProfileUserCategory",true,loader);
  Object resource=resourceFactory.getClass().getMethod("a",userId.getClass(),category,Class.forName("rbb",true,loader))
   .invoke(resourceFactory,userId,category.getField("FIRST_PERSON").get(null),null);
  Object cache=repository.getClass().getField("p").get(repository);
  LocalCourseCache.write(loader,cache,resource,user);
  // Use the original pure login-state reducer and its native cache wrappers.
  // Existing observers of chc.a must see the same isolated identity as bxn.c.
  // This is synthetic state input, not authentication with a real account.
  Class<?> reducerType=Class.forName("qqh",true,loader);
  Class<?> operationType=Class.forName("e490",true,loader);
  Object reducer=Class.forName("ygc",true,loader)
   .getConstructor(Class.forName("vwn",true,loader),int.class).newInstance(loginState,0);
  Object operation=Class.forName("d490",true,loader).getConstructor(reducerType).newInstance(reducer);
  Constructor<?> wrap=Class.forName("b490",true,loader).getConstructor(operationType,int.class);
  operation=wrap.newInstance(wrap.newInstance(operation,0),1);
  LocalCourseCache.apply(loader,cache,operation);
  // A new account has a known zero-day lifetime streak, not the all-null
  // "unavailable" UserStreak sentinel rejected by original loader c4x.A.
  Class<?> lifetimeType=Class.forName("com.duolingo.data.streak.StreakData$LifetimeStreak",true,loader);
  Object lifetime=lifetimeType.getConstructor(String.class,String.class,int.class,String.class).newInstance(null,null,0,null);
  Class<?> timelineType=Class.forName("com.duolingo.data.streak.TimelineStreak",true,loader);
  Class<?> streakType=Class.forName("com.duolingo.data.streak.UserStreak",true,loader);
  Object streak=streakType.getConstructor(lifetimeType,timelineType,timelineType).newInstance(lifetime,null,null);
  Object streakProvider=component.getClass().getField("e2").get(component);
  Method streakGet=streakProvider.getClass().getMethod("get");streakGet.setAccessible(true);
  Object streakFactory=streakGet.invoke(streakProvider);
  if(!streakFactory.getClass().getName().equals("ex50"))throw new IllegalStateException("Unexpected streak resource factory");
  Object streakResource=streakFactory.getClass().getMethod("a",userId.getClass()).invoke(streakFactory,userId);
  LocalCourseCache.write(loader,cache,streakResource,streak);
  if(defaultExperiments){
   LocalExperimentProfile.install(component,userId,loader);
  }
 }
}
