const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),crypto=require('node:crypto');
const {merge}=require('../shared/drive-sync.js');
const files=['config.js','inhouse-auth-functions.js','duoaero-auth-adapter.js'];
function runtime(store=new Map(),fetch=async()=>{throw Error('Unexpected network');}){
 const events=[],opened=[];
 const ctx={URL,URLSearchParams,TextEncoder,Uint8Array,crypto:crypto.webcrypto,btoa:s=>Buffer.from(s,'binary').toString('base64'),console,fetch,Date,
  setTimeout:()=>1,clearTimeout(){},Event:class{constructor(type){this.type=type;}},CustomEvent:class{constructor(type,init){this.type=type;this.detail=init?.detail;}},
  document:{getElementById:()=>({textContent:''})},localStorage:{getItem:k=>store.get(k)??null,setItem:(k,v)=>store.set(k,String(v)),removeItem:k=>store.delete(k)},
  location:{origin:'https://appassets.androidplatform.net',pathname:'/shared/auth-runtime.html',search:'',hash:''},history:{replaceState(){}},
  dispatchEvent:e=>events.push(e.type),InhouseNative:{openAuthUrl:u=>opened.push(u),onStatus(){}}};
 ctx.window=ctx;vm.createContext(ctx);for(const file of files)vm.runInContext(fs.readFileSync(require('node:path').join(__dirname,'../shared/auth',file),'utf8'),ctx);
 return {ctx,store,events,opened};
}
test('Android PKCE binds the new client, redirect and cryptographic challenge',async()=>{
 const r=runtime();await r.ctx.startAndroidPkceSignIn();const u=new URL(r.opened[0]);
 assert.equal(u.origin,'https://accounts.google.com');assert.equal(u.searchParams.get('client_id'),r.ctx.DUOAERO_ANDROID_CLIENT_ID);
 assert.equal(u.searchParams.get('redirect_uri'),'com.duoaero:/oauth2redirect');assert.equal(u.searchParams.get('access_type'),'offline');
 const verifier=r.store.get('duoaero-drive-pkce-verifier-v1');assert.equal(u.searchParams.get('code_challenge'),crypto.createHash('sha256').update(verifier).digest('base64url'));
 assert.equal(u.searchParams.get('scope'),'https://www.googleapis.com/auth/drive');
});
test('token exchange, restart and silent refresh retain the Google session',async()=>{
 const calls=[];const fetch=async(url,opts)=>{calls.push(new URLSearchParams(opts.body));return {ok:true,json:async()=>({access_token:'test-only-access',refresh_token:'test-only-refresh',expires_in:3600,scope:'https://www.googleapis.com/auth/drive'})};};
 const r=runtime(new Map(),fetch);await r.ctx.startAndroidPkceSignIn();await r.ctx.exchangeAuthCodeForTokens('test-only-code');
 assert.equal(calls[0].get('redirect_uri'),'com.duoaero:/oauth2redirect');assert.ok(calls[0].get('code_verifier'));assert.equal(r.store.has('duoaero-drive-pkce-verifier-v1'),false);
 const restarted=runtime(r.store,fetch);restarted.ctx.DuoAuth.init();assert.equal(await restarted.ctx.DuoAuth.token(),'test-only-access');assert.equal(calls.length,1);
 const data=JSON.parse(r.store.get('duoaero-drive-token-v1'));data.expiry=0;r.store.set('duoaero-drive-token-v1',JSON.stringify(data));
 const expired=runtime(r.store,fetch);await expired.ctx.refreshDriveAccessTokenWithRefreshToken();assert.equal(calls[1].get('grant_type'),'refresh_token');assert.equal(calls[1].get('refresh_token'),'test-only-refresh');
 expired.ctx.DuoAuth.signOut();assert.equal(r.store.has('duoaero-drive-refresh-token-v1'),false);assert.equal(expired.ctx.DuoAuth.connected(),false);
});
test('revoked refresh tokens are discarded',async()=>{
 const r=runtime(new Map([['duoaero-drive-refresh-token-v1','revoked']]),async()=>({ok:false,status:400,text:async()=>'invalid_grant'}));
 await assert.rejects(r.ctx.refreshDriveAccessTokenWithRefreshToken());assert.equal(r.store.has('duoaero-drive-refresh-token-v1'),false);
});
test('Android rejects unsolicited implicit tokens and callbacks without matching state',()=>{
 const r=runtime();assert.equal(r.ctx.handleInhouseNativeOAuth('access_token=injected&scope=https://www.googleapis.com/auth/drive'),false);
 assert.equal(r.ctx.handleInhouseNativeOAuth('code=unbound'),false);assert.equal(r.ctx.DuoAuth.connected(),false);
});
test('Drive merges preserve recent corrections, completed lessons and local session',()=>{
 const local={records:{a:{at:20,correct:true},b:{at:1,correct:false}},completedLessons:{l1:{at:5}},session:{cursor:4},xp:30};
 const remote={records:{a:{at:10,correct:false},b:{at:2,correct:true}},completedLessons:{l2:{at:6}},session:{cursor:99},xp:40};
 const out=merge(local,remote);assert.equal(out.records.a.correct,true);assert.equal(out.records.b.correct,true);assert.equal(out.session.cursor,4);assert.deepEqual(Object.keys(out.completedLessons),['l1','l2']);assert.equal(out.xp,40);assert.equal(local.records.b.correct,false);
});
test('Drive retries identity verification when the native account switch was rejected',async()=>{
 let reject=true,identified=0,uploaded=0;const reads=[],applies=[];
 const ctx={driveUserProfile:null,URLSearchParams,crypto:crypto.webcrypto,console,navigator:{onLine:true},document:{getElementById:()=>({textContent:''})},
  CustomEvent:class{},dispatchEvent(){},addEventListener(){},setInterval(){},setTimeout(){},clearTimeout(){},
  localStorage:{getItem:()=>null,setItem(){}},DuoAuth:{init(){},connected:()=>true,token:async()=>'synthetic-token'},
  InhouseNative:{onStatus(){},onAccount(id){identified++;if(reject)throw Error('Finish lesson');assert.equal(id,'account-b');},
   readProgressForAccount(id){reads.push(id);return '{"nativeSchema":1,"records":{},"completedLessons":{}}';},
   applyProgressForAccount(id,raw){applies.push(id);assert.equal(JSON.parse(raw).nativeSchema,1);}},
  fetch:async(url,opts)=>{
   if(url.includes('/about?'))return {ok:true,json:async()=>({user:{permissionId:'account-b'}})};
   if(url.includes('/upload/')){uploaded++;assert.match(opts.body,/account-b/);return {ok:true};}
   return {ok:true,json:async()=>({files:[]})};
  }};
 vm.createContext(ctx);vm.runInContext(fs.readFileSync(require('node:path').join(__dirname,'../shared/drive-sync.js'),'utf8'),ctx);
 await ctx.DuoSync.sync();assert.equal(identified,1);assert.deepEqual(reads,[]);assert.equal(uploaded,0);
 reject=false;await ctx.DuoSync.sync();assert.equal(identified,2);assert.equal(uploaded,1);
 assert.ok(reads.length>0);assert.ok(reads.every(id=>id==='account-b'));assert.deepEqual(applies,['account-b']);
});
