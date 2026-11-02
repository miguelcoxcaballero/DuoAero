"""Append a file resource while preserving every existing Android resource ID.

Used for the canonical updater's own provider paths. Existing layouts, styles,
configuration values and compiled XML are not rebuilt or renumbered.
"""
import struct

MASCOT_PATH = 'res/drawable/duoaero_launcher_mascot.png'
SCENE_MASCOT_PATH = 'res/drawable/duoaero_scene_mascot.png'


def append_scene_drawable(table, name, path):
    """Append a scene bitmap without changing existing resource IDs/configs."""
    top = list(chunks(table, 12, len(table)))
    offset, _, _, size = top[0]
    pool, path_index = append_string(table[offset:offset+size], path)
    offset, kind, header, size = top[1]
    if kind != 0x200 or header != 288:
        raise ValueError('Unexpected original application package')
    package = table[offset:offset+size]
    key_offset = struct.unpack_from('<I', package, 276)[0]
    type_offset = struct.unpack_from('<I', package, 268)[0]
    output = bytearray(package[:header])
    entry_id = None
    defaults = 0
    for start, kind, chunk_header, chunk_size in chunks(package, header, len(package)):
        chunk = bytearray(package[start:start+chunk_size])
        if start == type_offset:
            struct.pack_into('<I', output, 268, len(output))
        if start == key_offset:
            struct.pack_into('<I', output, 276, len(output))
            chunk, key_index = append_string(chunk, name)
        elif kind in (0x201, 0x202) and chunk[8] == 0x08:
            count = struct.unpack_from('<I', chunk, 12)[0]
            if chunk[9] != 0 or (entry_id is not None and count != entry_id):
                raise ValueError('Unexpected original drawable entries')
            entry_id = count
            if kind == 0x202:
                chunk += struct.pack('<I', 0)
            else:
                entries_start = struct.unpack_from('<I', chunk, 16)[0]
                if entries_start != chunk_header + count * 4:
                    raise ValueError('Unexpected drawable offset table')
                config_size = struct.unpack_from('<I', chunk, 20)[0]
                default = not any(chunk[24:20+config_size])
                values = chunk[entries_start:]
                if default:
                    defaults += 1
                    entry = struct.pack('<HHIHBBI', 8, 0, key_index, 8, 0, 3, path_index)
                    offset_value = len(values)
                else:
                    entry = b''
                    offset_value = 0xffffffff
                chunk = chunk[:entries_start] + struct.pack('<I', offset_value) + values + entry
                struct.pack_into('<I', chunk, 16, entries_start + 4)
            struct.pack_into('<I', chunk, 12, count + 1)
            struct.pack_into('<I', chunk, 4, len(chunk))
        output += chunk
    if defaults != 1 or entry_id is None:
        raise ValueError('Expected one default drawable configuration')
    struct.pack_into('<I', output, 4, len(output))
    result = bytearray(table[:12]) + pool + output
    struct.pack_into('<I', result, 4, len(result))
    return bytes(result), 0x7f080000 | entry_id


def scene_mascot(table):
    return append_scene_drawable(table, 'duoaero_scene_mascot', SCENE_MASCOT_PATH)


# Existing transparent character artwork used for the corresponding static
# original poses. Animation resources still use their own native Rive tracks.
MOOD_SCENES = {
    'think': 'think.png',
    'celebrate': 'overjoyed/frame-00.png',
    'surprised': 'surprised/frame-00.png',
    'plane': 'plane/frame-00.png',
    'foam': 'foam/frame-00.png',
    'hero': 'hero/frame-00.png',
    'lovey': 'lovey/frame-00.png',
    'chef': 'chef/frame-00.png',
    'zen': 'zen/frame-00.png',
    'sad': 'sad.png',
    'sad_animated': 'sad-atlas.png',
    'sally': 'characters/sally/idle/frame-00.png',
    'charlie': 'characters/charlie/idle/frame-00.png',
    'linus': 'characters/linus/idle/frame-00.png',
    'lucy': 'characters/lucy/idle/frame-00.png',
    'schroeder': 'characters/schroeder/idle/frame-00.png',
    'patty': 'characters/patty/idle/frame-00.png',
    'marcie': 'characters/marcie/idle/frame-00.png',
    'franklin': 'characters/franklin/idle/frame-00.png',
    'pigpen': 'characters/pigpen/idle/frame-00.png',
    'woodstock': 'characters/woodstock/idle/frame-00.png',
    'reading': 'reading.png',
    'gem': 'gem.png',
    'wave': 'wave-atlas.png',
}

