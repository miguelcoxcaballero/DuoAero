(function(global){
'use strict';
function merge(a={},b={}){const out=JSON.parse(JSON.stringify(a));out.records={...(a.records||{})};for(const [id,r] of Object.entries(b.records||{})){const l=out.records[id];if(!l||Number(r.at)>Number(l.at))out.records[id]=r;}out.completedLessons={...(a.completedLessons||{})};for(const [id,l] of Object.entries(b.completedLessons||{})){if(!out.completedLessons[id]||l.at>out.completedLessons[id].at)out.completedLessons[id]=l;}out.xp=Math.max(a.xp||0,b.xp||0);out.updatedAt=Math.max(a.updatedAt||0,b.updatedAt||0);return out;}
if(typeof module!=='undefined')module.exports={merge};
if(!global.document)return;
let busy=false,again=false,account=null,timer=null,generation=0;
const bridge=global.InhouseNative;
function status(message){document.getElementById('auth-status').textContent=message;if(bridge)bridge.onStatus(message);global.dispatchEvent(new CustomEvent('duoaero-sync-status',{detail:message}));}
async function api(path,options={}){const token=await DuoAuth.token();const res=await fetch('https://www.googleapis.com/drive/v3/'+path,{...options,headers:{...options.headers,Authorization:'Bearer '+token}});if(!res.ok){if(res.status===401){markDriveAuthNeedsReconnect();}throw Error('Drive '+res.status);}return res;}
function local(){return bridge?JSON.parse(bridge.readProgress()):JSON.parse(localStorage.getItem('duoaero-progress:'+account.permissionId)||'{}');}
function apply(state){if(bridge)bridge.applyProgress(JSON.stringify(state));else {localStorage.setItem('duoaero-progress:'+account.permissionId,JSON.stringify(state));global.dispatchEvent(new CustomEvent('duoaero-progress',{detail:state}));}}
async function identify(epoch){const data=await(await api('about?fields=user(permissionId,emailAddress,displayName)')).json();if(epoch!==generation)throw Error("Account changed");account=data.user;if(!account?.permissionId)throw Error('Missing account identity');driveUserProfile={email:account.emailAddress};localStorage.setItem('drive-hint-email',account.emailAddress||'');if(bridge)bridge.onAccount(account.permissionId,account.emailAddress||account.displayName||'Google account');global.dispatchEvent(new CustomEvent('duoaero-account',{detail:account}));return account;}
async function sync(){if(busy){again=true;return;}busy=true;const epoch=generation;const check=()=>{if(epoch!==generation)throw Error("Account changed");};try{
 if(!DuoAuth.connected())return;
 if(!account)await identify(epoch);check();
 status('Syncing with Google Drive...');
 let combined=local(),files=[],page='';do{const query=new URLSearchParams({q:"trashed=false and appProperties has { key='duoaeroProgress' and value='v1' }",fields:'nextPageToken,files(id,appProperties)',pageSize:'1000'});if(page)query.set('pageToken',page);const data=await(await api('files?'+query)).json();check();files.push(...data.files);page=data.nextPageToken||'';}while(page);
 for(const file of files){const remote=await(await api('files/'+encodeURIComponent(file.id)+'?alt=media')).json();check();if(remote.schema===1&&remote.account===account.permissionId)combined=merge(combined,remote.progress);}
 // Merge again: studying may have continued while the network requests ran.
 combined=merge(local(),combined);apply(combined);
 let device=localStorage.getItem('duoaero-device');if(!device){device=crypto.randomUUID();localStorage.setItem('duoaero-device',device);}
 const payload={schema:1,account:account.permissionId,progress:local()};delete payload.progress.session;
 const mine=files.find(f=>f.appProperties?.device===device);
 const token=await DuoAuth.token();check();let result;
 if(mine){result=await fetch('https://www.googleapis.com/upload/drive/v3/files/'+encodeURIComponent(mine.id)+'?uploadType=media',{method:'PATCH',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify(payload)});}
 else{const boundary='duoaero_'+crypto.randomUUID();const metadata={name:'DuoAero progress',mimeType:'application/json',appProperties:{duoaeroProgress:'v1',device}};const body='--'+boundary+'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+JSON.stringify(metadata)+'\r\n--'+boundary+'\r\nContent-Type: application/json\r\n\r\n'+JSON.stringify(payload)+'\r\n--'+boundary+'--';result=await fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart',{method:'POST',headers:{Authorization:'Bearer '+token,'Content-Type':'multipart/related; boundary='+boundary},body});}
 check();if(!result.ok)throw Error('Drive upload '+result.status);status('Saved to Google Drive');
 }catch(error){if(epoch===generation)status(navigator.onLine?'Progress saved on this device. Google Drive sync will retry.':'Offline. Progress saved on this device.');}finally{busy=false;if(again){again=false;queue();}}}
function queue(){clearTimeout(timer);timer=setTimeout(sync,1500);}
global.DuoSync={sync,changed:queue,merge,signOut(){generation++;account=null;clearTimeout(timer);again=false;DuoAuth.signOut();if(bridge)bridge.onSignedOut();}};
addEventListener('duoaero-sync',()=>{generation++;account=null;sync();});addEventListener('online',queue);addEventListener('focus',queue);setInterval(()=>{if(DuoAuth.connected())sync();},60000);
DuoAuth.init();
})(globalThis);
