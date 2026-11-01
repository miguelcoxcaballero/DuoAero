"""Reward/streak boundaries. Does not establish native counter UI acceptance."""
import os
import subprocess
from runtime_config import WORK, JAR, java, ROOT
import test_profile_response
source = WORK / 'RewardsCheck.java'
source.write_text(r'''
package com.duoaero.nativebase;
import java.time.*;
import java.util.*;
import org.json.*;
public class RewardsCheck {
 static int checks;
 static void check(boolean yes){if(!yes)throw new AssertionError("Reward check "+checks);checks++;}
 static JSONObject lesson(String day,ZoneId zone)throws Exception {
  return new JSONObject().put("nativeCompletion",new JSONObject().put("endTime",LocalDate.parse(day).atTime(23,30).atZone(zone).toEpochSecond()));
 }
 public static void main(String[] args)throws Exception {
  LocalDate today=LocalDate.of(2026,11,1);ZoneId zone=ZoneId.of("Europe/Madrid");
  Set<LocalDate> days=new HashSet<>();check(NativeRewards.streak(days,today)==0);
  days.add(today.minusDays(1));check(NativeRewards.streak(days,today)==1);
  days.add(today);check(NativeRewards.streak(days,today)==2);
  days.add(today.minusDays(3));check(NativeRewards.streak(days,today)==2);
  check(NativeRewards.streak(days,today.plusDays(2))==0);
  JSONObject lessons=new JSONObject().put("a",lesson("2026-10-31",zone)).put("b",lesson("2026-11-01",zone));
  JSONObject profile=NativeRewards.project(lessons,new JSONObject(),zone,today);
  check(profile.getJSONObject("gemsConfig").getInt("gems")==20);
  check(profile.getJSONObject("streakData").getInt("length")==2);
  check(profile.getJSONObject("streakData").getJSONObject("currentStreak").getInt("length")==2);
  check(profile.getJSONObject("streakData").getJSONObject("longestStreak").getInt("length")==2);
  check(NativeRewards.project(lessons,new JSONObject(),zone,today).toString().equals(profile.toString()));
  JSONObject expired=NativeRewards.project(lessons,new JSONObject(),zone,today.plusDays(2));
  check(expired.getJSONObject("streakData").getInt("length")==0);
  check(!expired.getJSONObject("streakData").has("currentStreak"));
  check(expired.getJSONObject("streakData").getJSONObject("previousStreak").getInt("length")==2);
  check(expired.getJSONObject("streakData").getJSONObject("longestStreak").getInt("length")==2);
  // Replay the same lesson on another day: streak grows but gems do not.
  lessons.getJSONObject("b").put("studyDays",new JSONArray().put("2026-11-02"));
  JSONObject replay=NativeRewards.project(lessons,new JSONObject(),zone,today.plusDays(1));
  check(replay.getJSONObject("gemsConfig").getInt("gems")==20);
  check(replay.getJSONObject("streakData").getInt("length")==3);
  // A local evening is already tomorrow UTC; keep the local study date.
  ZoneId west=ZoneId.of("America/Los_Angeles");
  JSONObject local=NativeRewards.project(new JSONObject().put("a",lesson("2026-10-31",west)),new JSONObject(),west,today.minusDays(1));
  check(local.getJSONObject("streakData").getInt("length")==1);
  JSONObject empty=NativeRewards.project(new JSONObject(),new JSONObject(),zone,today);
  check(empty.getJSONObject("gemsConfig").getInt("gems")==0);
  check(empty.getJSONObject("streakData").getJSONObject("longestStreak").getInt("length")==0);
  System.out.println("PASS: "+checks+" reward/streak projection checks; Android UI not asserted");
 }
}
''')
classpath = os.pathsep.join(map(str, [WORK/'json-20250517.jar', WORK/'classes', JAR]))
subprocess.run([java('javac'), '-cp', classpath, '-d', WORK/'classes', ROOT/'native-base/src/com/duoaero/nativebase/NativeRewards.java', source],check=True)
subprocess.run([java('java'), '-cp', classpath, 'com.duoaero.nativebase.RewardsCheck'],check=True)
