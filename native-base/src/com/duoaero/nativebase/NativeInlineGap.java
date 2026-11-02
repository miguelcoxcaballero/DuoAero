package com.duoaero.nativebase;

import android.util.Base64;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.json.JSONArray;

/** Uses the original Math figures and build-slot controller in a wrapping row. */
public final class NativeInlineGap {
 private static final String MARKER="duoaero-gap:";
 private NativeInlineGap(){}
 public static boolean isGap(Object figure){
  if(!NativeCourseBridge.hasLocalCourse()||figure==null||!figure.getClass().getName().endsWith("MathFigureUiState$LatexString"))return false;
  try{return ((String)figure.getClass().getField("a").get(figure)).startsWith(MARKER);}
  catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot inspect native gap figure",error);}
 }
 public static void render(Object figure,List<?> slots,Object onSelect,Object onDrop,boolean enabled,boolean checked,
                           Object modifier,float width,boolean measured,Object interaction,Object composer,int flags){
  try{
   ClassLoader l=figure.getClass().getClassLoader();
   Class<?> ui=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState",true,l);
   Class<?> cls=figure.getClass(),mod=Class.forName("z5q",true,l),o18=Class.forName("o18",true,l);
   Class<?> callback=Class.forName("qqh",true,l),state=Class.forName("s6p",true,l);
   String encoded=((String)cls.getField("a").get(figure)).substring(MARKER.length());
   JSONArray words=new JSONArray(new String(Base64.decode(encoded,Base64.DEFAULT),StandardCharsets.UTF_8));
   boolean equation=false;
   for(int i=0;i<words.length();i++)if(words.getString(i).startsWith("duoaero-math:formula:"))equation=true;
   Object defaultModifier=Class.forName("w5q",true,l).getField("a").get(null);
   Method prompt=Class.forName("jvo",true,l).getMethod("a",ui,mod,Class.forName("cvo",true,l),
       Class.forName("kotlin.jvm.functions.Function0",true,l),callback,callback,
       Class.forName("kotlin.jvm.functions.Function0",true,l),Integer.class,state,
       Class.forName("com.duolingo.feature.math.ui.figure.WebViewInteractionState",true,l),o18,int.class,int.class);
   Method slot=Class.forName("fz0",true,l).getMethod("d",List.class,callback,callback,boolean.class,boolean.class,mod,float.class,boolean.class,state,o18,int.class);
   Class<?> irh=Class.forName("irh",true,l);
   Object function=Proxy.newProxyInstance(l,new Class<?>[]{irh},(proxy,method,args)->{
    if(method.getName().equals("invoke")){
     int index=((Integer)args[1]).intValue();Object composition=args[2];String part=words.getString(index);
     if(part.equals("___"))slot.invoke(null,slots,onSelect,onDrop,enabled,checked,defaultModifier,width,measured,interaction,composition,flags);
     else{
      String spoken;
      if(part.startsWith("duoaero-math:")){
       String[] math=part.split(":",3);
       if(math.length!=3||math[1].isEmpty()||math[2].isEmpty())throw new IllegalArgumentException("Invalid inline math");
       spoken=math[1];part=math[2];
      }else{
       if(!part.startsWith("\\text{")||!part.endsWith("}"))throw new IllegalArgumentException("Invalid gap text");
       spoken=part.substring(6,part.length()-1);
      }
      Object entity=Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity$Algebraic",true,l)
       .getConstructor(String.class).newInstance("duoaero:"+spoken);
      Object term=cls.getConstructor(String.class,float.class,Class.forName("b8t",true,l),boolean.class,
          Class.forName("com.duolingo.core.math.models.network.LatexColorConfig",true,l),
          Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity",true,l),boolean.class)
       .newInstance(part,Math.max(16f,Math.min(26f,cls.getField("b").getFloat(figure)*.65f)),cls.getField("c").get(figure),cls.getField("d").getBoolean(figure),
          cls.getField("e").get(figure),entity,cls.getField("g").getBoolean(figure));
      prompt.invoke(null,term,null,null,null,null,null,null,null,null,null,composition,0x8000000,0x2fe);
     }
     return Class.forName("xv80",true,l).getField("a").get(null);
    }
    if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
    if(method.getName().equals("equals"))return proxy==args[0];
    if(method.getName().equals("toString"))return "DuoAero native sentence gap";
    return null;
   });
   Object composable=Class.forName("ul3",true,l).getMethod("r",int.class,o18,Class.forName("pqh",true,l)).invoke(null,0x44aa771,composer,function);
   Class<?> iv=Class.forName("iv1",true,l),spacing=Class.forName("hv1",true,l);
   Object vertical=spacing.getConstructor(float.class,boolean.class,iv).newInstance(4f,true,Class.forName("gal",true,l).getConstructor(int.class).newInstance(12));
   Object align=Class.forName("b9z",true,l).getField("o").get(null);
   Object horizontal=spacing.getConstructor(float.class,boolean.class,iv).newInstance(equation?4f:10f,true,Class.forName("lz",true,l).getConstructor(Object.class,int.class).newInstance(align,2));
   // Align every word and its original answer slot at the centre of its own
   // wrapped line.  The original optimized implementation hardcodes Top;
   // build.py restores its alignment argument for this call.
   Object lineCenter=Class.forName("b9z",true,l).getField("l").get(null);
   Class.forName("iz0",true,l).getMethod("t",int.class,mod,Class.forName("fv1",true,l),Class.forName("jv1",true,l),
       Class.forName("lj0",true,l),int.class,int.class,Class.forName("hl8",true,l),Class.forName("uv7",true,l),o18,int.class,int.class)
    .invoke(null,words.length(),defaultModifier,horizontal,vertical,lineCenter,0,0,null,composable,composer,0x6000d80,0xe0);
  }catch(Exception error){throw new IllegalStateException("Cannot compose original inline word gap",error);}
 }
}
