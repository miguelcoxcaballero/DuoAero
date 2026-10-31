package com.duoaero;

import android.content.Context;
import android.util.AtomicFile;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.*;

public final class Engine {
 public final JSONArray bank, nodes;
 public final Map<String,JSONObject> questions=new LinkedHashMap<>();
 public JSONObject state;
 public Runnable onSaved;
 private final AtomicFile file;
 public Engine(Context context,String filename)throws Exception{
  bank=new JSONArray(read(context.getAssets().open("questions.json")));
  nodes=new JSONArray(read(context.getAssets().open("lesson_plan.json")));
  for(int i=0;i<bank.length();i++){JSONObject q=bank.getJSONObject(i);questions.put(q.getString("id"),q);}
  file=new AtomicFile(new File(context.getFilesDir(),filename));
  try{state=new JSONObject(read(file.openRead()));}catch(Exception e){state=new JSONObject();}
  if(!state.has("records"))state.put("records",new JSONObject());
  if(!state.has("completedLessons"))state.put("completedLessons",new JSONObject());
  if(!state.has("settings"))state.put("settings",new JSONObject().put("sound",true).put("haptics",true).put("motion",true));
  if(!state.has("xp"))state.put("xp",0);
 }
 static String read(InputStream input)throws IOException{try(InputStream in=input;ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1)out.write(b,0,n);return out.toString("UTF-8");}}
 public void save()throws Exception{state.put("updatedAt",System.currentTimeMillis());FileOutputStream out=null;try{out=file.startWrite();out.write(state.toString().getBytes(StandardCharsets.UTF_8));file.finishWrite(out);if(onSaved!=null)onSaved.run();}catch(Exception e){if(out!=null)file.failWrite(out);throw e;}}
 public JSONObject records(){return state.optJSONObject("records");}
 public JSONObject settings(){return state.optJSONObject("settings");}
 public JSONObject session(){return state.optJSONObject("session");}
 public JSONObject current()throws Exception{return questions.get(session().getJSONArray("queue").getString(session().getInt("cursor")));}
 public boolean done(JSONObject lesson){JSONObject c=state.optJSONObject("completedLessons").optJSONObject(lesson.optString("id"));return c!=null&&c.optJSONArray("ids")!=null&&c.optLong("at")>0&&lesson.optJSONArray("ids").toString().equals(c.optJSONArray("ids").toString());}
 public JSONObject nextLesson(JSONObject node)throws Exception{JSONArray lessons=node.getJSONArray("lessons");for(int i=0;i<lessons.length();i++)if(!done(lessons.getJSONObject(i)))return lessons.getJSONObject(i);return lessons.getJSONObject(0);}
 public List<String> mistakes(){List<String> out=new ArrayList<>();for(String id:questions.keySet()){JSONObject r=records().optJSONObject(id);if(r!=null&&r.optInt("seen")>0&&!r.optBoolean("lastCorrect"))out.add(id);}return out;}
 public List<String> strings(JSONArray a)throws Exception{List<String> out=new ArrayList<>();for(int i=0;i<a.length();i++)out.add(a.getString(i));return out;}
 public void start(List<String> ids,String title,String kind,String lessonId)throws Exception{
  List<String> chosen=new ArrayList<>(ids);
  if(!kind.equals("pathlesson")){Collections.shuffle(chosen);chosen.sort(Comparator.comparingInt(id->{JSONObject r=records().optJSONObject(id);return r==null?0:r.optBoolean("lastCorrect")?2:1;}));if(chosen.size()>10)chosen=new ArrayList<>(chosen.subList(0,10));}
  if(chosen.isEmpty())return;
  JSONObject s=new JSONObject().put("ids",new JSONArray(chosen)).put("queue",new JSONArray(chosen)).put("cursor",0).put("title",title).put("kind",kind).put("lessonId",lessonId).put("checked",false).put("correct",false).put("initialResults",new JSONObject()).put("awarded",new JSONArray()).put("orders",new JSONObject()).put("combo",0);
  state.put("session",s);save();
 }
 public JSONArray order(JSONObject q)throws Exception{JSONObject orders=session().getJSONObject("orders");String id=q.getString("id");if(!orders.has(id)){JSONArray a=q.optJSONArray(q.optString("type").equals("matching")?"pairs":q.optString("type").equals("order")?"items":"options");List<Integer> ints=new ArrayList<>();for(int i=0;a!=null&&i<a.length();i++)ints.add(i);Collections.shuffle(ints);orders.put(id,new JSONArray(ints));}return orders.getJSONArray(id);}
 public void select(Object answer)throws Exception{if(session().optBoolean("checked"))return;session().put("answer",answer);save();}
 public static String normalize(Object value){return Normalizer.normalize(String.valueOf(value),Normalizer.Form.NFKC).trim().toLowerCase(Locale.ROOT).replaceAll("[\\s‐‑–—_-]+"," ");}
 static boolean sameArray(JSONArray a,JSONArray b){return a!=null&&b!=null&&a.toString().equals(b.toString());}
 public static boolean grade(JSONObject q,Object answer)throws Exception{
  String type=q.getString("type");
  if(type.equals("choice"))return answer instanceof Number&&((Number)answer).intValue()==q.getInt("answer");
  if(type.equals("gap")){JSONArray accepted=q.getJSONArray("answer");for(int i=0;i<accepted.length();i++)if(normalize(accepted.getString(i)).equals(normalize(answer)))return true;return false;}
  if(!(answer instanceof JSONArray))return false;JSONArray a=(JSONArray)answer;
  if(type.equals("order"))return sameArray(a,q.getJSONArray("answer"));
  if(type.equals("matching")){if(a.length()!=q.getJSONArray("pairs").length())return false;for(int i=0;i<a.length();i++)if(a.optInt(i,-1)!=i)return false;return true;}
  if(type.equals("multi")){JSONArray expected=q.getJSONArray("answer");if(a.length()!=expected.length())return false;Set<Integer> selected=new HashSet<>();for(int i=0;i<a.length();i++)selected.add(a.getInt(i));if(selected.size()!=expected.length())return false;for(int i=0;i<expected.length();i++)if(!selected.contains(expected.getInt(i)))return false;return true;}
  return false;
 }
 public boolean ready(JSONObject q,Object a)throws Exception{if(a==null||a==JSONObject.NULL)return false;switch(q.getString("type")){case "choice":return a instanceof Number;case "gap":return !String.valueOf(a).trim().isEmpty();case "multi":return a instanceof JSONArray&&((JSONArray)a).length()>0;case "order":return a instanceof JSONArray&&((JSONArray)a).length()==q.getJSONArray("items").length();case "matching":if(!(a instanceof JSONArray))return false;JSONArray arr=(JSONArray)a;if(arr.length()!=q.getJSONArray("pairs").length())return false;for(int i=0;i<arr.length();i++)if(arr.optInt(i,-1)<0)return false;return true;default:return false;}}
 public boolean check()throws Exception{
  JSONObject s=session(),q=current();if(s.optBoolean("checked")||!ready(q,s.opt("answer")))return false;
  boolean ok=grade(q,s.opt("answer"));s.put("checked",true).put("correct",ok);String id=q.getString("id");JSONObject r=records().optJSONObject(id);if(r==null)r=new JSONObject();r.put("seen",r.optInt("seen")+1).put("correct",r.optInt("correct")+(ok?1:0)).put("everCorrect",r.optBoolean("everCorrect")||ok).put("lastCorrect",ok).put("at",System.currentTimeMillis());records().put(id,r);
  if(s.getInt("cursor")<s.getJSONArray("ids").length())s.getJSONObject("initialResults").put(id,ok);
  if(ok){s.put("combo",s.optInt("combo")+1);if(!strings(s.getJSONArray("awarded")).contains(id)){s.getJSONArray("awarded").put(id);state.put("xp",state.optInt("xp")+(s.getInt("cursor")<s.getJSONArray("ids").length()?10:3));}}
  else{s.put("combo",0);s.getJSONArray("queue").put(id);}save();return true;
 }
 public boolean ended(){JSONObject s=session();return s!=null&&s.optInt("cursor")>=s.optJSONArray("queue").length();}
 public void advance()throws Exception{JSONObject s=session();if(!s.optBoolean("checked"))return;s.put("cursor",s.getInt("cursor")+1).put("checked",false);s.remove("answer");if(ended())recordCompletion();save();}
 private void recordCompletion()throws Exception{JSONObject s=session();if(!s.optString("kind").equals("pathlesson"))return;List<String> awarded=strings(s.getJSONArray("awarded"));if(!awarded.containsAll(strings(s.getJSONArray("ids"))))return;for(int i=0;i<nodes.length();i++){JSONArray ls=nodes.getJSONObject(i).getJSONArray("lessons");for(int j=0;j<ls.length();j++){JSONObject l=ls.getJSONObject(j);if(l.getString("id").equals(s.optString("lessonId"))&&sameArray(l.getJSONArray("ids"),s.getJSONArray("ids")))state.getJSONObject("completedLessons").put(l.getString("id"),new JSONObject().put("ids",l.getJSONArray("ids")).put("at",System.currentTimeMillis()));}}}
 public void leave()throws Exception{state.remove("session");save();}
 public String solution(JSONObject q)throws Exception{switch(q.getString("type")){case "choice":return q.getJSONArray("options").getString(q.getInt("answer"));case "gap":return q.getJSONArray("answer").getString(0);case "matching":{List<String> s=new ArrayList<>();JSONArray p=q.getJSONArray("pairs");for(int i=0;i<p.length();i++)s.add(p.getJSONArray(i).getString(0)+" → "+p.getJSONArray(i).getString(1));return String.join("\n",s);}default:{String field=q.getString("type").equals("order")?"items":"options";List<String> s=new ArrayList<>();JSONArray a=q.getJSONArray("answer");for(int i=0;i<a.length();i++)s.add(q.getJSONArray(field).getString(a.getInt(i)));return String.join(q.getString("type").equals("order")?" → ":"\n",s);}}}
}
