"""Check changing pixels in the mascot area of the actual quit-sheet video."""
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageChops

video = Path(os.environ['DUOAERO_EVIDENCE']) / 'sad-quit.mp4'
if not video.is_file():
    raise SystemExit('Missing original quit sheet recording')
ffmpeg=shutil.which('ffmpeg')
if ffmpeg is None:
    import imageio_ffmpeg
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
with tempfile.TemporaryDirectory() as folder:
    pattern = str(Path(folder) / '%03d.png')
    subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-i', str(video),
                    '-vf', 'fps=6,scale=360:-1', pattern], check=True, timeout=30)
    frames = sorted(Path(folder).glob('*.png'))
    if len(frames) < 8:
        raise SystemExit('Quit recording is too short to assess animation')
    crops = []
    for path in frames:
        with Image.open(path) as source:
            image = source.convert('RGB')
            width, height = image.size
            crops.append(image.crop((int(width*.25), int(height*.36), int(width*.75), int(height*.62))))
    changed = sum(ImageChops.difference(crops[0], image).getbbox() is not None for image in crops[1:])
    distinct = len({hashlib.sha256(image.tobytes()).digest() for image in crops})
    if changed < 4 or distinct < 4:
        raise SystemExit(f'Quit mascot did not visibly animate: {changed} changed, {distinct} distinct frames')
    print(f'PASS: {distinct} distinct frames in the actual quit-sheet mascot area; smoothness still needs visual review.')
