package com.duoaero.nativebase;

import android.content.Context;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.util.Arrays;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import org.json.JSONObject;

/** Synchronous, device-key-encrypted persistence for the unchanged Notes storage API. */
final class NativeAuthStorage {
 private static final String ALIAS="duoaero-google-storage",PREFS="duoaero-auth-encrypted";
 private static final String[] KEYS={"duoaero-drive-token-v1","duoaero-drive-remember-v1","duoaero-drive-refresh-token-v1","duoaero-drive-pkce-verifier-v1","duoaero-google-scope-version-v1","duoaero-google-granted-scopes-v1","drive-hint-email","drive-consent-granted","duoaero-device"};
 private static SecretKey key()throws Exception {
  KeyStore store=KeyStore.getInstance("AndroidKeyStore");store.load(null);
  if(!store.containsAlias(ALIAS)){
   KeyGenerator generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
   generator.init(new KeyGenParameterSpec.Builder(ALIAS,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT)
    .setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());
   return generator.generateKey();
  }
  return (SecretKey)store.getKey(ALIAS,null);
 }
 static synchronized String read(Context context)throws Exception {
  JSONObject result=new JSONObject();android.content.SharedPreferences prefs=context.getSharedPreferences(PREFS,0);
  for(String name:KEYS){
   String encoded=prefs.getString(name,null);if(encoded==null)continue;
   byte[] bytes=Base64.decode(encoded,Base64.NO_WRAP);if(bytes.length<28)throw new IllegalStateException("Invalid encrypted authentication storage");
   Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.DECRYPT_MODE,key(),new GCMParameterSpec(128,Arrays.copyOf(bytes,12)));
   cipher.updateAAD(name.getBytes(StandardCharsets.UTF_8));
   result.put(name,new String(cipher.doFinal(Arrays.copyOfRange(bytes,12,bytes.length)),StandardCharsets.UTF_8));
  }
  return result.toString();
 }
 static synchronized void write(Context context,String name,String value)throws Exception {
  if(!Arrays.asList(KEYS).contains(name))throw new SecurityException("Unrecognized authentication storage key");
  android.content.SharedPreferences.Editor editor=context.getSharedPreferences(PREFS,0).edit();
  if(value==null)editor.remove(name);
  else{
   byte[] plain=value.getBytes(StandardCharsets.UTF_8);if(plain.length>65536)throw new IllegalArgumentException("Authentication value too large");
   Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.ENCRYPT_MODE,key());cipher.updateAAD(name.getBytes(StandardCharsets.UTF_8));
   byte[] encrypted=cipher.doFinal(plain),nonce=cipher.getIV();if(nonce.length!=12)throw new IllegalStateException("Unexpected authentication nonce");
   byte[] result=Arrays.copyOf(nonce,nonce.length+encrypted.length);System.arraycopy(encrypted,0,result,nonce.length,encrypted.length);
   editor.putString(name,Base64.encodeToString(result,Base64.NO_WRAP));
  }
  if(!editor.commit())throw new java.io.IOException("Authentication storage commit failed");
 }
}
