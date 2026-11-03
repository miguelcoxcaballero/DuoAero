"""Check scroll helper definitions against references in the assembled APK DEX.

This validates binary descriptors, not layout or runtime behavior.
"""
import struct
import sys
import zipfile

OWNER='Lcom/duoaero/nativebase/NativeCourseBridge;'
NAME='scrollLongBuildSpace'
EXPECTED={
    '(Ljava/util/List;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;',
    '(Ljava/util/List;Ljava/lang/Object;Ljava/lang/Object;Z)Ljava/lang/Object;',
}

def uleb(data,pos):
    value=0
    for shift in range(0,35,7):
        b=data[pos];pos+=1;value|=(b&127)<<shift
        if not b&128:return value,pos
    raise ValueError('Invalid DEX uleb128')

def parse(data):
    if not data.startswith(b'dex\n'):raise ValueError('Not a DEX')
    u32=lambda offset:struct.unpack_from('<I',data,offset)[0]
    sizes=[(u32(i),u32(i+4)) for i in (56,64,72,88,96)]
    (string_count,string_off),(type_count,type_off),(proto_count,proto_off),(method_count,method_off),(class_count,class_off)=sizes
    strings=[]
    for i in range(string_count):
        _,p=uleb(data,u32(string_off+4*i));end=data.index(b'\0',p)
        strings.append(data[p:end].decode('utf-8','surrogateescape'))
    types=[strings[u32(type_off+4*i)] for i in range(type_count)]
    protos=[]
    for i in range(proto_count):
        _,ret,params=struct.unpack_from('<III',data,proto_off+12*i)
        args=[] if not params else [types[struct.unpack_from('<H',data,params+4+2*j)[0]] for j in range(u32(params))]
        protos.append('('+''.join(args)+')'+types[ret])
    methods=[]
    for i in range(method_count):
        cls,proto,name=struct.unpack_from('<HHI',data,method_off+8*i)
        methods.append((types[cls],strings[name],protos[proto]))
    references={p for owner,name,p in methods if owner==OWNER and name==NAME}
    definitions=set()
    for i in range(class_count):
        at=class_off+32*i;cls=u32(at);p=u32(at+24)
        if types[cls]!=OWNER or not p:continue
        counts=[]
        for _ in range(4):v,p=uleb(data,p);counts.append(v)
        for _ in range(counts[0]+counts[1]):_,p=uleb(data,p);_,p=uleb(data,p)
        for count in counts[2:]:
            index=0
            for _ in range(count):
                delta,p=uleb(data,p);index+=delta
                _,p=uleb(data,p);_,p=uleb(data,p)
                owner,name,proto=methods[index]
                if owner==OWNER and name==NAME:definitions.add(proto)
    return references,definitions

refs=set();defs=set()
with zipfile.ZipFile(sys.argv[1]) as apk:
    for name in apk.namelist():
        if name.startswith('classes') and name.endswith('.dex') and '/' not in name:
            r,d=parse(apk.read(name));refs.update(r);defs.update(d)
if not EXPECTED<=refs or not refs<=defs or not EXPECTED<=defs:
    raise SystemExit('Scroll DEX descriptor mismatch: refs='+repr(sorted(refs))+' definitions='+repr(sorted(defs)))
print('PASS: assembled APK scroll-helper references match both DEX definitions')
