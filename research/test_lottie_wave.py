"""Structural test only: does not claim actual Lottie playback or smoothness."""
import json,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'native-base'))
from runtime_config import APK
from lottie_wave import replace_wave
with zipfile.ZipFile(APK) as original:
    before=json.loads(original.read('res/raw/duo_waving.json'))
    after=json.loads(replace_wave(json.dumps(before)))
assert all(after.get(k)==before.get(k) for k in ('ip','op','fr','markers','w','h'))
assert len(after['layers'])==16
assets={a['id']:a for a in after['assets']}
assert all(len(assets[l['refId']]['layers'])==1 for l in after['layers'])
assert all(assets[l['refId']]['layers'][0]['refId']=='duoaero-wave-atlas' for l in after['layers'])
poses=[]
for t in range(int(after['ip']),int(after['op'])):
    active=0
    selected=None
    for i,layer in enumerate(after['layers']):
        keys=[k for k in layer['ks']['o']['k'] if k['t']<=t]
        assert keys
        if keys[-1]['s'][0]==100:active+=1;selected=i
    assert active==1,(t,active)
    poses.append(selected)
assert poses[0]==0 and poses[304]==15, 'Original 98.5% loop must return from final to initial pose'
print('PASS: one waving atlas cell per frame and original timing/markers; Android rendering, callback and smoothness remain unverified.')
