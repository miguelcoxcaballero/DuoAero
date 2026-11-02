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
   Context context=getTargetContext();String[] names={"duo_happy","duo_flying","duo_thinking","jaw_drop_duo","foam_finger_duo","duo_breathe",
    "practice_hub_duo_radio_falstaff_1","practice_hub_duo_radio_chatting_with_zari_01","practice_hub_duo_radio_junior_s_big_questions_01","duo_sad","duo_reading_stories","stories_duo_reading","duo_holding_gem","guidebook_header_duo_gem",
    "character_falstaff","duoradio_host_zari_exercise_correct","duoradio_host_zari_exercise_incorrect","duo_wave","duo_welcome","duo_chest"};
   Bitmap grid=Bitmap.createBitmap(720,1680,Bitmap.Config.ARGB_8888);Canvas canvas=new Canvas(grid);HashSet<Integer> variants=new HashSet<>();
   for(int i=0;i<names.length;i++){
    int id=context.getResources().getIdentifier(names[i],"drawable","com.duolingo");
    if(id==0)throw new IllegalStateException("Original drawable missing: "+names[i]);
    Drawable drawable=context.getResources().getDrawable(id,context.getTheme());
    if(drawable.getIntrinsicWidth()<=0||drawable.getIntrinsicHeight()<=0)throw new IllegalStateException("Invalid original bounds: "+names[i]);
    if(names[i].equals("duo_happy")||names[i].equals("duo_sad")){
     String animationName=names[i].equals("duo_happy")?"wave":"sad";
     String type=names[i].equals("duo_happy")?"NativeWaveDrawable":"NativeSadDrawable";
     Class<?> animationClass=Class.forName("com.duoaero.nativebase."+type,true,context.getClassLoader());
     Drawable animated=(Drawable)animationClass.getConstructor().newInstance();
     animationClass.getMethod("initialize",android.content.res.Resources.class,int.class,int.class)
       .invoke(animated,context.getResources(),drawable.getIntrinsicWidth(),drawable.getIntrinsicHeight());
     Drawable original=drawable;drawable=animated;
     drawable.setBounds(0,0,240,240);
     Bitmap first=Bitmap.createBitmap(240,240,Bitmap.Config.ARGB_8888),later=Bitmap.createBitmap(240,240,Bitmap.Config.ARGB_8888);
     drawable.draw(new Canvas(first));Thread.sleep(660);drawable.draw(new Canvas(later));
     if(first.sameAs(later))throw new IllegalStateException(animationName+" frames did not change");
     for(int frame=0;frame<2;frame++){
      try(FileOutputStream outputFrame=new FileOutputStream(new File(context.getExternalFilesDir(null),animationName+"-frame-"+frame+".png"))){
       if(!(frame==0?first:later).compress(Bitmap.CompressFormat.PNG,100,outputFrame))throw new IllegalStateException("Cannot capture "+animationName+" frame");
      }
     }
     ((android.graphics.drawable.Animatable)drawable).stop();first.recycle();later.recycle();drawable=original;
     report.append(animationName.equals("wave")?"WAVE_FRAMES_CHANGED=true":"SAD_FRAMES_CHANGED=true").append("; original screen playback and smoothness are unverified.\n");
    }
    // An ImageView's fit-centre policy scales the canvas around the
    // drawable's intrinsic bounds. Forcing smaller bounds directly does not
    // scale Android layer-list item dimensions and produces a false crop.
    Bitmap image=Bitmap.createBitmap(240,240,Bitmap.Config.ARGB_8888);
    int width=drawable.getIntrinsicWidth(),height=drawable.getIntrinsicHeight();
    float scale=Math.min(220f/width,220f/height);Canvas tile=new Canvas(image);
    tile.translate((240-width*scale)/2f,(240-height*scale)/2f);tile.scale(scale,scale);
    drawable.setBounds(0,0,width,height);drawable.draw(tile);
    int[] pixels=new int[240*240];image.getPixels(pixels,0,240,0,0,240,240);int hash=1,visible=0;
    for(int pixel:pixels){hash=31*hash+pixel;if((pixel>>>24)>16)visible++;}
    if(visible<500)throw new IllegalStateException("Empty drawn pose: "+names[i]);
    variants.add(hash);canvas.drawBitmap(image,(i%3)*240,(i/3)*240,null);image.recycle();
    report.append(names[i]).append(" original resource resolved and drawn\n");
   }
   if(variants.size()<11)throw new IllegalStateException("Distinct poses were not rendered");
   // Inflate the actual AppCompatImageView element with its original binary
   // layout attributes. Other views in this fragment require a live activity
   // theme and cannot be inflated from this instrumentation-only context.
   final Throwable[] layoutError={null};
   runOnMainSync(()->{
    try{
     int layout=context.getResources().getIdentifier("fragment_feedback_message","layout","com.duolingo");
     try(android.content.res.XmlResourceParser parser=context.getResources().getLayout(layout)){
      int event;
      do{event=parser.next();}while(event!=org.xmlpull.v1.XmlPullParser.END_DOCUMENT &&
        !(event==org.xmlpull.v1.XmlPullParser.START_TAG && parser.getName().equals("androidx.appcompat.widget.AppCompatImageView")));
      if(event==org.xmlpull.v1.XmlPullParser.END_DOCUMENT)throw new IllegalStateException("Original image element missing");
      android.view.View child=android.view.LayoutInflater.from(context).createView(parser.getName(),null,android.util.Xml.asAttributeSet(parser));
      android.widget.ImageView image=(android.widget.ImageView)child;
      if(image.getDrawable()==null)
       throw new IllegalStateException("Original feedback image cannot display mascot");
     }
    }catch(Throwable failure){layoutError[0]=failure;}
   });
   if(layoutError[0]!=null)throw new IllegalStateException("Original feedback image inflation failed",layoutError[0]);
   report.append("WAVE_IMAGE_INFLATED=true; static original image inflated; animated feedback is unverified.\n");
   try(FileOutputStream stream=new FileOutputStream(new File(context.getExternalFilesDir(null),"static-mascot-poses.png"))){
    if(!grid.compress(Bitmap.CompressFormat.PNG,100,stream))throw new IllegalStateException("Cannot capture poses");
   }finally{grid.recycle();}
   report.append("STATIC_MOODS_VERIFIED=true; rendered original IDs only, screen placement and animation unverified.\n");
  }catch(Throwable failure){report.append(android.util.Log.getStackTraceString(failure));}
  output.putString(Instrumentation.REPORT_KEY_STREAMRESULT,report.toString());finish(0,output);
 }
}
