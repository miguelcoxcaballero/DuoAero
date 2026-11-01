"""Exercise the packaged profile normalizer, including existing legacy data.

Host JSON checks complement the mandatory original User/UserStreak decoder
checks on Android; they do not establish lesson completion or saved progress.
"""
import hashlib
import os
import subprocess
import urllib.request
from runtime_config import WORK, JAR, java

dependency = WORK / 'json-20250517.jar'
digest = '3ea61b2a06e31edf1c91134fe9106b0ebb16628be169f3db75bc7a2b06b45796'
if not dependency.exists():
    dependency.write_bytes(urllib.request.urlopen('https://repo.maven.apache.org/maven2/org/json/json/20250517/json-20250517.jar', timeout=30).read())
assert hashlib.sha256(dependency.read_bytes()).hexdigest() == digest
source = WORK / 'ProfileResponseCheck.java'
source.write_text('''
import org.json.*;
import com.duoaero.nativebase.NativeCourseBridge;
public class ProfileResponseCheck {
 static JSONObject profile(){return new JSONObject().put("id",1).put("username","aerospace-local-test");}
 static JSONObject normalize(JSONObject p)throws Exception{return new JSONObject(NativeCourseBridge.setDiagnosticProfile(p.toString()));}
 static void zero(JSONObject p)throws Exception{
  JSONObject s=normalize(p).getJSONObject("streakData");
  if(s.getJSONObject("longestStreak").getInt("length")!=0||!s.getString("updatedTimeZone").equals("UTC"))throw new AssertionError(s);
 }
 public static void main(String[] args)throws Exception{
  zero(profile());
  zero(profile().put("streakData",JSONObject.NULL));
  zero(profile().put("streakData",new JSONObject().put("updatedTimeZone","UTC")));
  zero(profile().put("streakData",new JSONObject().put("longestStreak",JSONObject.NULL)));
  JSONObject existing=new JSONObject().put("length",7).put("updatedTimestamp",1234).put("updatedTimeZone","Europe/Madrid").put("longestStreak",new JSONObject().put("length",7));
  JSONObject kept=normalize(profile().put("streakData",existing)).getJSONObject("streakData");
  if(!kept.similar(existing))throw new AssertionError("Existing streak was changed");
  if(!normalize(normalize(profile())).similar(normalize(profile())))throw new AssertionError("Not idempotent");
  try{normalize(profile().put("id",2));throw new AssertionError("Accepted foreign identity");}catch(IllegalArgumentException expected){}
  System.out.println("PASS: seven packaged profile response checks; native decoding/UI checked separately");
 }
}
''', encoding='utf-8')
classpath = os.pathsep.join(map(str, [dependency, WORK / 'classes', JAR]))
subprocess.run([java('javac'), '-cp', classpath, '-d', WORK / 'classes', source], check=True)
subprocess.run([java('java'), '-cp', classpath, 'ProfileResponseCheck'], check=True)
