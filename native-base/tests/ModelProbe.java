package com.duoaero.nativebase;
import android.app.Instrumentation;
import android.os.Bundle;
import java.lang.reflect.*;
import java.io.*;
import org.json.*;

/** Verifies actual original deserialization, not a mock implementation. */
public final class ModelProbe extends Instrumentation {
 public void onCreate(Bundle args) {
  try{Class.forName("com.duoaero.nativebase.NativeCourseBridge",true,getTargetContext().getClassLoader()).getField("localOnly").setBoolean(null,true);}
  catch(Exception error){throw new IllegalStateException("Cannot isolate model diagnostic",error);}
  start();
 }
 public void onStart() {
  Bundle output=new Bundle(); StringBuilder report=new StringBuilder(); int passed=0,failed=0;
  try {
   ClassLoader loader=getTargetContext().getClassLoader();
   Object app=getTargetContext().getApplicationContext();
   Object component=app.getClass().getMethod("generatedComponent").invoke(app);
   Object provider=component.getClass().getField("a0").get(component);
   Method get=provider.getClass().getMethod("get"); get.setAccessible(true);
   Object factory=get.invoke(provider);
   Field field=factory.getClass().getDeclaredField("json"); field.setAccessible(true);
   Object json=field.get(factory);
   Class<?> jsonClass=Class.forName("a8l",true,loader);
   Object companion=Class.forName("com.duolingo.core.session.Session",true,loader).getField("Companion").get(null);
   Object serializer=companion.getClass().getMethod("serializer").invoke(companion);
   Method decode=jsonClass.getMethod("b",Class.forName("kotlinx.serialization.KSerializer",true,loader),String.class);
   ByteArrayOutputStream bytes=new ByteArrayOutputStream();
   try(InputStream stream=getContext().getAssets().open("native_sessions.json")) {
    byte[] buffer=new byte[8192];int n;while((n=stream.read(buffer))!=-1)bytes.write(buffer,0,n);
   }
   JSONArray sessions=new JSONArray(bytes.toString("UTF-8"));
   if(sessions.length()!=1195)throw new AssertionError("Expected 1195 supported question fixtures");
   for(int i=0;i<sessions.length();i++) {
    JSONObject input=sessions.getJSONObject(i);
    try {
     Object session=decode.invoke(json,serializer,input.toString());
     Object challenges=session.getClass().getField("b").get(session);
     if(((java.util.Collection<?>)challenges).size()!=1)throw new AssertionError("Question was dropped");
     passed++;
    }catch(Throwable error) {
     failed++;Throwable cause=error instanceof InvocationTargetException?error.getCause():error;
     if(failed<=12)report.append(input.getString("id")).append(": ").append(cause).append('\n');
    }
   }
  }catch(Throwable error){failed++;report.append(android.util.Log.getStackTraceString(error));}
  report.append("Native model decoding: ").append(passed).append(" passed, ").append(failed).append(" failed.\n");
  report.append("Does not verify rendering, grading, progression, or the five unsupported gap/order questions.\n");
  output.putString("stream",report.toString());output.putInt("passed",passed);output.putInt("failed",failed);
  finish(failed==0?-1:0,output);
 }
}
