package com.duoaero.nativebase;

import android.content.Context;
import java.lang.reflect.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicReference;
import org.json.*;

/** Diagnostic native cache input. Model decoding is not path/UI acceptance. */
final class LocalCourseCache {
 static String install(Context context,Object viewModel,boolean fullPath)throws Exception {
  ClassLoader loader=context.getClassLoader();
  Object app=context.getApplicationContext();
  Object component=app.getClass().getMethod("generatedComponent").invoke(app);
  Object provider=field(component,"a0");
  Object factory=Class.forName("ymw",true,loader).getMethod("get").invoke(provider);
  Field jsonField=factory.getClass().getDeclaredField("json");jsonField.setAccessible(true);
  Object json=jsonField.get(factory);
  Object summarySerializer=serializer(loader,"com.duolingo.data.course.CourseProgressSummary");
  Object descriptor=summarySerializer.getClass().getMethod("getDescriptor").invoke(summarySerializer);
  JSONObject course=(JSONObject)UserModelProbe.defaults(descriptor,Class.forName("kotlinx.serialization.descriptors.SerialDescriptor",true,loader),0);
  String sectionId="DUOAERO_DIAGNOSTIC_EMPTY";
  course.put("id","MATH_BT").put("title","Aerospace Technology")
   .put("subject","math").put("topic","math")
   .put("learningLanguage","en").put("fromLanguage","en")
   .put("activePathSectionId",sectionId).put("pathSectionsSummary",new JSONArray());
  JSONObject sectionJson=new JSONObject().put("id",sectionId).put("index",0).put("units",new JSONArray());
  if(fullPath){
   course=assetJson(context,"duoaero/course/path-info.json");
   sectionJson=assetJson(context,"duoaero/course/section.json");
   sectionId=sectionJson.getString("id");
  }
  Method decode=Class.forName("a8l",true,loader).getMethod("b",Class.forName("kotlinx.serialization.KSerializer",true,loader),String.class);
  Object info=decode.invoke(json,serializer(loader,"com.duolingo.data.path.common.CoursePathInfo"),course.toString());
  if(!info.getClass().getName().equals("mt8"))throw new IllegalStateException("Expected original Math CoursePathInfo; got "+info.getClass().getName());
  Object section=decode.invoke(json,serializer(loader,"com.duolingo.data.path.common.CoursePathSection"),sectionJson.toString());
  Object courseRepository=field(field(viewModel,"j"),"f");
  Object cache=field(courseRepository,"m");
  Class<?> userType=Class.forName("com.duolingo.core.data.model.UserId",true,loader);
  Class<?> courseType=Class.forName("com.duolingo.core.data.model.CourseId",true,loader);
  Object userId=userType.getConstructor(long.class).newInstance(1L);
  Object courseId=courseType.getConstructor(String.class).newInstance("MATH_BT");
  Object infoFactory=field(courseRepository,"c"),sectionFactory=field(courseRepository,"d");
  Object sectionResource=sectionFactory.getClass().getMethod("a",userType,courseType,String.class,String.class).invoke(sectionFactory,userId,courseId,sectionId,"en");
  Object infoResource=infoFactory.getClass().getMethod("a",userType,courseType,String.class).invoke(infoFactory,userId,courseId,"en");
  // Publish the section first so the original course observer can resolve it.
  write(loader,cache,sectionResource,section);
  write(loader,cache,infoResource,info);
  return "Native cache input: original Math CoursePathInfo and CoursePathSection with "+sectionJson.getJSONArray("units").length()+" units. This does not prove home/path rendering or lesson navigation.\n";
 }
 private static JSONObject assetJson(Context context,String name)throws Exception {
  try(java.io.InputStream stream=context.getAssets().open(name)){
   java.io.ByteArrayOutputStream bytes=new java.io.ByteArrayOutputStream();byte[] buffer=new byte[8192];int n;
   while((n=stream.read(buffer))!=-1)bytes.write(buffer,0,n);
   return new JSONObject(new String(bytes.toByteArray(),"UTF-8"));
  }
 }
 private static Object field(Object owner,String name)throws Exception{return owner.getClass().getField(name).get(owner);}
 static Object serializer(ClassLoader loader,String name)throws Exception {
  Object companion=Class.forName(name,true,loader).getField("Companion").get(null);
  return companion.getClass().getMethod("serializer").invoke(companion);
 }
 static void write(ClassLoader loader,Object cache,Object resource,Object model)throws Exception {
  Object operation=Class.forName("nrx",true,loader).getMethod("t",Object.class).invoke(resource,model);
  apply(loader,cache,operation);
 }
 static void apply(ClassLoader loader,Object cache,Object operation)throws Exception {
  Object completion=cache.getClass().getMethod("x0",Class.forName("e490",true,loader)).invoke(cache,operation);
  Class<?> observerType=Class.forName("fp7",true,loader);
  CountDownLatch done=new CountDownLatch(1);
  AtomicReference<Throwable> failure=new AtomicReference<>();
  AtomicReference<Object> subscription=new AtomicReference<>();
  Object observer=Proxy.newProxyInstance(loader,new Class[]{observerType},(proxy,method,args)->{
   switch(method.getName()){
    case "onSubscribe":subscription.set(args[0]);return null;
    case "onComplete":done.countDown();return null;
    case "onError":failure.set((Throwable)args[0]);done.countDown();return null;
    case "toString":return "Synthetic native course cache writer";
    case "hashCode":return System.identityHashCode(proxy);
    case "equals":return proxy==args[0];
    default:throw new UnsupportedOperationException(method.getName());
   }
  });
  try{
   Class.forName("yn7",true,loader).getMethod("a",observerType).invoke(completion,observer);
   if(!done.await(20,TimeUnit.SECONDS))throw new IllegalStateException("Native cache write timed out");
   if(failure.get()!=null)throw new IllegalStateException("Native cache write failed",failure.get());
  }finally{
   Object disposable=subscription.get();
   if(disposable!=null)Class.forName("arb",true,loader).getMethod("dispose").invoke(disposable);
  }
 }
}
