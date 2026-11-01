package com.duoaero.nativebase;

import android.content.Context;
import android.media.*;
import android.os.*;
import java.util.*;

/** Records emulator playback callbacks; this does not establish audibility. */
final class DevicePlaybackObservation implements AutoCloseable {
 private final AudioManager audio;
 private final Set<String> attributes=Collections.synchronizedSet(new TreeSet<String>());
 private final java.util.concurrent.atomic.AtomicInteger observations=new java.util.concurrent.atomic.AtomicInteger();
 private final AudioManager.AudioPlaybackCallback callback=new AudioManager.AudioPlaybackCallback(){
  public void onPlaybackConfigChanged(List<AudioPlaybackConfiguration> configurations){
   if(!configurations.isEmpty())observations.incrementAndGet();
   for(AudioPlaybackConfiguration configuration:configurations){
    AudioAttributes value=configuration.getAudioAttributes();
    attributes.add("usage="+value.getUsage()+", content="+value.getContentType());
   }
  }
 };
 DevicePlaybackObservation(Context context){
  audio=(AudioManager)context.getSystemService(Context.AUDIO_SERVICE);
  audio.registerAudioPlaybackCallback(callback,new Handler(Looper.getMainLooper()));
 }
 String report(){
  return "Emulator audio playback observations="+observations.get()+"; attributes="+attributes
   +"; media volume="+audio.getStreamVolume(AudioManager.STREAM_MUSIC)
   +". Anonymous platform callbacks are not proof of audible output or physical haptics.\n";
 }
 public void close(){audio.unregisterAudioPlaybackCallback(callback);}
}
