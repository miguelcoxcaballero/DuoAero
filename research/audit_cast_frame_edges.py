"""Flag Peanuts animation frames touching their image boundary.

An edge intersection is a review candidate, not proof of a visible crop or
proof of animation quality. The scanner never modifies artwork.
"""
from collections import Counter
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]/'app/assets/mascot/characters'
counts=Counter(); examples=[]; total=0
for p in sorted(root.glob('*/*/frame-*.png')):
 total+=1
 with Image.open(p) as image:
  if image.mode!='RGBA':raise ValueError('Missing alpha: '+str(p))
  a=image.getchannel('A');w,h=a.size
  opaque=sum(a.getpixel((x,y))>128 for x in range(w) for y in (0,h-1))
  opaque+=sum(a.getpixel((x,y))>128 for y in range(1,h-1) for x in (0,w-1))
  if opaque:
   counts[p.parts[-3]]+=1;examples.append((opaque,p.relative_to(root).as_posix()))
assert total==480,total
print(f'{total} frames checked; {len(examples)} have alpha > 128 at an image boundary.')
for name,count in sorted(counts.items()): print(name,count)
for pixels,name in sorted(examples,reverse=True)[:8]:print('review',name,'edge pixels',pixels)
print('Boundary contact alone does not prove a crop; inspect frames and native playback.')
