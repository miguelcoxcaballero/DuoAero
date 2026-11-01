"""Verify the app window uses S24 Ultra proportions; not physical Samsung QA."""
import os,re,struct,xml.etree.ElementTree as E
from pathlib import Path
out=Path(os.environ['DUOAERO_EVIDENCE'])
for name in ('standalone-home','standalone-question','standalone-restored-home','standalone-next-lesson'):
    png=(out/(name+'.png')).read_bytes()
    w,h=struct.unpack_from('>II',png,16)
    assert (w,h)==(1440,3120),(name,w,h)
    root=E.parse(out/(name+'.xml'))
    bounds=[list(map(int,re.findall(r'\d+',n.get('bounds','')))) for n in root.iter('node') if n.get('package')=='com.duoaero.nativebase']
    assert any(len(b)==4 and b[2]-b[0]>=w*.98 and b[3]-b[1]>=h*.9 for b in bounds), (name,'letterboxed app bounds')
(out/'s24-result.txt').write_text('PASS: original home, question, restored path and next lesson use 1440x3120 screenshots and app bounds above 90% of height. Emulator geometry, not a physical Samsung test.\n')
