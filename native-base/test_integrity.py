"""Ensure the native-base experiment has not replaced original screens/resources."""
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
import subprocess
import difflib

from runtime_config import WORK, APK, tool
from resource_extension import updater_paths
allowed = {'AndroidManifest.xml', 'resources.arsc', 'classes.dex', 'classes3.dex', 'classes4.dex', 'classes6.dex', 'classes7.dex'}
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
    assert 'classes13.dex' in built.namelist()
    table, resource_id = updater_paths(original.read('resources.arsc'))
    assert built.read('resources.arsc') == table
    assert resource_id == 0x7f160016
    assert 'assets/duoaero/licenses/NotoSansMath-OFL.txt' in built.namelist()
A = '{http://schemas.android.com/apk/res/android}'
manifest = ET.parse(WORK/'AndroidManifest.xml').getroot()
assert manifest.find('application').get(A+'name') == 'com.duolingo.core.DuoApp'
assert any(a.get(A+'name') == 'com.duolingo.session.SessionActivity' for a in manifest.findall('./application/activity'))
assert not any(a.get(A+'name') == 'com.duoaero.MainActivity' for a in manifest.findall('./application/activity'))
provider = next(p for p in manifest.findall('./application/provider') if p.get(A+'authorities','').endswith('.update-provider'))
assert provider.get(A+'name') == 'com.inhouse.services.updater.UpdateFileProvider'
assert provider.find('meta-data').get(A+'resource') == '@xml/inhouse_update_paths'
# Independently decode both tables: every pre-existing ID/configuration/value
# must be identical. Only the new XML entry and its type count may differ.
def resources(apk):
    return subprocess.check_output([str(tool('aapt2')), 'dump', 'resources', str(apk)], text=True).splitlines()
before = resources(APK)
after = resources(WORK/'DuoAero-native-base-test.apk')
changes = list(difflib.ndiff(before, after))
removed = [line[2:] for line in changes if line.startswith('- ')]
added = [line[2:] for line in changes if line.startswith('+ ')]
assert len(removed) == 1 and 'type xml id=16 entryCount=' in removed[0], removed
assert len(added) == 3 and 'type xml id=16 entryCount=' in added[0], added
assert 'resource 0x7f160016 xml/inhouse_update_paths' in added[1], added
assert 'res/xml/inhouse_update_paths.xml' in added[2], added
print(f'PASS: {checked} original APK entries preserved byte-for-byte, original application/session activity retained')
print('PASS: all original resource IDs/configurations/values unchanged; canonical updater provider added')
