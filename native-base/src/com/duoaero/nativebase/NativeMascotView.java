package com.duoaero.nativebase;

import android.graphics.drawable.Drawable;
import android.view.View;
import android.widget.ImageView;
import android.util.Log;

/** Replace only the quit sheet image, after the original layout is inflated. */
public final class NativeMascotView {
 private static java.lang.ref.WeakReference<ImageView> quitImage=new java.lang.ref.WeakReference<>(null);
 private NativeMascotView(){}
 public static void animateQuit(View root){
  try{
   // This ID belongs to the unchanged original resource table. Resource
   // lookups by package name are unreliable in the renamed application.
   int id=0x7f0a08ed;
   View found=root.findViewById(id);
   if(!(found instanceof ImageView)){Log.e("DuoAeroNative","Quit mascot ImageView was not found");return;}
   ImageView image=(ImageView)found;Drawable original=image.getDrawable();
   if(original==null){Log.e("DuoAeroNative","Quit mascot had no original drawable");return;}
   NativeSadDrawable replacement=new NativeSadDrawable();
   replacement.initialize(root.getResources(),original.getIntrinsicWidth(),original.getIntrinsicHeight());
   image.setImageDrawable(replacement);quitImage=new java.lang.ref.WeakReference<>(image);
   Log.i("DuoAeroNative","Quit mascot animation attached to original image");
  }catch(Exception error){Log.e("DuoAeroNative","Cannot animate quit mascot; retaining static pose",error);}
 }
 public static boolean quitAnimationAttached(){
  ImageView image=quitImage.get();return image!=null&&image.isAttachedToWindow()&&image.getDrawable() instanceof NativeSadDrawable;
 }
}
