package com.duoaero.nativebase;

import android.app.*;
import android.os.Bundle;
import android.view.*;
import android.widget.*;
import java.lang.reflect.Method;
import java.util.WeakHashMap;

/** Render the formula-only error feedback with the app's original math view. */
final class NativeFormulaFeedback {
 private NativeFormulaFeedback(){}
 private static boolean installed;
 static synchronized void install(Application app){
  if(installed)return;installed=true;
  app.registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
   final WeakHashMap<Activity,Overlay> overlays=new WeakHashMap<>();
   public void onActivityResumed(Activity activity){
    if(!activity.getClass().getName().endsWith("SessionActivity")||overlays.containsKey(activity))return;
    Overlay overlay=new Overlay(activity);overlays.put(activity,overlay);
    activity.getWindow().getDecorView().getViewTreeObserver().addOnGlobalLayoutListener(overlay);
   }
   public void onActivityDestroyed(Activity activity){
    Overlay overlay=overlays.remove(activity);if(overlay!=null)overlay.close();
   }
   public void onActivityCreated(Activity a,Bundle b){} public void onActivityStarted(Activity a){}
   public void onActivityPaused(Activity a){} public void onActivityStopped(Activity a){}
   public void onActivitySaveInstanceState(Activity a,Bundle b){}
  });
 }
 private static final class Overlay implements ViewTreeObserver.OnGlobalLayoutListener {
  final Activity activity;final FrameLayout root;View math;TextView source;String formula;
  Overlay(Activity activity){this.activity=activity;this.root=activity.findViewById(android.R.id.content);}
  public void onGlobalLayout(){
   try{
    TextView found=find(root);
    if(found==null){clear();return;}
    String text=found.getText().toString();
    if(source!=found||!text.equals(formula)){
     clear();source=found;formula=text;
     Class<?> type=Class.forName("com.duolingo.feature.math.ui.figure.MathLatexView",true,activity.getClassLoader());
     math=(View)type.getConstructor(android.content.Context.class).newInstance(activity);
     type.getMethod("setLatexString",String.class).invoke(math,text);
     type.getMethod("setFontSizeDp",float.class).invoke(math,24f);
     type.getMethod("setGlobalColor",Integer.class).invoke(math,found.getCurrentTextColor());
     math.setClickable(false);math.setFocusable(false);
     found.setAlpha(0f);
     // Reserve room for a fraction without overlapping the original button.
     found.setMinHeight(Math.round(52*activity.getResources().getDisplayMetrics().density));
     root.addView(math,new FrameLayout.LayoutParams(1,1));
    }
    int[] position=new int[2],origin=new int[2];found.getLocationInWindow(position);root.getLocationInWindow(origin);
    FrameLayout.LayoutParams params=(FrameLayout.LayoutParams)math.getLayoutParams();
    int left=position[0]-origin[0],top=position[1]-origin[1];
    int width=Math.max(1,root.getWidth()-left),height=Math.max(found.getHeight(),Math.round(52*activity.getResources().getDisplayMetrics().density));
    if(params.leftMargin!=left||params.topMargin!=top||params.width!=width||params.height!=height){
     params.leftMargin=left;params.topMargin=top;params.width=width;params.height=height;math.setLayoutParams(params);
    }
   }catch(Exception error){android.util.Log.e("DuoAeroNative","Cannot render original math feedback",error);clear();}
  }
  TextView find(View view){
   if(view==math)return null;
   if(view instanceof TextView && view.isShown()){
    TextView t=(TextView)view;CharSequence value=t.getText();
    if(value!=null&&value.toString().startsWith("\\textstyle ")&&isFooter(view))return t;
   }
   if(view instanceof ViewGroup){ViewGroup group=(ViewGroup)view;for(int i=0;i<group.getChildCount();i++){TextView result=find(group.getChildAt(i));if(result!=null)return result;}}
   return null;
  }
  boolean isFooter(View view){
   for(ViewParent p=view.getParent();p instanceof View;p=p.getParent()){
    View parent=(View)p;int id=parent.getId();
    if(id!=View.NO_ID)try{if("composeBottomContainer".equals(activity.getResources().getResourceEntryName(id)))return true;}catch(Exception ignored){}
   }
   return false;
  }
  void clear(){if(source!=null){source.setAlpha(1f);source.setMinHeight(0);}source=null;formula=null;if(math!=null){root.removeView(math);math=null;}}
  void close(){ViewTreeObserver observer=activity.getWindow().getDecorView().getViewTreeObserver();if(observer.isAlive())observer.removeOnGlobalLayoutListener(this);clear();}
 }
}
