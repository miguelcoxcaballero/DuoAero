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
    adb('shell','input','tap','1175','2775');time.sleep(4);snapshot('old-channel-slider')
    adb('shell','input','touchscreen','swipe','155','2515','1390','2515','1800');time.sleep(30);snapshot('old-check-release')
    adb('shell','appops','set','com.duoaero','REQUEST_INSTALL_PACKAGES','allow')
    (out/'install-appop.txt').write_bytes(adb('shell','appops','get','com.duoaero','REQUEST_INSTALL_PACKAGES'))
    adb('shell','sh','-c',"'echo updater-preservation-test > /data/user/0/com.duoaero/files/duoaero-update-probe'")
    adb('shell','input','tap','1195','2775');time.sleep(5);snapshot('old-update-started')
    installer=False
    for i in range(120):
        time.sleep(5)
        focused=adb('shell','dumpsys','window','windows').decode(errors='replace')
        (out/'last-window.txt').write_text(focused)
        if i%12==0:snapshot('download-'+str(i))
        current='\n'.join(line for line in focused.splitlines() if 'mCurrentFocus=' in line or 'mFocusedApp=' in line)
        if 'packageinstaller' in current.lower():
            installer=True;snapshot('old-system-installer');break
    if not installer:raise AssertionError('Android package installer did not appear in ten minutes')
finally:
    (out/'old-logcat.txt').write_bytes(adb('logcat','-d','-s','AndroidRuntime:E','DuoAeroNative:I'))
