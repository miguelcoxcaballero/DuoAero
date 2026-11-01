"""Add missing Greek glyphs, preserving every existing reference-font mapping.

The added outlines come from Noto Sans Math under the bundled OFL. No reference
font is committed here; it is read from the APK explicitly provided by the user.
"""
from pathlib import Path
import io
import json
import sys
import zipfile

sys.path.insert(0, str(Path.home()/'.codex/duoaero-build-deps/fonttools'))
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parent
DONOR = ROOT/'vendor/notosansmath/NotoSansMath-Regular.ttf'

def extend(original, donor_path=DONOR):
    target = TTFont(io.BytesIO(original))
    donor = TTFont(donor_path)
    before = dict(target.getBestCmap())
    source_map = donor.getBestCmap()
    source_glyphs = donor.getGlyphSet()
    scale = target['head'].unitsPerEm / donor['head'].unitsPerEm
    candidates = list(range(0x370, 0x400)) + list(range(0x1D6A8, 0x1D7CC)) + [0x22C6, 0x2605, 0x2606]
    additions = [cp for cp in candidates if cp not in before and cp in source_map]
    order = list(target.getGlyphOrder())
    for cp in additions:
        source_name = source_map[cp]
        name = f'aeroGreek{cp:04X}'
        outline = DecomposingRecordingPen(source_glyphs)
        source_glyphs[source_name].draw(outline)
        pen = TTGlyphPen(None)
        outline.replay(TransformPen(pen, (scale, 0, 0, scale, 0, 0)))
        target['glyf'][name] = pen.glyph()
        width, bearing = donor['hmtx'][source_name]
        target['hmtx'][name] = (round(width * scale), round(bearing * scale))
        order.append(name)
        for table in target['cmap'].tables:
            if table.isUnicode() and (table.format == 12 or (table.format == 4 and cp <= 0xFFFF)):
                table.cmap[cp] = name
    target.setGlyphOrder(order)
    result = io.BytesIO()
    target.save(result)
    verified = TTFont(io.BytesIO(result.getvalue()))
    after = verified.getBestCmap()
    assert all(after[cp] == glyph for cp, glyph in before.items())
    assert all(cp in after for cp in [0x3b1, 0x3b3, 0x3c1, 0x3c3, 0x3c0, 0x1d6fc, 0x1d6fe, 0x1d70c, 0x22c6, 0x2605, 0x2606])
    return result.getvalue(), additions

if __name__ == '__main__':
    from runtime_config import WORK, APK
    output = WORK/'font-overlays'
    output.mkdir(parents=True, exist_ok=True)
    receipt = {}
    with zipfile.ZipFile(APK) as apk:
        for name in apk.namelist():
            if name.startswith('res/font/duolingosansmath_') and name.endswith('.ttf'):
                data, additions = extend(apk.read(name))
                (output/Path(name).name).write_bytes(data)
                receipt[name] = {'added_codepoints': [f'U+{cp:04X}' for cp in additions], 'existing_mappings_preserved': True}
    (output/'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(f'Extended {len(receipt)} original math fonts; all existing Unicode mappings preserved.')
