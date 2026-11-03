"""Prototype a waving replacement inside the original mid-lesson Lottie.

This is not yet wired into the APK. The original frame range, frame rate and
markers remain intact; an atlas is referenced, never sliced or modified.
Android playback and the native scene's completion callback must be verified.
"""
import base64
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

def replace_wave(data):
    doc=json.loads(data)
    if (doc.get('w'),doc.get('h')) != (587,524) or not any(x.get('refId')=='comp_0' for x in doc.get('layers',[])):
        raise ValueError('Unexpected original waving composition')
    atlas=ROOT/'app/assets/mascot/wave-atlas.png'
    with Image.open(atlas) as image:
        if image.mode!='RGBA':raise ValueError('Waving atlas must be transparent RGBA')
        width,height=image.size
    image_id='duoaero-wave-atlas'
    if any(str(asset.get('id','')).startswith('duoaero-wave-') for asset in doc.get('assets',[])):
        raise ValueError('Waving replacement already present')
    doc.setdefault('assets',[]).append({'id':image_id,'w':width,'h':height,'u':'',
      'p':'data:image/png;base64,'+base64.b64encode(atlas.read_bytes()).decode('ascii'),'e':1})
    start,end=doc.get('ip',0),doc['op']
    if int(start)!=start or int(end)!=end or end<=start:raise ValueError('Unexpected Lottie frame range')
    start,end=int(start),int(end)
    # Original uses 60 fps. Each pose lasts six original frames (10 drawings/s),
    # preserving the existing full animation duration and completion event.
    frame_length=max(1,round(doc['fr']/10))
    layers=[]
    for i in range(16):
        row,col=divmod(i,4)
        x0,x1=width*col//4,width*(col+1)//4
        y0,y1=height*row//4,height*(row+1)//4
        w,h=x1-x0,y1-y0
        cell='duoaero-wave-cell-'+str(i)
        # A clipped composition selects a cell from the untouched atlas.
        doc['assets'].append({'id':cell,'w':w,'h':h,'layers':[{
          'ty':2,'ind':1,'nm':'wave atlas','refId':image_id,'ip':start,'op':end,'st':0,
          'ks':{'o':{'a':0,'k':100},'r':{'a':0,'k':0},'a':{'a':0,'k':[0,0,0]},
                's':{'a':0,'k':[100,100,100]},'p':{'a':0,'k':[-x0,-y0,0]}}}]})
        keys=[]
        for t in range(start,end):
            current=((t-start)//frame_length)%16
            previous=((t-start-1)//frame_length)%16
            if t==start or current!=previous:
                keys.append({'t':t,'s':[100 if current==i else 0],'h':1})
        scale=min(doc['w']/w,doc['h']/h)*90
        layers.append({'ty':0,'ind':i+1,'nm':'DuoAero waving pose '+str(i),'refId':cell,
          'w':w,'h':h,'ip':start,'op':end,'st':0,
          'ks':{'o':{'a':1,'k':keys},'r':{'a':0,'k':0},'a':{'a':0,'k':[w/2,h/2,0]},
                's':{'a':0,'k':[scale,scale,100]},'p':{'a':0,'k':[doc['w']/2,doc['h']/2,0]}}})
    doc['layers']=layers
    return json.dumps(doc,separators=(',',':')).encode()
