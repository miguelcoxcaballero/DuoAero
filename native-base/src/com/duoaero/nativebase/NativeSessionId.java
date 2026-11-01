package com.duoaero.nativebase;

/** Catalog session names may contain dots, but must remain safe file names. */
final class NativeSessionId {
 private NativeSessionId(){}
 static boolean valid(String id){
  return id!=null&&id.length()<=160&&id.matches("[A-Za-z0-9_-]+(?:\\.[A-Za-z0-9_-]+)*");
 }
}
