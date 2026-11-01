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

CHARACTER_CAST={
    'zari_inlesson_v01_04':'sally',
    'falstaff_inlesson_v01_08':'charlie',
    'junior_inlesson_v01_13':'linus',
}

def expressive_character(data,name):
    """Use frame-by-frame Peanuts poses in the original character state rig.

    Correct and idle timelines use happy drawings; incorrect timelines use
    disappointed drawings. The original artboard and state machine still own
    transitions, events and placement. No frame contains a scene background.
    """
    from io import BytesIO
    from PIL import Image
    header,objects,props=parse(data)
    target='character';cast=CHARACTER_CAST[name]
    folder=Path(__file__).resolve().parents[1]/'app/assets/mascot/characters'/cast
    frames=[(folder/mood/f'frame-{i:02}.png').read_bytes()
            for mood in ('happy','sad') for i in range(16)]
    asset_index=sum(t in ASSET for t,p,b in objects)
    asset_unique=max([p.get(204,0) for t,p,b in objects if t in ASSET]+[0])+1
    board=None;component_count=0
    for kind,values,_ in objects:
        if kind==1:board=values.get(4)
        elif board==target and (kind in COMPONENT or 'Interpolator' in SCHEMA['types'].get(str(kind),'')):
            component_count+=1
    if not component_count:raise ValueError('Missing original character artboard: '+name)
    keyed={25,26}|{int(k) for k,v in SCHEMA['types'].items() if 'KeyFrame' in v}
    output=bytearray(header);board=None;art=None;replace=False;animation=None;changed=[];track_count=0
    def finish_animation():
        nonlocal track_count
        if not animation or not replace:return
        timeline=animation.get(55,'').strip()
        if not timeline.startswith(('Idle_00','Correct_','Incorrect_')):return
        mood=1 if timeline.startswith('Incorrect_') else 0
        duration=max(1,animation.get(57,60));cycle=90
        # Fit whole cycles in looping idle timelines to avoid a visible jump.
        if timeline=='Idle_00' and duration>=180:
            cycle=max(16,round(duration/max(1,round(duration/90))))
        track_count+=1
        for i in range(32):
            output.extend(encode(25,{51:component_count+1+i}))
            output.extend(encode(26,{53:18}))
            for t in range(duration):
                current=(t*16//cycle)%16;previous=((t-1)*16//cycle)%16
                if t==0 or (current!=previous and i//16==mood):
                    output.extend(encode(30,{67:t,70:1. if i==mood*16+current else 0.}))
    def finish_board():
        if not replace:return
        w,h=art.get(7,500.),art.get(8,750.)
        for i,frame in enumerate(frames):
            fw,fh=struct.unpack_from('>II',frame,16);scale=min(w/fw,h/fh)*.9
            with Image.open(BytesIO(frame)) as im:
                box=im.getchannel('A').point(lambda a:255 if a>64 else 0).getbbox()
            if box is None:raise ValueError('Empty character animation frame')
            x=(fw/2-(box[0]+box[2])/2)*scale
            y=(fh*.82-box[3])*scale
            output.extend(encode(100,{4:f'DuoAero {cast} frame {i}',5:0,206:asset_index+i,
                13:x+w*(.5-art.get(11,0.)),14:y+h*(.5-art.get(12,0.)),
                16:scale,17:scale,18:1. if i==0 else 0.}))
    for kind,values,raw in objects:
        if animation is not None and kind not in keyed:
            finish_animation();animation=None
        if kind==1:
            finish_board();art=values;board=values.get(4);replace=board==target
            if replace:changed.append(board)
        if replace and kind==31:animation=values
        update=dict(values)
        if replace and kind in DRAWABLE:update[129]=values.get(129,0)|1
        if SCHEMA['types'].get(str(kind))=='TextValueRun':
            for key,value in values.items():
                if isinstance(value,str) and PROPS[key][1]=='textPropertyKey':update[key]=display_text(value)
        output.extend(raw if update==values else encode(kind,update,props))
    finish_animation();finish_board()
    if changed!=[target] or track_count<3:raise ValueError('Original character timelines unavailable: '+name)
    for i,frame in enumerate(frames):
        fw,fh=struct.unpack_from('>II',frame,16)
        output.extend(encode(105,{203:f'DuoAero {cast} frame {i}',204:asset_unique+i,207:float(fh),208:float(fw)}))
        output.extend(encode(106,{212:frame}))
    return bytes(output),changed

def rive(data,name,png,width,height):
    if name in CHARACTER_CAST:return expressive_character(data,name)
    header,objects,props=parse(data)
    artboard_names=[p.get(4,'') for t,p,b in objects if t==1]
    asset_index=sum(t in ASSET for t,p,b in objects)
    asset_unique=max([p.get(204,0) for t,p,b in objects if t in ASSET]+[0])+1
    pure=bool(re.search(r'(^|_)duo(?:_|$)|resurrectedduo',name)) and 'waveform' not in name
    animated_board={'duo_perfect_epic_03':'lc_character_artboard',
                    'lesson_complete_redesign_v72':'01_duo_epic_arboard'}.get(name)
    frames=[]
    anchors=[]
    if animated_board:
        from io import BytesIO
        from PIL import Image
        frame_dir=Path(__file__).resolve().parents[1]/'app/assets/mascot/celebrate'
        frames=[(frame_dir/f'frame-{i:02}.png').read_bytes() for i in range(16)]
        for frame in frames:
            with Image.open(BytesIO(frame)) as im:
                # Ignore almost transparent antialiasing when measuring the
                # pose. Keep the original pixels and register every frame to
                # a common centre and baseline inside the native artboard.
                box=im.getchannel('A').point(lambda a:255 if a>64 else 0).getbbox()
                if box is None:raise ValueError('Empty animation frame')
                anchors.append(((box[0]+box[2])/2,box[3]))
    # Rive's keyed-object IDs count interpolators as well as components.
    # Count the original IDs before appending our images to each artboard.
    counts={};count_board=None
    for kind,values,_ in objects:
        if kind==1:count_board=values.get(4,'');counts[count_board]=0
        elif count_board is not None and (kind in COMPONENT or 'Interpolator' in SCHEMA['types'].get(str(kind),'')):
            counts[count_board]+=1
    static_index=asset_index+len(frames)
    keyed={25,26}|{int(k) for k,v in SCHEMA['types'].items() if 'KeyFrame' in v}
    animation=None
    first=True;replace=False;art=None;output=bytearray(header);changed=[];component_id=0;motion_parent=0
    def finish():
        if not replace:return
        w,h=art.get(7,600.),art.get(8,600.)
        if art.get(4)==animated_board:
            for i,frame in enumerate(frames):
                fw,fh=struct.unpack_from('>II',frame,16);scale=min(w/fw,h/fh)*.90
                x=(anchors[0][0]-anchors[i][0])*scale
                y=(anchors[0][1]-anchors[i][1])*scale
                output.extend(encode(100,{4:f'DuoAero Snoopy frame {i}',5:motion_parent,206:asset_index+i,
                    13:w*(.5-art.get(11,0.))+x,14:h*(.5-art.get(12,0.))+y,16:scale,17:scale,18:1. if i==0 else 0.}))
            return
        scale=min(w/width,h/height)*.90
        output.extend(encode(100,{4:'DuoAero Snoopy',5:motion_parent,206:static_index,13:w*(.5-art.get(11,0.)),14:h*(.5-art.get(12,0.)),16:scale,17:scale}))
    def finish_animation():
        if not animation or not art or art.get(4)!=animated_board:return
        if animation.get(55) not in ('EpicDuo_Intro_Animation','EpicDuo_IdleLoop'):return
        duration=animation.get(57,60)
        for i in range(len(frames)):
            output.extend(encode(25,{51:counts[animated_board]+1+i}))
            output.extend(encode(26,{53:18}))
            # The original idle timeline loops between frames 70 and 190:
            # a 60-frame cycle repeats exactly at both ends of that range.
            for t in range(0,max(1,duration)):
                current=((t-70)*len(frames)//60)%len(frames)
                previous=((t-71)*len(frames)//60)%len(frames)
                if t==0 or current!=previous:
                    output.extend(encode(30,{67:t,70:1. if current==i else 0.}))
    for kind,values,raw in objects:
        if animation is not None and kind not in keyed:
            finish_animation();animation=None
        if kind==1:
            finish();art=values;component_id=0;motion_parent=0;label=values.get(4,'');w,h=values.get(7,0),values.get(8,0)
            # Some large character artboards nest another artboard containing
            # only eyes. Replacing both draws two full Snoopy images on top
            # of one another (and can put Snoopy inside Duo's eyes).
            auxiliary=re.search(r'sparkle|pupil|shine|waveform|(?:^|_)eyes(?:_|$)',label,re.I)
            replace=(pure and first) or (name=='lesson_complete_main_29' and label=='lc_character_artboard') or ('duo' in label.lower() and min(w,h)>=100 and not auxiliary)
            first=False
            if replace:changed.append(label)
        elif art is not None and kind in COMPONENT:
            component_id+=1
            # Follow the original character's centered root motion (intro,
            # bounce, fade); do not replace state machines or their events.
            if replace and not motion_parent and kind==2 and values.get(5)==0 and abs(values.get(13,0))<1 and abs(values.get(14,0))<1:
                motion_parent=component_id
        if replace and kind==31:animation=values
        update=dict(values)
        if replace and kind in DRAWABLE:update[129]=values.get(129,0)|1
        # The completion scene instantiates each character twice: the first
        # group (parent 371) is the moving character and the second (parent
        # 632) plays its sparkle-only state. Our full-image replacements also
        # draw in that sparkle-only instance, creating a stationary duplicate.
        # Hide only those secondary Duo instances; retain the moving group and
        # every non-Duo character and surrounding scene element.
        if (name=='lesson_complete_redesign_v72' and art is not None
            and art.get(4)=='_interstitial_main_artboard' and kind==92
            and values.get(5)==632):
            target=values.get(197,-1)
            if 0<=target<len(artboard_names) and re.search(r'(^|_)duo(?:_|$)',artboard_names[target],re.I):
                update[129]=values.get(129,0)|1
        # Text runs change; state-machine, input and artboard names stay intact.
        if SCHEMA['types'].get(str(kind))=='TextValueRun':
            for k,v in values.items():
                if isinstance(v,str) and PROPS[k][1]=='textPropertyKey':update[k]=display_text(v)
        output.extend(raw if update==values else encode(kind,update,props))
    finish_animation();finish()
    if changed:
        for i,frame in enumerate(frames):
            fw,fh=struct.unpack_from('>II',frame,16)
            output.extend(encode(105,{203:f'DuoAero frame {i}',204:asset_unique+i,207:float(fh),208:float(fw)}))
            output.extend(encode(106,{212:frame}))
        output.extend(encode(105,{203:'DuoAero Snoopy',204:asset_unique+len(frames),207:float(height),208:float(width)}))
        output.extend(encode(106,{212:png}))
    return bytes(output),changed

def lottie(data,name,png,width,height):
    doc=json.loads(data)
    if not isinstance(doc,dict) or 'layers' not in doc:return data,False
    if name=='duo_flying_up':
        # Keep the original heart, sparkles, trail, transforms, timing and
        # callbacks. Replace only the two character precompositions with a
        # transparent frame-by-frame plane and a turning propeller.
        folder=Path(__file__).resolve().parents[1]/'app/assets/mascot/plane'
        frames=[(folder/f'frame-{i:02}.png').read_bytes() for i in range(16)]
        for i,frame in enumerate(frames):
            fw,fh=struct.unpack_from('>II',frame,16)
            doc['assets'].append({'id':f'duoaero-plane-{i}','w':fw,'h':fh,'u':'',
                'p':'data:image/png;base64,'+base64.b64encode(frame).decode(),'e':1})
        replaced=[]
        for asset in doc['assets']:
            if asset.get('id') not in ('comp_1','comp_5'):continue
            end=20 if asset['id']=='comp_1' else 253
            layers=[]
            for i,frame in enumerate(frames):
                fw,fh=struct.unpack_from('>II',frame,16);keys=[]
                for t in range(end):
                    current=(t*2//3)%16;previous=((t-1)*2//3)%16
                    if t==0 or current!=previous:keys.append({'t':t,'s':[100 if current==i else 0],'h':1})
                layers.append({'ty':2,'ind':i+1,'nm':f'DuoAero flying frame {i}',
                    'refId':f'duoaero-plane-{i}','ip':0,'op':end,'st':0,
                    'ks':{'o':{'a':1,'k':keys},'r':{'a':0,'k':0},
                          'a':{'a':0,'k':[fw/2,fh/2,0]},'s':{'a':0,'k':[260,260,100]},
                          'p':{'a':0,'k':[1366,1648,0]}}})
            asset['layers']=layers;replaced.append(asset['id'])
        if set(replaced)!={'comp_1','comp_5'}:raise ValueError('Original flying scene changed')
        return json.dumps(doc,separators=(',',':')).encode(),True
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
