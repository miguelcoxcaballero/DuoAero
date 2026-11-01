package com.duoaero.nativebase;

import android.app.Instrumentation;
import android.graphics.Bitmap;
import android.graphics.Rect;
import android.view.accessibility.AccessibilityNodeInfo;
import java.io.*;
import org.json.*;

/** Screen evidence from the isolated, synthetic-profile instrumentation only. */
final class SessionScreen {
 static void capture(Instrumentation test)throws Exception {
  capture(test,"session-diagnostic","session-view-tree");
 }
 static void capture(Instrumentation test,String screenshotName,String treeName)throws Exception {
  File directory=test.getTargetContext().getExternalFilesDir(null);
  Bitmap screenshot=test.getUiAutomation().takeScreenshot();
  if(screenshot==null)throw new IllegalStateException("Cannot capture session screen");
  try(FileOutputStream file=new FileOutputStream(new File(directory,screenshotName+".png"))){
   if(!screenshot.compress(Bitmap.CompressFormat.PNG,100,file))throw new IOException("PNG compression failed");
  }finally{screenshot.recycle();}
  JSONArray nodes=new JSONArray();
  AccessibilityNodeInfo root=test.getUiAutomation().getRootInActiveWindow();
  if(root!=null)try{visit(root,nodes,0);}finally{root.recycle();}
  try(Writer writer=new OutputStreamWriter(new FileOutputStream(new File(directory,treeName+".json")),"UTF-8")){
   writer.write(nodes.toString(2));
  }
 }
 private static void visit(AccessibilityNodeInfo node,JSONArray nodes,int depth)throws JSONException {
  if(depth>50||nodes.length()>=2000)return;
  // Never collect nodes from system account dialogs or other applications.
  if("com.duoaero.nativebase".contentEquals(node.getPackageName()==null?"":node.getPackageName())){
   Rect bounds=new Rect();node.getBoundsInScreen(bounds);
   nodes.put(new JSONObject().put("class",String.valueOf(node.getClassName()))
    .put("text",String.valueOf(node.getText())).put("description",String.valueOf(node.getContentDescription()))
    .put("resource",node.getViewIdResourceName()).put("bounds",bounds.flattenToString())
    .put("clickable",node.isClickable()).put("visible",node.isVisibleToUser())
    .put("enabled",node.isEnabled()).put("selected",node.isSelected()));
  }
  for(int i=0;i<node.getChildCount();i++){
   AccessibilityNodeInfo child=node.getChild(i);
   if(child!=null)try{visit(child,nodes,depth+1);}finally{child.recycle();}
  }
 }
}
