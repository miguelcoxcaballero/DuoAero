"""Inspect the real 1.3.0 updater UI; no app or catalog changes."""
import os,subprocess,time
from pathlib import Path
out=Path(os.environ['DUOAERO_EVIDENCE']);out.mkdir(parents=True,exist_ok=True)
def adb(*args): return subprocess.check_output(['adb',*args],timeout=45)
def snapshot(name):
    (out/(name+'.png')).write_bytes(adb('exec-out','screencap','-p'))
try:
    adb('shell','am','start','-W','-n','com.duoaero/com.duolingo.splash.LaunchActivity')
    time.sleep(25);snapshot('old-home')
    adb('root');adb('wait-for-device')
    adb('shell','am','start','-W','-n','com.duoaero/com.inhouse.services.updater.UpdateActivity','--ez','settings','true')
    time.sleep(15);snapshot('old-updater')
    adb('shell','input','tap','200','2220');time.sleep(4);snapshot('old-channel-warning')
finally:
    (out/'old-logcat.txt').write_bytes(adb('logcat','-d','-s','AndroidRuntime:E','DuoAeroNative:I'))