# Existing drawings are distinct transparent poses for the corresponding
# Peanuts cast. These apply only to explicit single-character vector IDs.
CHARACTER_REPLACEMENTS = {
    'zari':'sally', 'falstaff':'charlie', 'junior':'linus', 'lily':'lucy',
    'oscar':'schroeder', 'bea':'patty', 'lin':'marcie', 'vikram':'franklin',
    'eddy':'pigpen', 'lucy':'woodstock',
}
for character in CHARACTER_REPLACEMENTS.values():
    for expression in ('happy', 'sad'):
        MOOD_SCENES[character+'_'+expression] = 'characters/'+character+'/'+expression+'/frame-00.png'

# Appended after existing scenes to keep their assigned resource IDs stable.
MOOD_SCENES['wave_static'] = 'wave-static.png'
MOOD_SCENES['phone_static'] = 'welcome-phone.png'
MOOD_SCENES['chest_hug'] = 'chest-hug.png'
MOOD_SCENES['flame_static'] = 'flame-static.png'
MOOD_SCENES['linus_grid_static'] = 'path-linus/grid-static.png'


def mood_scenes(table):
    ids = {}
    for mood in MOOD_SCENES:
        table, ids[mood] = append_scene_drawable(table, 'duoaero_scene_'+mood,
                                                 'res/drawable/duoaero_scene_'+mood+'.png')
    return table, ids


def launcher_mascot(table):
    """Point only the original launcher foreground ID at the approved artwork."""
    top = list(chunks(table, 12, len(table)))
    offset, _, _, size = top[0]
    pool, path_index = append_string(table[offset:offset+size], MASCOT_PATH)
    offset, kind, header, size = top[1]
    if kind != 0x200:
        raise ValueError('Expected original application package')
    package = bytearray(table[offset:offset+size])
    changed = 0
    for start, kind, chunk_header, chunk_size in chunks(package, header, len(package)):
        if kind != 0x201 or package[start+8] != 0x08:
            continue
        if package[start+9] != 0:
            raise ValueError('Unexpected drawable entry encoding')
        count = struct.unpack_from('<I', package, start+12)[0]
        if count <= 0x293e:
            continue
        entry_offset = struct.unpack_from('<I', package, start+chunk_header+4*0x293e)[0]
        if entry_offset == 0xffffffff:
            continue
        entry = start + struct.unpack_from('<I', package, start+16)[0] + entry_offset
        entry_size, flags = struct.unpack_from('<HH', package, entry)
        if entry_size != 8 or flags or package[entry+11] != 3:
            raise ValueError('Unexpected original launcher foreground value')
        struct.pack_into('<I', package, entry+12, path_index)
        changed += 1
    if changed != 1:
        raise ValueError('Original launcher foreground must have one configuration')
    result = bytearray(table[:12]) + pool + package
    struct.pack_into('<I', result, 4, len(result))
    return bytes(result)


def chunks(data, start, end):
    while start < end:
        kind, header, size = struct.unpack_from('<HHI', data, start)
        if header < 8 or size < header or start + size > end:
            raise ValueError('Invalid Android resource chunk')
        yield start, kind, header, size
        start += size
    if start != end:
        raise ValueError('Invalid resource chunk boundary')


