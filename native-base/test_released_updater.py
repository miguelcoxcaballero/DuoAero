"""Inspect the real 1.3.0 updater UI; no app or catalog changes."""
import os,re,subprocess,time
from pathlib import Path
out=Path(os.environ['DUOAERO_EVIDENCE']);out.mkdir(parents=True,exist_ok=True)
expected_version=os.environ.get('DUOAERO_EXPECT_VERSION','1.3.7')
expected_code=os.environ.get('DUOAERO_EXPECT_CODE','10307')
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
        # Android 15's 'dumpsys window windows' exposes the installer as a
        # WindowState, but does not include mCurrentFocus in this output.
        if 'com.google.android.packageinstaller/com.android.packageinstaller.PackageInstallerActivity' in focused:
            installer=True;snapshot('old-system-installer');break
    if not installer:raise AssertionError('Android package installer did not appear in ten minutes')
    adb('shell','input','tap','1185','1745')
    installed=False
    for i in range(120):
        time.sleep(2)
        info=adb('shell','dumpsys','package','com.duoaero').decode(errors='replace')
        if re.search(r'versionName='+re.escape(expected_version)+r'\s',info) and re.search(r'versionCode='+re.escape(expected_code)+r'\s',info):
            installed=True;(out/'installed-package.txt').write_text(info);break
    snapshot('old-update-result')
    if not installed:raise AssertionError('Android did not report the expected installed version')
    marker=adb('shell','cat','/data/user/0/com.duoaero/files/duoaero-update-probe').decode().strip()
    if marker!='updater-preservation-test':raise AssertionError('Synthetic app data was not preserved')
    # The installer can remain on its success dialog after package manager
    # reports the new version. Close it and require a fresh app process; a
    # mere successful intent or pid can otherwise produce a false positive.
    time.sleep(20)
    adb('shell','am','force-stop','com.google.android.packageinstaller')
    adb('shell','am','force-stop','com.duoaero')
    launch=adb('shell','am','start','-W','-n','com.duoaero/com.duolingo.splash.LaunchActivity').decode(errors='replace')
    (out/'updated-launch.txt').write_text(launch)
    if 'Status: ok' not in launch:raise AssertionError('Updated app did not launch')
    foreground=False
    for i in range(12):
        time.sleep(5)
        activities=adb('shell','dumpsys','activity','activities').decode(errors='replace')
        (out/'updated-activities.txt').write_text(activities)
        if re.search(r'(?:topResumedActivity|mResumedActivity).*com\.duoaero/',activities):
            foreground=True;break
    snapshot('updated-launch')
    if not foreground:raise AssertionError('Updated app did not reach a resumed foreground activity')
    if not adb('shell','pidof','com.duoaero').strip():raise AssertionError('Updated app process did not remain running')
    (out/'update-result.txt').write_text('PASS: signed 1.3.0 discovered and installed version '+expected_version+' (code '+expected_code+'); synthetic app data survived and the updated app launched. Real Google data and physical devices were not tested.\n')
finally:
    (out/'old-logcat.txt').write_bytes(adb('logcat','-d','-s','AndroidRuntime:E','DuoAeroNative:I'))
