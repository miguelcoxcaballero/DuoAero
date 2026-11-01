"""Check long labels are drawn completely, not only exposed to accessibility."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image
root=Path(os.environ['DUOAERO_EVIDENCE']);stem=root/'mixed-prompt-3'
nodes=json.loads(stem.with_suffix('.json').read_text())
with Image.open(stem.with_suffix('.png')) as image:
 for label in ('Mass density','Dynamic pressure'):
  node=next(n for n in nodes if n.get('description')==label and n.get('clickable'))
  bounds=tuple(map(int,node['bounds'].split()))
  crop=image.crop(bounds).convert('RGB')
  crop=crop.resize((crop.width*2,crop.height*2))
  evidence=root/('matching-'+label.lower().replace(' ','-')+'.png')
  crop.save(evidence)
  result=subprocess.run(['tesseract',str(evidence),'stdout','--psm','6'],capture_output=True,text=True,check=True,timeout=30)
  rendered=' '.join(result.stdout.casefold().split())
  assert label.casefold() in rendered, f'{label} not fully visible in matching card: {rendered!r}'
print('PASS: both long matching labels are visible in the original cards.')
