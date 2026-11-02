package com.duoaero.nativebase;

import android.app.Application;
import android.content.res.Resources;
import android.util.Log;
import android.util.TypedValue;

/** Compatibility for the original profile's Compose image loader. */
public final class NativeProfileDrawable {
 private NativeProfileDrawable(){}
 public static int supported(int id){
  if(!NativeCourseBridge.hasLocalCourse())return id;
  try{
   Application app=(Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
   Resources resources=app.getResources();TypedValue value=new TypedValue();resources.getValue(id,value,true);
   String path=value.string==null?"":value.string.toString();
   // Compose painterResource supports vector XML and raster images, but not
   // layer-list XML. Our replacement mascot layer lists preserve intrinsic
   // dimensions elsewhere; on this fixed-size profile icon use the same PNG.
   if(path.startsWith("res/drawable/duoaero_mascot_")&&path.endsWith(".xml")){
    int png=resources.getIdentifier("duoaero_scene_mascot","drawable",app.getPackageName());
    if(png==0)png=resources.getIdentifier("duoaero_scene_mascot","drawable","com.duolingo");
    if(png==0)throw new Resources.NotFoundException("DuoAero mascot PNG");
    Log.i("DuoAeroNative","Profile mascot drawable adapted for Compose: "+resources.getResourceName(id));
    return png;
   }
   Log.i("DuoAeroNative","Profile Compose drawable: "+resources.getResourceName(id)+" path="+path);
  }catch(Exception error){Log.w("DuoAeroNative","Could not inspect profile drawable "+id,error);}
  return id;
 }
}
