const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const source=fs.readFileSync('shared/auth/native-storage.js','utf8');
function boot(saved={},fail=false){
 class Storage{constructor(){this.values=new Map();}getItem(k){return this.values.get(k)??null;}setItem(k,v){this.values.set(k,String(v));}removeItem(k){this.values.delete(k);}clear(){this.values.clear();}}
 const localStorage=new Storage(),sessionStorage=new Storage();
 const bridge={readAuthStorage:()=>JSON.stringify(saved),writeAuthStorage(k,v){if(fail)throw Error('disk write failed');if(v===null)delete saved[k];else saved[k]=v;}};
 const context={Storage,window:{localStorage,InhouseNative:bridge}};
 vm.runInNewContext(source,context);return {localStorage,sessionStorage,saved};
}
test('Google storage survives a new WebView and deletions stay deleted',()=>{
 const key='duoaero-drive-refresh-token-v1',saved={};let page=boot(saved);
 page.localStorage.setItem(key,'synthetic-test-value');assert.equal(saved[key],'synthetic-test-value');
 page=boot(saved);assert.equal(page.localStorage.getItem(key),'synthetic-test-value');
 page.localStorage.removeItem(key);assert.equal(boot(saved).localStorage.getItem(key),null);
});
test('storage commits fail before the page claims durable state',()=>{
 const page=boot({},true);assert.throws(()=>page.localStorage.setItem('duoaero-drive-pkce-verifier-v1','synthetic-value'),/disk/);
 assert.equal(page.localStorage.getItem('duoaero-drive-pkce-verifier-v1'),null);
});
test('only allowed local keys are sent to native storage; session storage is independent',()=>{
 const page=boot({});page.localStorage.setItem('unrelated','value');page.sessionStorage.setItem('duoaero-drive-token-v1','session-only');
 assert.deepEqual(page.saved,{});page.localStorage.setItem('duoaero-device','test-device');page.localStorage.clear();assert.deepEqual(page.saved,{});
});
