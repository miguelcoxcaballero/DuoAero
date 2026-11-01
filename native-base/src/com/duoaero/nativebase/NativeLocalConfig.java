package com.duoaero.nativebase;

import android.content.Context;
import java.lang.reflect.Field;

/** Supplies original default Config through its real cache descriptor. */
final class NativeLocalConfig {
 static String install(Context context)throws Exception {
  ClassLoader loader=context.getClassLoader();
  Object component=context.getApplicationContext().getClass().getMethod("generatedComponent").invoke(context.getApplicationContext());
  Object provider=component.getClass().getField("a0").get(component);
  Object factory=Class.forName("ymw",true,loader).getMethod("get").invoke(provider);
  Field jsonField=factory.getClass().getDeclaredField("json");jsonField.setAccessible(true);
  Object json=jsonField.get(factory);
  Object config=Class.forName("a8l",true,loader).getMethod("b",Class.forName("kotlinx.serialization.KSerializer",true,loader),String.class)
   .invoke(json,NativeLocalCache.serializer(loader,"com.duolingo.core.config.Config"),"{}");
  Object configProvider=component.getClass().getField("w0").get(component);
  java.lang.reflect.Method get=configProvider.getClass().getMethod("get");get.setAccessible(true);
  Object repository=get.invoke(configProvider);
  if(!repository.getClass().getName().equals("fm1"))throw new IllegalStateException("Unexpected Config repository");
  Object resources=repository.getClass().getField("j").get(repository);
  Object resource=resources.getClass().getMethod("a").invoke(resources);
  NativeLocalCache.write(loader,repository.getClass().getField("o").get(repository),resource,config);
  return "Original default Config decoded from {} and written through native w58 cache descriptor. No launch or readiness flags replaced.\n";
 }
}
