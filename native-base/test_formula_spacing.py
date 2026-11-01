"""Verify the original gas-formula prompt is adjacent to its selected slot."""
import json, os
from pathlib import Path
from PIL import Image
p=Path(os.environ['DUOAERO_EVIDENCE'])
nodes=json.loads((p/'aerospace-formula-selected-2.json').read_text())
slot=next(n for n in nodes if n.get('description')=='T' and n.get('clickable'))
x1,y1,x2,y2=map(int,slot['bounds'].split())
im=Image.open(p/'aerospace-formula-selected-2.png').convert('RGB')
# Native MathLatexView has no accessibility bounds, so identify visible ink
# in the slot's row. The slot itself and all labels above/below are excluded.
ink=[]
for y in range(max(0,y1-25),min(im.height,y2+25)):
 for x in range(10,max(10,x1-3)):
  r,g,b=im.getpixel((x,y))
  if max(r,g,b)<170 or (b>130 and b>r*1.35 and g>r*1.15):ink.append(x)
assert ink,'No visible formula found next to the slot'
gap=x1-max(ink)
assert gap<=im.width*.09, f'Excessive formula-to-slot gap: {gap}px of {im.width}px'
print('PASS: native gas-formula slot is adjacent to the visible equation; gap',gap,'pixels.')
