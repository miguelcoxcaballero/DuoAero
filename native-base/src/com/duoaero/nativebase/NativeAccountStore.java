package com.duoaero.nativebase;

import android.content.Context;
import java.io.File;
import java.security.MessageDigest;
import java.util.Locale;

/** Google Drive permission identity selects the private on-device course store. */
final class NativeAccountStore {
 static final Object LOCK=new Object();
 private NativeAccountStore(){}
 static boolean required(Context context){
  if("com.duoaero".equals(context.getPackageName()))return true;
  try(java.io.InputStream marker=context.getAssets().open("duoaero/google-required")){return true;}
  catch(java.io.IOException absent){return false;}
 }
 static String current(Context context){return context.getSharedPreferences("duoaero-google",0).getString("account","");}
 static File root(Context context){
  String id=current(context);
  if(id.isEmpty())return new File(context.getFilesDir(),"duoaero-course/local-test");
  return new File(context.getFilesDir(),"duoaero-course/google-"+key(id));
 }
 static String key(String id){
  if(id==null||id.isEmpty()||id.length()>200)throw new IllegalArgumentException("Invalid Google identity");
  try{
   byte[] hash=MessageDigest.getInstance("SHA-256").digest(id.getBytes("UTF-8"));
   StringBuilder value=new StringBuilder();for(byte b:hash)value.append(String.format(Locale.ROOT,"%02x",b&255));
   return value.toString();
  }catch(java.security.NoSuchAlgorithmException|java.io.UnsupportedEncodingException error){throw new IllegalStateException(error);}
 }
 static void require(Context context,String expected){
  if(expected==null||expected.isEmpty()||!expected.equals(current(context)))throw new SecurityException("Google account changed");
 }
 static void select(Context context,String id,String label){
  if(!id.isEmpty())key(id);
  if(!context.getSharedPreferences("duoaero-google",0).edit().putString("account",id).putString("label",label==null?"":label).commit())throw new IllegalStateException("Could not save Google account selection");
 }
}
