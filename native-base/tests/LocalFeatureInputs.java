package com.duoaero.nativebase;

import android.content.Context;
import java.lang.reflect.*;

/** Known empty optional features of the isolated account, via native resources. */
final class LocalFeatureInputs {
 static String goals(Context context,Object sessionVm)throws Exception {
  ClassLoader loader=context.getClassLoader();
  Object repository=field(sessionVm,"X");
  if(!repository.getClass().getName().equals("hji"))throw new IllegalStateException("Unexpected goals repository");
  Object contextFlow=repository.getClass().getMethod("b").invoke(repository);
  Object scope=LocalCourseCache.first(loader,contextFlow,field(repository,"j"));
  if(!scope.getClass().getName().equals("uhi"))throw new IllegalStateException("Unexpected goals context");
  Object factory=field(repository,"h");
  Object resource=factory.getClass().getMethod("c",scope.getClass()).invoke(factory,scope);
  Object empty=Class.forName("v2z",true,loader).getMethod("h").invoke(null);
  Class<?> vector=Class.forName("com.duolingo.core.pcollections.migration.PVector",true,loader);
  Object schema=Class.forName("com.duolingo.data.goals.models.GoalsSchemaResponse",true,loader)
   .getConstructor(vector,vector,vector).newInstance(empty,empty,empty);
  LocalCourseCache.write(loader,field(repository,"p"),resource,schema);
  return "Original goals schema cache: no assigned goals or rewards for the isolated account.\n";
 }
 static void social(ClassLoader loader,Object endVm)throws Exception {
  Object repository=field(endVm,"C1"),factory=field(repository,"j");
  Class<?> userIdType=Class.forName("com.duolingo.core.data.model.UserId",true,loader);
  Object userId=userIdType.getConstructor(long.class).newInstance(1L);
  Object resource=factory.getClass().getMethod("a",userIdType).invoke(factory,userId);
  Object empty=Class.forName("v2z",true,loader).getMethod("h").invoke(null);
  Class<?> vector=Class.forName("com.duolingo.core.pcollections.migration.PVector",true,loader);
  Class<?> follows=Class.forName("jsf",true,loader);
  Object list=follows.getConstructor(int.class,String.class,vector).newInstance(0,null,empty);
  Object profile=Class.forName("com.duolingo.data.profile.follow.UserSocialProfile",true,loader)
   .getConstructor(int.class,int.class,follows,boolean.class,boolean.class,boolean.class,boolean.class)
   .newInstance(0,0,list,false,false,false,false);
  LocalCourseCache.write(loader,field(repository,"i"),resource,profile);
  for(String name:new String[]{"k","l"}){
   Object listFactory=field(repository,name);
   Object listResource=listFactory.getClass().getMethod("a",userIdType).invoke(listFactory,userId);
   LocalCourseCache.write(loader,field(repository,"i"),listResource,list);
  }
 }
 private static Object field(Object owner,String name)throws Exception{return owner.getClass().getField(name).get(owner);}
}
