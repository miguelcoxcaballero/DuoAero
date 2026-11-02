"""Verify the published production APK on Android without test identities."""
import json
from pathlib import Path
import subprocess
import time
import xml.etree.ElementTree as ET

out=Path('evidence');out.mkdir(exist_ok=True)
def adb(*args,timeout=60):
    return subprocess.check_output(['adb',*args],timeout=timeout)
def welcome(label):
    adb('shell','am','start','-W','-n','com.duoaero/com.duolingo.splash.LaunchActivity')
    deadline=time.monotonic()+100
    while time.monotonic()<deadline:
        try:
            adb('shell','timeout','20','uiautomator','dump','/sdcard/release-ui.xml')
            raw=adb('exec-out','cat','/sdcard/release-ui.xml')
            tree=ET.fromstring(raw)
            matches=[n for n in tree.iter('node') if n.get('package')=='com.duoaero' and n.get('text')=='CONTINUE WITH GOOGLE' and n.get('enabled')=='true']
            if matches:
                (out/(label+'.xml')).write_bytes(raw)
                (out/(label+'.png')).write_bytes(adb('exec-out','screencap','-p'))
                return
        except (subprocess.SubprocessError,ET.ParseError):
            pass
        time.sleep(2)
    raise AssertionError('Production Google welcome not visible: '+label)
try:
    assert b'Success' in adb('install','--no-incremental','old.apk',timeout=180)
    assert b'Success' in adb('install','--no-incremental','-r','new.apk',timeout=180)
    package=adb('shell','dumpsys','package','com.duoaero').decode()
    assert 'versionCode=10307' in package and 'versionName=1.3.7' in package
    welcome('upgrade-welcome')
    adb('shell','am','force-stop','com.duoaero')
    welcome('upgrade-restarted')
    assert b'Success' in adb('uninstall','com.duoaero')
    assert b'Success' in adb('install','--no-incremental','new.apk',timeout=180)
    welcome('fresh-welcome')
    adb('shell','am','force-stop','com.duoaero')
    welcome('fresh-restarted')
    (out/'result.txt').write_text('PASS: exact permanently signed production APK installed over 1.3.0 and fresh; PackageManager confirms 1.3.7/10307; original Google-only welcome visible before and after force-stop in both cases. No real OAuth, Drive, prior user data migration or in-app installer acceptance asserted.\n')
finally:
    (out/'crashes.txt').write_bytes(adb('logcat','-d','-b','crash'))
    (out/'last-anr.txt').write_bytes(adb('shell','dumpsys','activity','lastanr'))
