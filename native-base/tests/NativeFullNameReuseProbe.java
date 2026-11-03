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
    ClassLoader loader=context.getClassLoader();
    Class<?> bridge=Class.forName("com.duoaero.nativebase.NativeCourseBridge",true,loader);
    if(!(Boolean)bridge.getMethod("hasLocalCourse").invoke(null))throw new IllegalStateException("Local service context must stay active");
    Class<?> entityClass=Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity$Algebraic",true,loader);
    Object entity=entityClass.getConstructor(String.class).newInstance("x");
    Class<?> style=Class.forName("com.duolingo.core.math.models.figure.MathTextStyle",true,loader);
    Class<?> weight=Class.forName("com.duolingo.core.math.models.figure.MathTextStyle$MathFontWeight",true,loader);
    Class<?> family=Class.forName("com.duolingo.core.math.models.figure.MathTextStyle$MathFontFamily",true,loader);
    Class<?> alignment=Class.forName("com.duolingo.core.math.models.figure.MathTextStyle$MathTextAlignment",true,loader);
    Object center=alignment.getField("CENTER").get(null);
    Object textStyle=style.getConstructor(long.class,long.class,weight,family,alignment).newInstance(0L,0L,null,null,center);
    Class<?> scaleState=Class.forName("com.duolingo.core.math.models.figure.MathFigureScaleState",true,loader);
    Class<?> scale=Class.forName("com.duolingo.core.math.models.figure.MathFigureScaleInfo",true,loader);
    Object scaleInfo=scale.getConstructor(scaleState,boolean.class).newInstance(null,false);
    Class<?> figureBase=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState",true,loader);
    Class<?> mathEntity=Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity",true,loader);
    Class<?> attributed=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState$AttributedText",true,loader);
    Object originalFigure=attributed.getConstructor(java.util.List.class,style,scale,boolean.class,String.class,mathEntity)
      .newInstance(java.util.Collections.emptyList(),textStyle,scaleInfo,false,null,entity);
    Class<?> color=Class.forName("com.duolingo.feature.math.ui.tokendrag.BuildTokenState$ColorState",true,loader);
    Object token=Class.forName("qp3",true,loader).getConstructor(int.class,figureBase,color).newInstance(1,originalFigure,color.getField("DEFAULT").get(null));
    Class<?> scope=Class.forName("com.duoaero.nativebase.NativeNamedTokenSizing",true,context.getClassLoader());
    Method enter=scope.getDeclaredMethod("enter",boolean.class),exit=scope.getDeclaredMethod("exit",boolean.class),active=scope.getDeclaredMethod("active");
    enter.setAccessible(true);exit.setAccessible(true);active.setAccessible(true);
    for(String symbol:new String[]{"duoaero:k","duoaero:mu","duoaero:m_i","duoaero:c_e"}){
     Object localEntity=entityClass.getConstructor(String.class).newInstance(symbol);
     Object localFigure=attributed.getConstructor(java.util.List.class,style,scale,boolean.class,String.class,mathEntity)
       .newInstance(java.util.Collections.emptyList(),textStyle,scaleInfo,false,null,localEntity);
     Object localToken=Class.forName("qp3",true,loader).getConstructor(int.class,figureBase,color).newInstance(1,localFigure,color.getField("DEFAULT").get(null));
     if(((Float)scope.getMethod("width",Object.class,float.class).invoke(null,localToken,300f))!=300f ||
        ((Float)scope.getMethod("height",Object.class,float.class).invoke(null,localToken,43f))!=43f)
       throw new IllegalStateException("Local symbolic token sizing changed");
    }
    Object untouchedModifier=new Object();
    Object originalScroll=bridge.getMethod("scrollLongBuildSpace",java.util.List.class,Object.class,Object.class)
      .invoke(null,java.util.Arrays.asList(token,token,token,token),untouchedModifier,null);
    if(originalScroll!=untouchedModifier)throw new IllegalStateException("Unmarked expression unexpectedly scrolled");
    boolean outer=(Boolean)enter.invoke(null,true);
    if(!((Boolean)active.invoke(null)))throw new IllegalStateException("Named scope did not enter");
    if(((Float)scope.getMethod("width",Object.class,float.class).invoke(null,null,300f))!=160f ||
       ((Float)scope.getMethod("height",Object.class,float.class).invoke(null,null,43f))!=96f)
      throw new IllegalStateException("Empty named slot sizing not scoped");
    boolean inner=(Boolean)enter.invoke(null,false);
    if((Boolean)active.invoke(null))throw new IllegalStateException("Non-named nested scope inherited named sizing");
    exit.invoke(null,inner);
    if(!((Boolean)active.invoke(null)))throw new IllegalStateException("Named scope not restored after nesting");
    exit.invoke(null,outer);
    if((Boolean)active.invoke(null))throw new IllegalStateException("Named scope leaked after rendering");
    if(((Float)scope.getMethod("width",Object.class,float.class).invoke(null,token,77f))!=77f ||
       ((Float)scope.getMethod("height",Object.class,float.class).invoke(null,token,43f))!=43f)
      throw new IllegalStateException("Original unmarked token sizing changed");
    Class<?> helper=Class.forName("com.duoaero.nativebase.NativeFullNameProbe",true,context.getClassLoader());
    Method named=helper.getDeclaredMethod("setNamedPadding",FrameLayout.class);named.setAccessible(true);
    Method apply=helper.getMethod("apply",View.class,View.class,Object.class);
    for(boolean relative:new boolean[]{false,true}){
     FrameLayout card=new FrameLayout(context);View figure=new View(context);card.addView(figure);
     if(relative)card.setPaddingRelative(9,11,13,15);else card.setPadding(9,11,13,15);
     int left=card.getPaddingLeft(),right=card.getPaddingRight(),start=card.getPaddingStart(),end=card.getPaddingEnd();
     boolean wasRelative=card.isPaddingRelative();
     named.invoke(null,card);named.invoke(null,card);figure.setVisibility(View.INVISIBLE);
     apply.invoke(null,card,figure,originalFigure);
     if(card.getPaddingLeft()!=left||card.getPaddingRight()!=right||card.getPaddingStart()!=start||card.getPaddingEnd()!=end||
        card.getPaddingTop()!=11||card.getPaddingBottom()!=15||card.isPaddingRelative()!=wasRelative||figure.getVisibility()!=View.VISIBLE)
      throw new IllegalStateException("Original card padding or figure visibility not restored");
    }
   }catch(Throwable error){failure.set(error);}
  });
  if(failure.get()!=null)throw new IllegalStateException("Named-card reuse isolation failed",failure.get());
  android.util.Log.i("DuoAeroProbe","NAMED_CARD_PADDING_RESTORED=true");
  android.util.Log.i("DuoAeroProbe","ORIGINAL_UNMARKED_TOKEN_UNCHANGED=true");
  android.util.Log.i("DuoAeroProbe","LOCAL_SYMBOLS_AND_EMPTY_SCOPE_UNCHANGED=true");
 }
}
