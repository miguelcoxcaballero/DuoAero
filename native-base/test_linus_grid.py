"""Validate the original grid animation patch; Android playback is separate."""
from pathlib import Path
from PIL import Image
from mascot_assets import linus_grid, parse
from runtime_config import BASE, ROOT

source=(BASE/'res/raw/math_junior_grid.riv').read_bytes()
patched,boards=linus_grid(source)
_,original,_=parse(source);_,result,_=parse(patched)
assert boards==['math_junior_grid'] and source!=patched
def names(objects,kind,key):return [v.get(key) for k,v,_ in objects if k==kind]
assert names(original,31,55)==names(result,31,55)==['Timeline 1']
assert names(original,53,55)==names(result,53,55)  # preserve original state data
assert names(original,1,4)==names(result,1,4)==['math_junior_grid']
for name in ('Frog','Junior Grid','Junior','Face'):
    assert name in names(result,2,4),name
files=[ROOT/'app/assets/mascot/path-linus'/name for name in ('open.png','closed.png','half.png')]
for file in files:
    with Image.open(file) as im:
        assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0
assert [v[212] for k,v,_ in result if k==106]==[file.read_bytes() for file in files]
images=[v for k,v,_ in result if k==100 and v.get(4,'').startswith('DuoAero Linus')]
assert len(images)==3 and all(v.get(5)==260 for v in images)
assert sum(k==42 and v.get(92)==258 for k,v,_ in result)==2
assert {253,255}.issubset({v.get(51) for k,v,_ in result if k==25})
print('PASS: original grid state/timeline, transparent Linus frames and blink tracks; Android playback unverified.')
