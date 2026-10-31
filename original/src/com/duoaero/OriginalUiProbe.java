package com.duoaero;
import android.app.Activity;import android.os.Bundle;import android.view.*;import android.widget.*;
public class OriginalUiProbe extends Activity {
 public void onCreate(Bundle state){super.onCreate(state);try{
  LinearLayout page=new LinearLayout(this);page.setOrientation(1);page.setPadding(32,80,32,32);setContentView(page);
  for(String layout:new String[]{"duoaero_google","duoaero_solid","duoaero_outline"}){
   View button=getLayoutInflater().inflate(getResources().getIdentifier(layout,"layout",getPackageName()),page,false);
   ((TextView)button).setText(layout.equals("duoaero_google")?"GOOGLE ACCOUNT":layout.equals("duoaero_solid")?"CONTINUE":"Aerospace Technology");
   page.addView(button);android.util.Log.i("DuoAeroProbe","ORIGINAL VIEW "+button.getClass().getName());
  }
  android.util.Log.i("DuoAeroProbe","PASS original compiled controls and styles");
 }catch(Throwable t){android.util.Log.e("DuoAeroProbe","FAIL",t);TextView error=new TextView(this);error.setText(t.toString());setContentView(error);}}
}
