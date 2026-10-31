/* App wiring for the unchanged Inhouse Notes OAuth functions. */
const GOOGLE_CLIENT_ID='435784295430-cmug30o42f1vu4ijgor9sjb0ro4oo37o.apps.googleusercontent.com';
const DRIVE_SCOPE='https://www.googleapis.com/auth/drive';
// The reused scope validator checks this configured required scope; DuoAero needs Drive only.
const CALENDAR_SCOPE=DRIVE_SCOPE, GOOGLE_API_SCOPE=DRIVE_SCOPE;
const GOOGLE_SCOPE_VERSION='duoaero-drive-v1';
const DRIVE_TOKEN_KEY='duoaero-drive-token-v1', DRIVE_REMEMBER_KEY='duoaero-drive-remember-v1', DRIVE_REFRESH_TOKEN_KEY='duoaero-drive-refresh-token-v1', DRIVE_PKCE_VERIFIER_KEY='duoaero-drive-pkce-verifier-v1', GOOGLE_SCOPE_VERSION_KEY='duoaero-google-scope-version-v1', GOOGLE_GRANTED_SCOPES_KEY='duoaero-google-granted-scopes-v1';
const ANDROID_OAUTH_CLIENT_ID=window.DUOAERO_ANDROID_CLIENT_ID||'';
const ANDROID_PKCE_REDIRECT_URI='com.duoaero:/oauth2redirect';
const isInhouseApp=!!window.InhouseNative;
const useAndroidPkceFlow=()=>isInhouseApp&&!!ANDROID_OAUTH_CLIENT_ID;
let driveAccessToken=null,driveTokenExpiry=0,driveTokenClient=null,driveTokenRefreshTimer=null,driveSignedOut=false,driveAuthNeedsReconnect=false,driveUserProfile=null;
const driveStatusEl=document.getElementById('auth-status');
if(window.InhouseNative&&typeof MutationObserver!=='undefined')new MutationObserver(()=>window.InhouseNative.onStatus(driveStatusEl.textContent)).observe(driveStatusEl,{childList:true,characterData:true,subtree:true});
function updateDriveAuthUI(){window.dispatchEvent(new CustomEvent('duoaero-auth',{detail:{connected:!!driveAccessToken,reconnect:driveAuthNeedsReconnect}}));}
function refreshDriveFiles(){window.dispatchEvent(new Event('duoaero-sync'));}
function markDriveAuthNeedsReconnect(){driveAuthNeedsReconnect=true;driveAccessToken=null;driveTokenExpiry=0;clearDriveTokenStorage();updateDriveAuthUI();}
window.handleInhouseNativeOAuth=(payload)=>{const params=new URLSearchParams(String(payload||'').replace(/^[#?]/,''));const code=params.get('code');if(useAndroidPkceFlow()&&(!code||params.get('state')!=='inhouse_notes_pkce')){driveStatusEl.textContent=params.has('error')?'Google sign-in was cancelled. Please try again.':'Invalid sign-in response. Please try again.';return false;}if(code&&useAndroidPkceFlow()){exchangeAuthCodeForTokens(code).then(refreshDriveFiles).catch(()=>{driveStatusEl.textContent='Sign-in failed. Please try again.';});return true;}const ok=completeDriveSignInFromParams(params);if(ok)refreshDriveFiles();return ok;};
window.DuoAuth={init:()=>initDriveAuth(),signIn:()=>signInDrive(),token:()=>ensureDriveToken(false),connected:()=>!!driveAccessToken,signOut:()=>{driveSignedOut=true;driveAccessToken=null;driveTokenExpiry=0;clearTimeout(driveTokenRefreshTimer);for(const key of [DRIVE_TOKEN_KEY,DRIVE_REFRESH_TOKEN_KEY,DRIVE_REMEMBER_KEY,DRIVE_PKCE_VERIFIER_KEY,GOOGLE_SCOPE_VERSION_KEY,GOOGLE_GRANTED_SCOPES_KEY])localStorage.removeItem(key);updateDriveAuthUI();}};
