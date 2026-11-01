package com.duoaero.nativebase;
import android.app.Instrumentation;
import android.os.Bundle;
import java.lang.reflect.*;
import org.json.*;

/** Inspects only a synthetic local profile, never a real account or token. */
public final class UserModelProbe extends Instrumentation {
 public void onCreate(Bundle args){start();}
 public void onStart(){Bundle output=new Bundle();StringBuilder report=new StringBuilder();try{
  Object user=makeLocalUser(getTargetContext());
  report.append("Synthetic profile decoded: ").append(user.getClass().getName());
 }catch(Throwable error){if(error instanceof InvocationTargetException)error=error.getCause();report.append(android.util.Log.getStackTraceString(error));}
 output.putString("stream",report.toString());finish(-1,output);}
 public static Object makeLocalUser(android.content.Context context)throws Exception {
  return makeLocalUser(context,"DUOAERO_AEROSPACE_MIDTERM1");
 }
 public static Object makeLocalUser(android.content.Context context,String courseId)throws Exception {
  if(!courseId.equals("DUOAERO_AEROSPACE_MIDTERM1")&&!courseId.equals("MATH_BT")&&!courseId.equals("none"))throw new IllegalArgumentException("Unsupported diagnostic course variant");
  ClassLoader loader=context.getClassLoader();
  Object app=context.getApplicationContext();
  Object component=app.getClass().getMethod("generatedComponent").invoke(app);
  Object provider=component.getClass().getField("a0").get(component);
  Method get=provider.getClass().getMethod("get");get.setAccessible(true);
  Object factory=get.invoke(provider);Field jf=factory.getClass().getDeclaredField("json");jf.setAccessible(true);
  Object json=jf.get(factory);
  Object companion=Class.forName("com.duolingo.data.user.User",true,loader).getField("Companion").get(null);
  Object serializer=companion.getClass().getMethod("serializer").invoke(companion);
  Object descriptor=serializer.getClass().getMethod("getDescriptor").invoke(serializer);
  Class<?> dc=Class.forName("kotlinx.serialization.descriptors.SerialDescriptor",true,loader);
  JSONObject profile=(JSONObject)defaults(descriptor,dc,0);
  profile.put("id",1).put("username","aerospace-local-test").put("learningLanguage","en").put("fromLanguage","en");
  Object courseCompanion=Class.forName("com.duolingo.data.course.CourseProgressSummary",true,loader).getField("Companion").get(null);
  Object courseSerializer=courseCompanion.getClass().getMethod("serializer").invoke(courseCompanion);
  Object courseDescriptor=courseSerializer.getClass().getMethod("getDescriptor").invoke(courseSerializer);
  JSONObject course=(JSONObject)defaults(courseDescriptor,dc,0);
  course.put("id",courseId).put("title","Aerospace Technology").put("learningLanguage","en").put("fromLanguage","en");
  if(courseId.equals("MATH_BT"))course.put("subject","math").put("topic","math");
  if(courseId.equals("none")){profile.put("allCourses",new JSONArray());profile.put("currentCourseId",JSONObject.NULL);}
  else profile.put("allCourses",new JSONArray().put(course)).put("currentCourseId",courseId);
  Method decode=Class.forName("a8l",true,loader).getMethod("b",Class.forName("kotlinx.serialization.KSerializer",true,loader),String.class);
  String response=(String)Class.forName("com.duoaero.nativebase.NativeCourseBridge",true,loader).getMethod("setDiagnosticProfile",String.class).invoke(null,profile.toString());
  Object user=decode.invoke(json,serializer,response);
  Object streakCompanion=Class.forName("com.duolingo.data.streak.UserStreak",true,loader).getField("Companion").get(null);
  Object streakSerializer=streakCompanion.getClass().getMethod("serializer").invoke(streakCompanion);
  Object streak=decode.invoke(json,streakSerializer,response);
  if(streak.getClass().getField("a").get(streak)==null)throw new IllegalStateException("Local profile refresh loses known lifetime streak");
  return user;

 }
 static Object defaults(Object descriptor,Class<?> dc,int depth)throws Exception {
  if(depth>12)throw new IllegalStateException("Recursive descriptor");
  if((Boolean)dc.getMethod("b").invoke(descriptor))return JSONObject.NULL;
  String name=(String)dc.getMethod("h").invoke(descriptor);
  String kind=String.valueOf(dc.getMethod("getKind").invoke(descriptor));

  if(name.equals("kotlin.String")||name.equals("kotlin.Char"))return "";
  if(name.equals("kotlin.Boolean"))return false;
  if(name.matches("kotlin\\.(Byte|Short|Int|Long|Float|Double)")||name.equals("UserId"))return 0;
  if(kind.equals("LIST")||name.contains("PVector")||name.contains("PSet"))return new JSONArray();
  if(kind.equals("MAP")||name.contains("PMap"))return new JSONObject();
  int count=(Integer)dc.getMethod("d").invoke(descriptor);
  if(kind.equals("wf00"))return String.valueOf(dc.getMethod("e",int.class).invoke(descriptor,0)).toLowerCase(java.util.Locale.ROOT);
  JSONObject object=new JSONObject();
  for(int i=0;i<count;i++){
   if((Boolean)dc.getMethod("i",int.class).invoke(descriptor,i))continue;
   String field=(String)dc.getMethod("e",int.class).invoke(descriptor,i);
   Object child=dc.getMethod("g",int.class).invoke(descriptor,i);
   object.put(field,field.toLowerCase(java.util.Locale.ROOT).contains("timezone")?"UTC":defaults(child,dc,depth+1));
  }
  return object;
 }
}
