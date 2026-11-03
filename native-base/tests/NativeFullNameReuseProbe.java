package com.duoaero.nativebase;

import android.app.Instrumentation;
import android.view.View;
import android.widget.FrameLayout;
import java.lang.reflect.Method;
import java.util.concurrent.atomic.AtomicReference;

/** Isolated card lifecycle control; never touches session answers or slots. */
final class NativeFullNameReuseProbe {
 static void verify(Instrumentation test)throws Exception{
  AtomicReference<Throwable> failure=new AtomicReference<>();
  test.runOnMainSync(()->{
   try{
    android.content.Context context=test.getTargetContext();
    Class<?> helper=Class.forName("com.duoaero.nativebase.NativeFullNameProbe",true,context.getClassLoader());
    Method named=helper.getDeclaredMethod("setNamedPadding",FrameLayout.class);named.setAccessible(true);
    Method apply=helper.getMethod("apply",View.class,View.class,Object.class);
    for(boolean relative:new boolean[]{false,true}){
     FrameLayout card=new FrameLayout(context);View figure=new View(context);card.addView(figure);
     if(relative)card.setPaddingRelative(9,11,13,15);else card.setPadding(9,11,13,15);
     int left=card.getPaddingLeft(),right=card.getPaddingRight(),start=card.getPaddingStart(),end=card.getPaddingEnd();
     boolean wasRelative=card.isPaddingRelative();
     named.invoke(null,card);named.invoke(null,card);figure.setVisibility(View.INVISIBLE);
     apply.invoke(null,card,figure,null);
     if(card.getPaddingLeft()!=left||card.getPaddingRight()!=right||card.getPaddingStart()!=start||card.getPaddingEnd()!=end||
        card.getPaddingTop()!=11||card.getPaddingBottom()!=15||card.isPaddingRelative()!=wasRelative||figure.getVisibility()!=View.VISIBLE)
      throw new IllegalStateException("Original card padding or figure visibility not restored");
    }
   }catch(Throwable error){failure.set(error);}
  });
  if(failure.get()!=null)throw new IllegalStateException("Named-card reuse isolation failed",failure.get());
  android.util.Log.i("DuoAeroProbe","NAMED_CARD_PADDING_RESTORED=true");
 }
}
