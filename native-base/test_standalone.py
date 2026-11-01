"""Cold-start the installed APK and tap native path controls through adb only.

No profile injection, instrumentation activity, mock grade or backend bypass is
performed by this driver. The APK itself must initialize its original runtime.
"""
import os
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as ET

OUT=Path(os.environ.get('DUOAERO_EVIDENCE','/tmp/duoaero-evidence'))
OUT.mkdir(parents=True,exist_ok=True)
PACKAGE='com.duoaero.nativebase'

def adb(*args):
    return subprocess.check_output(['adb',*args],timeout=30)

def capture(name):
    (OUT/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'))
    adb('shell','uiautomator','dump','/sdcard/duoaero-standalone.xml')
    xml=adb('exec-out','cat','/sdcard/duoaero-standalone.xml')
    (OUT/(name+'.xml')).write_bytes(xml)
    return ET.fromstring(xml)

def tap(tree,resource):
    node=next((n for n in tree.iter('node') if n.get('package')==PACKAGE and n.get('resource-id')==resource and n.get('enabled')=='true'),None)
    if node is None:raise AssertionError('Native control unavailable: '+resource)
    x1,y1,x2,y2=map(int,re.findall(r'\d+',node.get('bounds')))
    adb('shell','input','tap',str((x1+x2)//2),str((y1+y2)//2))

try:
    adb('shell','am','force-stop',PACKAGE)
    assert b'Success' in adb('shell','pm','clear',PACKAGE)
    adb('shell','am','start','-W','-n',PACKAGE+'/com.duolingo.splash.LaunchActivity')
    tree=None
    for attempt in range(12):
        time.sleep(3)
        tree=capture('standalone-home')
        if any(n.get('resource-id')=='com.duolingo:id/oval' for n in tree.iter('node')):break
    assert any('Midterm 1' in n.get('text','') for n in tree.iter('node')), 'Original Aerospace home missing'
    tap(tree,'com.duolingo:id/oval')
    time.sleep(2)
    tree=capture('standalone-node')
    tap(tree,'com.duolingo:id/learnButton')
    time.sleep(15)
    tree=capture('standalone-question')
    assert any('Low delivery times.' in (n.get('text','')+n.get('content-desc','')) for n in tree.iter('node')), 'Original first course question missing'
    (OUT/'standalone-result.txt').write_text('PASS: cold start, original home, named node, first question. No completion or persistence asserted.\n')
finally:
    (OUT/'standalone-log.txt').write_bytes(adb('logcat','-d','-s','DuoAeroNative:I','AndroidRuntime:E','chromium:E'))
    (OUT/'standalone-anr.txt').write_bytes(adb('shell','dumpsys','activity','lastanr'))
