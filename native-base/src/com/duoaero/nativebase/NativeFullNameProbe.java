package com.duoaero.nativebase;

import android.content.res.Configuration;
import android.graphics.Color;
import android.graphics.Typeface;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.TextView;

/** Isolated diagnostic: full text in the existing native token card. */
public final class NativeFullNameProbe {
 private static final String TAG="duoaero-full-name-probe";
 public static void apply(View card, View figure, Object state) {
  if(!(card instanceof FrameLayout) || figure==null)return;
  FrameLayout host=(FrameLayout)card;
  View existing=host.findViewWithTag(TAG);
  String name=null;
  try {
   if(NativeCourseBridge.hasLocalCourse() && state!=null &&
      state.getClass().getName().endsWith("MathFigureUiState$AttributedText")) {
    Object entity=state.getClass().getField("f").get(state);
    if(entity!=null && entity.getClass().getName().endsWith("MathEntity$Algebraic")) {
     String raw=(String)entity.getClass().getField("a").get(entity);
     if(raw!=null && raw.startsWith("duoaero:") && raw.indexOf(' ')>=0)
      name=raw.substring(8);
    }
   }
  } catch(ReflectiveOperationException ignored) {}
  if(name==null){
   if(existing!=null)existing.setVisibility(View.GONE);
   figure.setVisibility(View.VISIBLE);return;
  }
  int hostPad=Math.round(3*host.getResources().getDisplayMetrics().density);
  host.setPaddingRelative(hostPad,hostPad,hostPad,hostPad);
  TextView label;
  if(existing instanceof TextView) label=(TextView)existing;
  else {
   label=new TextView(host.getContext());label.setTag(TAG);
   label.setGravity(Gravity.CENTER);label.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
   label.setMaxLines(3);label.setIncludeFontPadding(false);label.setClickable(false);label.setFocusable(false);
   int pad=Math.round(2*host.getResources().getDisplayMetrics().density);
   label.setPadding(pad,0,pad,0);
   label.setAutoSizeTextTypeUniformWithConfiguration(12,18,1,TypedValue.COMPLEX_UNIT_SP);
   host.addView(label,new FrameLayout.LayoutParams(-1,-1));
  }
  boolean night=(host.getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK)==Configuration.UI_MODE_NIGHT_YES;
  label.setTextColor(night?Color.WHITE:Color.rgb(60,60,60));
  label.setText(name);label.setVisibility(View.VISIBLE);figure.setVisibility(View.INVISIBLE);
 }
}
