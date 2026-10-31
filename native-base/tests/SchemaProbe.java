package com.duoaero.nativebase;
import android.app.Instrumentation;import android.os.Bundle;import java.lang.reflect.*;import org.json.*;
public class SchemaProbe extends Instrumentation {
 public void onCreate(Bundle args){start();}
 public void onStart(){Bundle out=new Bundle();StringBuilder report=new StringBuilder();try{
 ClassLoader cl=getTargetContext().getClassLoader();Class<?> jsonClass=Class.forName("a8l",true,cl);Object json=jsonClass.getField("d").get(null);Object app=getTargetContext().getApplicationContext();Object component=app.getClass().getMethod("generatedComponent").invoke(app);report.append("Component "+component.getClass().getName()+"\n");for(Method m:component.getClass().getDeclaredMethods()){if(m.getParameterTypes().length==0&&jsonClass.isAssignableFrom(m.getReturnType())){m.setAccessible(true);json=m.invoke(component);report.append("Using original Json provider "+m.getName()+"\n");break;}}Object provider=component.getClass().getField("a0").get(component);Method get=provider.getClass().getMethod("get");get.setAccessible(true);Object factory=get.invoke(provider);Field jf=factory.getClass().getDeclaredField("json");jf.setAccessible(true);json=jf.get(factory);Class<?> sessionClass=Class.forName("com.duolingo.core.session.Session",true,cl);Object companion=sessionClass.getField("Companion").get(null);Object serializer=companion.getClass().getMethod("serializer").invoke(companion);Method decode=jsonClass.getMethod("b",Class.forName("kotlinx.serialization.KSerializer",true,cl),String.class);
 String[] types={"assist","select","readComprehension","translate","match","completeReverseTranslation"};
 for(String type:types){try{
 JSONObject challenge=new JSONObject().put("id","aero-probe").put("type",type).put("prompt","Which force opposes weight?").put("question","Which force opposes weight?").put("choices",new JSONArray("[{\"text\":\"Lift\"},{\"text\":\"Drag\"},{\"text\":\"Thrust\"},{\"text\":\"Weight\"}]")).put("options",new JSONArray("[{\"text\":\"Lift\"},{\"text\":\"Drag\"},{\"text\":\"Thrust\"},{\"text\":\"Weight\"}]")).put("correctIndex",0).put("correctIndices",new JSONArray("[0]")).put("correctSolutions",new JSONArray("[\"Lift\"]")).put("sourceLanguage","en").put("targetLanguage","en");
 challenge.put("tokens",new JSONArray());
 if(type.equals("translate"))challenge.remove("choices");
 if(type.equals("readComprehension"))challenge.put("passage","In steady level flight, lift balances weight.").put("choices",new JSONArray("[\"Lift\",\"Drag\",\"Thrust\",\"Weight\"]"));
 if(type.equals("completeReverseTranslation"))challenge.put("displayTokens",new JSONArray("[{\"text\":\"Lift\",\"isBlank\":true},{\"text\":\"balances weight\",\"isBlank\":false}]"));
 if(type.equals("translate")||type.equals("select")){Object sc=Class.forName("com.duolingo.core.challenges.ChallengeSurrogate",true,cl).getField("Companion").get(null);Object ss=sc.getClass().getMethod("serializer").invoke(sc);Object sr=decode.invoke(json,ss,challenge.toString());for(String field:new String[]{"M1","W1","p","b2"})report.append(type+" "+field+"="+sr.getClass().getField(field).get(sr)+"\n");}
 JSONObject session=new JSONObject().put("id","aero-probe").put("type","GLOBAL_PRACTICE").put("fromLanguage","en").put("learningLanguage","en").put("challenges",new JSONArray().put(challenge));
 Object result=decode.invoke(json,serializer,session.toString());report.append(type+": PASS "+result.getClass().getName()+"\n");
 }catch(Throwable e){Throwable cause=e instanceof InvocationTargetException?e.getCause():e;report.append(type+": "+android.util.Log.getStackTraceString(cause)+"\n");}}
 }catch(Throwable e){report.append(android.util.Log.getStackTraceString(e));}out.putString("stream",report.toString());finish(-1,out);}
}
