package com.duoaero.nativebase;

/** Isolated diagnostic: size named tokens, preserving default symbolic tokens. */
public final class NativeNamedTokenSizing {
 private static final ThreadLocal<Boolean> NAMED_ROW=new ThreadLocal<>();
 private static Object bankClipBlock;
 private NativeNamedTokenSizing(){}
 static boolean active(){return Boolean.TRUE.equals(NAMED_ROW.get());}
 static boolean enter(boolean named){boolean old=Boolean.TRUE.equals(NAMED_ROW.get());if(named)NAMED_ROW.set(Boolean.TRUE);else NAMED_ROW.remove();return old;}
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
 /** Clip only the named answer bank to its own bounds while it scrolls. */
 public static Object clipBank(java.util.List<?> tokens,Object modifier){
  if(!NativeCourseBridge.hasLocalCourse()||tokens==null||modifier==null)return modifier;
  boolean any=false;for(Object token:tokens)if(named(token)){any=true;break;}
  if(!any)return modifier;
  try{
   ClassLoader loader=modifier.getClass().getClassLoader();
   Class<?> callback=Class.forName("qqh",true,loader),mod=Class.forName("z5q",true,loader);
   Object block;
   synchronized(NativeNamedTokenSizing.class){
    if(bankClipBlock==null)bankClipBlock=java.lang.reflect.Proxy.newProxyInstance(loader,new Class<?>[]{callback},(proxy,method,args)->{
     if(method.getName().equals("invoke")){
      Object scope=args[0];scope.getClass().getMethod("d",boolean.class).invoke(scope,true);
      return Class.forName("xv80",true,loader).getField("a").get(null);
     }
     if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
     if(method.getName().equals("equals"))return proxy==args[0];
     if(method.getName().equals("toString"))return "DuoAero named bank clip";
     return null;
    });
    block=bankClipBlock;
   }
   return Class.forName("yuk",true,loader).getMethod("j",mod,callback).invoke(null,modifier,block);
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot clip named answer bank",error);}
 }

}

