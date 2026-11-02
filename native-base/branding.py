"""Rebrand displayed Android values without changing IDs or protocol strings."""
import re
import struct
from resource_extension import chunks, MOOD_SCENES, CHARACTER_REPLACEMENTS

MASCOT_PATH = 'res/drawable/duoaero_launcher_mascot.png'
LOGO_PATH = 'res/drawable/duoaero_wordmark.xml'
WORDMARKS = frozenset(('duolingo_logo_350','duolingo_max_wordmark',
    'duolingo_max_wordmark_onboarding','duo_logo_green','duo_logo_grey',
    'duo_logo_white','intro_duo_logo_green'))

def rebrand_app_display_names(smali):
    """Change only human-readable icon titles, preserving runtime identifiers."""
    pattern = re.compile(r'(?m)^(\s*const-string(?:/jumbo)?\s+\w+,\s+")([^"\n]*Duolingo[^"\n]*)(")')
    result, count = pattern.subn(lambda match: match.group(1)+match.group(2).replace('Duolingo','DuoAero')+match.group(3), smali)
    if count != 22:
        raise ValueError('Unexpected original AppDisplayName layout: '+str(count))
    return result

def display_text(text):
    if text.startswith(('res/','com.duolingo')):return text
    # URLs, email addresses, resource paths and package names keep their routing.
    protected = re.compile(r'https?://[^\s<>"\']+|[\w.+-]+@[\w.-]+|(?:[\w-]+\.)*duolingo\.[\w./?=&%+-]+', re.I)
    def words(value):
        value = re.sub(r'(?<![A-Za-z0-9_])duolingo(?![A-Za-z0-9_])', 'DuoAero', value, flags=re.I)
        return re.sub(r'(?<![A-Za-z0-9_])#duolingo(?=\d)', '#DuoAero', value, flags=re.I)
    parts=[]; start=0
    for match in protected.finditer(text):
        parts.extend((words(text[start:match.start()]),match.group()))
        start=match.end()
    parts.append(words(text[start:]))
    return ''.join(parts)

def strings(pool):
    kind, header, size, count, styles, flags, start, style_start = struct.unpack_from('<HHIIIIII',pool)
    assert kind==1 and header==28 and flags&0x100 and not styles and not style_start
    def length(at):
        v=pool[at];return (((v&127)<<8)|pool[at+1],at+2) if v&128 else (v,at+1)
    values=[]
    for i in range(count):
        at=start+struct.unpack_from('<I',pool,header+4*i)[0]
        _,at=length(at); n,at=length(at)
        values.append(pool[at:at+n].decode('utf8'))
    return values

