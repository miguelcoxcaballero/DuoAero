package com.duoaero.nativebase;

import java.lang.reflect.*;

/** Places the original prompt and interactive token slots in one native row. */
public final class NativeInlineFormula {
 private NativeInlineFormula(){}
 public static boolean begin(Object figure,Object composer){
  return begin(figure,composer,null);
 }
 public static boolean begin(Object figure,Object composer,Object suppliedModifier){
  if(!NativeCourseBridge.hasLocalCourse()||figure==null||!figure.getClass().getName().endsWith("MathFigureUiState$LatexString"))return false;
  try{
   ClassLoader loader=figure.getClass().getClassLoader();
   Class<?> compose=Class.forName("cuh",true,loader),o18=Class.forName("o18",true,loader);
   Class<?> modifiers=Class.forName("z5q",true,loader),arrangements=Class.forName("h1z",true,loader),alignment=Class.forName("b9z",true,loader);
   Object modifier=suppliedModifier!=null?suppliedModifier:Class.forName("w5q",true,loader).getField("a").get(null);
   Object policy=Class.forName("i0z",true,loader).getMethod("a",Class.forName("fv1",true,loader),Class.forName("lj0",true,loader),o18,int.class)
    .invoke(null,arrangements.getField("a").get(null),alignment.getField("l").get(null),composer,0);
   long key=(Long)Class.forName("yuk",true,loader).getMethod("f",o18).invoke(null,composer);
   Object locals=compose.getMethod("l").invoke(composer);
   modifier=arrangements.getMethod("t",o18,modifiers).invoke(null,composer,modifier);
   compose.getMethod("j0").invoke(composer);
   if(compose.getField("S").getBoolean(composer))compose.getMethod("k",Class.forName("kotlin.jvm.functions.Function0",true,loader))
    .invoke(composer,Class.forName("androidx.compose.ui.node.LayoutNode",true,loader).getField("S").get(null));
   else compose.getMethod("s0").invoke(composer);
   Class<?> updater=Class.forName("u6z",true,loader),function=Class.forName("erh",true,loader);
   Method set=updater.getMethod("v",o18,function,Object.class);
   set.invoke(null,composer,alignment.getField("B").get(null),policy);
   set.invoke(null,composer,alignment.getField("A").get(null),locals);
   set.invoke(null,composer,alignment.getField("C").get(null),Long.hashCode(key));
   updater.getMethod("u",o18,Class.forName("m97",true,loader)).invoke(null,composer,alignment.getField("D").get(null));
   set.invoke(null,composer,alignment.getField("z").get(null),modifier);
   return true;
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot compose native inline formula slots",error);}
 }
 public static void end(boolean opened,Object composer){
  if(!opened)return;
  try{composer.getClass().getMethod("q",boolean.class).invoke(composer,true);}
  catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot finish native inline formula row",error);}
 }
}
