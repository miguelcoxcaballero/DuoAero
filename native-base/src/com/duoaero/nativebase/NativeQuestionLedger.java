package com.duoaero.nativebase;

import org.json.*;
import java.util.*;

/** Question outcomes across every lesson, including corrections on later retries. */
public final class NativeQuestionLedger {
 private NativeQuestionLedger(){}
 public static void record(JSONObject records,String id,boolean correct,long at,String session)throws JSONException {
  if(id==null||id.isEmpty()||at<=0||session==null||session.isEmpty())throw new IllegalArgumentException("Invalid question outcome");
  JSONObject previous=records.optJSONObject(id);
  if(previous!=null&&at<previous.getLong("at"))return;
  int misses=previous==null?0:previous.optInt("misses");
  records.put(id,new JSONObject().put("correct",correct).put("at",at).put("session",session)
   .put("misses",misses+(correct?0:1)));
 }
 public static List<String> unresolved(JSONObject records)throws JSONException {
  List<String> ids=new ArrayList<>();
  for(Iterator<String> keys=records.keys();keys.hasNext();){String id=keys.next();if(Boolean.FALSE.equals(records.getJSONObject(id).opt("correct")))ids.add(id);}
  ids.sort((a,b)->Long.compare(records.optJSONObject(a).optLong("at"),records.optJSONObject(b).optLong("at")));
  return ids;
 }
}
