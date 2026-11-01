package com.duoaero.nativebase;
import android.content.Context;
import java.lang.reflect.*;

/** Installs only the isolated diagnostic identity and original default config. */
final class NativeLocalProfile {
 static void clearLogin(Context context)throws Exception {
  ClassLoader loader=context.getClassLoader();Object app=context.getApplicationContext();
  Object component=app.getClass().getMethod("generatedComponent").invoke(app);
  Object provider=component.getClass().getField("q2").get(component);
  Method get=provider.getClass().getMethod("get");get.setAccessible(true);
  Object repository=get.invoke(provider),cache=repository.getClass().getField("p").get(repository);
  Class<?> method=Class.forName("com.duolingo.core.signuplogin.LoginState$LogoutMethod",true,loader);
  Object state=Class.forName("rwn",true,loader).getConstructor(method).newInstance(method.getField("SETTINGS_MENU").get(null));
  Object reducer=Class.forName("ygc",true,loader).getConstructor(Class.forName("vwn",true,loader),int.class).newInstance(state,0);
  Class<?> operationType=Class.forName("e490",true,loader);
  Object operation=Class.forName("d490",true,loader).getConstructor(Class.forName("qqh",true,loader)).newInstance(reducer);
  Constructor<?> wrap=Class.forName("b490",true,loader).getConstructor(operationType,int.class);
  NativeLocalCache.apply(loader,cache,wrap.newInstance(wrap.newInstance(operation,0),1));
 }
 static Object decodeStreak(Context context)throws Exception {
  ClassLoader loader=context.getClassLoader();
  Object component=context.getApplicationContext().getClass().getMethod("generatedComponent").invoke(context.getApplicationContext());
  Object provider=component.getClass().getField("a0").get(component);
  Method get=provider.getClass().getMethod("get");get.setAccessible(true);
  Object factory=get.invoke(provider);Field field=factory.getClass().getDeclaredField("json");field.setAccessible(true);
  Object json=field.get(factory);
  String data=NativeRewards.profile((android.app.Application)context.getApplicationContext(),new org.json.JSONObject()).toString();
  return Class.forName("a8l",true,loader).getMethod("b",Class.forName("kotlinx.serialization.KSerializer",true,loader),String.class)
   .invoke(json,NativeLocalCache.serializer(loader,"com.duolingo.data.streak.UserStreak"),data);
 }
 static void refreshRewards(Context context)throws Exception {
  ClassLoader loader=context.getClassLoader();Object app=context.getApplicationContext();
  Object component=app.getClass().getMethod("generatedComponent").invoke(app);
  Object provider=component.getClass().getField("q2").get(component);
  Method get=provider.getClass().getMethod("get");get.setAccessible(true);
  Object repository=get.invoke(provider),cache=repository.getClass().getField("p").get(repository);
  Object user=NativeLocalUser.makeLocalUser(context,"MATH_BT"),userId=user.getClass().getField("b").get(user);
  Object factory=repository.getClass().getField("r").get(repository);
  Class<?> category=Class.forName("com.duolingo.core.data.ProfileUserCategory",true,loader);
  Object resource=factory.getClass().getMethod("a",userId.getClass(),category,Class.forName("rbb",true,loader))
   .invoke(factory,userId,category.getField("FIRST_PERSON").get(null),null);
  NativeLocalCache.write(loader,cache,resource,user);
  provider=component.getClass().getField("e2").get(component);
  get=provider.getClass().getMethod("get");get.setAccessible(true);factory=get.invoke(provider);
  resource=factory.getClass().getMethod("a",userId.getClass()).invoke(factory,userId);
  NativeLocalCache.write(loader,cache,resource,decodeStreak(context));
 }
 static void install(Context context,String courseId,boolean defaultExperiments)throws Exception {
  ClassLoader loader=context.getClassLoader();
  Class<?> bridge=Class.forName("com.duoaero.nativebase.NativeCourseBridge",true,loader);
  bridge.getField("localOnly").setBoolean(null,true);
  bridge.getField("captureLocalRequests").setBoolean(null,true);

  Object user=NativeLocalUser.makeLocalUser(context,courseId);
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
  Object loginRepository=repository.getClass().getField("l").get(repository);
  Object userId=user.getClass().getField("b").get(user);
  Class<?> loginMethod=Class.forName("com.duolingo.core.signuplogin.LoginState$LoginMethod",true,loader);
  Object loginState=Class.forName("qwn",true,loader).getConstructor(userId.getClass(),loginMethod).newInstance(userId,loginMethod.getField("UNKNOWN").get(null));
  // Feed the original first-person cache too. Existing observers may have
  // captured repository flows before the diagnostic lazy holders were replaced.
  Object resourceFactory=repository.getClass().getField("r").get(repository);
  Class<?> category=Class.forName("com.duolingo.core.data.ProfileUserCategory",true,loader);
  Object resource=resourceFactory.getClass().getMethod("a",userId.getClass(),category,Class.forName("rbb",true,loader))
   .invoke(resourceFactory,userId,category.getField("FIRST_PERSON").get(null),null);
  Object cache=repository.getClass().getField("p").get(repository);
  NativeLocalCache.write(loader,cache,resource,user);
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
  NativeLocalCache.apply(loader,cache,operation);
  // Decode the same durable reward projection used by the original User.
  Object streak=decodeStreak(context);
  Object streakProvider=component.getClass().getField("e2").get(component);
  Method streakGet=streakProvider.getClass().getMethod("get");streakGet.setAccessible(true);
  Object streakFactory=streakGet.invoke(streakProvider);
  if(!streakFactory.getClass().getName().equals("ex50"))throw new IllegalStateException("Unexpected streak resource factory");
  Object streakResource=streakFactory.getClass().getMethod("a",userId.getClass()).invoke(streakFactory,userId);
  NativeLocalCache.write(loader,cache,streakResource,streak);
  if(defaultExperiments){
   NativeLocalExperiments.install(component,userId,loader);
  }
 }
}
