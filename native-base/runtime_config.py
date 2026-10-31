"""Local diagnostic paths. No production credentials are used by these builds."""
import os
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
def path(name, default):
    return Path(os.environ.get(name, str(default))).expanduser().resolve()
WORK = path('DUOAERO_WORK', HOME/'.codex/duoaero-native-base')
BASE = path('DUOAERO_DECODED', HOME/'.codex/duolingo-reference-decoded')
SMALI = path('DUOAERO_SMALI', HOME/'.codex/duoaero-original-patch')
APK = path('DUOAERO_APK', HOME/'Downloads/Duolingo_v6.103.5.apk')
SDK = path('ANDROID_HOME', os.environ.get('ANDROID_SDK_ROOT', HOME/'AppData/Local/Android/Sdk'))
BT = SDK/'build-tools'/os.environ.get('DUOAERO_BUILD_TOOLS', '35.0.0')
JAR = SDK/'platforms'/os.environ.get('DUOAERO_PLATFORM', 'android-36')/'android.jar'
APKTOOL = path('DUOAERO_APKTOOL', HOME/'.codex/apktool_2.12.1.jar')
KEY = ROOT/'build/debug.p12'
def executable(folder, name):
    return folder/(name + ('.exe' if os.name == 'nt' else ''))
def java(name):
    if os.environ.get('JAVA_HOME'):
        return executable(Path(os.environ['JAVA_HOME'])/'bin', name)
    found = shutil.which(name)
    if found:
        return Path(found)
    if os.name == 'nt':
        return executable(Path('C:/Program Files/Android/Android Studio/jbr/bin'), name)
    raise FileNotFoundError(f'{name} is missing; install a JDK and set JAVA_HOME')
def tool(name):
    return executable(BT, name)
ADB = executable(SDK/'platform-tools', 'adb')
