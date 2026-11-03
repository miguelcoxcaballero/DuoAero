package com.duoaero.nativebase;
import android.app.Application;
import android.util.Log;
import org.json.*;
import java.lang.reflect.*;
import java.io.*;
import java.util.*;

/** Development-only schema probe. Never reads or records authentication headers. */
public final class NativeCourseBridge {
 public static volatile boolean localOnly = false;
 public static volatile boolean captureNativeFlows = false;
 // The local course marks a viewed formula as a miss only when checked.
 public static volatile boolean formulaHintRetryEnabled = true;
 private static final Map<Object,Boolean> hintedFragments=Collections.synchronizedMap(new WeakHashMap<>());
 public static void formulaTipOpened(){
  if(!formulaHintRetryEnabled||!hasLocalCourse())return;
  try{
   android.app.Activity activity=NativeFormulaFeedback.currentSession();
   if(activity==null)return;
   Object manager=activity.getClass().getMethod("getSupportFragmentManager").invoke(activity);
   Object fragment=visibleMathFragment(manager,0);
   if(fragment!=null){hintedFragments.put(fragment,Boolean.TRUE);Log.i("DuoAeroNative","Formula hint opened");}
  }catch(ReflectiveOperationException error){Log.e("DuoAeroNative","Cannot bind hint to fragment",error);}
 }
 private static Object visibleMathFragment(Object manager,int depth)throws ReflectiveOperationException{
  if(depth>10)return null;
  Object store=manager.getClass().getField("c").get(manager);
  for(Object fragment:(List<?>)store.getClass().getMethod("f").invoke(store)){
   if(!(Boolean)fragment.getClass().getMethod("isVisible").invoke(fragment))continue;
   if(fragment.getClass().getName().equals("com.duolingo.session.challenges.math.MathBlobSelectOneFragment"))return fragment;
   Object found=visibleMathFragment(fragment.getClass().getMethod("getChildFragmentManager").invoke(fragment),depth+1);
   if(found!=null)return found;
  }
  return null;
 }
 /** Called only by the original Check event, never on hint open or selection. */
 public static Object formulaHintGuess(Object fragment,Object guess){
  if(!formulaHintRetryEnabled||!hasLocalCourse()||fragment==null||guess==null||hintedFragments.remove(fragment)==null)return guess;
  try{
   Class<?> type=guess.getClass();
   if(!type.getName().endsWith("FragmentGuess$MathBlobCorrectness"))return guess;
   Object state=type.getField("a").get(guess);
   if(!((Enum<?>)state).name().equals("CORRECT"))return guess;
   Object incorrect=state.getClass().getField("INCORRECT").get(null);
   for(Constructor<?> constructor:type.getConstructors())if(constructor.getParameterTypes().length==7){
    Object value=constructor.newInstance(incorrect,type.getField("b").get(guess),type.getField("c").get(guess),
      type.getField("d").get(guess),type.getField("e").get(guess),type.getField("f").get(guess),type.getField("g").get(guess));
    Log.i("DuoAeroNative","Hinted answer marked for original retry at Check");return value;
   }
  }catch(ReflectiveOperationException error){Log.e("DuoAeroNative","Cannot apply hint retry",error);}
  return guess;
 }
 // A locally enrolled Aerospace learner must be able to open the original
 // home with zero XP. Enrollment is set only after both native path writes.
 public static volatile boolean localCourseInstalled = false;
 public static volatile boolean serveLocalCourse = false;
 private static volatile String diagnosticProfile = null;
 public static String setDiagnosticProfile(String value)throws JSONException {
  JSONObject user=new JSONObject(value);
  String username=user.getString("username");
  if(user.getLong("id")!=1||!("aerospace-local-test".equals(username)||"aerospace-learner".equals(username)))throw new IllegalArgumentException("Only the local Aerospace profile is supported");
  // Both original profile readers share /users/1: the legacy User model and
  // the nested UserStreak resource. A missing longestStreak becomes the
  // all-null 'unavailable' sentinel on refresh, erasing the seeded zero streak.
  JSONObject streak=user.optJSONObject("streakData");
  if(streak==null){streak=new JSONObject();user.put("streakData",streak);}
  if(!streak.has("length"))streak.put("length",0);
  if(!streak.has("updatedTimestamp"))streak.put("updatedTimestamp",0);
  if(!streak.has("updatedTimeZone"))streak.put("updatedTimeZone","UTC");
  if(!streak.has("longestStreak")||streak.isNull("longestStreak"))streak.put("longestStreak",new JSONObject().put("length",0));
  diagnosticProfile=user.toString();
  return diagnosticProfile;
 }
 public static boolean hasLocalCourse(){return localOnly && localCourseInstalled;}
 /** Keep the original bank's rows/cards, but fit long Aerospace word blocks. */
 public static int bankColumns(java.util.List<?> tokens,float measuredWidth,int original){
  if(!hasLocalCourse())return original;
  try{
   Application app=(Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
   android.util.DisplayMetrics metrics=app.getResources().getDisplayMetrics();
   android.text.TextPaint paint=new android.text.TextPaint();
   paint.setTypeface(android.graphics.Typeface.create("sans-serif",android.graphics.Typeface.BOLD));
   paint.setTextSize(20*metrics.scaledDensity);
   float width=Math.max(56,measuredWidth)*metrics.density;
   for(Object token:tokens){
    if(!token.getClass().getName().equals("qp3"))continue;
    Object figure=field(token,"b");
    if(figure==null)continue;
    String label=formulaAccessibility(figure);
    if(label==null)label=(String)figure.getClass().getMethod("r1").invoke(figure);
    if(label!=null)width=Math.max(width,paint.measureText(label)+32*metrics.density);
   }
   float available=metrics.widthPixels-28*metrics.density,gap=8*metrics.density;
   return Math.max(1,Math.min(original,(int)((available+gap)/(width+gap))));
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot measure original Aerospace bank",error);}
 }
 /** Retry only this course's explicitly marked pure function on the original
  * JS engine. Preserve its result; a missing result remains a grading error.
  */
 public static String retryOriginalEvaluation(Object evaluator,Object coroutine,String previous){
  if(previous!=null||!hasLocalCourse()||android.os.Looper.myLooper()==android.os.Looper.getMainLooper())return previous;
  try{
   String function=(String)field(coroutine,"l"),variables=(String)field(coroutine,"m");
   if(function==null||!function.startsWith("/*duoaero-pure-choice*/"))return null;
   String script="JSON.stringify((\n"+function+"\n)("+variables+"));";
   ClassLoader loader=evaluator.getClass().getClassLoader();
   Object type=Class.forName("com.duolingo.feature.math.javascript.ExecutionContextType",true,loader).getField("SESSION").get(null);
   for(int attempt=1;attempt<=6;attempt++){
    Thread.sleep(250L*attempt);
    Object context=((Map<?,?>)field(evaluator,"f")).get(type);
    if(context==null)continue;
    context.getClass().getField("b").set(context,field(coroutine,"h"));
    try{
     String result=(String)context.getClass().getMethod("b",String.class).invoke(context,script);
     if(result!=null){Log.i("DuoAeroNative","Original pure grading returned a result after retry "+attempt);return result;}
    }catch(InvocationTargetException failure){reportGradingFailure(failure.getCause());}
   }
   Log.e("DuoAeroNative","Original pure grading still has no result after bounded retries");
   return null;
  }catch(InterruptedException interrupted){Thread.currentThread().interrupt();return null;}
  catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot retry original grading engine",error);}
 }
 public static void reportGradingFailure(Throwable error){
  if(localOnly&&captureLocalRequests)Log.e("DuoAeroNative","Original Math grader failed",error);
 }
 public static void reportRuntimeFailure(Object owner,int priority,Throwable error){
  if(!localOnly||!captureLocalRequests||priority<5||error==null)return;
  // Synthetic runtime diagnosis only. Do not export exception messages,
  // request bodies, headers, query strings or arbitrary app data.
  StringBuilder report=new StringBuilder("Original runtime failure owner=").append(owner);
  for(int cause=0;error!=null&&cause<6;cause++,error=error.getCause()){
   report.append("\n").append(error.getClass().getName());
   StackTraceElement[] frames=error.getStackTrace();
   for(int i=0;i<Math.min(frames.length,35);i++)report.append("\n at ").append(frames[i]);
  }
  Log.e("DuoAeroNative",report.toString());
 }
 public static long sandboxStartupTimeoutSeconds(){return hasLocalCourse()?20L:3L;}
 public static void reportSandboxStartupTimeout(){
  if(hasLocalCourse())Log.e("DuoAeroNative","Original JavaScript sandbox startup timed out; no grading context created");
 }
 private static final Map<android.view.View,Boolean> formulaLabels=new WeakHashMap<>();
 /** Fit longer labels in the original square matching cards. */
 public static Object fitMatchFigure(android.view.View view,Object figure){
  if(!hasLocalCourse()||figure==null||!figure.getClass().getName().endsWith("MathFigureUiState$AttributedText"))return figure;
  boolean match=false;
  for(android.view.ViewParent parent=view.getParent();parent instanceof android.view.View;parent=parent.getParent())
   if(parent.getClass().getName().equals("com.duolingo.session.challenges.match.MatchButtonView")){match=true;break;}
  if(!match)return figure;
  try{
   String label=(String)figure.getClass().getMethod("r1").invoke(figure);
   if(label==null||label.length()<11)return figure;
   ClassLoader loader=figure.getClass().getClassLoader();
   Class<?> state=Class.forName("com.duolingo.core.math.models.figure.MathFigureScaleState",true,loader);
   Class<?> scale=Class.forName("com.duolingo.core.math.models.figure.MathFigureScaleInfo",true,loader);
   Object smaller=state.getField(label.length()>20?"CONTENT_X_SMALL":"CONTENT_SMALL").get(null);
   Object info=scale.getConstructor(state,boolean.class).newInstance(smaller,false);
   Class<?> style=Class.forName("com.duolingo.core.math.models.figure.MathTextStyle",true,loader);
   Class<?> entity=Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity",true,loader);
   Class<?> type=figure.getClass();
   Object originalStyle=type.getField("b").get(figure);
   int font=label.length()>20?11:14;
   Method sp=Class.forName("u6z",true,loader).getMethod("p",int.class);
   long fontSize=(Long)sp.invoke(null,font),lineHeight=(Long)sp.invoke(null,font+3);
   Object fittedStyle=style.getConstructor(long.class,long.class,
      Class.forName("com.duolingo.core.math.models.figure.MathTextStyle$MathFontWeight",true,loader),
      Class.forName("com.duolingo.core.math.models.figure.MathTextStyle$MathFontFamily",true,loader),
      Class.forName("com.duolingo.core.math.models.figure.MathTextStyle$MathTextAlignment",true,loader))
    .newInstance(fontSize,lineHeight,style.getField("c").get(originalStyle),style.getField("d").get(originalStyle),style.getField("e").get(originalStyle));
   if(captureLocalRequests)Log.i("DuoAeroNative","Fitted native matching label, characters="+label.length());
   return type.getConstructor(java.util.List.class,style,scale,boolean.class,String.class,entity)
    .newInstance(type.getField("a").get(figure),fittedStyle,info,
       type.getField("d").getBoolean(figure),type.getField("e").get(figure),type.getField("f").get(figure));
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot fit native matching label",error);}
 }
 public static synchronized void bindFormulaAccessibility(android.view.View view,Object figure){
  String label=formulaAccessibility(figure);
  for(int depth=0;view!=null&&depth<12;depth++){
   boolean target=depth==0;
   if(view.getId()!=android.view.View.NO_ID)try{target|="mathCard".equals(view.getResources().getResourceEntryName(view.getId()));}catch(android.content.res.Resources.NotFoundException ignored){}
   if(target){
    if(label!=null){view.setContentDescription(label);formulaLabels.put(view,Boolean.TRUE);}
    else if(formulaLabels.remove(view)!=null)view.setContentDescription(null);
   }
   android.view.ViewParent parent=view.getParent();view=parent instanceof android.view.View?(android.view.View)parent:null;
  }
 }
 /** Give original native cards a semantic label for marked LaTeX blocks. */
 public static String formulaAccessibility(Object figure){
  if(!hasLocalCourse()||figure==null||!figure.getClass().getName().endsWith("MathFigureUiState$LatexString"))return null;
  try{
   Object entity=field(figure,"f");if(entity==null)return null;
   String kind=entity.getClass().getName();
   if(kind.endsWith("MathEntity$Algebraic")){
    String name=(String)field(entity,"a");return name.startsWith("duoaero:")?name.substring(8):null;
   }
   if(kind.endsWith("MathEntity$Symbol")){
    String name=((Enum<?>)field(entity,"a")).name();
    if(name.equals("MULTIPLICATION"))return "×";
    if(name.equals("DIVISION"))return "÷";
    if(name.equals("ADDITION"))return "+";
    if(name.equals("EQUALITY"))return "=";
   }
   return null;
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot describe Aerospace formula block",error);}
 }
 /** Decode explicitly marked formula figures using the original LaTeX renderer.
  * The original optional MathEntity is retained for native slot grading.
  */
 public static Object latexFigure(Object factory,Object optionalEntity,Object taggedText){
  if(!hasLocalCourse())return null;
  try{
   String value=(String)field(taggedText,"a");
   String marker="duoaero-latex:";
   if(!value.startsWith(marker))return null;
   ClassLoader loader=factory.getClass().getClassLoader();
   Object entity=factory.getClass().getMethod("l",Class.forName("com.duolingo.core.math.models.network.OptionalMathEntity",true,loader)).invoke(factory,optionalEntity);
   return Class.forName("com.duolingo.core.math.models.network.challenge.MathFigure$LatexString",true,loader)
    .getConstructor(String.class,boolean.class,Class.forName("com.duolingo.core.math.models.network.challenge.MathEntity",true,loader))
    .newInstance(value.substring(marker.length()),false,entity);
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot convert Aerospace formula figure",error);}
 }
 public static Object pathHeaderText(Object index,String section,Object original){
  String title=pathTopicTitle(index,section,null);
  if(title==null)return original;
  try{return Class.forName("wg90",true,index.getClass().getClassLoader()).getConstructor(String.class).newInstance(title);}
  catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot bind original Aerospace header text",error);}
 }
 private static volatile String[] pathTopics,pathTopics2;
 public static String pathTopicTitle(Object index,String section,String original){
  if(!localOnly||index==null||!("DUOAERO_MIDTERM1".equals(section)||"DUOAERO_MIDTERM2".equals(section)))return original;
  try{
   boolean second="DUOAERO_MIDTERM2".equals(section);
   String[] topics=second?pathTopics2:pathTopics;
   if(topics==null){
    Application app=(Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
    JSONArray units=new JSONObject(asset(app,second?"duoaero/course/section-2.json":"duoaero/course/section.json")).getJSONArray("units");
    topics=new String[units.length()];
    for(int i=0;i<topics.length;i++)topics[i]=units.getJSONObject(i).getString("teachingObjective");
    if(second)pathTopics2=topics;else pathTopics=topics;
   }
   int position=(Integer)field(index,"a");
   return position>=0&&position<topics.length?topics[position]:original;
  }catch(Exception error){throw new IllegalStateException("Cannot bind original Aerospace topic header",error);}
 }
 /** Compare actual native slots for explicitly marked Aerospace symbolic tasks.
  * Original numeric expression grading remains the fallback (null result).
  */
 public static Object gradeSymbolicExpression(Object viewModel,Object pair,boolean ready){
  if(!hasLocalCourse())return null;
  try{
   Object prompt=field(viewModel,"b"),input=field(prompt,"b"),content=field(input,"a"),spec=field(content,"a");
   List<?> rules=(List<?>)field(spec,"a");
   if(rules.size()!=1)return null;
   List<?> exact=(List<?>)field(rules.get(0),"b");
   if(exact.size()!=1)return null;
   Object expected=field(exact.get(0),"a");
   List<String> required=new ArrayList<>();
   if(expected.getClass().getName().endsWith("Entity$MathList")){
    for(Object term:(List<?>)field(field(expected,"a"),"a"))required.add(networkTerm(term));
   }else required.add(networkTerm(expected));
   boolean scoped=false;for(String term:required)if(term!=null&&term.startsWith("duoaero:"))scoped=true;
   if(!scoped)return null;
   List<String> selected=new ArrayList<>();
   for(Object slot:(List<?>)field(pair,"a")){
    if(!slot.getClass().getName().equals("qp3")){selected.add(null);continue;}
    Object figure=field(slot,"b");
    if(!figure.getClass().getName().endsWith("MathFigureUiState$AttributedText")&&!figure.getClass().getName().endsWith("MathFigureUiState$LatexString")){selected.add(null);continue;}
    Object term=field(figure,"f");
    if(term==null){selected.add(null);continue;}
    String name=term.getClass().getName();
    if(name.endsWith("MathEntity$Algebraic"))selected.add((String)field(term,"a"));
    else if(name.endsWith("MathEntity$Symbol"))selected.add("symbol:"+((Enum<?>)field(term,"a")).name());
    else selected.add(null);
   }
   boolean correct=ready&&matchesFormulaTerms(required,selected);
   return Class.forName("com.duolingo.core.session.FragmentGuess$Correctness",true,viewModel.getClass().getClassLoader())
    .getConstructor(boolean.class,String.class,String.class).newInstance(correct,null,null);
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot grade native Aerospace expression",error);}
 }
 public static boolean matchesFormulaTerms(List<String> required,List<String> selected){
  if(required.isEmpty()||required.size()!=selected.size()||required.contains(null)||selected.contains(null))return false;
  if(required.equals(selected))return true;
  // Multiplication and addition of these scalar components commute. Division
  // and mixed operators must keep their positions; missing/extra terms fail.
  if(required.size()<3||required.size()%2==0)return false;
  String op=required.get(1);
  if(!op.equals("symbol:MULTIPLICATION")&&!op.equals("symbol:ADDITION"))return false;
  List<String> left=new ArrayList<>(),right=new ArrayList<>();
  for(int i=0;i<required.size();i++){
   if(i%2==1){if(!op.equals(required.get(i))||!op.equals(selected.get(i)))return false;}
   else{left.add(required.get(i));right.add(selected.get(i));}
  }
  Collections.sort(left);Collections.sort(right);return left.equals(right);
 }
 private static String networkTerm(Object term)throws ReflectiveOperationException {
  String name=term.getClass().getName();
  if(name.endsWith("Entity$Variable"))return (String)field(field(field(term,"a"),"a"),"a");
  if(name.endsWith("Entity$Symbol"))return "symbol:"+((Enum<?>)field(term,"a")).name();
  return null;
 }
 private static Object field(Object value,String name)throws ReflectiveOperationException{return value.getClass().getField(name).get(value);}
 /** Keep the native figure and cards, bounding only the prompt's scroll area. */
 public static Object scrollPrompt(Object figure,Object modifier,Object composer){
  if(!hasLocalCourse()||figure==null||!figure.getClass().getName().equals("com.duolingo.core.math.models.figure.MathFigureUiState$LatexString"))return modifier;
  try{
   ClassLoader loader=figure.getClass().getClassLoader();
   Class<?> compose=Class.forName("cuh",true,loader);
   String prompt=(String)figure.getClass().getField("a").get(figure);
   compose.getMethod("f0",int.class).invoke(composer,0x44554145^prompt.hashCode());
   try{
    Application app=(Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
    float maximum=Math.max(120f,Math.min(240f,app.getResources().getConfiguration().screenHeightDp*0.30f));
    Class<?> mod=Class.forName("z5q",true,loader),state=Class.forName("qxz",true,loader),scroll=Class.forName("kqp",true,loader);
    Object bounded=Class.forName("androidx.compose.foundation.layout.b",true,loader).getMethod("i",mod,float.class,float.class).invoke(null,modifier,Float.NaN,maximum);
    Object position=scroll.getMethod("R",int.class,Class.forName("o18",true,loader),int.class).invoke(null,0,composer,0);
    return scroll.getMethod("d0",mod,state,boolean.class,int.class).invoke(null,bounded,position,true,0);
   }finally{compose.getMethod("q",boolean.class).invoke(composer,false);}
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot bind original prompt scrolling",error);}
 }
 /** Experimental: retain original build controls while limiting very long local equations. */
 public static Object scrollLongBuildSpace(java.util.List<?> items,Object modifier,Object composer){
  if(!hasLocalCourse()||items==null||items.size()<7)return modifier;
  try{
   ClassLoader loader=composer.getClass().getClassLoader();
   Class<?> compose=Class.forName("cuh",true,loader);
   compose.getMethod("f0",int.class).invoke(composer,0x44554146);
   try{
    Application app=(Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
    float maximum=Math.max(160f,Math.min(300f,app.getResources().getConfiguration().screenHeightDp*0.38f));
    Class<?> mod=Class.forName("z5q",true,loader),state=Class.forName("qxz",true,loader),scroll=Class.forName("kqp",true,loader);
    Object bounded=Class.forName("androidx.compose.foundation.layout.b",true,loader).getMethod("i",mod,float.class,float.class).invoke(null,modifier,Float.NaN,maximum);
    Object position=scroll.getMethod("R",int.class,Class.forName("o18",true,loader),int.class).invoke(null,0,composer,0);
    return scroll.getMethod("d0",mod,state,boolean.class,int.class).invoke(null,bounded,position,true,0);
   }finally{compose.getMethod("q",boolean.class).invoke(composer,false);}
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot bind experimental build-space scrolling",error);}
 }
 private static final Map<String,Object> namedFlows=new LinkedHashMap<>();
 public static synchronized void recordFlow(Object flow,String name){
  if(!localOnly||!captureNativeFlows||flow==null||name==null||!name.matches("[A-Za-z][A-Za-z0-9_.-]{0,100}"))return;
  if(namedFlows.containsKey(name)||namedFlows.size()<256)namedFlows.put(name,flow);
 }
 public static synchronized Map<String,Object> diagnosticFlows(){return new LinkedHashMap<>(namedFlows);}
 private static Object[] profileInputs;
 public static synchronized void recordProfileInputs(Object[] inputs){
  if(localOnly&&captureNativeFlows&&inputs!=null&&inputs.length==15)profileInputs=inputs.clone();
 }
 public static synchronized Object[] diagnosticProfileInputs(){return profileInputs==null?new Object[0]:profileInputs.clone();}

 public static volatile boolean captureLocalRequests = false;
 private static final Map<String,Integer> localRequests = new LinkedHashMap<>();
 public static synchronized String diagnosticRequests(){return localRequests.toString();}
 private static synchronized void recordLocal(Object request)throws Exception {
  if(!captureLocalRequests)return;
  Object url=call(request,"url");String path=(String)call(url,"encodedPath");
  // Synthetic-user diagnostics only. Never collect query strings, headers,
  // bodies, auth endpoints or arbitrary external-service URLs.
  if(!path.matches("^/(?:[0-9-]+/)?(?:sessions(?:/.*)?|users/1(?:/(?:courses|sessions|path)(?:/.*)?)?|config)$"))return;
  String key=call(request,"method")+" "+path.replace("/users/1","/users/{synthetic}");
  if(localRequests.containsKey(key))localRequests.put(key,localRequests.get(key)+1);
  else if(localRequests.size()<64)localRequests.put(key,1);
 }
 public static void install(Object builder) {
  try {
   ClassLoader loader=builder.getClass().getClassLoader();
   Class<?> interceptor=Class.forName("okhttp3.Interceptor",true,loader);
   List list=(List)builder.getClass().getMethod("interceptors").invoke(builder);
   for(Object value:list)if(Proxy.isProxyClass(value.getClass())&&Proxy.getInvocationHandler(value) instanceof Probe)return;
   list.add(0,Proxy.newProxyInstance(loader,new Class[]{interceptor},new Probe()));
  }catch(Exception e){Log.e("DuoAeroNative","Cannot bind course bridge",e);}
 }
 static final class Probe implements InvocationHandler {
  public Object invoke(Object proxy,Method method,Object[] args)throws Throwable {
   if(method.getName().equals("toString"))return "DuoAero native course bridge";
   if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
   if(method.getName().equals("equals"))return proxy==args[0];
   Object chain=args[0],request=call(chain,"request");
   if(localOnly){try{recordLocal(request);}catch(Exception ignored){}try{return offlineResponse(request);}catch(Exception error){Log.e("DuoAeroNative","Local course request failed",error);throw new IOException("Cannot serve local course request",error);}}
   Object response;
   try{response=chain.getClass().getMethod("proceed",request.getClass()).invoke(chain,request);}catch(InvocationTargetException e){throw e.getCause();}
   try{
    Object url=call(request,"url");String path=(String)call(url,"encodedPath");
    String host=(String)call(url,"host");
    if(host.endsWith("duolingo.com")&&(path.contains("sessions")||path.contains("courses")||path.contains("path"))){
     Object body=response.getClass().getMethod("peekBody",long.class).invoke(response,8L*1024*1024);
     String json=(String)call(body,"string");JSONObject data=new JSONObject(json);
     JSONObject selected=new JSONObject();
     for(String key:new String[]{"challenges","adaptiveChallenges","interleavedChallenges","path","sections","units","courses","currentCourse","learningLanguage","fromLanguage","type","sessionType","id"})if(data.has(key))selected.put(key,data.get(key));
     if(selected.length()>0){
      Application app=(Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
      File folder=new File(app.getFilesDir(),"native-course-schemas");folder.mkdirs();
      File file=new File(folder,Integer.toHexString(path.hashCode())+".json");
      try(FileOutputStream out=new FileOutputStream(file)){out.write(selected.toString(2).getBytes("UTF-8"));}
      Log.i("DuoAeroNative","Course schema captured: "+file.getName()+" keys="+selected.names());
     }
    }
   }catch(Exception e){Log.d("DuoAeroNative","No course schema",e);}
   return response;
  }
 }
 static boolean isLocalAvailability(String method,String host,String path){
  return "GET".equals(method)&&"zombie.duolingo.com".equals(host)
       &&path!=null&&path.matches("/[0-9]+/android\\.json");
 }
 static Object offlineResponse(Object request)throws Exception {
  int code=503;String payload="{}";
  Object url=call(request,"url");String path=(String)call(url,"encodedPath"),method=(String)call(request,"method"),host=(String)call(url,"host");
  // The original zombie availability check uses a retrying request whose
  // response model has one boolean field, enforce_offline. This local course
  // does not depend on the original service being available. Returning its
  // explicit disabled state avoids repeated 503s without affecting updates,
  // Google/Drive, session submissions, or any other host or route.
  if(localOnly&&hasLocalCourse()&&isLocalAvailability(method,host,path)){
   if(captureLocalRequests)Log.i("DuoAeroNative","Synthetic availability check served locally: enforce_offline=false");
   return jsonResponse(request,200,"{\"enforce_offline\":false}");
  }
  // Original analytics sender oir.b accepts any2xx without reading a body.
  // This local course does not export Duolingo telemetry. Discard explicitly
  // instead of returning503 and triggering its tight event-batch retry loop.
  // Opt-in synthetic diagnostics only: report route categories and counts,
  // never batch bodies, query strings, identifiers or user data. The request
  // and its response stay unchanged; some batched operations can be stateful.
  if(localOnly&&captureLocalRequests&&method.equals("POST")&&path.equals("/2017-06-30/batch")){
   try{diagnosticBatchCategories(request);}catch(Exception ignored){Log.i("DuoAeroNative","Synthetic batch categories unavailable");}
  }
  if(localOnly&&method.equals("POST")&&(path.equals("/api/1/sync/batch")
       ||path.equals("/api/1/sync/challenge_response/batch")))return jsonResponse(request,204,"");
  if(serveLocalCourse&&hasLocalCourse()){
   Application app=(Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
   if(method.equals("GET")&&path.matches("/(?:[0-9-]+/)?config")){code=200;}
   else if(method.equals("GET")&&path.matches("/(?:[0-9-]+/)?users/1")&&diagnosticProfile!=null){code=200;payload=NativeRewards.profile(app,new JSONObject(diagnosticProfile)).toString();}
   else if(method.equals("GET")&&path.matches("/(?:[0-9-]+/)?users/1/available-features")){
    code=200;payload="{\"subscriptionFeatures\":[]}";
   }
   else if(method.equals("GET")&&path.matches("/(?:[0-9-]+/)?users/1/energy-rewards")){
    // This offline course has unlimited energy; there are no remote
    // in-lesson energy refills to consume. A valid empty native response
    // avoids repeatedly retrying a 503 while end-of-lesson UI is loading.
    // Gem chests are tracked independently by NativeChestRewards.
    code=200;payload="{\"inLessonRewards\":[]}";
   }
   else if(method.equals("GET")&&path.matches("/(?:[0-9-]+/)?users/1/energy-info")){
    // The standalone course uses unlimited energy. Return the original
    // model's full-energy state instead of retrying an unavailable service.
    code=200;payload="{\"energy\":5,\"maxEnergy\":5,\"secondsPerEnergyUnit\":3600,\"secondsUntilNextEnergyUnit\":0,\"lastEnergyUnitRegeneratedDatetime\":0,\"regeneratedEnergyUnit\":0,\"hasFullEnergy\":true}";
   }
   else if(method.equals("GET")&&path.equals("/users/1/progress")){
    // GoalsProgressResponse's original empty/default state: no assigned quests.
    code=200;
   }
   else if(method.equals("GET")&&path.matches("/(?:[0-9-]+/)?users/1/avatar-builder-config")){
    // The original resource may reload when Profile starts observing it.
    // Answer its normal request as well as seeding its native cache.
    code=200;payload=NativeLocalFeatures.avatarResponse();
    Log.i("DuoAeroNative","Original avatar configuration request served locally");
   }
   else if(method.equals("GET")&&path.matches("/(?:[0-9-]+/)?users/1/courses/MATH_BT(?:/sections/DUOAERO_MIDTERM[12])?")){
    boolean second=path.endsWith("DUOAERO_MIDTERM2");
    JSONObject info=new JSONObject(asset(app,"duoaero/course/path-info.json")),section=new JSONObject(asset(app,second?"duoaero/course/section-2.json":"duoaero/course/section.json"));
    java.util.Set<String> completed=NativeSessionStore.projectedCompletedLessons(app),chests=NativeChestRewards.ids(NativeChestRewards.snapshot(app));
    NativeCourseProgress.project(info,section,completed,chests);
    if(path.endsWith("MATH_BT"))try{
     JSONObject other=new JSONObject(asset(app,"duoaero/course/section-2.json"));
     NativeCourseProgress.project(info,other,completed,chests);
    }catch(java.io.FileNotFoundException absent){}
    code=200;payload=(path.endsWith("MATH_BT")?info:section).toString();
   }
   else if(method.equals("PUT")&&path.matches("/(?:[0-9-]+/)?sessions/[A-Za-z0-9_.-]+")){
    String sessionId=path.substring(path.lastIndexOf('/')+1);
    JSONObject catalog=sessionCatalog(app);
    if(NativeSessionId.valid(sessionId)&&catalog.has(sessionId)){
     JSONObject submission=requestJson(request);
     NativeSessionStore.record(app,sessionId,submission);
     code=200;
     Log.i("DuoAeroNative","Native session submission durably stored: "+sessionId+"; field names="+submission.names());
    }else if(NativeReviewStore.lookup(app,sessionId)!=null){
     NativeReviewStore.record(app,sessionId,requestJson(request));code=200;
    }else code=404;
   }
   else if(method.equals("POST")&&path.matches("/(?:[0-9-]+/)?sessions")){
    JSONObject input=requestJson(request);JSONObject index=sessionCatalog(app);
    String selected=null;JSONObject metadata=input.optJSONObject("metadata");
    if(metadata!=null&&index.has(metadata.optString("id")))selected=metadata.getString("id");
    if(selected==null){
     String skill=input.optString("skillId");int position=input.optInt("levelSessionIndex",0);
     for(Iterator<String> keys=index.keys();keys.hasNext();){String key=keys.next();JSONObject candidate=index.getJSONObject(key);
      if(candidate.getString("skillId").equals(skill)&&candidate.getInt("levelSessionIndex")==position){selected=key;break;}}
    }
    JSONObject review=metadata==null?null:NativeReviewStore.lookup(app,metadata.optString("id"));
    if(review!=null){payload=review.toString();code=200;Log.i("DuoAeroNative","Local original mistake review selected: "+review.getString("id"));}
    else if(selected!=null){payload=index.getJSONObject(selected).toString();code=200;Log.i("DuoAeroNative","Local original session selected: "+selected);}
    else{code=422;Log.e("DuoAeroNative","No supported local session for original request; field names="+input.names());}
   }
  }
  if(captureLocalRequests){
   Object diagnosticUrl=call(request,"url");
   Log.i("DuoAeroNative","Synthetic local response "+call(request,"method")+" "+call(diagnosticUrl,"encodedPath")+" status="+code);
  }
  return jsonResponse(request,code,payload);
 }
 // Installed assets are immutable for the lifetime of this Android process.
 // Every caller treats this shared JSONObject and its descendants as read-only.
 // Sharing the parsed catalog avoids repeated full-course parsing on the
 // session request and on each durable completion/progress refresh.
 private static JSONObject sessionCatalog;
 static synchronized JSONObject sessionCatalog(Application app)throws Exception {
  if(sessionCatalog==null)sessionCatalog=new JSONObject(asset(app,"duoaero/course/session-catalog.json"));
  return sessionCatalog;
 }
 static String asset(Application app,String path)throws IOException {
  ByteArrayOutputStream bytes=new ByteArrayOutputStream();
  try(InputStream stream=app.getAssets().open(path)){byte[] buffer=new byte[8192];int n;while((n=stream.read(buffer))!=-1)bytes.write(buffer,0,n);}
  return bytes.toString("UTF-8");
 }
 static void diagnosticBatchCategories(Object request)throws Exception {
  org.json.JSONArray requests=requestJson(request).optJSONArray("requests");
  if(requests==null){Log.i("DuoAeroNative","Synthetic batch has no request array");return;}
  Map<String,Integer> counts=new java.util.TreeMap<>();
  for(int i=0;i<requests.length();i++){
   JSONObject item=requests.optJSONObject(i);if(item==null)continue;
   String value=item.optString("url","");String route;
   try{route=new java.net.URI(value).getPath();}catch(Exception invalid){route="";}
   if(route==null)route="";
   String category=route.contains("/sessions")?"sessions":route.contains("/quests")?"quests":
       route.contains("/streak")?"streak":route.contains("/leaderboards")?"leaderboards":
       route.contains("/shop")?"shop":route.contains("/friends")?"friends":
       route.contains("/goals")?"goals":route.contains("/events")||route.contains("/tracking")||route.contains("/analytics")?"events":
       route.contains("/users/")?"other-user":"other";
   String method=item.optString("method","").toUpperCase(java.util.Locale.ROOT);
   if(!java.util.Arrays.asList("GET","POST","PUT","PATCH","DELETE").contains(method))method="UNKNOWN";
   String key=method+":"+category;counts.put(key,counts.containsKey(key)?counts.get(key)+1:1);
  }
  Log.i("DuoAeroNative","Synthetic batch route categories: "+counts);
 }
 static JSONObject requestJson(Object request)throws Exception {
  Object body=call(request,"body");if(body==null)throw new IllegalArgumentException("Missing local session request");
  ClassLoader loader=request.getClass().getClassLoader();
  // R8 removed Buffer's constructor and invokes Object.<init> in DEX.
  // Obtain a real empty Buffer through the original public ResponseBody factory.
  Class<?> responseBody=Class.forName("okhttp3.ResponseBody",true,loader);
  Object empty=responseBody.getMethod("create",String.class,Class.forName("okhttp3.MediaType",true,loader)).invoke(null,"",null);
  Object buffer=call(empty,"source");
  if(!buffer.getClass().getName().equals("bo3"))throw new IllegalStateException("Unexpected original buffer implementation");
  Class.forName("okhttp3.RequestBody",true,loader).getMethod("writeTo",Class.forName("mo3",true,loader)).invoke(body,buffer);
  byte[] bytes=(byte[])buffer.getClass().getMethod("Q0").invoke(buffer);
  if(bytes.length>1048576)throw new IllegalArgumentException("Local session request too large");
  // Parsed only for isolated session routing; never logged or exported.
  return new JSONObject(new String(bytes,"UTF-8"));
 }
 static Object jsonResponse(Object request,int code,String payload)throws Exception {
  ClassLoader loader=request.getClass().getClassLoader();
  Class<?> builderClass=Class.forName("okhttp3.Response$Builder",true,loader);
  Class<?> protocolClass=Class.forName("okhttp3.Protocol",true,loader);
  Class<?> bodyClass=Class.forName("okhttp3.ResponseBody",true,loader);
  Class<?> mediaClass=Class.forName("okhttp3.MediaType",true,loader);
  Object builder=builderClass.getConstructor().newInstance();
  builderClass.getMethod("request",request.getClass()).invoke(builder,request);
  builderClass.getMethod("protocol",protocolClass).invoke(builder,protocolClass.getField("HTTP_1_1").get(null));
  builderClass.getMethod("code",int.class).invoke(builder,code);
  builderClass.getMethod("message",String.class).invoke(builder,"Offline native-course diagnostic");
  Object body=bodyClass.getMethod("create",String.class,mediaClass).invoke(null,payload,null);
  builderClass.getMethod("body",bodyClass).invoke(builder,body);
  return builderClass.getMethod("build").invoke(builder);
 }
 static Object call(Object value,String name)throws Exception{return value.getClass().getMethod(name).invoke(value);}
}
