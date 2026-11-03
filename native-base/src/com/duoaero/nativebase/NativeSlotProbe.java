package com.duoaero.nativebase;

import java.util.List;

/** Diagnostic only: copy the original controller's ordered slot identities. */
public final class NativeSlotProbe {
 private static volatile String last;
 private static volatile boolean enabled;
 private NativeSlotProbe(){}
 public static void enable(){enabled=true;}
 public static boolean isEnabled(){return enabled;}
 public static void capture(List<?> slots){
  if(!enabled)return;
  if(slots==null){last=null;return;}
  StringBuilder result=new StringBuilder();
  try{
   for(Object slot:slots){
    if(slot==null)throw new IllegalStateException("Missing original slot");
    String kind=slot.getClass().getName();
    if(!kind.equals("pp3")&&!kind.equals("op3")&&!kind.equals("qp3"))
     throw new IllegalStateException("Unexpected original slot class");
    Object id=slot.getClass().getMethod("getId").invoke(slot);
    result.append(kind).append(':').append(id).append(';');
   }
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot read original slot identity",error);}
  last=result.toString();
 }
 public static String snapshot(){return last;}
}
