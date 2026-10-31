package com.duoaero;
import android.view.*;
import android.widget.*;
final class ViewChecks {
 static void assertOriginalLayouts(MainActivity a)throws Exception{
  View session=a.getLayoutInflater().inflate(a.res("layout","duoaero_session"),null);
  if(session.findViewById(a.res("id","challengeContainer")).getVisibility()!=View.VISIBLE)throw new AssertionError("Exercise container hidden");
  View tabs=a.getLayoutInflater().inflate(a.res("layout","duoaero_tabs"),null);
  if(!tabs.findViewById(a.res("id","tabLearn")).getClass().getName().equals("com.duolingo.home.DuoTabView"))throw new AssertionError("Original navigation class");
  a.screen="learn";a.home();a.root.findViewById(a.res("id","tabProfile")).performClick();
  if(!a.screen.equals("settings"))throw new AssertionError("Original profile tab navigation");
  View loading=a.getLayoutInflater().inflate(a.res("layout","duoaero_loading"),null);
  if(!((TextView)loading.findViewById(a.res("id","loadingText"))).getText().toString().equals("LOADING LESSON"))throw new AssertionError("Loading screen text");
  View answer=a.answerCard("A deliberately long answer describing aerodynamic lift, atmospheric density, true airspeed and the pressure distribution over a lifting wing.",true,false,false,false,null);
  TextView label=answer.findViewById(a.res("id","optionName"));label.setTextSize(28);
  answer.measure(View.MeasureSpec.makeMeasureSpec(a.dp(240),View.MeasureSpec.EXACTLY),View.MeasureSpec.makeMeasureSpec(0,View.MeasureSpec.UNSPECIFIED));answer.layout(0,0,answer.getMeasuredWidth(),answer.getMeasuredHeight());
  if(label.getLayout().getLineEnd(label.getLayout().getLineCount()-1)!=label.length())throw new AssertionError("Original answer card clips text");
  if(label.getHeight()<label.getLayout().getHeight()+label.getCompoundPaddingTop()+label.getCompoundPaddingBottom())throw new AssertionError("Original answer card clips height");
 }
}
