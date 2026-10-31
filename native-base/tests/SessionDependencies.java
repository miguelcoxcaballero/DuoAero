package com.duoaero.nativebase;

import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** Observes the actual loader inputs without replacing states or readiness flags. */
final class SessionDependencies implements AutoCloseable {
 private final ClassLoader loader;
 private final List<Object> subscriptions = new ArrayList<>();
 private final Map<String,String> states = new ConcurrentHashMap<>();
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
  } catch(Exception error) { close(); throw error; }
 }
 private void observe(String name,Object flow,Object dispatcher) throws Exception {
  states.put(name,"NO_EMISSION");
  Class<?> consumer=Class.forName("qb8",true,loader);
  Object next=consumer(consumer,name,false),error=consumer(consumer,name,true);
  Object observable=Class.forName("mao",true,loader)
   .getMethod("b",Class.forName("qdf",true,loader),Class.forName("pn8",true,loader))
   .invoke(null,flow,dispatcher);
  Object disposable=Class.forName("ohf",true,loader).getMethod("l0",consumer,consumer).invoke(observable,next,error);
  subscriptions.add(disposable);
 }
 private Object consumer(Class<?> type,String name,boolean error) {
  return Proxy.newProxyInstance(loader,new Class[]{type},(proxy,method,args)->{
   if(method.getName().equals("accept")) {
    // Report classes only: no account data, payloads, URLs or tokens.
    Object value=args[0];
    states.put(name,(error?"ERROR ":"EMITTED ")+(value==null?"null":value.getClass().getName()));
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
  for(String name:new String[]{"course","user","streak"})text.append("Dependency ").append(name).append(": ").append(states.get(name)).append('\n');
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
