package com.duoaero.nativebase;

import android.util.Base64;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.json.JSONArray;

/** Uses the original Math figures and build-slot controller in a wrapping row. */
public final class NativeInlineGap {
 private static final String MARKER="duoaero-gap:";
 private static final String OPERATOR_GAP="duoaero-operator-gap:";
 private static final String OPERATOR_POWER="duoaero-operator-power:";
 private static final String OPERATOR_NEGATIVE="duoaero-operator-negative:";
 private static final String FRACTION="duoaero-fraction-slots";
 private static final String SQUARED_FRACTION="duoaero-squared-fraction-slots";
 private static final String SQUARED_TWICE="duoaero-squared-over-twice";
 private static final String DEFLECTION_FRACTION="duoaero-deflection-fraction";
 private static final String CANTILEVER_FRACTION="duoaero-cantilever-fraction";
 private static final String PRODUCT_FRACTION_21="duoaero-product-fraction-21";
 private static final String PRODUCT_FRACTION_22="duoaero-product-fraction-22";
 private static final String POWER="duoaero-power-slot:";
 private static final String NEGATIVE_EXPONENT="duoaero-negative-exponent";
 private static int countSlots(String part){return part.equals(PRODUCT_FRACTION_22)||part.equals(DEFLECTION_FRACTION)?4:part.equals(PRODUCT_FRACTION_21)||part.equals(CANTILEVER_FRACTION)?3:part.equals(FRACTION)||part.equals(SQUARED_FRACTION)||part.equals(SQUARED_TWICE)?2:part.equals("___")||part.equals(NEGATIVE_EXPONENT)||part.startsWith(OPERATOR_GAP)||part.startsWith(OPERATOR_POWER)||part.startsWith(OPERATOR_NEGATIVE)||part.startsWith(POWER)?1:0;}
 private static int slotsBefore(List<String> parts,int index){int n=0;for(int i=0;i<index;i++)n+=countSlots(parts.get(i));return n;}
 private NativeInlineGap(){}
 public static boolean isGap(Object figure){
  if(!NativeCourseBridge.hasLocalCourse()||figure==null||!figure.getClass().getName().endsWith("MathFigureUiState$LatexString"))return false;
  try{return ((String)figure.getClass().getField("a").get(figure)).startsWith(MARKER);}
  catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot inspect native gap figure",error);}
 }
 public static void render(Object figure,List<?> slots,Object onSelect,Object onDrop,boolean enabled,boolean checked,
                           Object modifier,float width,boolean measured,Object interaction,Object composer,int flags){
  NativeSlotProbe.capture(slots);
  try{
   ClassLoader l=figure.getClass().getClassLoader();
   Class<?> ui=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState",true,l);
   Class<?> cls=figure.getClass(),mod=Class.forName("z5q",true,l),o18=Class.forName("o18",true,l);
   Class<?> callback=Class.forName("qqh",true,l),state=Class.forName("s6p",true,l);
   String encoded=((String)cls.getField("a").get(figure)).substring(MARKER.length());
   JSONArray words=new JSONArray(new String(Base64.decode(encoded,Base64.DEFAULT),StandardCharsets.UTF_8));
   // Keep a binary operator together with the next interactive operand.
   // Otherwise FlowRow may leave '+' or '×' stranded at the end of a line.
   ArrayList<String> parts=new ArrayList<>();
   for(int i=0;i<words.length();i++){
    String part=words.getString(i);
    // Keep division and the opening parenthesis with the first denominator
    // slot, so neither symbol is stranded at the end of a wrapped line.
    if(i+2<words.length()&&part.equals("duoaero-math:formula:\\textstyle \\div")
       &&words.getString(i+1).equals("duoaero-math:formula:\\textstyle (")
       &&words.getString(i+2).equals("___")){
     parts.add(OPERATOR_GAP+"duoaero-math:formula:\\textstyle \\div(");i+=2;
    }else if(i+1<words.length()&&("___".equals(words.getString(i+1))||words.getString(i+1).startsWith(POWER)||words.getString(i+1).equals(NEGATIVE_EXPONENT))
       &&(part.equals("duoaero-math:formula:\\textstyle (")
          ||part.equals("duoaero-math:formula:\\textstyle +")
          ||part.equals("duoaero-math:formula:\\textstyle -")
          ||part.equals("duoaero-math:formula:\\textstyle \\times")
          ||part.equals("duoaero-math:formula:\\textstyle \\div"))){
     String next=words.getString(i+1);
     parts.add(next.startsWith(POWER)?OPERATOR_POWER+part+"|"+next.substring(POWER.length()):next.equals(NEGATIVE_EXPONENT)?OPERATOR_NEGATIVE+part:OPERATOR_GAP+part);i++;
    }else parts.add(part);
   }
   boolean equation=false;
   for(int i=0;i<words.length();i++)if(words.getString(i).startsWith("duoaero-math:formula:"))equation=true;
   Object defaultModifier=Class.forName("w5q",true,l).getField("a").get(null);
   Method prompt=Class.forName("jvo",true,l).getMethod("a",ui,mod,Class.forName("cvo",true,l),
       Class.forName("kotlin.jvm.functions.Function0",true,l),callback,callback,
       Class.forName("kotlin.jvm.functions.Function0",true,l),Integer.class,state,
       Class.forName("com.duolingo.feature.math.ui.figure.WebViewInteractionState",true,l),o18,int.class,int.class);
   Method slot=Class.forName("fz0",true,l).getMethod("d",List.class,callback,callback,boolean.class,boolean.class,mod,float.class,boolean.class,state,o18,int.class);
   Class<?> irh=Class.forName("irh",true,l);
   int gaps=0;for(String part:parts)gaps+=countSlots(part);
   final int gapCount=gaps;
   // The original BuildSpace composable lays out the whole list. For several
   // separated inline holes, invoke its original per-slot composable with the
   // full list and real slot index, preserving drag/drop and selection IDs.
   final Object originalSlot;
   final Method renderSlot;
   if(gapCount>1){
    if(slots.size()!=gapCount)throw new IllegalStateException("Inline slot count mismatch");
    Class<?> gp=Class.forName("gp3",true,l);
    originalSlot=gp.getConstructor(List.class,boolean.class,callback,callback,boolean.class,float.class,boolean.class,state)
     .newInstance(slots,enabled,onSelect,onDrop,checked,width,measured,interaction);
    renderSlot=gp.getMethod("invoke",Object.class,Object.class,Object.class,Object.class);
   }else{originalSlot=null;renderSlot=null;}
   Object function=Proxy.newProxyInstance(l,new Class<?>[]{irh},(proxy,method,args)->{
    if(method.getName().equals("invoke")){
     int index=((Integer)args[1]).intValue();Object composition=args[2];String part=parts.get(index);
     boolean powerPaired=part.startsWith(OPERATOR_POWER),negativePaired=part.startsWith(OPERATOR_NEGATIVE);
     String pairedPower=null;
     if(powerPaired){String value=part.substring(OPERATOR_POWER.length());int separator=value.lastIndexOf('|');if(separator<0)throw new IllegalStateException("Invalid grouped power");pairedPower=value.substring(separator+1);part=value.substring(0,separator);}
     boolean paired=powerPaired||negativePaired||part.startsWith(OPERATOR_GAP);
     if(paired){
      if(negativePaired)part=part.substring(OPERATOR_NEGATIVE.length());
      else if(!powerPaired)part=part.substring(OPERATOR_GAP.length());
      if(!NativeInlineFormula.begin(figure,composition))throw new IllegalStateException("Cannot group operator and operand");
     }
     if(part.equals("___")){
      if(gapCount<=1)slot.invoke(null,slots,onSelect,onDrop,enabled,checked,defaultModifier,width,measured,interaction,composition,flags);
      else{
       int ordinal=slotsBefore(parts,index);
       renderSlot.invoke(originalSlot,args[0],Integer.valueOf(ordinal),composition,args[3]);
      }
     }
     else if(part.equals(FRACTION)){
      Object fraction=NativeFractionSlot.create(figure,args[0],originalSlot,renderSlot,slotsBefore(parts,index));
      prompt.invoke(null,fraction,null,null,null,null,null,null,null,null,null,composition,0x8000000,0x2fe);
     }
     else if(part.equals(SQUARED_FRACTION)){
      Object fraction=NativeFractionSlot.createSquaredNumerator(figure,args[0],originalSlot,renderSlot,slotsBefore(parts,index));
      prompt.invoke(null,fraction,null,null,null,null,null,null,null,null,null,composition,0x8000000,0x2fe);
     }
     else if(part.equals(SQUARED_TWICE)){
      Object fraction=NativeFractionSlot.createSquaredOverTwice(figure,args[0],originalSlot,renderSlot,slotsBefore(parts,index));
      prompt.invoke(null,fraction,null,null,null,null,null,null,null,null,null,composition,0x8000000,0x2fe);
     }
     else if(part.equals(NEGATIVE_EXPONENT)){
      Object power=NativeFractionSlot.createNegativeExponent(figure,args[0],originalSlot,renderSlot,slotsBefore(parts,index));
      prompt.invoke(null,power,null,null,null,null,null,null,null,null,null,composition,0x8000000,0x2fe);
     }
     else if(part.equals(DEFLECTION_FRACTION)){
      Object fraction=NativeFractionSlot.createSparDeflection(figure,args[0],originalSlot,renderSlot,slotsBefore(parts,index));
      prompt.invoke(null,fraction,null,null,null,null,null,null,null,null,null,composition,0x8000000,0x2fe);
     }
     else if(part.equals(CANTILEVER_FRACTION)){
      Object fraction=NativeFractionSlot.createCantilever(figure,args[0],originalSlot,renderSlot,slotsBefore(parts,index));
      prompt.invoke(null,fraction,null,null,null,null,null,null,null,null,null,composition,0x8000000,0x2fe);
     }
     else if(part.equals(PRODUCT_FRACTION_21)||part.equals(PRODUCT_FRACTION_22)){
      Object fraction=NativeFractionSlot.createProduct(figure,args[0],originalSlot,renderSlot,slotsBefore(parts,index),2,part.equals(PRODUCT_FRACTION_21)?1:2);
      prompt.invoke(null,fraction,null,null,null,null,null,null,null,null,null,composition,0x8000000,0x2fe);
     }
     else if(part.startsWith(POWER)){
      if(gapCount<=1)throw new IllegalStateException("Power slot requires a multi-slot equation");
      Object power=NativeFractionSlot.createPower(figure,args[0],originalSlot,renderSlot,slotsBefore(parts,index),part.substring(POWER.length()));
      prompt.invoke(null,power,null,null,null,null,null,null,null,null,null,composition,0x8000000,0x2fe);
     }
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
     if(paired){
      if(negativePaired){
       Object power=NativeFractionSlot.createNegativeExponent(figure,args[0],originalSlot,renderSlot,slotsBefore(parts,index));
       prompt.invoke(null,power,null,null,null,null,null,null,null,null,null,composition,0x8000000,0x2fe);
      }
      else if(powerPaired){
       if(gapCount<=1)throw new IllegalStateException("Power slot requires a multi-slot equation");
       Object power=NativeFractionSlot.createPower(figure,args[0],originalSlot,renderSlot,slotsBefore(parts,index),pairedPower);
       prompt.invoke(null,power,null,null,null,null,null,null,null,null,null,composition,0x8000000,0x2fe);
      }
      else if(gapCount<=1)slot.invoke(null,slots,onSelect,onDrop,enabled,checked,defaultModifier,width,measured,interaction,composition,flags);
      else{
       int ordinal=slotsBefore(parts,index);
       renderSlot.invoke(originalSlot,args[0],Integer.valueOf(ordinal),composition,Integer.valueOf(0));
      }
      NativeInlineFormula.end(true,composition);
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
   // The interactive negative exponent is raised above its line. Reserve
   // enough space between wrapped rows so it cannot overlap the prior row.
   boolean raisedExponent=false;for(String part:parts)if(part.equals(NEGATIVE_EXPONENT)||part.startsWith(OPERATOR_NEGATIVE))raisedExponent=true;
   Object vertical=spacing.getConstructor(float.class,boolean.class,iv).newInstance(raisedExponent?32f:4f,true,Class.forName("gal",true,l).getConstructor(int.class).newInstance(12));
   Object align=Class.forName("b9z",true,l).getField("o").get(null);
   Object horizontal=spacing.getConstructor(float.class,boolean.class,iv).newInstance(equation?4f:10f,true,Class.forName("lz",true,l).getConstructor(Object.class,int.class).newInstance(align,2));
   // Align every word and its original answer slot at the centre of its own
   // wrapped line.  The original optimized implementation hardcodes Top;
   // build.py restores its alignment argument for this call.
   Object lineCenter=Class.forName("b9z",true,l).getField("l").get(null);
   Class.forName("iz0",true,l).getMethod("t",int.class,mod,Class.forName("fv1",true,l),Class.forName("jv1",true,l),
       Class.forName("lj0",true,l),int.class,int.class,Class.forName("hl8",true,l),Class.forName("uv7",true,l),o18,int.class,int.class)
    .invoke(null,parts.size(),defaultModifier,horizontal,vertical,lineCenter,0,0,null,composable,composer,0x6000d80,0xe0);
  }catch(Exception error){throw new IllegalStateException("Cannot compose original inline word gap",error);}
 }
}
