"""Check the visible word and answer block in an actual graded native gap."""
import csv
import io
import os
from pathlib import Path
import subprocess
from PIL import Image

folder = Path(os.environ['DUOAERO_EVIDENCE'])
original = folder / 'mixed-graded-0.png'
with Image.open(original) as image:
    height = image.height
result = subprocess.run(['tesseract', str(original), 'stdout', '--psm', '6', 'tsv'],
                        text=True, capture_output=True, check=True, timeout=30)
rows = list(csv.DictReader(io.StringIO(result.stdout), delimiter='\t'))
def find(word):
    hits = [r for r in rows if r.get('text', '').strip().lower().strip('.,') == word
            and int(r.get('top') or 0) < height * .52]
    assert len(hits) == 1, (word, [(r.get('text'), r.get('conf')) for r in rows])
    r = hits[0]
    return int(r['top']) + int(r['height']) / 2, int(r['height'])
block_y, block_h = find('decreases')
neighbors = [find('generally'), find('as')]
distance = min(abs(block_y-y) for y, _ in neighbors)
tolerance = max(8, max(block_h, *(h for _, h in neighbors)) * .30)
assert distance <= tolerance, f'Gap text is vertically misaligned: {distance:.1f}px > {tolerance:.1f}px'
print(f'PASS: native gap answer and adjacent words align within {distance:.1f}px')
