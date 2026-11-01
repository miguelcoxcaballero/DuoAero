package com.duoaero.nativebase;

import android.app.Instrumentation;
import android.os.Bundle;
import android.view.accessibility.AccessibilityNodeInfo;

/** Accessibility action on the original visible card, from a separate process. */
public final class IndependentClickProbe extends Instrumentation {
 private String label;
 public void onCreate(Bundle args){label=args.getString("label","");start();}
 public void onStart(){
  Bundle result=new Bundle();
  try{
   if(label.isEmpty())throw new IllegalArgumentException("Missing label");
   AccessibilityNodeInfo match=null;
   for(int attempt=0;attempt<40&&match==null;attempt++){
    AccessibilityNodeInfo root=getUiAutomation().getRootInActiveWindow();
    if(root!=null)try{match=find(root,0);}finally{root.recycle();}
    if(match==null)Thread.sleep(250);
   }
   if(match==null)throw new IllegalStateException("Original token not visible");
   try{
    for(int depth=0;depth<8&&!match.isClickable();depth++){
     AccessibilityNodeInfo parent=match.getParent();if(parent==null)break;match.recycle();match=parent;
    }
    if(!match.isEnabled()||!match.isClickable()||!match.performAction(AccessibilityNodeInfo.ACTION_CLICK))
     throw new IllegalStateException("Original token did not accept accessibility action");
   }finally{match.recycle();}
   result.putString("result","INDEPENDENT_CLICK_VERIFIED=true");
  }catch(Throwable error){result.putString("result","INDEPENDENT_CLICK_VERIFIED=false "+error);}
  finish(0,result);
 }
 private AccessibilityNodeInfo find(AccessibilityNodeInfo node,int depth){
  if(depth>50||!"com.duoaero.nativebase".contentEquals(node.getPackageName()==null?"":node.getPackageName()))return null;
  for(int i=node.getChildCount()-1;i>=0;i--){AccessibilityNodeInfo child=node.getChild(i);if(child!=null)try{AccessibilityNodeInfo found=find(child,depth+1);if(found!=null)return found;}finally{child.recycle();}}
  if(node.isVisibleToUser()&&(label.contentEquals(node.getText()==null?"":node.getText())||label.contentEquals(node.getContentDescription()==null?"":node.getContentDescription())))return AccessibilityNodeInfo.obtain(node);
  return null;
 }
}
