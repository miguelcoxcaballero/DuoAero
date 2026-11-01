package com.duoaero.nativebase;

import android.app.Activity;
import android.os.Bundle;
import android.widget.Toast;

/** Validates the configured native redirect before forwarding to Notes PKCE. */
public final class NativeOAuthCallbackActivity extends Activity {
 public void onCreate(Bundle state){
  super.onCreate(state);
  if(!NativeGoogleHost.acceptCallback(getApplication(),getIntent().getData()))Toast.makeText(this,"Sign-in response expired or was not requested. Please try again.",Toast.LENGTH_LONG).show();
  finish();
 }
}
