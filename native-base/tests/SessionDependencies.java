package com.duoaero.nativebase;

import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** Observes the actual loader inputs without replacing states or readiness flags. */
final class SessionDependencies implements AutoCloseable {
 private final ClassLoader loader;
 private final List<Object> subscriptions = new ArrayList<>();
 private final List<String> names = new ArrayList<>();
 private final Map<String,String> states = new ConcurrentHashMap<>();
 private SessionDependencies(ClassLoader classLoader){loader=classLoader;}
 static SessionDependencies end(android.app.Instrumentation test,android.app.Activity activity)throws Exception {
  SessionDependencies result=new SessionDependencies(activity.getClassLoader());
  java.util.concurrent.atomic.AtomicReference<Object> found=new java.util.concurrent.atomic.AtomicReference<>();
  java.util.concurrent.atomic.AtomicReference<Exception> failure=new java.util.concurrent.atomic.AtomicReference<>();
  test.runOnMainSync(()->{try{found.set(endFragment(activity.getClass().getMethod("getSupportFragmentManager").invoke(activity),0));}catch(Exception e){failure.set(e);}});
  if(failure.get()!=null)throw failure.get();
  Object fragment=found.get();
  if(fragment==null)throw new IllegalStateException("Original SessionEndFragment not found");
  Method getter=fragment.getClass().getDeclaredMethod("getViewModel");getter.setAccessible(true);
  Object vm=getter.invoke(fragment),dispatcher=field(vm,"z");
  try{
   Map<?,?> named=(Map<?,?>)Class.forName("com.duoaero.nativebase.NativeCourseBridge",true,result.loader).getMethod("diagnosticFlows").invoke(null);
   for(Map.Entry<?,?> entry:named.entrySet())result.observe("end.named."+entry.getKey(),entry.getValue(),dispatcher);
   result.observe("end.configure-args",field(field(vm,"W0"),"a"),dispatcher);
   Object sequence=field(vm,"Y0");
   result.observe("end.sequence-state",field(sequence,"h"),dispatcher);
   result.observe("end.sequence-current",field(sequence,"k"),dispatcher);
   result.observe("end.ui-ready",field(field(vm,"Z0"),"b"),dispatcher);
   Object saved=field(vm,"f1");
   Object args=saved.getClass().getMethod("a",String.class).invoke(saved,"config_args");
   result.names.add("end.saved-config");result.states.put("end.saved-config",args==null?"null":args.getClass().getName());
   // Observe existing repository flows only; do not invoke mutations or write readiness.
   Class<?> flow=Class.forName("qdf",true,result.loader);
   for(Field repositoryField:vm.getClass().getFields()){
    if(Modifier.isStatic(repositoryField.getModifiers()))continue;
    Object repository=repositoryField.get(vm);if(repository==null)continue;
    for(Field operand:repository.getClass().getFields()){
     if(Modifier.isStatic(operand.getModifiers())||!flow.isAssignableFrom(operand.getType()))continue;
     Object value=operand.get(repository);
     if(value!=null)result.observe("end.repository."+repositoryField.getName()+"."+operand.getName(),value,dispatcher);
    }
   }
   return result;
  }catch(Exception e){result.close();throw e;}
 }
 private static Object endFragment(Object manager,int depth)throws Exception {
  if(depth>10)return null;
  Object store=field(manager,"c");
  for(Object fragment:(List<?>)store.getClass().getMethod("f").invoke(store)){
   if(fragment.getClass().getName().equals("com.duolingo.sessionend.SessionEndFragment"))return fragment;
   Object found=endFragment(fragment.getClass().getMethod("getChildFragmentManager").invoke(fragment),depth+1);
   if(found!=null)return found;
  }
  return null;
 }
 static SessionDependencies home(android.app.Activity activity)throws Exception {
  SessionDependencies result=new SessionDependencies(activity.getClassLoader());
  try{
   Object host=activity.getClass().getMethod("v").invoke(activity);
   Object dispatcher=field(host,"g"),bridge=field(host,"e");
   for(String name:new String[]{"d","f","j"})result.observe("home.bridge."+name,field(bridge,name),dispatcher);
   Object manager=activity.getClass().getMethod("getSupportFragmentManager").invoke(activity);
   Object fragment=manager.getClass().getMethod("F",String.class).invoke(manager,"launch_fragment");
   if(fragment!=null){
    Object vm=fragment.getClass().getMethod("w").invoke(fragment);
    for(String name:new String[]{"K","L","N","S","V"})result.observe("home.launch."+name,field(vm,name),dispatcher);
    Object config=field(vm,"i");
    for(String name:new String[]{"q","r","u","v"})result.observe("home.config."+name,field(config,name),dispatcher);
    Object onboarding=field(field(vm,"x"),"a");
    result.observe("home.onboarding-completion",Class.forName("qvl",true,result.loader).getMethod("getValue").invoke(field(onboarding,"c")),dispatcher);
    Object accounts=field(vm,"r");
    result.observe("home.saved-accounts",accounts.getClass().getMethod("e").invoke(accounts),dispatcher);
    Object user=field(vm,"G");
    result.observe("home.user",user.getClass().getMethod("f").invoke(user),dispatcher);
    Object check=Class.forName("qvl",true,result.loader).getMethod("getValue").invoke(field(fragment,"l"));
    result.observeRx("home.check."+check.getClass().getName(),Class.forName("com.duolingo.splash.LaunchCheckViewModel",true,result.loader).getMethod("G0").invoke(check));
   }
   return result;
  }catch(Exception error){result.close();throw error;}
 }
 SessionDependencies(Object viewModel) throws Exception {
  loader = viewModel.getClass().getClassLoader();
  Object sessionLoader = viewModel.getClass().getField("j").get(viewModel);
  Object dispatcher = sessionLoader.getClass().getField("g").get(sessionLoader);
  Object course = sessionLoader.getClass().getField("f").get(sessionLoader);
  Object user = sessionLoader.getClass().getField("H").get(sessionLoader);
  Object streak = sessionLoader.getClass().getField("I").get(sessionLoader);
  try {
   observe("course", course.getClass().getMethod("h",String.class,boolean.class).invoke(course,null,true),dispatcher);
   observe("user",user.getClass().getMethod("f").invoke(user),dispatcher);
   observe("streak",streak.getClass().getMethod("a").invoke(streak),dispatcher);
   observeRx("loader-combined", sessionLoader.getClass().getMethod("a",Class.forName("com.duolingo.data.home.path.PathLevelSessionEndInfo",true,loader)).invoke(sessionLoader,new Object[]{null}));
   observeRx("vm.V",field(viewModel,"V"));
   observeRx("vm.l2",field(viewModel,"l2"));
   observeRx("vm.G3",field(viewModel,"G3"));
   for(String[] item:new String[][]{{"n0","a"},{"T1","b"},{"S1","a"},{"Z0","a"},{"M0","a"},{"X0","getNetworkStatus"}}) {
    Object repository=field(viewModel,item[0]);
    observe("vm."+item[0]+"."+item[1],repository.getClass().getMethod(item[1]).invoke(repository),dispatcher);
   }
   observe("vm.C.v",field(field(viewModel,"C"),"v"),dispatcher);
   observe("vm.g1.d",field(field(viewModel,"g1"),"d"),dispatcher);
   for(String parent:new String[]{"S1","z1"}) {
    Object lazy=field(field(viewModel,parent),"d");
    Object value=Class.forName("qvl",true,loader).getMethod("getValue").invoke(lazy);
    observe("vm."+parent+".d",value,dispatcher);
   }
   Object selector=Class.forName("pd10",true,loader).getConstructor(int.class).newInstance(26);
   observe("user-pd10-26",user.getClass().getMethod("g",Class.forName("qqh",true,loader)).invoke(user,selector),dispatcher);
   observe("user-w9o.h",Class.forName("w9o",true,loader).getMethod("h",Class.forName("ce90",true,loader)).invoke(null,user),dispatcher);
   List<Object> experiments=new ArrayList<>();
   for(String[] entry:new String[][]{{"g9w","b"},{"z8q","g"},{"z8q","o"},{"z8q","f"},{"z8q","l"},{"buo","i"},{"bd10","i"}})
    experiments.add(Class.forName(entry[0],true,loader).getField(entry[1]).get(null));
   Class<?> registry=Class.forName("com.duolingo.core.experiments.Experiments",true,loader);
   Object instance=registry.getField("INSTANCE").get(null);
   for(String getter:new String[]{"getENERGY_ANDROID_DECREASE_REWARD_EV","getSPACK_DECREASE_PERFECT_LESSON_ENERGY_REWARD"})experiments.add(registry.getMethod(getter).invoke(instance));
   observeRx("session-experiments",Class.forName("com.duolingo.core.experiments.ExperimentsRepository",true,loader).getMethod("observeTreatmentRecords",Collection.class).invoke(field(viewModel,"U"),experiments));
   Object experimentRepository=field(viewModel,"U");
   observe("experiments-implementation-selector",field(experimentRepository,"d"),dispatcher);
   observe("user-id",user.getClass().getMethod("h").invoke(user),dispatcher);
   for(String[] entry:new String[][]{{"a","p"},{"b","n"}}){
    Object repository=field(experimentRepository,entry[0]);
    Object lazy=field(repository,entry[1]);
    observe("experiments-entries-"+entry[0],Class.forName("qvl",true,loader).getMethod("getValue").invoke(lazy),dispatcher);
   }
   for(String name:new String[]{"w2","x2","i3","j3","o3","q3","m3","n3"})observeRx("view."+name,field(viewModel,name));
   observe("view.preload-completion",field(field(viewModel,"A1"),"u"),dispatcher);
   observeRx("view.loading-indicator",field(field(viewModel,"x1"),"k"));
   observe("view.course",field(viewModel,"F").getClass().getMethod("d").invoke(field(viewModel,"F")),dispatcher);
   observe("view.loading-experiment",field(field(viewModel,"z0"),"a"),dispatcher);
   Object preload=field(viewModel,"A1");
   for(String[] item:new String[][]{{"f","d"},{"c","b"}}){
    Object repository=field(preload,item[0]);
    observe("preload."+item[0]+"."+item[1],repository.getClass().getMethod(item[1]).invoke(repository),dispatcher);
   }
   observe("preload.h.c",field(field(preload,"h"),"c"),dispatcher);
   Object preloadUserSelector=Class.forName("pd10",true,loader).getConstructor(int.class).newInstance(15);
   observe("preload.user15",user.getClass().getMethod("g",Class.forName("qqh",true,loader)).invoke(user,preloadUserSelector),dispatcher);
   Object preloadLogin=field(field(preload,"o"),"d");
   observe("preload.login",preloadLogin.getClass().getMethod("b").invoke(preloadLogin),dispatcher);
   Object first=field(preload,"a");
   observeRx("preload.a.c",first.getClass().getMethod("c").invoke(first));
   Object route=viewModel.getClass().getMethod("L0").invoke(viewModel);
   Object beforeLesson=field(preload,"l");
   observe("preload.l.a",beforeLesson.getClass().getMethod("a",Class.forName("com.duolingo.data.session.SessionRouteParams",true,loader)).invoke(beforeLesson,route),dispatcher);
   // Observe the original pre-lesson screen selector's operands, including
   // nullable emissions. Do not bypass the selector or signal completion.
   for(String[] item:new String[][]{{"e","h"},{"h","a"},{"g","b"}}){
    Object repository=field(beforeLesson,item[0]);
    observe("before."+item[0]+"."+item[1],repository.getClass().getMethod(item[1]).invoke(repository),dispatcher);
   }
   observe("before.d.c",field(field(beforeLesson,"d"),"c"),dispatcher);
   observe("before.f.e.h",field(field(field(beforeLesson,"f"),"e"),"h"),dispatcher);
   Object beforeUserSelector=Class.forName("pd10",true,loader).getConstructor(int.class).newInstance(21);
   observe("before.user21",user.getClass().getMethod("g",Class.forName("qqh",true,loader)).invoke(user,beforeUserSelector),dispatcher);
   Object sponsor=field(beforeLesson,"i");
   Object sponsorUser=field(sponsor,"e");
   Object sponsorUserFlow=sponsorUser.getClass().getMethod("h").invoke(sponsorUser);
   Class<?> continuation=Class.forName("ql8",true,loader);
   Object sponsorSelector=Class.forName("h740",true,loader).getConstructor(continuation,Class.forName("l740",true,loader),int.class).newInstance(null,sponsor,1);
   Object sponsorFlow=Class.forName("mff",true,loader).getMethod("e",Class.forName("qdf",true,loader),Class.forName("grh",true,loader)).invoke(null,sponsorUserFlow,sponsorSelector);
   observe("before.sponsor",sponsorFlow,dispatcher);
   observe("before.j.i",field(field(beforeLesson,"j"),"i"),dispatcher);
   observe("before.a.d",field(field(beforeLesson,"a"),"d"),dispatcher);
   Object preference=Class.forName("g70",true,loader).getField("b").get(null);
   Object preferences=field(beforeLesson,"c");
   observe("before.c.b",preferences.getClass().getMethod("b",Class.forName("age",true,loader)).invoke(preferences,preference),dispatcher);
   Object energy=field(beforeLesson,"e");
   Object energyCourse=field(energy,"c"),energyPrefs=field(energy,"i");
   observe("energy.course-info",energyCourse.getClass().getMethod("j").invoke(energyCourse),dispatcher);
   observe("energy.preferences",energyPrefs.getClass().getMethod("a").invoke(energyPrefs),dispatcher);
   Object middle=field(preload,"m");
   Object source=field(middle,"a");
   observe("preload.m.a.n",source.getClass().getMethod("n").invoke(source),dispatcher);
   source=field(middle,"b");
   observe("preload.m.b.b",source.getClass().getMethod("b").invoke(source),dispatcher);
   Object last=field(preload,"e");
   Class<?> lastType=Class.forName("m3m",true,loader);
   observe("preload.e.a",lastType.getMethod("a",lastType).invoke(null,last),dispatcher);
   Object preloadExperiment=Class.forName("bcm",true,loader).getField("b").get(null);
   observeRx("preload.experiment",Class.forName("com.duolingo.core.experiments.ExperimentsRepository",true,loader).getMethod("observeTreatmentRecords",Collection.class).invoke(field(preload,"b"),Collections.singletonList(preloadExperiment)));
  } catch(Exception error) { close(); throw error; }
 }
 private void observe(String name,Object flow,Object dispatcher) throws Exception {

  Object observable=Class.forName("mao",true,loader)
   .getMethod("b",Class.forName("qdf",true,loader),Class.forName("pn8",true,loader))
   .invoke(null,flow,dispatcher);
  observeRx(name,observable);
 }
 private static Object field(Object owner,String name)throws Exception {return owner.getClass().getField(name).get(owner);}
 private void observeRx(String name,Object observable)throws Exception {
  names.add(name);
  states.put(name,"NO_EMISSION");
  Class<?> consumer=Class.forName("qb8",true,loader);
  Object next=consumer(consumer,name,false),error=consumer(consumer,name,true);
  Object disposable=Class.forName("ohf",true,loader).getMethod("l0",consumer,consumer).invoke(observable,next,error);
  subscriptions.add(disposable);
 }
 private Object consumer(Class<?> type,String name,boolean error) {
  return Proxy.newProxyInstance(loader,new Class[]{type},(proxy,method,args)->{
   if(method.getName().equals("accept")) {
    // Report classes and Boolean values: no account data, payloads, URLs or tokens.
    Object value=args[0];
    states.put(name,(error?"ERROR ":"EMITTED ")+(value==null?"null":value.getClass().getName())+(value instanceof Boolean?"="+value:""));
    return null;
   }
   if(method.getName().equals("toString"))return "Session dependency observer: "+name;
   if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
   if(method.getName().equals("equals"))return proxy==args[0];
   throw new UnsupportedOperationException(method.getName());
  });
 }
 String report() {
  StringBuilder text=new StringBuilder();
  for(String name:names)text.append("Dependency ").append(name).append(": ").append(states.get(name)).append('\n');
  return text.toString();
 }
 public void close() throws Exception {
  Exception failure=null;
  for(Object subscription:subscriptions)try {
   Class.forName("arb",true,loader).getMethod("dispose").invoke(subscription);
  }catch(Exception e){failure=e;}
  subscriptions.clear();
  if(failure!=null)throw failure;
 }
}
