"""Check transparent source poses and the original Rive animation tracks."""
import io
import json
import struct
import zipfile
from pathlib import Path

from PIL import Image

from mascot_assets import CHARACTER_CAST, COMPONENT, SCHEMA, lottie, parse, rive
from runtime_config import APK, ROOT

frames = [(ROOT / 'app/assets/mascot/celebrate' / f'frame-{i:02}.png').read_bytes() for i in range(16)]
assert len(set(frames)) == 16
for frame in frames:
    with Image.open(io.BytesIO(frame)) as image:
        assert image.mode == 'RGBA'
        alpha = image.getchannel('A')
        assert alpha.getextrema() == (0, 255)
        # Fully opaque portions of every pose remain safely within the cell.
        box = alpha.point(lambda a: 255 if a > 64 else 0).getbbox()
        assert box and box[0] >= 4 and box[1] >= 4
        assert box[2] <= image.width - 4 and box[3] <= image.height - 4

png = (ROOT / 'app/assets/mascot/welcome.png').read_bytes()
width, height = struct.unpack_from('>II', png, 16)
with zipfile.ZipFile(APK) as original:
    # In this original scene an auxiliary pupil precedes the 600px character.
    # The old first-artboard rule rendered Snoopy inside Duo's eye.
    _, obsessed = rive(original.read('res/raw/duo_obsessed_02.riv'), 'duo_obsessed_02', png, width, height)
    assert 'lc_character_artboard' in obsessed
    assert 'ObsessedDuo_LPupilGlisten_artboard' not in obsessed
    for name, target, idle, start, end in [
            ('duo_perfect_epic_03', 'lc_character_artboard', 'EpicDuo_IdleLoop', 70, 190),
            ('duo_perfect_lfg_03', 'lc_character_artboard', 'Duo_LFG_IdleLoop', 60, 180),
            ('duo_perfect_jaw_drop_04', 'lc_character_artboard', 'JawdropDuo_Loop_animation', 120, 240),
            ('duo_obsessed_02', 'lc_character_artboard', 'ObsessedDuo_IdleLoop', 120, 240),
            ('duo_perfect_starry_eyed_03', 'lc_character_artboard', 'StarryEyedDuo_Loop_animation', 120, 240),
            ('duo_perfect_buff_03', 'lc_character_artboard', 'BuffDuo_IdleLoop', 61, 183),
            ('duo_normal_lovey_dovey_03', 'lc_character_artboard', 'LoveyDoveyDuo_Loop_animation', 120, 240),
            ('duo_perfect_chefs_kiss_03', 'lc_character_artboard', 'ChefsKissDuo_Loop_animation', 120, 240),
            ('duo_normal_foam_finger_02', 'lc_character_artboard', 'FoamFingerDuo_Loop_animation', 120, 240),
            ('duo_zen_04', '36_zen_duo', 'duo_meditate_loop', 69, 171),
            ('lesson_complete_main_29', 'lc_character_artboard', 'BuffDuo_IdleLoop', 61, 183),
            ('lesson_complete_redesign_v72', '01_duo_epic_arboard', 'EpicDuo_IdleLoop', 70, 190),
            ('lesson_complete_redesign_v72', '04_duo_lfg_artboard', 'Duo_LFG_IdleLoop', 60, 180),
            ('lesson_complete_redesign_v72', '02_duo_obsessed_artboard', 'ObsessedDuo_IdleLoop', 120, 240),
            ('lesson_complete_redesign_v72', '00_duo_buff_artboard', 'BuffDuo_IdleLoop', 61, 183),
            ('lesson_complete_redesign_v72', '22_duo_perfect_starry_eyed_artboard', 'StarryEyedDuo_Loop_animation', 120, 240),
            ('lesson_complete_redesign_v72', '20_duo_normal_lovey_dovey_artboard', 'LoveyDoveyDuo_Loop_animation', 120, 240),
            ('lesson_complete_redesign_v72', '26_duo_perfect_chefs_kiss_artboard', 'ChefsKissDuo_Loop_animation', 120, 240),
            ('lesson_complete_redesign_v72', '25_duo_normal_foam_finger_artboard', 'FoamFingerDuo_Loop_animation', 120, 240),
            ('lesson_complete_redesign_v72', '17_duo_perfect_jaw_drop_artboard', 'JawdropDuo_Loop_animation', 120, 240)]:
        source = original.read(f'res/raw/{name}.riv')
        _, before, _ = parse(source)
        board = None
        original_count = 0
        for kind, values, _ in before:
            if kind == 1:
                board = values.get(4)
            elif board == target and (kind in COMPONENT or 'Interpolator' in SCHEMA['types'].get(str(kind), '')):
                original_count += 1
        output, changed = rive(source, name, png, width, height)
        assert target in changed
        _, objects, _ = parse(output)
        board = animation = None
        layer = None
        object_id = None
        tracks = {}
        poses = []
        foam_switches = 0
        for kind, values, _ in objects:
            if kind == 1:
                board, animation = values.get(4), None
                layer = None
            elif board == target and kind == 57:
                layer = values.get(138)
            elif (board == target and layer == 'idleLoop' and kind == 65
                  and (name, target) in (('duo_normal_foam_finger_02','lc_character_artboard'),
                                         ('lesson_complete_redesign_v72','25_duo_normal_foam_finger_artboard'))
                  and 158 in values):
                assert values[158] == 0
                foam_switches += 1
            elif board == target and kind == 31:
                animation = values.get(55)
            elif board == target and kind == 100 and values.get(4, '').startswith('DuoAero Snoopy frame '):
                poses.append(values)
            elif board == target and animation == idle:
                if kind == 25:
                    object_id = values.get(51)
                elif kind == 30 and original_count + 1 <= (object_id or 0) <= original_count + 16:
                    tracks.setdefault(object_id, []).append((values[67], values[70]))
        assert len(poses) == len(tracks) == 16
        if (name, target) in (('duo_normal_foam_finger_02','lc_character_artboard'),
                              ('lesson_complete_redesign_v72','25_duo_normal_foam_finger_artboard')):
            assert foam_switches == 1
        assert len({pose[206] for pose in poses}) == 16
        # Exactly one pose is visible throughout the looping native segment.
        for time in range(start, end + 1):
            assert sum(next(value for frame, value in reversed(track) if frame <= time)
                       for track in tracks.values()) == 1
        assert [next(v for t, v in reversed(track) if t <= start) for track in tracks.values()] == [
            next(v for t, v in reversed(track) if t <= end) for track in tracks.values()]
    for mood in ('surprised', 'determined', 'overjoyed', 'hero'):
        for path in (ROOT/'app/assets/mascot'/mood).glob('*.png'):
            with Image.open(path) as image:
                alpha=image.convert('RGBA').getchannel('A')
                assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] >= 250
                assert max(alpha.getpixel(p) for p in [(0, 0), (0, image.height-1),
                           (image.width-1, 0), (image.width-1, image.height-1)]) <= 8
    for name, character in CHARACTER_CAST.items():
        source = original.read(f'res/raw/{name}.riv')
        _, before, _ = parse(source)
        board = None
        original_count = 0
        for kind, values, _ in before:
            if kind == 1: board = values.get(4)
            elif board == 'character' and (kind in COMPONENT or 'Interpolator' in SCHEMA['types'].get(str(kind), '')):
                original_count += 1
        result, changed = rive(source, name, png, width, height)
        assert changed == ['character']
        _, objects, _ = parse(result)
        board = timeline = object_id = None
        tracks = {}
        poses = []
        for kind, values, _ in objects:
            if kind == 1: board, timeline = values.get(4), None
            elif board == 'character' and kind == 31: timeline = values.get(55, '').strip().lower()
            elif board == 'character' and kind == 100 and values.get(4, '').startswith(f'DuoAero {character} frame '):
                poses.append(values)
            elif board == 'character' and timeline in ('idle_00', 'correct_00', 'incorrect_00'):
                if kind == 25: object_id = values.get(51)
                elif kind == 30 and original_count + 1 <= (object_id or 0) <= original_count + 48:
                    tracks.setdefault(timeline, {}).setdefault(object_id, []).append((values[67], values[70]))
        assert len(poses) == 48 and len({p[206] for p in poses}) == 48
        for timeline, emotion in [('idle_00', 0), ('correct_00', 1), ('incorrect_00', 2)]:
            group = tracks[timeline]
            assert len(group) == 48
            for time in range(60):
                active = [object_id for object_id, track in group.items()
                          if next(value for frame, value in reversed(track) if frame <= time)]
                assert len(active) == 1 and (active[0] - original_count - 1)//16 == emotion
        for mood in ('idle', 'happy', 'sad'):
            for image_path in (ROOT/'app/assets/mascot/characters'/character/mood).glob('*.png'):
                with Image.open(image_path) as image:
                    assert image.mode == 'RGBA'
                    alpha = image.getchannel('A')
                    assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] >= 250
                    assert max(alpha.getpixel(p) for p in [(0, 0), (0, image.height-1),
                               (image.width-1, 0), (image.width-1, image.height-1)]) <= 8
    source = original.read('res/raw/duo_flying_up.json')
    result, changed = lottie(source, 'duo_flying_up', png, width, height)
    assert changed
    before, after = json.loads(source), json.loads(result)
    assert before['layers'] == after['layers']
    original_assets = {asset['id']: asset for asset in before['assets']}
    assets = {asset['id']: asset for asset in after['assets']}
    for asset_id in ('comp_0', 'comp_2', 'comp_3', 'comp_4', 'comp_6', 'comp_7'):
        assert assets[asset_id] == original_assets[asset_id]
    for asset_id in ('comp_1', 'comp_5'):
        layers = assets[asset_id]['layers']
        assert len(layers) == 16 and len({layer['refId'] for layer in layers}) == 16
        for t in range(20):
            assert sum(next(key['s'][0] for key in reversed(layer['ks']['o']['k']) if key['t'] <= t)
                       for layer in layers) == 100
    for image_path in (ROOT/'app/assets/mascot/plane').glob('*.png'):
        with Image.open(image_path) as image:
            alpha = image.convert('RGBA').getchannel('A')
            assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] >= 250
            assert max(alpha.getpixel(p) for p in [(0, 0), (0, image.height-1),
                       (image.width-1, 0), (image.width-1, image.height-1)]) <= 8
print('PASS: transparent poses and one-frame-at-a-time native Rive loop')
