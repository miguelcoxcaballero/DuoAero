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
 public static volatile boolean captureNativeFlows = false;
 // A locally enrolled Aerospace learner must be able to open the original
 // home with zero XP. Enrollment is set only after both native path writes.
 public static volatile boolean localCourseInstalled = false;
 public static volatile boolean serveLocalCourse = false;
 private static volatile String diagnosticProfile = null;
 public static void setDiagnosticProfile(String value)throws JSONException {
  JSONObject user=new JSONObject(value);
  if(user.getLong("id")!=1||!"aerospace-local-test".equals(user.getString("username")))throw new IllegalArgumentException("Only the isolated test identity is supported");
  diagnosticProfile=value;
 }
 public static boolean hasLocalCourse(){return localOnly && localCourseInstalled;}
 /** Keep the native figure and cards, bounding only the prompt's scroll area. */
 public static Object scrollPrompt(Object figure,Object modifier,Object composer){
  if(!hasLocalCourse()||figure==null||!figure.getClass().getName().equals("com.duolingo.core.math.models.figure.MathFigureUiState$LatexString"))return modifier;
  try{
   ClassLoader loader=figure.getClass().getClassLoader();
   Class<?> compose=Class.forName("cuh",true,loader);
   String prompt=(String)figure.getClass().getField("a").get(figure);
   compose.getMethod("f0",int.class).invoke(composer,0x44554145^prompt.hashCode());
   try{
    Application app=(Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
    float maximum=Math.max(120f,Math.min(240f,app.getResources().getConfiguration().screenHeightDp*0.30f));
    Class<?> mod=Class.forName("z5q",true,loader),state=Class.forName("qxz",true,loader),scroll=Class.forName("kqp",true,loader);
    Object bounded=Class.forName("androidx.compose.foundation.layout.b",true,loader).getMethod("i",mod,float.class,float.class).invoke(null,modifier,Float.NaN,maximum);
    Object position=scroll.getMethod("R",int.class,Class.forName("o18",true,loader),int.class).invoke(null,0,composer,0);
    return scroll.getMethod("d0",mod,state,boolean.class,int.class).invoke(null,bounded,position,true,0);
   }finally{compose.getMethod("q",boolean.class).invoke(composer,false);}
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot bind original prompt scrolling",error);}
 }
 private static final Map<String,Object> namedFlows=new LinkedHashMap<>();
 public static synchronized void recordFlow(Object flow,String name){
  if(!localOnly||!captureNativeFlows||flow==null||name==null||!name.matches("[A-Za-z][A-Za-z0-9_.-]{0,100}"))return;
  if(namedFlows.containsKey(name)||namedFlows.size()<256)namedFlows.put(name,flow);
 }
 public static synchronized Map<String,Object> diagnosticFlows(){return new LinkedHashMap<>(namedFlows);}

 public static volatile boolean captureLocalRequests = false;
 private static final Map<String,Integer> localRequests = new LinkedHashMap<>();
 public static synchronized String diagnosticRequests(){return localRequests.toString();}
 private static synchronized void recordLocal(Object request)throws Exception {
  if(!captureLocalRequests)return;
  Object url=call(request,"url");String path=(String)call(url,"encodedPath");
  // Synthetic-user diagnostics only. Never collect query strings, headers,
  // bodies, auth endpoints or arbitrary external-service URLs.
  if(!path.matches("^/(?:[0-9-]+/)?(?:sessions(?:/.*)?|users/1(?:/(?:courses|sessions|path)(?:/.*)?)?|config)$"))return;
  String key=call(request,"method")+" "+path.replace("/users/1","/users/{synthetic}");
  if(localRequests.containsKey(key))localRequests.put(key,localRequests.get(key)+1);
  else if(localRequests.size()<64)localRequests.put(key,1);
 }
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
   if(localOnly){try{recordLocal(request);}catch(Exception ignored){}return offlineResponse(request);}
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
  int code=503;String payload="{}";
  if(serveLocalCourse&&hasLocalCourse()){
   Object url=call(request,"url");String path=(String)call(url,"encodedPath"),method=(String)call(request,"method");
   Application app=(Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
   if(method.equals("GET")&&path.matches("/(?:[0-9-]+/)?config")){code=200;}
   else if(method.equals("GET")&&path.matches("/(?:[0-9-]+/)?users/1")&&diagnosticProfile!=null){code=200;payload=diagnosticProfile;}
   else if(method.equals("GET")&&path.matches("/(?:[0-9-]+/)?users/1/courses/MATH_BT")){code=200;payload=asset(app,"duoaero/course/path-info.json");}
   else if(method.equals("GET")&&path.matches("/(?:[0-9-]+/)?users/1/courses/MATH_BT/sections/DUOAERO_MIDTERM1")){code=200;payload=asset(app,"duoaero/course/section.json");}
   else if(method.equals("POST")&&path.matches("/(?:[0-9-]+/)?sessions")){
    JSONObject input=requestJson(request);JSONObject index=new JSONObject(asset(app,"duoaero/course/session-catalog.json"));
    String selected=null;JSONObject metadata=input.optJSONObject("metadata");
    if(metadata!=null&&index.has(metadata.optString("id")))selected=metadata.getString("id");
    if(selected==null){
     String skill=input.optString("skillId");int position=input.optInt("levelSessionIndex",0);
     for(Iterator<String> keys=index.keys();keys.hasNext();){String key=keys.next();JSONObject candidate=index.getJSONObject(key);
      if(candidate.getString("skillId").equals(skill)&&candidate.getInt("levelSessionIndex")==position){selected=key;break;}}
    }
    if(selected!=null){payload=index.getJSONObject(selected).toString();code=200;Log.i("DuoAeroNative","Local original session selected: "+selected);}
    else{code=422;Log.e("DuoAeroNative","No supported local session for original request; field names="+input.names());}
   }
  }
  return jsonResponse(request,code,payload);
 }
 static String asset(Application app,String path)throws IOException {
  ByteArrayOutputStream bytes=new ByteArrayOutputStream();
  try(InputStream stream=app.getAssets().open(path)){byte[] buffer=new byte[8192];int n;while((n=stream.read(buffer))!=-1)bytes.write(buffer,0,n);}
  return bytes.toString("UTF-8");
 }
 static JSONObject requestJson(Object request)throws Exception {
  Object body=call(request,"body");if(body==null)throw new IllegalArgumentException("Missing local session request");
  ClassLoader loader=request.getClass().getClassLoader();
  Object buffer=Class.forName("bo3",true,loader).getConstructor().newInstance();
  Class.forName("okhttp3.RequestBody",true,loader).getMethod("writeTo",Class.forName("mo3",true,loader)).invoke(body,buffer);
  byte[] bytes=(byte[])buffer.getClass().getMethod("Q0").invoke(buffer);
  if(bytes.length>1048576)throw new IllegalArgumentException("Local session request too large");
  // Parsed only for isolated session routing; never logged or exported.
  return new JSONObject(new String(bytes,"UTF-8"));
 }
 static Object jsonResponse(Object request,int code,String payload)throws Exception {
  ClassLoader loader=request.getClass().getClassLoader();
  Class<?> builderClass=Class.forName("okhttp3.Response$Builder",true,loader);
  Class<?> protocolClass=Class.forName("okhttp3.Protocol",true,loader);
  Class<?> bodyClass=Class.forName("okhttp3.ResponseBody",true,loader);
  Class<?> mediaClass=Class.forName("okhttp3.MediaType",true,loader);
  Object builder=builderClass.getConstructor().newInstance();
  builderClass.getMethod("request",request.getClass()).invoke(builder,request);
  builderClass.getMethod("protocol",protocolClass).invoke(builder,protocolClass.getField("HTTP_1_1").get(null));
  builderClass.getMethod("code",int.class).invoke(builder,code);
  builderClass.getMethod("message",String.class).invoke(builder,"Offline native-course diagnostic");
  Object body=bodyClass.getMethod("create",String.class,mediaClass).invoke(null,payload,null);
  builderClass.getMethod("body",bodyClass).invoke(builder,body);
  return builderClass.getMethod("build").invoke(builder);
 }
 static Object call(Object value,String name)throws Exception{return value.getClass().getMethod(name).invoke(value);}
}
