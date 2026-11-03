package com.duoaero.nativebase;

/** Isolated diagnostic: size named tokens, preserving default symbolic tokens. */
public final class NativeNamedTokenSizing {
 private static final ThreadLocal<Boolean> NAMED_ROW=new ThreadLocal<>();
 private NativeNamedTokenSizing(){}
 static boolean enter(boolean named){boolean old=Boolean.TRUE.equals(NAMED_ROW.get());if(named)NAMED_ROW.set(Boolean.TRUE);return old;}
 static void exit(boolean old){if(old)NAMED_ROW.set(Boolean.TRUE);else NAMED_ROW.remove();}
 private static boolean named(Object token){
  if(!NativeCourseBridge.hasLocalCourse())return false;
  if(Boolean.TRUE.equals(NAMED_ROW.get()))return true;
  if(token==null||!token.getClass().getName().equals("qp3"))return false;
  try{
   Object figure=token.getClass().getField("b").get(token);
   if(figure==null||!figure.getClass().getName().endsWith("MathFigureUiState$AttributedText"))return false;
   Object entity=figure.getClass().getField("f").get(figure);
   if(entity==null||!entity.getClass().getName().endsWith("MathEntity$Algebraic"))return false;
   Object raw=entity.getClass().getField("a").get(entity);
   return raw instanceof String && ((String)raw).startsWith("duoaero:");
  }catch(ReflectiveOperationException ignored){return false;}
 }
 public static float height(Object token,float original){return named(token)?96f:original;}
 public static float width(Object token,float original){return named(token)?Math.min(original,160f):original;}
}
