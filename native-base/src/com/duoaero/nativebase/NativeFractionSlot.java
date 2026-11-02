package com.duoaero.nativebase;

import java.lang.ref.WeakReference;
import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;
import java.util.WeakHashMap;
import java.util.concurrent.atomic.AtomicLong;

/** Experimental: original fraction figure with original interactive slots. */
public final class NativeFractionSlot {
 private static final String PREFIX="duoaero-fracslot:";
 private static final AtomicLong NEXT=new AtomicLong();
 private static final WeakHashMap<Object,Context> LIVE=new WeakHashMap<>();
 private static final Map<String,WeakReference<Object>> KEYS=new HashMap<>();
 private static final class Context {
  final Object scope,slot;final Method render;final int first;
  Context(Object scope,Object slot,Method render,int first){this.scope=scope;this.slot=slot;this.render=render;this.first=first;}
 }
 private NativeFractionSlot(){}
 /** Original exponentiation figure with an interactive base and fixed power. */
 public static Object createPower(Object template,Object scope,Object slot,Method render,int first,String power) throws Exception {
  if(!power.matches("[0-9]{1,2}"))throw new IllegalArgumentException("Unsupported fixed power");
  ClassLoader l=template.getClass().getClassLoader();Class<?> ui=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState",true,l);
  Class<?> cls=template.getClass(),entityClass=Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity",true,l);
  Constructor<?> latex=cls.getConstructor(String.class,float.class,Class.forName("b8t",true,l),boolean.class,
      Class.forName("com.duolingo.core.math.models.network.LatexColorConfig",true,l),entityClass,boolean.class);
  String key=Long.toString(NEXT.incrementAndGet());
  Object entity=Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity$Algebraic",true,l)
      .getConstructor(String.class).newInstance("duoaero:power-slot");
  Object base=latex.newInstance(PREFIX+key+":0",cls.getField("b").getFloat(template),cls.getField("c").get(template),
      cls.getField("d").getBoolean(template),cls.getField("e").get(template),entity,cls.getField("g").getBoolean(template));
  Object exponentRange=Class.forName("b8t",true,l).getConstructor(Object.class,Object.class).newInstance(Float.valueOf(22f),Float.valueOf(22f));
  Object exponent=latex.newInstance("\\scriptstyle "+power,22f,exponentRange,
      cls.getField("d").getBoolean(template),cls.getField("e").get(template),entity,cls.getField("g").getBoolean(template));
  Object figure=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState$Exponentiation",true,l)
      .getConstructor(ui,ui,String.class,entityClass).newInstance(base,exponent,"power",null);
  synchronized(LIVE){KEYS.entrySet().removeIf(e->e.getValue().get()==null);LIVE.put(figure,new Context(scope,slot,render,first));KEYS.put(key,new WeakReference<>(figure));}
  return figure;
 }
 public static Object create(Object template,Object scope,Object slot,Method render,int first) throws Exception {
  return createFraction(template,scope,slot,render,first,false,false);
 }
 public static Object createSquaredNumerator(Object template,Object scope,Object slot,Method render,int first) throws Exception {
  return createFraction(template,scope,slot,render,first,true,false);
 }
 /** Numerator squared; fixed two multiplying the denominator quantity. */
 public static Object createSquaredOverTwice(Object template,Object scope,Object slot,Method render,int first) throws Exception {
  return createFraction(template,scope,slot,render,first,true,true);
 }
 /** Original fraction and horizontal sequences with two or three factors. */
 public static Object createProduct(Object template,Object scope,Object slot,Method render,int first,int numeratorCount,int denominatorCount) throws Exception {
  if(numeratorCount<1||numeratorCount>2||denominatorCount<1||denominatorCount>2||numeratorCount+denominatorCount<3)throw new IllegalArgumentException("Unsupported fraction product");
  ClassLoader l=template.getClass().getClassLoader();Class<?> ui=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState",true,l);
  Class<?> cls=template.getClass(),entityClass=Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity",true,l);
  Constructor<?> latex=cls.getConstructor(String.class,float.class,Class.forName("b8t",true,l),boolean.class,Class.forName("com.duolingo.core.math.models.network.LatexColorConfig",true,l),entityClass,boolean.class);
  Class<?> state=Class.forName("com.duolingo.core.math.models.figure.MathFigureScaleState",true,l),scale=Class.forName("com.duolingo.core.math.models.figure.MathFigureScaleInfo",true,l);
  Object scaleInfo=scale.getConstructor(state,boolean.class).newInstance(state.getField("PROMPT_DEFAULT").get(null),false);
  Class<?> placement=Class.forName("com.duolingo.core.math.models.figure.MathFigurePlacement",true,l),orientation=Class.forName("com.duolingo.core.math.models.network.challenge.MathFigureOrientation",true,l),promptType=Class.forName("com.duolingo.core.math.models.figure.MathPromptType",true,l);
  Constructor<?> sequence=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState$Sequence",true,l).getConstructor(placement,java.util.List.class,orientation,scale,boolean.class,promptType);
  String key=Long.toString(NEXT.incrementAndGet());Object[] sides=new Object[2];int ordinal=0;
  for(int side=0;side<2;side++){
   int count=side==0?numeratorCount:denominatorCount;java.util.ArrayList<Object> factors=new java.util.ArrayList<>();
   for(int i=0;i<count;i++){
    Object entity=Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity$Algebraic",true,l).getConstructor(String.class).newInstance("duoaero:fraction-factor");
    if(i>0)factors.add(latex.newInstance("\\times",cls.getField("b").getFloat(template),cls.getField("c").get(template),cls.getField("d").getBoolean(template),cls.getField("e").get(template),entity,cls.getField("g").getBoolean(template)));
    factors.add(latex.newInstance(PREFIX+key+":"+(ordinal++),cls.getField("b").getFloat(template),cls.getField("c").get(template),cls.getField("d").getBoolean(template),cls.getField("e").get(template),entity,cls.getField("g").getBoolean(template)));
   }
   if(count==1)sides[side]=factors.get(0);
   else{
    Constructor<?> token=Class.forName("com.duolingo.core.math.models.figure.SequenceTokenUiState",true,l).getConstructor(float.class,ui);
    java.util.ArrayList<Object> tokens=new java.util.ArrayList<>();
    for(Object factor:factors)tokens.add(token.newInstance(2f,factor));
    sides[side]=sequence.newInstance(placement.getField("PROMPT").get(null),tokens,orientation.getField("HORIZONTAL").get(null),scaleInfo,false,promptType.getField("NON_IDENTITY").get(null));
   }
  }
  float padding=Math.max(2f,cls.getField("b").getFloat(template)*.14f);
  Object fraction=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState$Fraction",true,l).getConstructor(ui,ui,float.class,float.class,String.class,scale,boolean.class,entityClass).newInstance(sides[0],sides[1],padding,padding,"fraction",scaleInfo,false,null);
  synchronized(LIVE){KEYS.entrySet().removeIf(e->e.getValue().get()==null);LIVE.put(fraction,new Context(scope,slot,render,first));KEYS.put(key,new WeakReference<>(fraction));}
  return fraction;
 }
 private static Object createFraction(Object template,Object scope,Object slot,Method render,int first,boolean squaredNumerator,boolean twiceDenominator) throws Exception {
  ClassLoader l=template.getClass().getClassLoader();Class<?> ui=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState",true,l);
  Class<?> cls=template.getClass(),entityClass=Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity",true,l);
  Constructor<?> latex=cls.getConstructor(String.class,float.class,Class.forName("b8t",true,l),boolean.class,
      Class.forName("com.duolingo.core.math.models.network.LatexColorConfig",true,l),entityClass,boolean.class);
  String key=Long.toString(NEXT.incrementAndGet());Object[] contents=new Object[2];
  for(int i=0;i<2;i++){
   Object entity=Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity$Algebraic",true,l)
       .getConstructor(String.class).newInstance("duoaero:fraction-slot");
   contents[i]=latex.newInstance(PREFIX+key+":"+i,cls.getField("b").getFloat(template),cls.getField("c").get(template),
       cls.getField("d").getBoolean(template),cls.getField("e").get(template),entity,cls.getField("g").getBoolean(template));
  }
  if(squaredNumerator){
   Object entity=Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity$Algebraic",true,l)
       .getConstructor(String.class).newInstance("duoaero:fixed-square");
   Object exponentRange=Class.forName("b8t",true,l).getConstructor(Object.class,Object.class).newInstance(Float.valueOf(22f),Float.valueOf(22f));
   Object exponent=latex.newInstance("\\scriptstyle 2",22f,exponentRange,
       cls.getField("d").getBoolean(template),cls.getField("e").get(template),entity,cls.getField("g").getBoolean(template));
   contents[0]=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState$Exponentiation",true,l)
       .getConstructor(ui,ui,String.class,entityClass).newInstance(contents[0],exponent,"power",null);
  }
  Class<?> state=Class.forName("com.duolingo.core.math.models.figure.MathFigureScaleState",true,l);
  Class<?> scale=Class.forName("com.duolingo.core.math.models.figure.MathFigureScaleInfo",true,l);
  Object scaleInfo=scale.getConstructor(state,boolean.class).newInstance(state.getField("PROMPT_DEFAULT").get(null),false);
  if(twiceDenominator){
   Class<?> placement=Class.forName("com.duolingo.core.math.models.figure.MathFigurePlacement",true,l),orientation=Class.forName("com.duolingo.core.math.models.network.challenge.MathFigureOrientation",true,l),promptType=Class.forName("com.duolingo.core.math.models.figure.MathPromptType",true,l);
   Object entity=Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity$Algebraic",true,l).getConstructor(String.class).newInstance("duoaero:fixed-two");
   Object two=latex.newInstance("2\\times",cls.getField("b").getFloat(template),cls.getField("c").get(template),cls.getField("d").getBoolean(template),cls.getField("e").get(template),entity,cls.getField("g").getBoolean(template));
   Constructor<?> token=Class.forName("com.duolingo.core.math.models.figure.SequenceTokenUiState",true,l).getConstructor(float.class,ui);
   java.util.ArrayList<Object> tokens=new java.util.ArrayList<>();tokens.add(token.newInstance(2f,two));tokens.add(token.newInstance(2f,contents[1]));
   contents[1]=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState$Sequence",true,l).getConstructor(placement,java.util.List.class,orientation,scale,boolean.class,promptType).newInstance(placement.getField("PROMPT").get(null),tokens,orientation.getField("HORIZONTAL").get(null),scaleInfo,false,promptType.getField("NON_IDENTITY").get(null));
  }
  float padding=Math.max(2f,cls.getField("b").getFloat(template)*.14f);
  Object fraction=Class.forName("com.duolingo.core.math.models.figure.MathFigureUiState$Fraction",true,l)
     .getConstructor(ui,ui,float.class,float.class,String.class,scale,boolean.class,entityClass)
     .newInstance(contents[0],contents[1],padding,padding,"fraction",scaleInfo,false,null);
  synchronized(LIVE){
   KEYS.entrySet().removeIf(e->e.getValue().get()==null);
   LIVE.put(fraction,new Context(scope,slot,render,first));KEYS.put(key,new WeakReference<>(fraction));
  }
  return fraction;
 }
 public static boolean render(Object figure,Object composer,int flags){
  if(figure==null||!figure.getClass().getName().endsWith("MathFigureUiState$LatexString"))return false;
  try{
   String text=(String)figure.getClass().getField("a").get(figure);if(!text.startsWith(PREFIX))return false;
   String[] part=text.substring(PREFIX.length()).split(":",2);if(part.length!=2)throw new IllegalStateException("Invalid fraction slot marker");
   Context context;
   synchronized(LIVE){WeakReference<Object> reference=KEYS.get(part[0]);Object key=reference==null?null:reference.get();context=key==null?null:LIVE.get(key);}
   if(context==null)throw new IllegalStateException("Fraction slot context no longer exists");
   int offset=Integer.parseInt(part[1]);if(offset<0||offset>3)throw new IllegalStateException("Invalid fraction slot position");
   context.render.invoke(context.slot,context.scope,Integer.valueOf(context.first+offset),composer,Integer.valueOf(0));
   return true;
  }catch(Exception failure){throw new IllegalStateException("Cannot render native fraction slot",failure);}
 }
}
