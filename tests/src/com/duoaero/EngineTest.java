package com.duoaero;
import android.app.Instrumentation;
import android.content.Context;
import android.os.Bundle;
import org.json.*;
import java.util.*;
public class EngineTest extends Instrumentation {
 int assertions=0;
 void require(boolean ok,String msg){assertions++;if(!ok)throw new AssertionError(msg);}
 Object correct(JSONObject q)throws Exception{if(q.getString("type").equals("matching")){JSONArray a=new JSONArray();for(int i=0;i<q.getJSONArray("pairs").length();i++)a.put(i);return a;}if(q.getString("type").equals("gap"))return q.getJSONArray("answer").getString(0);return q.get("answer");}
 public void onCreate(Bundle args){super.onCreate(args);start();}
 public void onStart(){Bundle result=new Bundle();Context c=getTargetContext();String file="test-progress.json";c.deleteFile(file);try{
  Engine e=new Engine(c,file);require(e.bank.length()==1200,"bank size");int[] levels=new int[4];Set<String> types=new HashSet<>();
  for(JSONObject q:e.questions.values()){levels[q.getInt("difficulty")]++;types.add(q.getString("type"));require(Engine.grade(q,correct(q)),"canonical answer "+q.getString("id"));}
  require(levels[1]==400&&levels[2]==400&&levels[3]==400,"difficulty quotas");require(types.size()==5,"all question types");
  Set<String> assigned=new HashSet<>();int lessons=0;for(int i=0;i<e.nodes.length();i++){JSONArray ls=e.nodes.getJSONObject(i).getJSONArray("lessons");require(ls.length()>=1&&ls.length()<=3,"node lesson counts");for(int j=0;j<ls.length();j++){JSONObject l=ls.getJSONObject(j);JSONArray ids=l.getJSONArray("ids");require(ids.length()>=10&&ids.length()<=20,"lesson size");require(!e.done(l),"no invented completion");for(String id:e.strings(ids))require(assigned.add(id),"unique lesson assignment");lessons++;}}
  require(assigned.equals(e.questions.keySet()),"all questions assigned");
  JSONObject lesson=e.nodes.getJSONObject(0).getJSONArray("lessons").getJSONObject(0);String first=lesson.getJSONArray("ids").getString(0);JSONObject q=e.questions.get(first);
  e.start(e.strings(lesson.getJSONArray("ids")),"test","pathlesson",lesson.getString("id"));e.select((q.getInt("answer")+1)%4);e.check();require(e.mistakes().contains(first),"mistake retained");int seen=e.records().getJSONObject(first).getInt("seen");e.check();require(e.records().getJSONObject(first).getInt("seen")==seen,"double grade blocked");e.advance();
  e=new Engine(c,file);require(e.mistakes().contains(first)&&e.session().getInt("cursor")==1,"restart persistence");require(!e.done(lesson),"partial lesson stays grey");
  while(!e.ended()){e.select(correct(e.current()));e.check();e.advance();}
  require(e.done(lesson),"completed lesson full green");require(e.mistakes().isEmpty(),"retry clears mistake");e=new Engine(c,file);require(e.done(lesson),"completion persisted");e.leave();
  JSONObject other=e.nodes.getJSONObject(1).getJSONArray("lessons").getJSONObject(0);e.start(e.strings(other.getJSONArray("ids")),"practice","practice","");while(!e.ended()){e.select(correct(e.current()));e.check();e.advance();}require(!e.done(other),"practice cannot complete path");
  JSONObject multi=null;for(JSONObject item:e.questions.values())if(item.getString("type").equals("multi")){multi=item;break;}JSONArray duplicate=new JSONArray();for(int i=0;i<multi.getJSONArray("answer").length();i++)duplicate.put(99);require(!Engine.grade(multi,duplicate),"invalid multi rejected");
  android.content.Intent intent=new android.content.Intent(c,MainActivity.class).addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK);
  MainActivity activity=(MainActivity)startActivitySync(intent);final Throwable[] uiFailure={null};
  java.util.concurrent.CountDownLatch runtimeReady=new java.util.concurrent.CountDownLatch(1);
  final String[] runtimeResult={null};
  for(int wait=0;wait<100&&!activity.cloud.ready;wait++)Thread.sleep(100);
  runOnMainSync(()->activity.cloud.web.evaluateJavascript("JSON.stringify({auth:typeof DuoAuth.signIn,sync:typeof DuoSync.sync,client:window.DUOAERO_ANDROID_CLIENT_ID})",value->{runtimeResult[0]=value;runtimeReady.countDown();}));
  require(runtimeReady.await(10,java.util.concurrent.TimeUnit.SECONDS),"Google runtime responds");
  require(runtimeResult[0].contains("function")&&runtimeResult[0].contains("unt269845"),"Google and Drive runtime loaded with registered Android client");
  require(!GoogleProgress.accountKey("Aa").equals(GoogleProgress.accountKey("BB")),"account files resist Java hash collisions");
  require(c.getPackageManager().resolveContentProvider("com.duoaero.update-provider",0).name.equals("com.inhouse.services.updater.UpdateFileProvider"),"canonical updater provider registered");
  runOnMainSync(()->{JSONObject saved=activity.engine.state;try{
   require(activity.button("Test",true,()->{}).getClass().getName().equals("com.duolingo.core.design.juicy.ui.JuicyButton"),"original compiled button");
   require(activity.text("Test",16,false).getClass().getName().equals("com.duolingo.core.design.juicy.ui.JuicyTextView"),"original compiled typography");
   activity.engine.state=new JSONObject(saved.toString());activity.engine.state.put("completedLessons",new JSONObject());
   Set<String> rendered=new HashSet<>();for(JSONObject item:activity.engine.questions.values())if(rendered.add(item.getString("type"))){
    activity.engine.start(Collections.singletonList(item.getString("id")),"UI test","practice","");activity.quiz();require(activity.body.getChildCount()>3,"question controls rendered");activity.engine.select(correct(item));activity.engine.check();activity.quiz();require(activity.footer.getChildCount()>=3,"feedback rendered");activity.engine.advance();activity.quiz();
   }
   activity.engine.leave();for(String tab:new String[]{"learn","review","bank","settings"}){activity.screen=tab;activity.home();require(activity.body.getChildCount()>0,"tab rendered "+tab);}
   for(int i=0;i<activity.engine.nodes.length();i++){
    JSONObject node=activity.engine.nodes.getJSONObject(i);MainActivity.RingView ring=activity.new RingView(node);ring.layout(0,0,124,124);android.graphics.Bitmap bitmap=android.graphics.Bitmap.createBitmap(124,124,android.graphics.Bitmap.Config.ARGB_8888);android.graphics.Canvas canvas=new android.graphics.Canvas(bitmap);canvas.drawColor(android.graphics.Color.WHITE);ring.draw(canvas);
    require(bitmap.getPixel(62,11)==(node.getJSONArray("lessons").length()==1?activity.GREY:android.graphics.Color.WHITE),"single full ring / multiple gaps");bitmap.recycle();
   }
  }catch(Throwable t){uiFailure[0]=t;}finally{activity.engine.state=saved;try{activity.engine.save();}catch(Exception ignored){}activity.finish();}});
  if(uiFailure[0]!=null)throw new AssertionError("Native UI test",uiFailure[0]);
  java.io.File updateProbe=new java.io.File(c.getCacheDir(),"updates/provider-test.apk");updateProbe.getParentFile().mkdirs();
  try(java.io.FileOutputStream stream=new java.io.FileOutputStream(updateProbe)){stream.write(42);}
  Class<?> provider=Class.forName("com.inhouse.shadow.androidx.core.content.FileProvider",true,c.getClassLoader());
  android.net.Uri updateUri=(android.net.Uri)provider.getMethod("getUriForFile",Context.class,String.class,java.io.File.class).invoke(null,c,"com.duoaero.update-provider",updateProbe);
  try(java.io.InputStream stream=c.getContentResolver().openInputStream(updateUri)){require(stream.read()==42,"canonical updater provider reads verified cache directory");}finally{updateProbe.delete();}
  android.app.Activity updater=startActivitySync(new android.content.Intent().setClassName(c,"com.inhouse.services.updater.UpdateActivity").putExtra("settings",true).addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK));
  require(updater!=null,"canonical updater Activity starts with Kotlin installer");runOnMainSync(()->updater.finish());
  result.putString("stream","PASS: "+assertions+" assertions; "+lessons+" lessons; grading, retries, persistence and completion.\n");finish(-1,result);
 }catch(Throwable t){result.putString("stream","FAIL: "+t.toString()+"\n"+android.util.Log.getStackTraceString(t));finish(0,result);}finally{c.deleteFile(file);}}
}
