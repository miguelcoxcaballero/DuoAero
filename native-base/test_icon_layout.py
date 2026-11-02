"""Check the opaque launcher artwork fits Android's circular safe zone."""
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
with Image.open(root / 'app/assets/mascot/launcher.png') as image:
    assert image.mode == 'RGBA' and image.width == image.height
    width, height = image.size
    alpha = image.getchannel('A')
    assert alpha.getextrema() == (0, 255), 'The icon foreground must have transparency'
    radius2 = max(((x + .5) / width - .5) ** 2 + ((y + .5) / height - .5) ** 2
                  for y in range(height) for x in range(width) if alpha.getpixel((x, y)) > 128)
    assert radius2 ** .5 * .61 < 1/3, 'Launcher foreground exceeds the adaptive icon safe circle'
    assert radius2 ** .5 * .35 < 1/3, 'Splash foreground exceeds its circular mask'
source = (root / 'native-base/build.py').read_text()
assert 'android:inset="19.5%"' in source
print('PASS: close-up launcher and padded splash foreground fit the safe circle; device appearance remains separate.')
