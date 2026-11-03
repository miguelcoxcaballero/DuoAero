"""Verify final-feedback OCR on preserved original Android screenshots."""
import tempfile
from pathlib import Path
from visual_controls import native_positive_banner

source = Path(__file__).parent / 'evidence/2026-11-01'
with tempfile.TemporaryDirectory() as directory:
    crop = Path(directory) / 'banner.png'
    assert native_positive_banner(source / 'typed-math-correct.png', crop)
    assert native_positive_banner(source.parent / '2026-11-03/final-good-job.png', crop)
    assert native_positive_banner(source.parent / '2026-11-03/s24-final-correct.png', crop)
    assert not native_positive_banner(source / 'typed-math-wrong.png', crop)
print('PASS: original correct feedback is recognized and wrong feedback rejected.')
