"""Check the rebranded wordmark on the actual original welcome screen."""
import os
import re
import subprocess
import time
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image

OUT = Path(os.environ['DUOAERO_EVIDENCE'])
PACKAGE = 'com.duoaero.nativebase'

def adb(*args):
    return subprocess.check_output(['adb', *args], timeout=30)

adb('shell','am','force-stop',PACKAGE)
assert b'Success' in adb('shell','pm','clear',PACKAGE)
adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
deadline=time.monotonic()+90
while time.monotonic()<deadline:
    try:
        adb('shell','timeout','15','uiautomator','dump','/sdcard/welcome-wordmark.xml')
        xml=adb('exec-out','cat','/sdcard/welcome-wordmark.xml')
        root=ElementTree.fromstring(xml)
        logos=[n for n in root.iter('node') if n.get('resource-id')=='com.duolingo:id/logo']
        if logos:
            break
    except (subprocess.SubprocessError,ElementTree.ParseError):
        pass
    time.sleep(2)
else:
    raise AssertionError('Original welcome logo not observed')
(OUT/'welcome-wordmark.xml').write_bytes(xml)
(OUT/'welcome-wordmark.png').write_bytes(adb('exec-out','screencap','-p'))
a,b,c,d=map(int,re.findall(r'\d+',logos[0].get('bounds')))
with Image.open(OUT/'welcome-wordmark.png') as image:
    crop=image.convert('RGB').crop((a,b,c,d))
    points=[(x,y) for y in range(crop.height) for x in range(crop.width)
            if (lambda r,g,bl: bl>130 and g>70 and bl>r*1.2)(*crop.getpixel((x,y)))]
assert points, 'Wordmark has no visible blue lettering'
width=max(x for x,y in points)-min(x for x,y in points)
assert width>crop.width*.45, f'Wordmark is unexpectedly narrow: {width}/{crop.width}'
print('PASS: DuoAero wordmark occupies the original welcome logo view; other screens unverified.')
