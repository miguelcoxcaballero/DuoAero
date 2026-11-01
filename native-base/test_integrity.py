"""Ensure the native-base experiment has not replaced original screens/resources."""
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

from runtime_config import WORK, APK
allowed = {'AndroidManifest.xml', 'classes.dex', 'classes3.dex', 'classes4.dex', 'classes6.dex', 'classes7.dex'}
with zipfile.ZipFile(APK) as original, zipfile.ZipFile(WORK/'DuoAero-native-base-test.apk') as built:
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
