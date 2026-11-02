"""Ensure the native-base experiment has not replaced original screens/resources."""
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
import subprocess
import difflib
import os

from runtime_config import WORK, APK, BASE, tool
from resource_extension import updater_paths, launcher_mascot, scene_mascot, mood_scenes, MOOD_SCENES, MASCOT_PATH, SCENE_MASCOT_PATH
from branding import rebrand_table, animation_overlays, mascot_drawables, LOGO_PATH
from mascot_assets import parse
allowed = {'AndroidManifest.xml', 'resources.arsc', 'classes.dex', 'classes3.dex', 'classes4.dex', 'classes6.dex', 'classes7.dex', 'res/mipmap-anydpi-v21/ic_launcher.xml'}
if os.environ.get('DUOAERO_FORCE_SWOON')=='1':
    allowed.add('classes5.dex')  # Diagnostic-only forced character selector.
target = Path(os.environ.get('DUOAERO_VERIFY_APK', str(WORK/'DuoAero-native-base-test.apk')))
with zipfile.ZipFile(APK) as original, zipfile.ZipFile(target) as built:
    approved=(Path(__file__).resolve().parents[1]/'app/assets/mascot/welcome.png').read_bytes()
    overlays, animation_report=animation_overlays(original,approved)
    completion=animation_report['res/raw/lesson_complete_redesign_v72.riv']['artboards']
    assert '01_duo_epic_arboard' in completion
    assert 'EpicDuo_Eyes_artboard' not in completion, 'Do not draw a second mascot in a nested eye artboard'
    _, scene, _ = parse(overlays['res/raw/lesson_complete_redesign_v72.riv'])
    names = [values.get(4,'') for kind,values,_ in scene if kind == 1]
    secondary=[]; primary=[]; root=False
    for kind,values,_ in scene:
        if kind == 1: root=values.get(4)=='_interstitial_main_artboard'
        elif root and kind == 92 and values.get(5) in (371,632):
            target_id=values.get(197,-1)
            if 0<=target_id<len(names) and '_duo_' in names[target_id].lower():
                (primary if values[5]==371 else secondary).append(values.get(129,0))
    assert primary and secondary and any(not flags&1 for flags in primary)
    assert all(flags&1 for flags in secondary), 'Sparkle-only copies of the mascot must stay hidden'
    checked = 0
    for entry in original.infolist():
        name = entry.filename
        if name.startswith('META-INF/') or name in allowed:
            continue
        if name in overlays:
            assert built.read(name)==overlays[name], name
            continue
        if name.startswith('res/font/duolingosansmath_') and name.endswith('.ttf'):
            continue
        assert original.read(name) == built.read(name), f'Original entry was changed: {name}'
        checked += 1
    assert 'classes12.dex' in built.namelist()
    assert 'classes13.dex' in built.namelist()
    table, resource_id = updater_paths(original.read('resources.arsc'))
    table, scene_id = scene_mascot(table)
    table, mood_ids = mood_scenes(table)
    mascot_paths,wrappers,_=mascot_drawables(BASE,original.read('resources.arsc'))
    assert built.read('resources.arsc') == rebrand_table(launcher_mascot(table),mascot_paths)[0]
    assert set(wrappers)<=set(built.namelist())
    assert LOGO_PATH in built.namelist()
    assert built.read(MASCOT_PATH) == (Path(__file__).resolve().parents[1]/'app/assets/mascot/launcher.png').read_bytes()
    assert built.read(SCENE_MASCOT_PATH) == (Path(__file__).resolve().parents[1]/'app/assets/mascot/welcome.png').read_bytes()
    for mood,source in MOOD_SCENES.items():
        assert built.read('res/drawable/duoaero_scene_'+mood+'.png') == (Path(__file__).resolve().parents[1]/'app/assets/mascot'/source).read_bytes()
    assert built.read('res/mipmap-anydpi-v21/ic_launcher.xml') != original.read('res/mipmap-anydpi-v21/ic_launcher.xml')
    assert resource_id == 0x7f160016
    assert 'assets/duoaero/licenses/NotoSansMath-OFL.txt' in built.namelist()
    assert built.read('assets/duoaero/course/lesson-migrations.json') == (Path(__file__).resolve().parents[1]/'native-base/lesson-migrations.json').read_bytes()
    badging=subprocess.check_output([str(tool('aapt2')),'dump','badging',str(target)],text=True)
    if "package: name='com.duoaero' " in badging:
        assert 'assets/duoaero/google-required' in built.namelist()
        assert 'assets/duoaero/standalone-bootstrap' in built.namelist()
        assert 'application-debuggable' not in badging
        assert built.read('assets/shared/auth/inhouse-auth-functions.js') == (Path(__file__).resolve().parents[1]/'shared/auth/inhouse-auth-functions.js').read_bytes()
A = '{http://schemas.android.com/apk/res/android}'
manifest = ET.parse(WORK/'AndroidManifest.xml').getroot()
assert manifest.find('application').get(A+'name') == 'com.duolingo.core.DuoApp'
assert manifest.find('application').get(A+'resizeableActivity') == 'true'
assert all(c.get(A+'resizeableActivity')!='false' and A+'maxAspectRatio' not in c.attrib for c in manifest.findall('./application/activity'))
for component in manifest.find('application'):
    if any(any(category.get(A+'name') == 'android.intent.category.LAUNCHER' for category in intent.findall('category')) for intent in component.findall('intent-filter')):
        assert component.get(A+'label') == manifest.find('application').get(A+'label')
        assert component.get(A+'icon') == '@mipmap/ic_launcher'
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
after = resources(target)
before_ids=[line.strip() for line in before if line.strip().startswith('resource 0x')]
after_ids=[line.strip() for line in after if line.strip().startswith('resource 0x')]
added_ids={0x7f160016,scene_id,*mood_ids.values()}
assert [line for line in after_ids if not any(f'0x{item:08x} ' in line for item in added_ids)]==before_ids, 'Original resource IDs changed'
assert any('resource 0x7f160016 xml/inhouse_update_paths' in line for line in after_ids)
assert any(f'resource 0x{scene_id:08x} drawable/duoaero_scene_mascot' in line for line in after_ids)
assert any('Already on DuoAero' in line for line in after), 'A visible plural still uses the old app name'
assert not any('Already on Duolingo' in line for line in after), 'Plural branding was not replaced'
print(f'PASS: {checked} original APK entries preserved byte-for-byte, original application/session activity retained')
print(f'PASS: original resource IDs preserved, branding and {len(overlays)} mascot animations replaced, canonical provider retained, portrait window resizable')
