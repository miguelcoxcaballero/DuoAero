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
    'lily_inlesson_v02_19':'lucy',
    'oscar_inlesson_v01_02':'schroeder',
    'bea_inlesson_v01_03':'patty',
    'lin_inlesson_v01_02':'marcie',
    'vikram_inlesson_v01_03':'franklin',
    'eddy_inlesson_v01_02':'pigpen',
    'lucy_inlesson_v01_02':'woodstock',
}

def expressive_character(data,name):
    """Use frame-by-frame Peanuts poses in the original character state rig.

    Waiting, correct and incorrect timelines use different drawings. The original artboard and state machine still own
    transitions, events and placement. No frame contains a scene background.
    """
    from io import BytesIO
    from PIL import Image
    header,objects,props=parse(data)
    target='character';cast=CHARACTER_CAST[name]
    folder=Path(__file__).resolve().parents[1]/'app/assets/mascot/characters'/cast
    frames=[(folder/mood/f'frame-{i:02}.png').read_bytes()
            for mood in ('idle','happy','sad') for i in range(16)]
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
        timeline=animation.get(55,'').strip().lower()
        if not timeline.startswith(('idle_00','correct_','incorrect_')):return
        mood=2 if timeline.startswith('incorrect_') else 1 if timeline.startswith('correct_') else 0
        duration=max(1,animation.get(57,60));cycle=90
        # Fit whole cycles in looping idle timelines to avoid a visible jump.
        if timeline=='idle_00' and duration>=180:
            cycle=max(16,round(duration/max(1,round(duration/90))))
        track_count+=1
        for i in range(len(frames)):
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

def linus_grid(data):
    """Replace Junior while preserving the original grid, frog and Rive timing.

    Three transparent renderings share the same placement. Eye-only clips and
    interpolated opacity tracks add a blink without swapping the whole body.
    Component references are shifted because the new drawables must precede
    the grid in Rive's original draw order. The source layout is asserted.
    """
    header,objects,props=parse(data)
    boards=[v.get(4) for k,v,_ in objects if k==1]
    if boards != ['math_junior_grid']:raise ValueError('Unexpected grid artboard')
    first=next(i for i,(kind,_,_) in enumerate(objects) if kind==31)
    parent={};indices={};group=None;insert=None;index=0
    for i,(kind,values,_) in enumerate(objects[:first]):
        if kind==1:index=0;continue
        if kind in COMPONENT or 'Interpolator' in SCHEMA['types'].get(str(kind),''):
            index+=1;indices[i]=index;parent[index]=values.get(5)
            if values.get(4)=='Junior Grid':group=index
            if values.get(4)=='Junior':insert=(i,index)
    if group!=235 or insert!=(254,253):raise ValueError('Unexpected original grid component layout')
    if any(kind in ASSET for kind,_,_ in objects):raise ValueError('Unexpected original grid image assets')
    allowed_ids={5,51,69,92,149,151,236}
    for kind,values,_ in objects:
        unexpected=[key for key in values if props.get(key,('',))[0]=='Id' and key not in allowed_ids]
        if unexpected:raise ValueError('Unexpected grid reference fields: '+repr(unexpected))
    folder=Path(__file__).resolve().parents[1]/'app/assets/mascot/path-linus'
    frames=[(folder/name).read_bytes() for name in ('open.png','closed.png','half.png')]
    sizes=[struct.unpack_from('>II',frame,16) for frame in frames]
    asset_index=0;asset_unique=1;added=7;junior=insert[1]+added;mask=insert[1]+5
    keyed={25,26}|{int(k) for k,v in SCHEMA['types'].items() if 'KeyFrame' in v}
    output=bytearray(header);changed=0;animation=False;tracks=False
    for i,(kind,original,raw) in enumerate(objects):
        if i==insert[0]:
            # Foreground eye states, base figure, then a non-painted mask.
            for frame_index in (1,2,0):
                width,height=sizes[frame_index]
                sx=.42*sizes[0][0]/width;sy=.42*sizes[0][1]/height
                image_id=insert[1]+(0 if frame_index==1 else 2 if frame_index==2 else 4)
                output.extend(encode(100,{4:'DuoAero Linus '+str(frame_index),5:junior,
                    206:asset_index+frame_index,13:16.276,14:-156.545,
                    16:sx,17:sy,18:0. if frame_index else 1.}))
                if frame_index:output.extend(encode(42,{5:image_id,92:mask}))
            output.extend(encode(3,{4:'Linus eye mask',5:junior,13:-73.,14:-165.}))
            output.extend(encode(7,{5:mask,20:100.,21:64.}))
        if animation and kind not in keyed:
            # Two short three-state blinks within the original 120 fps loop.
            blink=[(insert[1],[(0,0.),(239,0.),(245,1.),(251,1.),(257,0.),(599,0.),(605,1.),(611,1.),(617,0.)]),
                   (insert[1]+2,[(0,0.),(233,0.),(239,1.),(245,0.),(251,0.),(257,1.),(263,0.),(593,0.),(599,1.),(605,0.),(611,0.),(617,1.),(623,0.)])]
            for image_id,sequence in blink:
                output.extend(encode(25,{51:image_id}));output.extend(encode(26,{53:18}))
                for frame,value in sequence:output.extend(encode(30,{67:frame,68:1,70:value}))
            animation=False;tracks=True
        if kind==31:
            if original.get(55)!='Timeline 1' or original.get(56)!=120:raise ValueError('Unexpected grid timeline')
            animation=True
        values=dict(original)
        if i in indices and kind in DRAWABLE:
            current=indices[i];seen=set()
            while current is not None and current not in seen:
                seen.add(current)
                if current==group:
                    values[129]=values.get(129,0)|1;changed+=1;break
                current=parent.get(current)
        for key in (5,92,51,69):
            if key in values and values[key]>=insert[1]:values[key]+=added
        output.extend(raw if values==original else encode(kind,values,props))
    if changed!=23 or not tracks:raise ValueError('Original Junior grid shapes or timeline changed')
    for frame_index,frame in enumerate(frames):
        width,height=sizes[frame_index]
        output.extend(encode(105,{203:'DuoAero Linus '+str(frame_index),204:asset_unique+frame_index,
                                  207:float(height),208:float(width)}))
        output.extend(encode(106,{212:frame}))
    return bytes(output),boards

