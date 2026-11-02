package com.duoaero.nativebase;

import android.util.Log;

/** Reports the original completion scene enum, never changes its selection. */
public final class NativeCompletionObservation {
 private static String previous="";
 private NativeCompletionObservation(){}
 public static void selected(Object character){
  if(!NativeCourseBridge.hasLocalCourse()||!(character instanceof Enum))return;
  String current=((Enum<?>)character).name();
  if(!current.equals(previous)){previous=current;Log.i("DuoAeroNative","Original completion character: "+current);}
 }
}
