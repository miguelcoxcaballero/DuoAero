package com.duoaero.nativebase;

import android.app.Application;
import android.util.AtomicFile;
import org.json.JSONObject;
import java.io.*;

/** Durable native session submissions. Completion is interpreted separately. */
public final class NativeSessionStore {
 private NativeSessionStore(){}
 static synchronized void record(Application app,String sessionId,JSONObject submission)throws Exception {
  if(!NativeCourseBridge.hasLocalCourse()||!sessionId.matches("[A-Za-z0-9_-]{1,160}"))throw new IllegalArgumentException("Invalid local course session");
  File folder=new File(app.getFilesDir(),"duoaero-course/local-test/submissions");
  if(!folder.isDirectory()&&!folder.mkdirs())throw new IOException("Cannot create native session store");
  AtomicFile file=new AtomicFile(new File(folder,sessionId+".json"));
  JSONObject record=new JSONObject().put("schema",1).put("sessionId",sessionId)
   .put("savedAt",System.currentTimeMillis()).put("nativeSubmission",submission);
  FileOutputStream output=null;
  try{
   output=file.startWrite();output.write(record.toString().getBytes("UTF-8"));file.finishWrite(output);
  }catch(Exception failure){if(output!=null)file.failWrite(output);throw failure;}
  // Read back the committed bytes before acknowledging the original request.
  try(FileInputStream input=file.openRead()){
   ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buffer=new byte[8192];int n;
   while((n=input.read(buffer))!=-1)bytes.write(buffer,0,n);
   JSONObject saved=new JSONObject(bytes.toString("UTF-8"));
   if(!sessionId.equals(saved.getString("sessionId"))||!saved.has("nativeSubmission"))throw new IOException("Invalid stored native session");
  }
 }
}