def rive(data,name,png,width,height):
    if name in CHARACTER_CAST:return expressive_character(data,name)
    if name=='math_junior_grid':return linus_grid(data)
    header,objects,props=parse(data)
    artboard_names=[p.get(4,'') for t,p,b in objects if t==1]
    asset_index=sum(t in ASSET for t,p,b in objects)
    asset_unique=max([p.get(204,0) for t,p,b in objects if t in ASSET]+[0])+1
    pure=bool(re.search(r'(^|_)duo(?:_|$)|resurrectedduo',name)) and 'waveform' not in name
    # Some source files put an eye or sparkle artboard before the character.
    # Selecting the first artboard would put the entire replacement in an
    # eye while leaving the original Duo visible in the main scene.
    boards=[p for t,p,b in objects if t==1]
    def auxiliary(label):
        return re.search(r'sparkle|pupil|shine|waveform|(?:^|_)eyes(?:_|$)',label,re.I)
    primary=next((p.get(4,'') for p in boards if p.get(4)=='lc_character_artboard'),None)
    if primary is None:
        primary=next((p.get(4,'') for p in boards if min(p.get(7,0),p.get(8,0))>=100
                      and not auxiliary(p.get(4,''))),None)
    epic=('celebrate',('EpicDuo_Intro_Animation','EpicDuo_IdleLoop'))
    surprised=('surprised',('JawdropDuo_Intro_animation','JawdropDuo_Loop_animation'))
    determined=('determined',('Duo_LFG_Intro_Animation','Duo_LFG_IdleLoop'))
    overjoyed=('overjoyed',('ObsessedDuo_Intro_Animation','ObsessedDuo_IdleLoop'))
    starry=('overjoyed',('StarryEyedDuo_intro_animation','StarryEyedDuo_Loop_animation'))
    hero=('hero',('BuffDuo_Intro_Animation','BuffDuo_IdleLoop'))
    lovey=('lovey',('LoveyDoveyDuo_Intro_animation','LoveyDoveyDuo_Loop_animation'))
    swoon=('swoon',('SwoonDuo_Loop_animation',))
    chef=('chef',('ChefsKissDuo_Intro_animation','ChefsKissDuo_Loop_animation'))
    foam=('foam',('FoamFingerDuo_Intro_animation','FoamFingerDuo_Loop_animation'))
    zen=('zen',('duo_zen','duo_meditate','duo_meditate_loop'))
    targets={'duo_perfect_epic_03':{'lc_character_artboard':epic},
             'duo_perfect_jaw_drop_04':{'lc_character_artboard':surprised},
             'duo_perfect_lfg_03':{'lc_character_artboard':determined},
             'duo_obsessed_02':{'lc_character_artboard':overjoyed},
             'duo_perfect_starry_eyed_03':{'lc_character_artboard':starry},
             'duo_perfect_buff_03':{'lc_character_artboard':hero},
             'duo_normal_lovey_dovey_03':{'lc_character_artboard':lovey},
             'duo_normal_swoon_03':{'lc_character_artboard':swoon},
             'duo_perfect_chefs_kiss_03':{'lc_character_artboard':chef},
             'duo_normal_foam_finger_02':{'lc_character_artboard':foam},
             'duo_zen_04':{'36_zen_duo':zen},
             'lesson_complete_main_29':{'lc_character_artboard':hero},
             'lesson_complete_redesign_v72':{'01_duo_epic_arboard':epic,
                 '17_duo_perfect_jaw_drop_artboard':surprised,
                 '04_duo_lfg_artboard':determined,
                 '02_duo_obsessed_artboard':overjoyed,
                 '00_duo_buff_artboard':hero,
                 '20_duo_normal_lovey_dovey_artboard':lovey,
                 '21_duo_normal_swoon_artboard':swoon,
                 '26_duo_perfect_chefs_kiss_artboard':chef,
                 '25_duo_normal_foam_finger_artboard':foam,
                 '22_duo_perfect_starry_eyed_artboard':starry}}.get(name,{})
    all_frames=[];frame_sets={}
    if targets:
        from io import BytesIO
        from PIL import Image
        for board,(mood,timelines) in targets.items():
            frame_dir=Path(__file__).resolve().parents[1]/'app/assets/mascot'/mood
            frames=[(frame_dir/f'frame-{i:02}.png').read_bytes() for i in range(16)]
            anchors=[]
            for frame in frames:
                with Image.open(BytesIO(frame)) as im:
                    # Ignore almost transparent antialiasing when measuring
                    # poses and register their centres and baselines.
                    box=im.getchannel('A').point(lambda a:255 if a>64 else 0).getbbox()
                    if box is None:raise ValueError('Empty animation frame')
                    anchors.append(((box[0]+box[2])/2,box[3]))
            frame_sets[board]=(frames,anchors,len(all_frames),timelines)
            all_frames.extend(frames)
    # Rive's keyed-object IDs count interpolators as well as components.
    # Count the original IDs before appending our images to each artboard.
    counts={};count_board=None
    for kind,values,_ in objects:
        if kind==1:count_board=values.get(4,'');counts[count_board]=0
        elif count_board is not None and (kind in COMPONENT or 'Interpolator' in SCHEMA['types'].get(str(kind),'')):
            counts[count_board]+=1
    static_index=asset_index+len(all_frames)
    keyed={25,26}|{int(k) for k,v in SCHEMA['types'].items() if 'KeyFrame' in v}
    animation=None
    replace=False;art=None;output=bytearray(header);changed=[];component_id=0;motion_parent=0;state_layer=None
    def finish():
        if not replace:return
        w,h=art.get(7,600.),art.get(8,600.)
        if art.get(4) in frame_sets:
            frames,anchors,offset,_=frame_sets[art.get(4)]
            for i,frame in enumerate(frames):
                fw,fh=struct.unpack_from('>II',frame,16);scale=min(w/fw,h/fh)*.90
                x=(anchors[0][0]-anchors[i][0])*scale
                y=(anchors[0][1]-anchors[i][1])*scale
                output.extend(encode(100,{4:f'DuoAero Snoopy frame {i}',5:motion_parent,206:asset_index+offset+i,
                    13:w*(.5-art.get(11,0.))+x,14:h*(.5-art.get(12,0.))+y,16:scale,17:scale,18:1. if i==0 else 0.}))
            return
        scale=min(w/width,h/height)*.90
        output.extend(encode(100,{4:'DuoAero Snoopy',5:motion_parent,206:static_index,13:w*(.5-art.get(11,0.)),14:h*(.5-art.get(12,0.)),16:scale,17:scale}))
    def finish_animation():
        if not animation or not art or art.get(4) not in frame_sets:return
        frames,_,_,timelines=frame_sets[art.get(4)]
        if animation.get(55) not in timelines:return
        duration=animation.get(57,60)
        start=animation.get(60,0);end=animation.get(61,duration)
        if animation.get(59)==1 and end>start:
            # Fit an integral number of cycles into the native work area,
            # including the 122-frame BuffDuo loop.
            span=end-start;cycle=max(16,round(span/max(1,round(span/60))));phase=start
            if art.get(4) in ('21_duo_normal_swoon_artboard','lc_character_artboard') and name in ('duo_normal_swoon_03','lesson_complete_redesign_v72'):
                cycle=span
        else:
            cycle=60;phase=0
        for i in range(len(frames)):
            output.extend(encode(25,{51:counts[art.get(4)]+1+i}))
            output.extend(encode(26,{53:18}))
            # A native loop can end exactly at its timeline duration; key the
            # endpoint too so its final sample agrees with the loop start.
            for t in range(0,max(1,duration)+1):
                current=((t-phase)*len(frames)//cycle)%len(frames)
                previous=((t-1-phase)*len(frames)//cycle)%len(frames)
                if name in ('duo_normal_swoon_03','lesson_complete_redesign_v72') and art.get(4) in ('21_duo_normal_swoon_artboard','lc_character_artboard'):
                    # Group the open-eyed poses and the closed-eyed poses into
                    # one gradual cycle, instead of flickering between them.
                    order=(0,15,14,13,12,11,10,7,1,2,3,4,5,6,8,9)
                    current,previous=order[current],order[previous]
                if t==0 or current!=previous:
                    output.extend(encode(30,{67:t,70:1. if current==i else 0.}))
    for kind,values,raw in objects:
        if animation is not None and kind not in keyed:
            finish_animation();animation=None
        if kind==1:
            finish();art=values;component_id=0;motion_parent=0;state_layer=None;label=values.get(4,'');w,h=values.get(7,0),values.get(8,0)
            # Some large character artboards nest another artboard containing
            # only eyes. Replacing both draws two full Snoopy images on top
            # of one another (and can put Snoopy inside Duo's eyes).
            replace=(pure and label==primary) or (name=='lesson_complete_main_29' and label=='lc_character_artboard') or ('duo' in label.lower() and min(w,h)>=100 and not auxiliary(label))
            # The zen scene's outer board nests its actual character board.
            # Replacing both would draw two full characters on top of each other.
            if name=='duo_zen_04' and label=='lc_character_artboard':replace=False
            if replace:changed.append(label)
        elif art is not None and kind in COMPONENT:
            component_id+=1
            # Follow the original character's centered root motion (intro,
            # bounce, fade); do not replace state machines or their events.
            if replace and not motion_parent and kind==2 and values.get(5)==0 and abs(values.get(13,0))<1 and abs(values.get(14,0))<1:
                motion_parent=component_id
        if replace and kind==31:animation=values
        if replace and kind==57:state_layer=values.get(138,'')
        update=dict(values)
        if replace and kind in DRAWABLE:update[129]=values.get(129,0)|1
        # The original foam rig cross-fades its intro into the loop. That
        # blends several opaque sprite poses at once. The two tracks meet at
        # the same registered pose, so switch at the boundary instead.
        if (art is not None and kind==65 and state_layer=='idleLoop'
            and values.get(158)==800 and (name,art.get(4)) in (
                ('duo_normal_foam_finger_02','lc_character_artboard'),
                ('lesson_complete_redesign_v72','25_duo_normal_foam_finger_artboard'),
                ('duo_normal_swoon_03','lc_character_artboard'),
                ('lesson_complete_redesign_v72','21_duo_normal_swoon_artboard'))):
            update[158]=0
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
        if (kind==63 and art is not None and state_layer=='idleLoop'
            and (name,art.get(4)) in (('duo_normal_swoon_03','lc_character_artboard'),
                                      ('lesson_complete_redesign_v72','21_duo_normal_swoon_artboard'))):
            # The original entry has no initial transition: select its existing
            # loop state so the idle pose animates without an external trigger.
            output.extend(encode(65,{151:1 if name=='duo_normal_swoon_03' else 3}))
    finish_animation();finish()
    if changed:
        for i,frame in enumerate(all_frames):
            fw,fh=struct.unpack_from('>II',frame,16)
            output.extend(encode(105,{203:f'DuoAero frame {i}',204:asset_unique+i,207:float(fh),208:float(fw)}))
            output.extend(encode(106,{212:frame}))
        output.extend(encode(105,{203:'DuoAero Snoopy',204:asset_unique+len(all_frames),207:float(height),208:float(width)}))
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
