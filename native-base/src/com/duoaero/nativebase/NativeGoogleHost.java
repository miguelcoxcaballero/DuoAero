package com.duoaero.nativebase;

import android.app.*;
import android.content.*;
import android.net.Uri;
import android.os.*;
import android.view.*;
import android.webkit.*;
import android.widget.*;
import java.io.*;
import java.lang.ref.WeakReference;
import java.util.*;
import java.util.concurrent.*;
import org.json.JSONObject;

/** Native host for the unchanged Notes PKCE functions and account-bound Drive. */
public final class NativeGoogleHost implements Application.ActivityLifecycleCallbacks {
 private static NativeGoogleHost instance;
 private final Application app;
 private final Handler main=new Handler(Looper.getMainLooper());
 private final MutableContextWrapper webContext;
 private final WebView web;
 private final Set<Activity> sessions=Collections.newSetFromMap(new WeakHashMap<Activity,Boolean>());
 private final Map<Activity,ViewTreeObserver.OnGlobalLayoutListener> welcomeObservers=new WeakHashMap<>();
 private WeakReference<Activity> foreground=new WeakReference<>(null);
 private boolean ready,manualSync,manualSignIn;
 private final ExecutorService pathRefresh=Executors.newSingleThreadExecutor(r->new Thread(r,"duoaero-drive-path"));
 private String pendingPathAccount="";
 private static Object logoutClick;
 private String pending="",status="Progress saved on this device";
 private NativeGoogleHost(Application application){
  app=application;webContext=new MutableContextWrapper(app);web=new WebView(webContext);
  web.setVisibility(View.INVISIBLE);web.setFocusable(false);web.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS);
  WebSettings settings=web.getSettings();settings.setJavaScriptEnabled(true);settings.setDomStorageEnabled(true);
  settings.setAllowFileAccess(false);settings.setAllowContentAccess(false);settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
  web.addJavascriptInterface(this,"InhouseNative");
  web.setWebViewClient(new WebViewClient(){
   public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request){
    Uri uri=request.getUrl();if(!"https".equals(uri.getScheme())||!"appassets.androidplatform.net".equals(uri.getHost()))return null;
    String path=uri.getPath();
    if(path==null||!path.startsWith("/shared/")||path.contains(".."))return empty();
    try{return new WebResourceResponse(path.endsWith(".js")?"application/javascript":"text/html","UTF-8",app.getAssets().open(path.substring(1)));}
    catch(IOException error){return empty();}
   }
   public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){return true;}
   public void onPageFinished(WebView view,String url){
    if(!"https://appassets.androidplatform.net/shared/auth-runtime.html".equals(url))return;
    ready=true;if(!pending.isEmpty()){String value=pending;pending="";callback(value);}
   }
  });
  app.registerActivityLifecycleCallbacks(this);
  web.loadUrl("https://appassets.androidplatform.net/shared/auth-runtime.html");
 }
 private static WebResourceResponse empty(){return new WebResourceResponse("text/plain","UTF-8",new ByteArrayInputStream(new byte[0]));}
 public static synchronized void install(Application app){if(instance==null)instance=new NativeGoogleHost(app);}
 public static void connect(Activity activity){
  install(activity.getApplication());instance.foreground=new WeakReference<>(activity);
  if(!instance.ready){Toast.makeText(activity,"Google sign-in is loading. Please try again.",Toast.LENGTH_SHORT).show();return;}
  if(NativeAccountStore.current(activity).isEmpty()){instance.manualSignIn=true;instance.web.evaluateJavascript("DuoAuth.signIn()",null);}
  else{instance.manualSync=true;instance.web.evaluateJavascript("DuoSync.sync()",null);}
 }
 public static void changeAccount(Activity activity){
  install(activity.getApplication());instance.foreground=new WeakReference<>(activity);
  if(instance.ready){instance.manualSignIn=true;instance.web.evaluateJavascript("localStorage.removeItem('drive-hint-email');localStorage.removeItem('drive-consent-granted');DuoAuth.signIn()",null);}
 }
 public static Object logoutHandler(Object original){
  NativeGoogleHost host=instance;if(host==null||!NativeAccountStore.required(host.app))return original;
  if(logoutClick!=null)return logoutClick;
  ClassLoader loader=original.getClass().getClassLoader();
  try{
   logoutClick=java.lang.reflect.Proxy.newProxyInstance(loader,new Class<?>[]{Class.forName("kotlin.jvm.functions.Function0",true,loader)},(proxy,method,args)->{
    if(method.getName().equals("invoke")){
     if(host.ready)host.web.evaluateJavascript("DuoSync.signOut()",null);
     return Class.forName("xv80",true,loader).getField("a").get(null);
    }
    if(method.getName().equals("equals"))return proxy==args[0];
    if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);
    return "DuoAero Google sign out";
   });
   return logoutClick;
  }catch(ReflectiveOperationException error){throw new IllegalStateException("Cannot attach original sign-out control",error);}
 }
 public static void changed(Application app){
  NativeGoogleHost host=instance;if(host==null)return;
  host.main.post(()->{if(host.ready&&!NativeAccountStore.current(app).isEmpty())host.web.evaluateJavascript("DuoSync.changed()",null);});
 }
 public static boolean acceptCallback(Application app,Uri uri){
  if(uri==null||!"com.duoaero".equals(uri.getScheme())||!"/oauth2redirect".equals(uri.getPath())||uri.getHost()!=null)return false;
  long requested=app.getSharedPreferences("duoaero-google",0).getLong("oauth-pending",0),now=System.currentTimeMillis();
  if(requested<=0||now<requested||now-requested>15*60*1000L||!"inhouse_notes_pkce".equals(uri.getQueryParameter("state")))return false;
  if(uri.getQueryParameter("code")==null&&uri.getQueryParameter("error")==null)return false;
  if(!app.getSharedPreferences("duoaero-google",0).edit().remove("oauth-pending").commit())return false;
  install(app);instance.callback(uri.getEncodedQuery());return true;
 }
 private void callback(String query){
  if(!ready){pending=query;return;}
  web.evaluateJavascript("window.handleInhouseNativeOAuth("+JSONObject.quote(query)+")",null);
 }
 private <T>T ui(Callable<T> action){
  if(Looper.myLooper()==Looper.getMainLooper())try{return action.call();}catch(Exception error){throw new IllegalStateException("Google account action failed",error);}
  FutureTask<T> task=new FutureTask<>(action);main.post(task);
  try{return task.get(20,TimeUnit.SECONDS);}catch(Exception error){task.cancel(false);throw new IllegalStateException("Google account action failed",error);}
 }
 private boolean hasSession(){for(Activity activity:sessions)if(!activity.isFinishing()&&!activity.isDestroyed())return true;return false;}
 private void launch(){Intent intent=app.getPackageManager().getLaunchIntentForPackage(app.getPackageName());if(intent==null)throw new IllegalStateException("Original launcher unavailable");app.startActivity(intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK));}
 @JavascriptInterface public void openAuthUrl(String raw){
  Uri uri=Uri.parse(raw);
  if(!"https".equals(uri.getScheme())||!"accounts.google.com".equals(uri.getHost())||!"/o/oauth2/v2/auth".equals(uri.getPath())
   ||!"com.duoaero:/oauth2redirect".equals(uri.getQueryParameter("redirect_uri"))||!"S256".equals(uri.getQueryParameter("code_challenge_method"))
   ||!"435784295430-unt269845n77h7k4g599is7ni2b0c9qb.apps.googleusercontent.com".equals(uri.getQueryParameter("client_id"))
   ||!"inhouse_notes_pkce".equals(uri.getQueryParameter("state"))||!"code".equals(uri.getQueryParameter("response_type"))
   ||!"https://www.googleapis.com/auth/drive".equals(uri.getQueryParameter("scope"))
   ||uri.getQueryParameter("code_challenge")==null||!uri.getQueryParameter("code_challenge").matches("[A-Za-z0-9_-]{43}"))throw new SecurityException("Unexpected Google authorization URL");
  ui(()->{
   if(hasSession())throw new IllegalStateException("Finish the current lesson before changing accounts");
   if(!app.getSharedPreferences("duoaero-google",0).edit().putLong("oauth-pending",System.currentTimeMillis()).commit())throw new IOException("Cannot preserve sign-in request");
   Activity activity=foreground.get();Intent intent=new Intent(Intent.ACTION_VIEW,uri);
   if(activity!=null)activity.startActivity(intent);else app.startActivity(intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));return null;
  });
 }
 @JavascriptInterface public void onAccount(String id,String label){
  NativeAccountStore.key(id);
  // JavascriptInterface calls arrive on the bridge thread. Wait for a path
  // refresh there, before posting the account transition to the UI thread.
  synchronized(NativeAccountStore.LOCK){
   ui(()->{
    String previous=NativeAccountStore.current(app);
    if(previous.equals(id)){NativeAccountStore.select(app,id,label);return null;}
    if(hasSession())throw new IllegalStateException("Finish the current lesson before changing accounts");
    String oldLabel=app.getSharedPreferences("duoaero-google",0).getString("label","");
    NativeAccountStore.select(app,id,label);
    try{NativeBootstrap.accountChanged(app,true);}
    catch(Exception error){NativeAccountStore.select(app,previous,oldLabel);NativeBootstrap.accountChanged(app,!previous.isEmpty());throw error;}
    manualSignIn=false;launch();return null;
   });
  }
 }
 @JavascriptInterface public String readProgressForAccount(String id){try{return NativeProgressSync.read(app,id);}catch(Exception error){throw new IllegalStateException("Cannot read this account's progress",error);}}
 @JavascriptInterface public String readAuthStorage(){try{return NativeAuthStorage.read(app);}catch(Exception error){throw new IllegalStateException("Cannot restore Google authentication storage",error);}}
 @JavascriptInterface public void writeAuthStorage(String key,String value){try{NativeAuthStorage.write(app,key,value);}catch(Exception error){throw new IllegalStateException("Cannot save Google authentication storage",error);}}
 @JavascriptInterface public void applyProgressForAccount(String id,String raw){
  final boolean changed;
  try{changed=NativeProgressSync.apply(app,id,raw);}catch(Exception error){throw new IllegalStateException("Cannot merge this account's progress",error);}
  if(changed)main.post(()->{pendingPathAccount=id;refreshPathIfIdle();});
 }
 private void refreshPathIfIdle(){
  if(pendingPathAccount.isEmpty()||hasSession())return;
  final String id=pendingPathAccount;pendingPathAccount="";
  pathRefresh.execute(()->{
   synchronized(NativeAccountStore.LOCK){
    if(!id.equals(NativeAccountStore.current(app)))return;
    try{NativeLocalCache.install(app,true);}catch(Exception error){android.util.Log.e("DuoAeroNative","Could not refresh original path after Drive merge",error);}
   }
  });
 }
 @JavascriptInterface public void onStatus(String message){
  main.post(()->{
   status=message;
   String lower=message.toLowerCase(java.util.Locale.ROOT);
   if(manualSignIn&&(lower.contains("failed")||lower.contains("cancelled")||lower.contains("retry")||lower.contains("invalid"))){
    Activity activity=foreground.get();if(activity!=null)Toast.makeText(activity,message,Toast.LENGTH_LONG).show();manualSignIn=false;
   }
   if(manualSync&&!message.startsWith("Syncing")){
    Activity activity=foreground.get();if(activity!=null)Toast.makeText(activity,message,Toast.LENGTH_LONG).show();manualSync=false;
   }
  });
 }
 @JavascriptInterface public void onSignedOut(){
  synchronized(NativeAccountStore.LOCK){
   ui(()->{
    if(hasSession())throw new IllegalStateException("Finish the current lesson before signing out");
    NativeAccountStore.select(app,"","");NativeBootstrap.accountChanged(app,false);launch();return null;
   });
  }
 }
 public void onActivityCreated(Activity activity,Bundle state){if(activity.getClass().getName().equals("com.duolingo.session.SessionActivity"))sessions.add(activity);}
 public void onActivityResumed(Activity activity){
  foreground=new WeakReference<>(activity);webContext.setBaseContext(activity);
  if(web.getParent()!=null)((ViewGroup)web.getParent()).removeView(web);
  View root=activity.findViewById(android.R.id.content);if(root instanceof ViewGroup)((ViewGroup)root).addView(web,new ViewGroup.LayoutParams(1,1));
  web.onResume();
  String screen=activity.getClass().getName();
  if(NativeAccountStore.required(app)&&NativeAccountStore.current(app).isEmpty()
    &&(screen.equals("com.duolingo.onboarding.WelcomeFlowActivity")||screen.equals("com.duolingo.splash.LaunchActivity"))){
   ViewTreeObserver.OnGlobalLayoutListener listener=()->welcome(activity);
   if(!welcomeObservers.containsKey(activity)){welcomeObservers.put(activity,listener);activity.getWindow().getDecorView().getViewTreeObserver().addOnGlobalLayoutListener(listener);}
   welcome(activity);
  }
 }
 private void welcome(Activity activity){
  if(!NativeAccountStore.current(app).isEmpty())return;
  int primaryId=app.getResources().getIdentifier("primaryButton","id","com.duolingo");
  View button=activity.findViewById(primaryId);
  if(button==null)button=activity.findViewById(app.getResources().getIdentifier("introFlowNewUserButton","id","com.duolingo"));
  if(button instanceof TextView){TextView text=(TextView)button;if(!"CONTINUE WITH GOOGLE".contentEquals(text.getText()))text.setText("CONTINUE WITH GOOGLE");button.setEnabled(true);button.setOnClickListener(view->connect(activity));}
  int secondaryId=app.getResources().getIdentifier("secondaryButton","id","com.duolingo");View secondary=activity.findViewById(secondaryId);
  if(secondary==null)secondary=activity.findViewById(app.getResources().getIdentifier("introFlowLoginButton","id","com.duolingo"));
  if(secondary!=null&&secondary.getVisibility()!=View.GONE)secondary.setVisibility(View.GONE);
 }
 public void onActivityPaused(Activity activity){if(foreground.get()==activity)web.onPause();}
 public void onActivityDestroyed(Activity activity){
  sessions.remove(activity);ViewTreeObserver.OnGlobalLayoutListener listener=welcomeObservers.remove(activity);
  main.post(this::refreshPathIfIdle);
  if(listener!=null&&activity.getWindow().getDecorView().getViewTreeObserver().isAlive())activity.getWindow().getDecorView().getViewTreeObserver().removeOnGlobalLayoutListener(listener);
  if(foreground.get()==activity){foreground.clear();if(web.getParent()!=null)((ViewGroup)web.getParent()).removeView(web);webContext.setBaseContext(app);}
 }
 public void onActivityStarted(Activity activity){}
 public void onActivityStopped(Activity activity){}
 public void onActivitySaveInstanceState(Activity activity,Bundle state){}
}
