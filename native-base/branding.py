"""Rebrand displayed Android values without changing IDs or protocol strings."""
import re
import struct
from resource_extension import chunks

MASCOT_PATH = 'res/drawable/duoaero_launcher_mascot.png'
LOGO_PATH = 'res/drawable/duoaero_wordmark.xml'

def display_text(text):
    # URLs, email addresses, resource paths and package names keep their routing.
    protected = re.compile(r'https?://[^\s<>"\']+|[\w.+-]+@[\w.-]+|(?:[\w-]+\.)*duolingo\.[\w./?=&%+-]+', re.I)
    def words(value):
        return re.sub(r'\bduolingo\b', 'DuoAero', value, flags=re.I)
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

def mascot_name(name):
    # Internal vector pieces belong to their parent animated-vector resources.
    return not name.startswith('$') and bool(re.search(r'(^|_)duo($|_)',name))

def rebrand_table(table):
    top=list(chunks(table,12,len(table))); off,_,_,size=top[0]
    pool=table[off:off+size]; values=strings(pool)
    off,_,header,size=top[1]; package=bytearray(table[off:off+size])
    key_off=struct.unpack_from('<I',package,276)[0]
    key_size=struct.unpack_from('<I',package,key_off+4)[0]
    keys=strings(package[key_off:key_off+key_size])
    replacements={}; text_indices=set(); affected={}
    def index(value):
        if value not in values:values.append(value)
        return values.index(value)
    for start,kind,ch,cs in chunks(package,header,len(package)):
        if kind!=0x201:continue
        tid=package[start+8]
        if tid not in (8,19):continue
        assert package[start+9]==0, 'Unexpected resource offsets'
        count=struct.unpack_from('<I',package,start+12)[0]
        entries=start+struct.unpack_from('<I',package,start+16)[0]
        for i in range(count):
            relative=struct.unpack_from('<I',package,start+ch+4*i)[0]
            if relative==0xffffffff:continue
            at=entries+relative; es,flags,key=struct.unpack_from('<HHI',package,at)
            if flags or es!=8 or package[at+11]!=3:continue
            old=struct.unpack_from('<I',package,at+12)[0]; name=keys[key]
            if tid==19:text_indices.add(old)
            elif mascot_name(name) or name in ('duolingo_logo_350','duolingo_max_wordmark','duolingo_max_wordmark_onboarding'):
                path=LOGO_PATH if 'duolingo' in name else MASCOT_PATH
                struct.pack_into('<I',package,at+12,index(path));affected[name]=path
    for i in text_indices:
        updated=display_text(values[i])
        if updated!=values[i]:replacements[i]=(values[i],updated); values[i]=updated
    out=bytearray(table[:12])+pool_bytes(pool,values)+package
    struct.pack_into('<I',out,4,len(out))
    return bytes(out), {'text_values':len(replacements),'drawable_resources':affected}

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
