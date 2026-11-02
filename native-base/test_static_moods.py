"""Check source pose selection and resource table extensions; Android UI is separate."""
from pathlib import Path
from PIL import Image
from branding import LOGO_PATH, mascot_name, static_mood, mascot_drawables, rebrand_table
from resource_extension import MOOD_SCENES, mood_scenes, scene_mascot, updater_paths
from runtime_config import APK, ROOT, BASE
import zipfile

for name,expected in {'duo_chest':'chest_hug','duo_welcome':'phone_static','duo_wave':'wave_static','duo_happy':'wave','duo_flying':'plane','duo_thinking':'think',
                      'jaw_drop_duo':'surprised','lovey_dovey_duo':'lovey',
                      'foam_finger_duo':'foam','duo_breathe':'zen',
                      'practice_hub_duo_radio_falstaff_1':'charlie',
                      'practice_hub_duo_radio_chatting_with_zari_01':'sally',
                      'duo_radio_host_static_bea':'patty'}.items():
    assert mascot_name(name) and static_mood(name)==expected,(name,expected)
for name in ('duo_radio_play','duo_radio_check_correct','super_duo_fly_glow','super_duo_light_beam'):
    assert not mascot_name(name), name
assert static_mood('duo_sad') == 'sad'
assert static_mood('duo_reading_stories') == 'reading'
assert static_mood('stories_duo_reading') == 'reading'
assert static_mood('duo_holding_gem') == 'gem'
assert static_mood('guidebook_header_duo_gem') == 'gem'
assert static_mood('character_falstaff') == 'charlie'
assert static_mood('duoradio_host_zari_exercise_correct') == 'sally_happy'
assert static_mood('duoradio_host_zari_exercise_incorrect') == 'sally_sad'
assert not mascot_name('duoradio_play') and not mascot_name('bea_junior_zari')
for mood,source in MOOD_SCENES.items():
    with Image.open(ROOT/'app/assets/mascot'/source) as image:
        assert image.mode=='RGBA' and image.getchannel('A').getextrema()[0]==0,mood
# The native drawable slices this atlas at quarter-width/height boundaries.
# No visible pixels may touch a seam: otherwise a neighbouring pose leaks
# into the next frame or its body is clipped at the boundary.
for atlas in ('wave-atlas.png','sad-atlas.png'):
    with Image.open(ROOT/'app/assets/mascot'/atlas) as image:
        alpha=image.getchannel('A');width,height=image.size
        for i in range(1,4):
            x=width*i//4;y=height*i//4
            assert max(alpha.getpixel((x,v)) for v in range(height))<=8,(atlas,'column',i)
            assert max(alpha.getpixel((u,y)) for u in range(width))<=8,(atlas,'row',i)
with zipfile.ZipFile(APK) as base:table=base.read('resources.arsc')
paths,xml,_=mascot_drawables(BASE,table)
assert all('class="com.duoaero.nativebase.' not in value for value in xml.values())
_,report=rebrand_table(table,paths)
for name in ('intro_duo_logo_green','duo_logo_green','duo_logo_grey','duo_logo_white'):
    assert report['drawable_resources'][name]==LOGO_PATH,name
for path,name in report['original_paths'].items():
    if name=='duo_happy' and path in paths:
        assert '@drawable/duoaero_scene_celebrate' in xml[paths[path]]
table,provider=updater_paths(table);table,scene=scene_mascot(table);table,ids=mood_scenes(table)
assert provider==0x7f160016 and len(ids)==len(MOOD_SCENES)
assert len(set(ids.values())|{scene})==len(MOOD_SCENES)+1
print('PASS: explicit static poses, alpha and added drawable IDs; native appearance not yet tested.')
