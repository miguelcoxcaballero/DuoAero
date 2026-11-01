"""Check transparent source poses and the original Rive animation tracks."""
import io
import struct
import zipfile
from pathlib import Path

from PIL import Image

from mascot_assets import ASSET, COMPONENT, SCHEMA, parse, rive
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
    for name, target in [('duo_perfect_epic_03', 'lc_character_artboard'),
                         ('lesson_complete_redesign_v72', '01_duo_epic_arboard')]:
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
        object_id = None
        tracks = {}
        poses = []
        for kind, values, _ in objects:
            if kind == 1:
                board, animation = values.get(4), None
            elif board == target and kind == 31:
                animation = values.get(55)
            elif board == target and kind == 100 and values.get(4, '').startswith('DuoAero Snoopy frame '):
                poses.append(values)
            elif board == target and animation == 'EpicDuo_IdleLoop':
                if kind == 25:
                    object_id = values.get(51)
                elif kind == 30 and original_count + 1 <= (object_id or 0) <= original_count + 16:
                    tracks.setdefault(object_id, []).append((values[67], values[70]))
        assert len(poses) == len(tracks) == 16
        assert len({pose[206] for pose in poses}) == 16
        # Exactly one pose is visible throughout the looping native segment.
        for time in range(70, 191):
            assert sum(next(value for frame, value in reversed(track) if frame <= time)
                       for track in tracks.values()) == 1
        assert [next(v for t, v in reversed(track) if t <= 70) for track in tracks.values()] == [
            next(v for t, v in reversed(track) if t <= 190) for track in tracks.values()]
print('PASS: transparent poses and one-frame-at-a-time native Rive loop')
