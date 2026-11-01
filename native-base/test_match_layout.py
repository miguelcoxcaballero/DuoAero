"""Check long labels are actually drawn, not merely present in accessibility."""
import os,re,subprocess
from pathlib import Path
image=Path(os.environ['DUOAERO_EVIDENCE'])/'mixed-prompt-3.png'
result=subprocess.run(['tesseract',str(image),'stdout','--psm','6'],capture_output=True,text=True,check=True,timeout=30)
text=' '.join(result.stdout.casefold().split())
assert re.search(r'\bmass\s+density\b',text), 'Mass density is not fully visible in the native matching card'
assert re.search(r'\bdynamic\s+pressure\b',text), 'Dynamic pressure is not fully visible in the native matching card'
print('PASS: both long matching labels are visible in the original cards.')