def pool_bytes(pool, values):
    def length(n):
        if n>=32768:raise ValueError('Resource text too long')
        return bytes([n]) if n<128 else bytes([(n>>8)|128,n&255])
    offsets=[]; data=bytearray()
    for value in values:
        raw=value.encode('utf8'); offsets.append(len(data))
        data+=length(len(value.encode('utf-16-le'))//2)+length(len(raw))+raw+b'\0'
    data+=b'\0'*(-len(data)%4)
    out=bytearray(pool[:28]);out+=struct.pack('<'+'I'*len(offsets),*offsets)+data
    struct.pack_into('<I',out,4,len(out));struct.pack_into('<I',out,8,len(values))
    struct.pack_into('<I',out,16,struct.unpack_from('<I',out,16)[0]&~1)
    struct.pack_into('<I',out,20,28+4*len(values))
    return bytes(out)

def explicit_character(name):
    """Identify single-character static vectors, excluding controls/groups."""
    names='|'.join(CHARACTER_REPLACEMENTS)
    match=re.fullmatch(r'(?:character_('+names+r')(?:_small)?|in_challenge_('+names+r')|duoradio_host_('+names+r')_(exercise(?:_correct|_incorrect)?|listening|talking))',name.lower())
    if not match:return None
    original=next(group for group in match.group(1,2,3) if group)
    suffix=match.group(4) or ''
    expression='_happy' if suffix.endswith('_correct') and not suffix.endswith('_incorrect') else '_sad' if suffix.endswith('_incorrect') else ''
    return CHARACTER_REPLACEMENTS[original]+expression


def mascot_name(name):
    # Internal vector pieces belong to their parent animated-vector resources.
    # "Duo Radio" also names playback and answer controls. They are not
    # pictures of the character and replacing them corrupts the interface.
    if explicit_character(name):return True
    if name.startswith('duo_radio_') and name != 'duo_radio_host_static_bea':
        return False
    if any(part in name for part in ('_light_beam','_lightbeam','_glow','_sparkles','_confetti','_shadow','_particle')):return False
    return not name.startswith('$') and bool(re.search(r'(^|_)duo($|_)',name))


def static_mood(name):
    """Select an authored pose only where the original name is unambiguous."""
    name=name.lower()
    character=explicit_character(name)
    if character:return character
    if name=='duo_radio_host_static_bea':return 'patty'
    if name=='duo_happy':return 'wave'
    if name=='duo_wave':return 'wave_static'
    if name.startswith('practice_hub_duo_radio_'):
        cast={'zari':'sally','falstaff':'charlie','junior':'linus','lily':'lucy',
              'oscar':'schroeder','bea':'patty','lin':'marcie','vikram':'franklin',
              'eddy':'pigpen','lucy':'woodstock'}
        for original,replacement in cast.items():
            if re.search(r'(^|_)'+original+r'(_|$)',name):return replacement
    if any(word in name for word in ('sad','cry','fail','noooo')):return 'sad'
    if name in ('duo_reading_stories','stories_duo_reading'):return 'reading'
    if name in ('duo_holding_gem','guidebook_header_duo_gem'):return 'gem'
    if any(word in name for word in ('jaw_drop','surprised','shocked','amaze')):return 'surprised'
    if any(word in name for word in ('flying','_fly','flight','plane')):return 'plane'
    if any(word in name for word in ('thinking','ponder','detective','smart')):return 'think'
    if any(word in name for word in ('chef','cooking')):return 'chef'
    if any(word in name for word in ('lovey','swoon','romantic','heart_throb')):return 'lovey'
    if any(word in name for word in ('foam_finger','cheer')):return 'foam'
    if any(word in name for word in ('meditat','breathe','_zen')):return 'zen'
    if any(word in name for word in ('buff','hero')):return 'hero'
    if any(word in name for word in ('happy','celebrat','epic','lfg','legendary_complete')):return 'celebrate'
    return None

def rebrand_table(table,drawable_paths=None):
    top=list(chunks(table,12,len(table))); off,_,_,size=top[0]
    pool=table[off:off+size]; values=strings(pool)
    off,_,header,size=top[1]; package=bytearray(table[off:off+size])
    key_off=struct.unpack_from('<I',package,276)[0]
    key_size=struct.unpack_from('<I',package,key_off+4)[0]
    keys=strings(package[key_off:key_off+key_size])
    replacements={}; text_indices=set(); affected={};original_paths={}
    def index(value):
        if value not in values:values.append(value)
        return values.index(value)
    for start,kind,ch,cs in chunks(package,header,len(package)):
        if kind!=0x201:continue
        tid=package[start+8]
        # Both strings and plurals can carry user-facing text. Plural entries
        # are complex resource bags, which cannot be read like simple values.
        if tid not in (8,17,19):continue
        assert package[start+9]==0, 'Unexpected resource offsets'
        count=struct.unpack_from('<I',package,start+12)[0]
        entries=start+struct.unpack_from('<I',package,start+16)[0]
        for i in range(count):
            relative=struct.unpack_from('<I',package,start+ch+4*i)[0]
            if relative==0xffffffff:continue
            at=entries+relative; es,flags,key=struct.unpack_from('<HHI',package,at)
            if tid in (17,19) and flags&1:
                if es<16:raise ValueError('Unexpected complex text resource entry')
                count_values=struct.unpack_from('<I',package,at+12)[0]
                for n in range(count_values):
                    value_at=at+es+12*n
                    if value_at+12>start+cs:raise ValueError('Invalid text resource map')
                    if package[value_at+7]==3:
                        text_indices.add(struct.unpack_from('<I',package,value_at+8)[0])
                continue
            if flags or es!=8 or package[at+11]!=3:continue
            old=struct.unpack_from('<I',package,at+12)[0]; name=keys[key]
            if tid in (17,19):text_indices.add(old)
            elif mascot_name(name) or name in WORDMARKS:
                original_paths[values[old]]=name
                if name not in WORDMARKS and drawable_paths is not None and values[old] not in drawable_paths:continue
                path=LOGO_PATH if name in WORDMARKS else (drawable_paths or {}).get(values[old],MASCOT_PATH)
                struct.pack_into('<I',package,at+12,index(path));affected[name]=path
    for i in text_indices:
        updated=display_text(values[i])
        if updated!=values[i]:replacements[i]=(values[i],updated); values[i]=updated
    out=bytearray(table[:12])+pool_bytes(pool,values)+package
    struct.pack_into('<I',out,4,len(out))
    return bytes(out), {'text_values':len(replacements),'drawable_resources':affected,'original_paths':original_paths}

def wordmark_xml(font_path):
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    font=TTFont(font_path);glyphs=font.getGlyphSet();cmap=font.getBestCmap()
    pen=SVGPathPen(glyphs);x=0;upm=font['head'].unitsPerEm
    for char in 'DuoAero':
        glyph=glyphs[cmap[ord(char)]]
        glyph.draw(TransformPen(pen,(1,0,0,-1,x,upm*.8)))
        x+=glyph.width
    return ('<vector xmlns:android="http://schemas.android.com/apk/res/android" '
      f'android:width="240dp" android:height="64dp" android:viewportWidth="{x}" android:viewportHeight="{upm}">'
      f'<path android:fillColor="#1CB0F6" android:pathData="{pen.getCommands()}"/></vector>')

def animation_overlays(original,png):
    from mascot_assets import rive,lottie
    # PNG IHDR dimensions; no image modification or raster regeneration.
    width,height=struct.unpack_from('>II',png,16)
    overlays={};report={}
    for path in original.namelist():
        if not path.startswith(('res/raw/','assets/')):continue
        name=path.rsplit('/',1)[-1].rsplit('.',1)[0]
        if path.endswith('.riv'):
            source=original.read(path);result,boards=rive(source,name,png,width,height)
            if result!=source:overlays[path]=result;report[path]={'artboards':boards}
        elif path.endswith('.json') and re.search(r'(^|_)duo(?:_|$)|resurrectedduo',name):
            source=original.read(path)
            try:result,changed=lottie(source,name,png,width,height)
            except (ValueError,KeyError,TypeError):continue
            if changed:overlays[path]=result;report[path]={'lottie':True}
    return overlays,report

def mascot_drawables(decoded,table):
    """Keep original intrinsic bounds while fitting the unchanged PNG inside."""
    import hashlib,xml.etree.ElementTree as E
    from PIL import Image
    from pathlib import Path
    decoded=Path(decoded);A='{http://schemas.android.com/apk/res/android}'
    dimensions={e.get('name'):e.text for p in (decoded/'res').glob('values/dimens.xml') for e in E.parse(p).getroot()}
    def number(value):
        if value.startswith('@dimen/'):value=dimensions[value.split('/',1)[1]]
        return float(re.sub(r'(dp|dip|px)$','',value))
    def size(path,seen=()):
        if path in seen:raise ValueError('Circular drawable '+path)
        file=decoded/path
        if not file.exists():
            folder=re.sub(r'-v\d+$','',file.parent.name)
            choices=list((decoded/'res').glob(folder+'/'+file.name))+list((decoded/'res').glob(folder+'-v*/'+file.name))
            if not choices:raise FileNotFoundError(path)
            file=choices[0]
        if file.suffix!='.xml':
            with Image.open(file) as im:w,h=im.size
            folder=file.parent.name;density=next((v for k,v in [('xxxhdpi',640),('xxhdpi',480),('xhdpi',320),('hdpi',240),('mdpi',160),('ldpi',120)] if k in folder),160)
            return w*160/density,h*160/density
        root=E.parse(file).getroot()
        if root.tag=='vector' and root.get(A+'width') and root.get(A+'height'):return number(root.get(A+'width')),number(root.get(A+'height'))
        for e in root.iter():
            if e.tag=='vector' and e.get(A+'width') and e.get(A+'height'):return number(e.get(A+'width')),number(e.get(A+'height'))
        for e in root.iter():
            ref=e.get(A+'drawable') or e.get(A+'src')
            if ref and ref.startswith('@drawable/'):
                target=ref.split('/',1)[1]
                candidates=list((decoded/'res/drawable').glob(target+'.*'))
                if not candidates:candidates=list((decoded/'res').glob('drawable*/'+target+'.*'))
                if candidates:return size(str(candidates[0].relative_to(decoded)),seen+(path,))
        return None  # A border/solid/gradient is not mascot artwork.
    paths={};files={};sizes={}
    for path,name in rebrand_table(table)[1]['original_paths'].items():
        if 'duolingo' in name:continue
        intrinsic=size(path)
        if intrinsic is None:continue
        w,h=intrinsic
        if w<=0 or h<=0:raise ValueError('Invalid original mascot size: '+path)
        target='res/drawable/duoaero_mascot_'+hashlib.sha256(path.encode()).hexdigest()[:16]+'.xml'
        mood=static_mood(name)
        # The wave image is a 4x4 atlas, not a standalone pose. A resource
        # loaded by Android must show one image even before an app hook runs.
        if mood=='wave':mood='celebrate'
        source=MOOD_SCENES[mood] if mood else 'welcome.png'
        png=(Path(__file__).resolve().parents[1]/'app/assets/mascot'/source).read_bytes()
        iw,ih=struct.unpack_from('>II',png,16);scale=min(w/iw,h/ih)
        if name == 'duo_eyes':
            # Android applies a circular splash mask; keep the complete face
            # within it instead of enlarging the old doghouse to 288dp.
            image_w, image_h = w*.35, h*.35
            drawable = '@drawable/ic_launcher_foreground'
        else:
            image_w, image_h = iw*scale, ih*scale
            drawable = '@drawable/duoaero_scene_'+mood if mood else '@drawable/duoaero_scene_mascot'
        files[target]=f'<layer-list xmlns:android="http://schemas.android.com/apk/res/android"><item><shape><size android:width="{w:g}dp" android:height="{h:g}dp"/><solid android:color="#00000000"/></shape></item><item android:width="{image_w:g}dp" android:height="{image_h:g}dp" android:gravity="center"><bitmap android:src="{drawable}" android:gravity="fill" android:filter="true"/></item></layer-list>'
        paths[path]=target;sizes[path]=[w,h]
    return paths,files,sizes
