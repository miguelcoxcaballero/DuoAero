package com.duoaero.nativebase;

import android.app.Instrumentation;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import java.io.File;
import java.io.FileOutputStream;
import java.util.HashSet;

/** Resolve and draw real original resource IDs in Android, not a screen-flow test. */
public final class StaticMascotProbe extends Instrumentation {
 public void onCreate(Bundle arguments){start();}
 public void onStart(){
  Bundle output=new Bundle();StringBuilder report=new StringBuilder();
  try{
   Context context=getTargetContext();String[] names={"duo_happy","duo_flying","duo_thinking","jaw_drop_duo","foam_finger_duo","duo_breathe"};
   Bitmap grid=Bitmap.createBitmap(720,480,Bitmap.Config.ARGB_8888);Canvas canvas=new Canvas(grid);HashSet<Integer> variants=new HashSet<>();
   for(int i=0;i<names.length;i++){
    int id=context.getResources().getIdentifier(names[i],"drawable","com.duolingo");
    if(id==0)throw new IllegalStateException("Original drawable missing: "+names[i]);
    Drawable drawable=context.getResources().getDrawable(id,context.getTheme());
    if(drawable.getIntrinsicWidth()<=0||drawable.getIntrinsicHeight()<=0)throw new IllegalStateException("Invalid original bounds: "+names[i]);
    Bitmap image=Bitmap.createBitmap(240,240,Bitmap.Config.ARGB_8888);
    drawable.setBounds(0,0,240,240);drawable.draw(new Canvas(image));
    int[] pixels=new int[240*240];image.getPixels(pixels,0,240,0,0,240,240);int hash=1,visible=0;
    for(int pixel:pixels){hash=31*hash+pixel;if((pixel>>>24)>16)visible++;}
    if(visible<500)throw new IllegalStateException("Empty drawn pose: "+names[i]);
    variants.add(hash);canvas.drawBitmap(image,(i%3)*240,(i/3)*240,null);image.recycle();
    report.append(names[i]).append(" original resource resolved and drawn\n");
   }
   if(variants.size()<5)throw new IllegalStateException("Distinct poses were not rendered");
   try(FileOutputStream stream=new FileOutputStream(new File(context.getExternalFilesDir(null),"static-mascot-poses.png"))){
    if(!grid.compress(Bitmap.CompressFormat.PNG,100,stream))throw new IllegalStateException("Cannot capture poses");
   }finally{grid.recycle();}
   report.append("STATIC_MOODS_VERIFIED=true; rendered original IDs only, screen placement and animation unverified.\n");
  }catch(Throwable failure){report.append(android.util.Log.getStackTraceString(failure));}
  output.putString(Instrumentation.REPORT_KEY_STREAMRESULT,report.toString());finish(0,output);
 }
}
