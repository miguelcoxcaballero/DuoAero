/* Android-only persistence adapter. The copied Notes OAuth functions stay unchanged. */
(function () {
 'use strict';
 const bridge=window.InhouseNative;
 if(!bridge||typeof bridge.readAuthStorage!=='function')return;
 const keys=new Set(['duoaero-drive-token-v1','duoaero-drive-remember-v1','duoaero-drive-refresh-token-v1','duoaero-drive-pkce-verifier-v1','duoaero-google-scope-version-v1','duoaero-google-granted-scopes-v1','drive-hint-email','drive-consent-granted','duoaero-device']);
 const storage=window.localStorage,proto=Storage.prototype,set=proto.setItem,remove=proto.removeItem,clear=proto.clear;
 const saved=JSON.parse(bridge.readAuthStorage());
 for(const key of keys){if(Object.hasOwn(saved,key))set.call(storage,key,saved[key]);else remove.call(storage,key);}
 proto.setItem=function(key,value){key=String(key);value=String(value);if(this===storage&&keys.has(key))bridge.writeAuthStorage(key,value);return set.call(this,key,value);};
 proto.removeItem=function(key){key=String(key);if(this===storage&&keys.has(key))bridge.writeAuthStorage(key,null);return remove.call(this,key);};
 proto.clear=function(){if(this===storage)for(const key of keys)bridge.writeAuthStorage(key,null);return clear.call(this);};
})();
