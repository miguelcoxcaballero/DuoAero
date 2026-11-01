"""Replace mascot artwork while keeping native animation timelines and controls.

Rive wire field metadata is recorded in rive-schema.json; its upstream runtime
is MIT licensed (vendor/rive/LICENSE). Images are the approved, unchanged PNGs.
"""
import base64,json,re,struct
from pathlib import Path
from branding import display_text
SCHEMA=json.loads(Path(__file__).with_name('rive-schema.json').read_text())
PROPS={int(k):v for k,v in SCHEMA['properties'].items()}
DRAWABLE=set(SCHEMA['drawable_types']); COMPONENT=set(SCHEMA['component_types'])
ASSET=set(SCHEMA['asset_types'])

def vu(n):
    out=bytearray()
    while n>=128:out.append((n&127)|128);n>>=7
    out.append(n);return bytes(out)
class Reader:
    def __init__(self,data):self.data=data;self.pos=4
    def take(self,n):
        value=self.data[self.pos:self.pos+n];self.pos+=n
        if len(value)!=n:raise ValueError('Truncated Rive resource')
        return value
    def u(self):
        value=0;shift=0
        while True:
            b=self.take(1)[0];value|=(b&127)<<shift
            if not b&128:return value
            shift+=7
            if shift>70:raise ValueError('Invalid Rive integer')
    def value(self,ty):
        if ty in ('Uint','Uint64','Id'):return self.u()
        if ty=='Bool':return self.take(1)[0]
        if ty=='Double':return struct.unpack('<f',self.take(4))[0]
        if ty=='Color':return struct.unpack('<I',self.take(4))[0]
        if ty in ('String','Bytes'):
            b=self.take(self.u());return b.decode('utf8') if ty=='String' else b
        raise ValueError(ty)
def parse(data):
    if data[:4]!=b'RIVE':raise ValueError('Not Rive')
    r=Reader(data);version=(r.u(),r.u(),r.u());keys=[];props=dict(PROPS)
    if version[0]!=7:raise ValueError('Unexpected Rive major version')
    while (key:=r.u()):keys.append(key)
    for i in range(0,len(keys),4):
        bits=struct.unpack('<I',r.take(4))[0]
        for j,key in enumerate(keys[i:i+4]):props.setdefault(key,(['Uint','String','Double','Color'][(bits>>(j*2))&3],str(key)))
    header=data[:r.pos];objects=[]
    while r.pos<len(data):
        start=r.pos;kind=r.u();values={}
        while (key:=r.u()):values[key]=r.value(props[key][0])
        objects.append((kind,values,data[start:r.pos]))
    return header,objects,props

def encode(kind,values,props=PROPS):
    out=bytearray(vu(kind))
    for key,value in values.items():
        ty=props[key][0];out+=vu(key)
        if ty in ('Uint','Uint64','Id'):out+=vu(value)
        elif ty=='Bool':out.append(value)
        elif ty=='Double':out+=struct.pack('<f',value)
        elif ty=='Color':out+=struct.pack('<I',value)
        else:
            b=value.encode('utf8') if ty=='String' else value
            out+=vu(len(b))+b
    return bytes(out)+b'\0'

def rive(data,name,png,width,height):
    header,objects,props=parse(data)
    asset_index=sum(t in ASSET for t,p,b in objects)
    asset_unique=max([p.get(204,0) for t,p,b in objects if t in ASSET]+[0])+1
    pure=bool(re.search(r'(^|_)duo(?:_|$)|resurrectedduo',name)) and 'waveform' not in name
    first=True;replace=False;art=None;output=bytearray(header);changed=[];component_id=0;motion_parent=0
    def finish():
        if not replace:return
        w,h=art.get(7,600.),art.get(8,600.)
        scale=min(w/width,h/height)*.90
        output.extend(encode(100,{4:'DuoAero Snoopy',5:motion_parent,206:asset_index,13:w*(.5-art.get(11,0.)),14:h*(.5-art.get(12,0.)),16:scale,17:scale}))
    for kind,values,raw in objects:
        if kind==1:
            finish();art=values;component_id=0;motion_parent=0;label=values.get(4,'');w,h=values.get(7,0),values.get(8,0)
            replace=(pure and first) or (name=='lesson_complete_main_29' and label=='lc_character_artboard') or ('duo' in label.lower() and min(w,h)>=100 and not re.search('sparkle|pupil|shine|waveform',label,re.I))
            first=False
            if replace:changed.append(label)
        elif art is not None and kind in COMPONENT:
            component_id+=1
            # Follow the original character's centered root motion (intro,
            # bounce, fade); do not replace state machines or their events.
            if replace and not motion_parent and kind==2 and values.get(5)==0 and abs(values.get(13,0))<1 and abs(values.get(14,0))<1:
                motion_parent=component_id
        update=dict(values)
        if replace and kind in DRAWABLE:update[129]=values.get(129,0)|1
        # Text runs change; state-machine, input and artboard names stay intact.
        if SCHEMA['types'].get(str(kind))=='TextValueRun':
            for k,v in values.items():
                if isinstance(v,str) and PROPS[k][1]=='textPropertyKey':update[k]=display_text(v)
        output.extend(raw if update==values else encode(kind,update,props))
    finish()
    if changed:
        output.extend(encode(105,{203:'DuoAero Snoopy',204:asset_unique,207:float(height),208:float(width)}))
        output.extend(encode(106,{212:png}))
    return bytes(output),changed

def lottie(data,name,png,width,height):
    doc=json.loads(data)
    if not isinstance(doc,dict) or 'layers' not in doc:return data,False
    pure=bool(re.search(r'(^|_)duo(?:_|$)|resurrectedduo',name)) and not any(x in name for x in ['audio','sound','waveform'])
    if not pure:return data,False
    w,h=doc['w'],doc['h'];scale=min(w/width,h/height)*90
    # Keep duration, framerate, markers and native completion callbacks. The
    # approved artwork gets a small breathing motion, not a stretched bitmap.
    ip,op=doc.get('ip',0),doc['op'];mid=(ip+op)/2
    doc['assets']=[{'id':'duoaero_snoopy','w':width,'h':height,'u':'','p':'data:image/png;base64,'+base64.b64encode(png).decode(),'e':1}]
    doc['layers']=[{'ty':2,'ind':1,'nm':'DuoAero Snoopy','refId':'duoaero_snoopy','ip':ip,'op':op,'st':ip,
      'ks':{'o':{'a':0,'k':100},'r':{'a':0,'k':0},'a':{'a':0,'k':[width/2,height/2,0]},'s':{'a':0,'k':[scale,scale,100]},
       'p':{'a':1,'k':[{'t':ip,'s':[w/2,h/2,0],'e':[w/2,h/2-h*.015,0],'i':{'x':.5,'y':1},'o':{'x':.5,'y':0}}, {'t':mid,'s':[w/2,h/2-h*.015,0],'e':[w/2,h/2,0],'i':{'x':.5,'y':1},'o':{'x':.5,'y':0}}, {'t':op,'s':[w/2,h/2,0]}]}}}]
    return json.dumps(doc,separators=(',',':')).encode(),True