def append_string(pool, value):
    kind, header, size, count, styles, flags, strings_start, styles_start = struct.unpack_from('<HHIIIIII', pool)
    if kind != 1 or header != 28 or styles or styles_start or not flags & 0x100:
        raise ValueError('Expected original UTF-8 string pool without styles')
    encoded = value.encode('utf-8')
    units = len(value.encode('utf-16-le')) // 2
    def length(n):
        if n >= 32768:
            raise ValueError('Resource string too long')
        return bytes([n]) if n < 128 else bytes([(n >> 8) | 0x80, n & 255])
    string_data = pool[strings_start:]
    addition = length(units) + length(len(encoded)) + encoded + b'\0'
    new_data = string_data + addition
    new_data += b'\0' * (-len(new_data) % 4)
    result = bytearray(pool[:header])
    result += pool[header:strings_start] + struct.pack('<I', len(string_data)) + new_data
    struct.pack_into('<I', result, 4, len(result))
    struct.pack_into('<I', result, 8, count + 1)
    struct.pack_into('<I', result, 16, flags & ~1)  # Appended pool is not sorted.
    struct.pack_into('<I', result, 20, strings_start + 4)
    return bytes(result), count


def updater_paths(table):
    """Add xml/inhouse_update_paths to this exact original APK's XML type."""
    if struct.unpack_from('<HHI', table)[:2] != (2, 12):
        raise ValueError('Unexpected resource table')
    top = list(chunks(table, 12, len(table)))
    if [c[1] for c in top] != [1, 0x200]:
        raise ValueError('Expected one global pool and original package')
    offset, _, _, size = top[0]
    global_pool, path_index = append_string(table[offset:offset+size], 'res/xml/inhouse_update_paths.xml')
    offset, _, header, size = top[1]
    package = table[offset:offset+size]
    if header != 288 or struct.unpack_from('<I', package, 8)[0] != 0x7f:
        raise ValueError('Unexpected original application package')
    key_offset = struct.unpack_from('<I', package, 276)[0]
    type_offset = struct.unpack_from('<I', package, 268)[0]
    output = bytearray(package[:header])
    entry_id = None
    changed_types = 0
    for start, kind, chunk_header, chunk_size in chunks(package, header, len(package)):
        chunk = bytearray(package[start:start+chunk_size])
        if start == type_offset:
            struct.pack_into('<I', output, 268, len(output))
        if start == key_offset:
            struct.pack_into('<I', output, 276, len(output))
            chunk, key_index = append_string(chunk, 'inhouse_update_paths')
        elif kind in (0x201, 0x202) and chunk[8] == 0x16:
            count = struct.unpack_from('<I', chunk, 12)[0]
            if count != 22 or chunk[9] != 0:
                raise ValueError('Original XML entries or offset encoding changed')
            entry_id = count
            if kind == 0x202:
                if chunk_header != 16:
                    raise ValueError('Unexpected XML type specification')
                chunk += struct.pack('<I', 0)
            else:
                changed_types += 1
                # The original XML type has only its default configuration.
                config_size = struct.unpack_from('<I', chunk, 20)[0]
                if any(chunk[24:20+config_size]):
                    raise ValueError('Unexpected qualified XML resource type')
                entries_start = struct.unpack_from('<I', chunk, 16)[0]
                if entries_start != chunk_header + count * 4:
                    raise ValueError('Unexpected XML entry offsets')
                values = chunk[entries_start:]
                entry = struct.pack('<HHIHBBI', 8, 0, key_index, 8, 0, 3, path_index)
                chunk = chunk[:entries_start] + struct.pack('<I', len(values)) + values + entry
                struct.pack_into('<I', chunk, 16, entries_start + 4)
            struct.pack_into('<I', chunk, 12, count + 1)
            struct.pack_into('<I', chunk, 4, len(chunk))
        output += chunk
    if changed_types != 1 or entry_id is None:
        raise ValueError('Original XML resource type not found')
    struct.pack_into('<I', output, 4, len(output))
    result = bytearray(table[:12]) + global_pool + output
    struct.pack_into('<I', result, 4, len(result))
    return bytes(result), 0x7f160000 | entry_id
