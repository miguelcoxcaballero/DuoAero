package com.duoaero.nativebase;

import android.graphics.drawable.Drawable;
import android.view.View;
import android.widget.ImageView;
import android.util.Log;

/** Replace only the quit sheet image, after the original layout is inflated. */
public final class NativeMascotView {
 private static java.lang.ref.WeakReference<ImageView> quitImage=new java.lang.ref.WeakReference<>(null);
 private NativeMascotView(){}
 /** Called after the original quit view model applies its image. */
 public static void animateQuitImage(ImageView image){
  try{
   Drawable original=image.getDrawable();
   if(original==null){Log.e("DuoAeroNative","Quit mascot had no original drawable");return;}
   NativeSadDrawable replacement=new NativeSadDrawable();
   replacement.initialize(image.getResources(),original.getIntrinsicWidth(),original.getIntrinsicHeight());
   image.setImageDrawable(replacement);quitImage=new java.lang.ref.WeakReference<>(image);
   Log.i("DuoAeroNative","Quit mascot animation attached to original image");
  }catch(Exception error){Log.e("DuoAeroNative","Cannot animate quit mascot; retaining static pose",error);}
 }
 public static boolean quitAnimationAttached(){
  ImageView image=quitImage.get();return image!=null&&image.isAttachedToWindow()&&image.getDrawable() instanceof NativeSadDrawable;
 }
}
