"""Check source pose selection and resource table extensions; Android UI is separate."""
from pathlib import Path
from PIL import Image
from branding import mascot_name, static_mood
from resource_extension import MOOD_SCENES, mood_scenes, scene_mascot, updater_paths
from runtime_config import APK, ROOT
import zipfile

for name,expected in {'duo_happy':'celebrate','duo_flying':'plane','duo_thinking':'think',
                      'jaw_drop_duo':'surprised','lovey_dovey_duo':'lovey',
                      'foam_finger_duo':'foam','duo_breathe':'zen',
                      'practice_hub_duo_radio_falstaff_1':'charlie',
                      'practice_hub_duo_radio_chatting_with_zari_01':'sally',
                      'duo_radio_host_static_bea':'patty'}.items():
    assert mascot_name(name) and static_mood(name)==expected,(name,expected)
for name in ('duo_radio_play','duo_radio_check_correct','super_duo_fly_glow','super_duo_light_beam'):
    assert not mascot_name(name), name
assert static_mood('duo_sad') == 'sad'
for mood,source in MOOD_SCENES.items():
    with Image.open(ROOT/'app/assets/mascot'/source) as image:
        assert image.mode=='RGBA' and image.getchannel('A').getextrema()[0]==0,mood
with zipfile.ZipFile(APK) as base:table=base.read('resources.arsc')
table,provider=updater_paths(table);table,scene=scene_mascot(table);table,ids=mood_scenes(table)
assert provider==0x7f160016 and len(ids)==len(MOOD_SCENES)
assert len(set(ids.values())|{scene})==len(MOOD_SCENES)+1
print('PASS: explicit static poses, alpha and added drawable IDs; native appearance not yet tested.')
