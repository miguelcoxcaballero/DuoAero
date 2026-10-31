package com.duoaero.nativebase;
import android.app.Application;
import android.util.Log;
import org.json.*;
import java.lang.reflect.*;
import java.io.*;
import java.util.*;

/** Development-only schema probe. Never reads or records authentication headers. */
public final class NativeCourseBridge {
 public static volatile boolean localOnly = false;
 public static void install(Object builder) {
  try {
   ClassLoader loader=builder.getClass().getClassLoader();
   Class<?> interceptor=Class.forName("okhttp3.Interceptor",true,loader);
   List list=(List)builder.getClass().getMethod("interceptors").invoke(builder);
   for(Object value:list)if(Proxy.isProxyClass(value.getClass())&&Proxy.getInvocationHandler(value) instanceof Probe)return;
   list.add(0,Proxy.newProxyInstance(loader,new Class[]{interceptor},new Probe()));
  }catch(Exception e){Log.e("DuoAeroNative","Cannot bind course bridge",e);}
 }
 static final class Probe implements InvocationHandler {
  public Object invoke(Object proxy,Method method,Object[] args)throws Throwable {
   if(method.getName().equals("toString"))return "DuoAero native course bridge";
   if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
   if(method.getName().equals("equals"))return proxy==args[0];
   Object chain=args[0],request=call(chain,"request");
   if(localOnly)return offlineResponse(request);
   Object response;
   try{response=chain.getClass().getMethod("proceed",request.getClass()).invoke(chain,request);}catch(InvocationTargetException e){throw e.getCause();}
   try{
    Object url=call(request,"url");String path=(String)call(url,"encodedPath");
    String host=(String)call(url,"host");
    if(host.endsWith("duolingo.com")&&(path.contains("sessions")||path.contains("courses")||path.contains("path"))){
     Object body=response.getClass().getMethod("peekBody",long.class).invoke(response,8L*1024*1024);
     String json=(String)call(body,"string");JSONObject data=new JSONObject(json);
     JSONObject selected=new JSONObject();
     for(String key:new String[]{"challenges","adaptiveChallenges","interleavedChallenges","path","sections","units","courses","currentCourse","learningLanguage","fromLanguage","type","sessionType","id"})if(data.has(key))selected.put(key,data.get(key));
     if(selected.length()>0){
      Application app=(Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
      File folder=new File(app.getFilesDir(),"native-course-schemas");folder.mkdirs();
      File file=new File(folder,Integer.toHexString(path.hashCode())+".json");
      try(FileOutputStream out=new FileOutputStream(file)){out.write(selected.toString(2).getBytes("UTF-8"));}
      Log.i("DuoAeroNative","Course schema captured: "+file.getName()+" keys="+selected.names());
     }
    }
   }catch(Exception e){Log.d("DuoAeroNative","No course schema",e);}
   return response;
  }
 }
 static Object offlineResponse(Object request)throws Exception {
  ClassLoader loader=request.getClass().getClassLoader();
  Class<?> builderClass=Class.forName("okhttp3.Response$Builder",true,loader);
  Class<?> protocolClass=Class.forName("okhttp3.Protocol",true,loader);
  Class<?> bodyClass=Class.forName("okhttp3.ResponseBody",true,loader);
  Class<?> mediaClass=Class.forName("okhttp3.MediaType",true,loader);
  Object builder=builderClass.getConstructor().newInstance();
  builderClass.getMethod("request",request.getClass()).invoke(builder,request);
  builderClass.getMethod("protocol",protocolClass).invoke(builder,protocolClass.getField("HTTP_1_1").get(null));
  builderClass.getMethod("code",int.class).invoke(builder,503);
  builderClass.getMethod("message",String.class).invoke(builder,"Offline native-course diagnostic");
  Object body=bodyClass.getMethod("create",String.class,mediaClass).invoke(null,"{}",null);
  builderClass.getMethod("body",bodyClass).invoke(builder,body);
  return builderClass.getMethod("build").invoke(builder);
 }
 static Object call(Object value,String name)throws Exception{return value.getClass().getMethod(name).invoke(value);}
}
