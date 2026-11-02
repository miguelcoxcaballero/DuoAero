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
   if(sessions.length()!=1200)throw new AssertionError("Expected 1200 supported question fixtures");
   for(int i=0;i<sessions.length();i++) {
    JSONObject input=sessions.getJSONObject(i);
    try {
     Object session=decode.invoke(json,serializer,input.toString());
     Object challenges=session.getClass().getField("b").get(session);
     int expected=input.getJSONArray("challenges").length();
     if(expected<1||((java.util.Collection<?>)challenges).size()!=expected)
      throw new AssertionError("A question step was dropped");
     passed++;
    }catch(Throwable error) {
     failed++;Throwable cause=error instanceof InvocationTargetException?error.getCause():error;
     if(failed<=12)report.append(input.getString("id")).append(": ").append(cause).append('\n');
    }
   }
   String[] types={"com.duolingo.data.subscription.max.SubscriptionFeatureGroup","com.duolingo.data.goals.models.GoalsProgressResponse","com.duolingo.data.energyrewards.EnergyRewardsTemplate","com.duolingo.core.energy.models.EnergyConfig"};
   String[] responses={"{\"subscriptionFeatures\":[]}","{}","{\"inLessonRewards\":[]}","{\"energy\":5,\"maxEnergy\":5,\"secondsPerEnergyUnit\":3600,\"secondsUntilNextEnergyUnit\":0,\"lastEnergyUnitRegeneratedDatetime\":0,\"regeneratedEnergyUnit\":0,\"hasFullEnergy\":true}"};
   for(int i=0;i<types.length;i++){
    Object c=Class.forName(types[i],true,loader).getField("Companion").get(null);
    Object model=decode.invoke(json,c.getClass().getMethod("serializer").invoke(c),responses[i]);
    if(!model.getClass().getName().equals(types[i]))throw new AssertionError("Invalid local optional-feature response");
   }
   // Check both boolean values through the actual legacy availability
   // converter: accepting JSON alone must not be confused with reading the
   // correct field or proving any end-of-lesson speedup.
   Class<?> availability=Class.forName("pp2",true,loader);
   Object converter=availability.getField("b").get(null);
   Class<?> reader=Class.forName("com.google.gson.stream.JsonReader",true,loader);
   Method parse=converter.getClass().getMethod("parseExpected",reader);
   for(boolean enforce:new boolean[]{false,true}){
    Object input=reader.getConstructor(java.io.Reader.class).newInstance(new StringReader("{\"enforce_offline\":"+enforce+"}"));
    Object decoded=parse.invoke(converter,input);
    if(availability.getField("a").getBoolean(decoded)!=enforce)throw new AssertionError("Availability boolean ignored");
   }
   Method route=Class.forName("com.duoaero.nativebase.NativeCourseBridge",true,loader).getDeclaredMethod("isLocalAvailability",String.class,String.class,String.class);
   route.setAccessible(true);
   if(!(Boolean)route.invoke(null,"GET","zombie.duolingo.com","/1/android.json")
      ||(Boolean)route.invoke(null,"POST","zombie.duolingo.com","/1/android.json")
      ||(Boolean)route.invoke(null,"GET","example.com","/1/android.json")
      ||(Boolean)route.invoke(null,"GET","zombie.duolingo.com","/1/android.json/other"))
    throw new AssertionError("Availability routing is not scoped to the original check");
   report.append("Original offline-availability response reads both boolean values.\n");
   report.append("Original optional-feature response models decoded.\n");
  }catch(Throwable error){failed++;report.append(android.util.Log.getStackTraceString(error));}
  report.append("Native model decoding: ").append(passed).append(" passed, ").append(failed).append(" failed.\n");
  report.append("Does not verify rendering, grading, progression, or layout of gap/order questions.\n");
  output.putString("stream",report.toString());output.putInt("passed",passed);output.putInt("failed",failed);
  finish(failed==0?-1:0,output);
 }
}
