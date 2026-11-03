"""Locate a real rendered Rive footer when Android exposes no text node."""
import csv
import io
import subprocess
from PIL import Image, ImageOps


def claim_xp(screenshot, evidence):
    with Image.open(screenshot) as source:
        width, height = source.size
        left, top = int(width * .1), int(height * .83)
        footer = source.crop((left, top, int(width * .9), int(height * .95))).convert('L')
        # Preserve the original screenshot. This crop only improves OCR of the
        # white lettering on the original blue button; no text is supplied.
        ImageOps.invert(footer).save(evidence)
    try:
        result = subprocess.run(['tesseract', str(evidence), 'stdout', '--psm', '6', 'tsv'],
                                capture_output=True, text=True, check=True, timeout=15)
    except subprocess.TimeoutExpired:
        # The caller owns the overall screen deadline and may retry a slow
        # emulator screenshot; a timed-out OCR pass is not a detected button.
        return None
    evidence.with_suffix('.tsv').write_text(result.stdout)
    words = [r for r in csv.DictReader(io.StringIO(result.stdout), delimiter='\t')
             if r.get('text', '').strip() and float(r['conf']) >= 80]
    if [r['text'].strip().upper() for r in words] != ['CLAIM', 'XP']:
        return None
    x1 = min(int(r['left']) for r in words)
    y1 = min(int(r['top']) for r in words)
    x2 = max(int(r['left']) + int(r['width']) for r in words)
    y2 = max(int(r['top']) + int(r['height']) for r in words)
    return left + (x1 + x2) // 2, top + (y1 + y2) // 2


def native_positive_banner(screenshot, evidence):
    """Recognize the original final-question positive banner when absent from a11y.

    Only a narrow footer crop is inspected; words must have high OCR confidence
    and match a known native success phrase. Continue alone cannot pass.
    """
    with Image.open(screenshot) as source:
        width, height = source.size
        rgb = source.convert('RGB')
        samples = [rgb.getpixel((int(width * x), int(height * y)))
                   for x in (.03, .5, .97) for y in (.80, .84)]
        if sum(g > r * 1.05 and g > b * 1.10 for r,g,b in samples) < 3:
            return False
        source.crop((0, int(height * .77), width, int(height * .86))).save(evidence)
    try:
        result = subprocess.run(['tesseract', str(evidence), 'stdout', '--psm', '6', 'tsv'],
                                capture_output=True, text=True, check=True, timeout=15)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return False
    evidence.with_suffix('.tsv').write_text(result.stdout)
    words = [r['text'].strip().upper().strip('!.,')
             for r in csv.DictReader(io.StringIO(result.stdout), delimiter='\t')
             if r.get('text', '').strip() and float(r['conf']) >= 80]
    positive = {('AMAZING',), ('AWESOME',), ('CORRECT',), ('EXCELLENT',),
                ('GREAT',), ('NICE',), ('WOW',), ('GOOD', 'JOB'),
                ('GREAT', 'JOB'), ('NICE', 'JOB'), ('NICELY', 'DONE')}
    return any(tuple(words[i:i+len(phrase)]) == phrase
               for phrase in positive for i in range(len(words)))
