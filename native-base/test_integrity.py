"""Ensure the native-base experiment has not replaced original screens/resources."""
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

HOME = Path.home()
WORK = HOME/'.codex/duoaero-native-base'
allowed = {'AndroidManifest.xml', 'classes4.dex'}
with zipfile.ZipFile(HOME/'Downloads/Duolingo_v6.103.5.apk') as original, zipfile.ZipFile(WORK/'DuoAero-native-base-test.apk') as built:
    checked = 0
    for entry in original.infolist():
        name = entry.filename
        if name.startswith('META-INF/') or name in allowed:
            continue
        if name.startswith('res/font/duolingosansmath_') and name.endswith('.ttf'):
            continue
        assert original.read(name) == built.read(name), f'Original entry was changed: {name}'
        checked += 1
    assert 'classes12.dex' in built.namelist()
    assert 'assets/duoaero/licenses/NotoSansMath-OFL.txt' in built.namelist()
A = '{http://schemas.android.com/apk/res/android}'
manifest = ET.parse(WORK/'AndroidManifest.xml').getroot()
assert manifest.find('application').get(A+'name') == 'com.duolingo.core.DuoApp'
assert any(a.get(A+'name') == 'com.duolingo.session.SessionActivity' for a in manifest.findall('./application/activity'))
assert not any(a.get(A+'name') == 'com.duoaero.MainActivity' for a in manifest.findall('./application/activity'))
print(f'PASS: {checked} original APK entries preserved byte-for-byte, original application/session activity retained')
