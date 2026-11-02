package com.duoaero.nativebase;

import android.graphics.drawable.Drawable;
import android.view.View;
import android.widget.ImageView;
import android.util.Log;

/** Replace only the quit sheet image, after the original layout is inflated. */
public final class NativeMascotView {
 private NativeMascotView(){}
 public static void animateQuit(View root){
  try{
   int id=root.getResources().getIdentifier("imageView","id","com.duolingo");
   View found=root.findViewById(id);
   if(!(found instanceof ImageView))return;
   ImageView image=(ImageView)found;Drawable original=image.getDrawable();
   if(original==null)return;
   NativeSadDrawable replacement=new NativeSadDrawable();
   replacement.initialize(root.getResources(),original.getIntrinsicWidth(),original.getIntrinsicHeight());
   image.setImageDrawable(replacement);
  }catch(Exception error){Log.e("DuoAeroNative","Cannot animate quit mascot; retaining static pose",error);}
 }
}
