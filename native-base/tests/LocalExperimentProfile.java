package com.duoaero.nativebase;

import java.lang.reflect.*;

/** Synthetic-profile experiment data; uses the original empty/default model.
 * Never changes SessionInitializationBridge, engine state or treatment booleans.
 * This is an isolated diagnostic input, not a production repository integration.
 */
final class LocalExperimentProfile {
 static void install(Object component,Object userId,ClassLoader loader)throws Exception {
  Object defaults=Class.forName("com.duolingo.core.experiments.ExperimentsState",true,loader).getConstructor().newInstance();
  Object entries=defaults.getClass().getMethod("getExperiments").invoke(defaults);
  Object map=entries.getClass().getMethod("getEntries").invoke(entries);
  Class<?> idType=Class.forName("com.duolingo.core.data.model.UserId",true,loader);
  Class<?> mapType=Class.forName("com.duolingo.core.pcollections.migration.PMap",true,loader);
  // Both original implementations receive the same per-user default entries.
  // The original client experiment still selects which implementation to use.
  for(String[] spec:new String[][]{{"D7","p","gsd"},{"H7","n","vir"}}) {
   Object provider=component.getClass().getField(spec[0]).get(component);
   Object repository=Class.forName("ymw",true,loader).getMethod("get").invoke(provider);
   Object state=Class.forName(spec[2],true,loader).getConstructor(idType,mapType).newInstance(userId,map);
   Object flow=Class.forName("if40",true,loader).getConstructor(Object.class).newInstance(state);
   Class<?> lazy=Class.forName("qvl",true,loader);
   Object holder=Proxy.newProxyInstance(loader,new Class[]{lazy},(proxy,method,args)->{
    if(method.getName().equals("getValue"))return flow;
    if(method.getName().equals("isInitialized"))return true;
    if(method.getName().equals("toString"))return "Synthetic default experiment entries";
    if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
    if(method.getName().equals("equals"))return proxy==args[0];
    throw new UnsupportedOperationException(method.getName());
   });
   Field target=repository.getClass().getField(spec[1]);target.setAccessible(true);target.set(repository,holder);
  }
 }
}
