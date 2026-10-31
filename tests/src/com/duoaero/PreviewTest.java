package com.duoaero;
import android.app.Instrumentation;import android.os.Bundle;import android.content.Intent;
public class PreviewTest extends Instrumentation {
 String screen="learn",mode="light";
 public void onCreate(Bundle args){if(args!=null){screen=args.getString("screen","learn");mode=args.getString("mode","light");}start();}
 public void onStart(){getTargetContext().getSharedPreferences("appearance",0).edit().putString("mode",mode).commit();MainActivity a=(MainActivity)startActivitySync(new Intent().setClassName(getTargetContext(),"com.duoaero.MainActivity").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));runOnMainSync(()->{try{a.engine=new Engine(a,"preview-only.json");a.screen=screen;if(screen.equals("complete")){org.json.JSONObject q=a.engine.questions.values().iterator().next();a.engine.start(java.util.Collections.singletonList(q.getString("id")),"Preview","practice","");a.engine.select(q.get("answer"));a.engine.check();a.engine.advance();a.quiz();}else a.home();}catch(Exception e){throw new RuntimeException(e);}});try{Thread.sleep(600000);}catch(Exception ignored){}finish(-1,new Bundle());}
}