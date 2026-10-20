#!/usr/bin/env python3
"""Read-only IL2CPP24.2 type/token -> owner NSO method mapping.

Uses Il2CppDumper MetadataClass.cs's public structure descriptions, not a
borrowed game's addresses. Emits names/offsets, never native code or game data.
Requires the owner's metadata, image segments, and inspect_nso JSON report.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path
import capstone


def inspect(metadata, image, report, type_name):
    raw = metadata.read_bytes()
    if struct.unpack_from('<II', raw) != (0xfab11baf, 24):
        raise ValueError('requires metadata version24; derive another schema separately')
    def section(header):
        offset, size = struct.unpack_from('<II', raw, header)
        if offset + size > len(raw):
            raise ValueError('metadata section out of bounds')
        return offset, size
    strings, string_size = section(24)
    types, type_size = section(160)
    methods, method_size = section(48)
    fields, field_size = section(96)
    images, image_size = section(168)
    if type_size % 92 or method_size % 32 or field_size % 12 or image_size % 40:
        raise ValueError('not the supported 24.2 structure layout')
    def name(index):
        if index >= string_size:
            raise ValueError('invalid metadata string offset')
        start = strings + index
        return raw[start:raw.index(b'\0', start, strings + string_size)].decode('utf8')
    td = [struct.unpack_from('<17I8H2I', raw, types + i) for i in range(0, type_size, 92)]
    for row in td:
        name(row[0])
        if row[-1] >> 24 != 2:
            raise ValueError('type token mismatch; metadata subversion is not proven')
    md = [struct.unpack_from('<6I4H', raw, methods + i) for i in range(0, method_size, 32)]
    for row in md:
        name(row[0])
        if row[5] >> 24 != 6 or row[1] >= len(td):
            raise ValueError('method token/type mismatch')
    found = [i for i, row in enumerate(td) if name(row[0]) == type_name]
    if len(found) != 1:
        raise ValueError('type must match exactly once')
    ti = found[0]
    im = [struct.unpack_from('<10I', raw, images + i) for i in range(0, image_size, 40)]
    owner = [r for r in im if r[2] <= ti < r[2] + r[3]]
    if len(owner) != 1:
        raise ValueError('type image ambiguous')
    assembly = name(owner[0][0])
    ns = json.loads(report.read_text())
    segments = []
    for s in ns['segments']:
        data = (image / ('main.' + s['name'] + '.seg')).read_bytes()
        if hashlib.sha256(data[:s['size']]).hexdigest() != s['sha256']:
            raise ValueError('main segment identity mismatch')
        segments.append((s['address'], data))
    def read(address, size):
        for start, data in segments:
            if start <= address and address + size <= start + len(data):
                return data[address-start:address-start+size]
        raise ValueError('unmapped NSO read')
    def u64(address):
        return struct.unpack('<Q', read(address, 8))[0]
    reloc = {r['target']: r for r in ns['relocations'] if r['type'] == 1027}
    def module(assembly_name):
        needle = assembly_name.encode() + b'\0'
        string_addresses = set()
        for start, data in segments:
            pos = 0
            while (pos := data.find(needle, pos)) >= 0:
                string_addresses.add(start + pos)
                pos += len(needle)
        matches = []
        for r in reloc.values():
            if r['addend'] in string_addresses:
                address = r['target']
                count = u64(address + 8)
                table = u64(address + 16)
                if 0 < count <= len(md) and address + 16 in reloc:
                    read(table, count * 8)
                    matches.append((address, count, table))
        if len(matches) != 1:
            raise ValueError('codegen module match is not unique: ' + assembly_name)
        return matches[0]
    modules = {}
    address_names = {}
    # Build cross-assembly direct-call names from each image's token-indexed table.
    for row in im:
        asm = name(row[0])
        try:
            mod = module(asm)
        except ValueError:
            continue
        modules[asm] = mod
        for type_index in range(row[2], row[2] + row[3]):
            typ = td[type_index]
            for method_index in range(typ[10], typ[10] + typ[17]):
                method = md[method_index]
                slot = (method[5] & 0xffffff) - 1
                if not 0 <= slot < mod[1]:
                    raise ValueError('token exceeds module method table')
                pointer = u64(mod[2] + 8 * slot)
                if pointer:
                    address_names.setdefault(pointer, []).append(name(typ[0]) + '.' + name(method[0]))
    mod = modules[assembly]
    # MetadataRegistration has adjacent fieldOffsetsCount and
    # typeDefinitionsSizesCount pairs, both equal to the metadata type count.
    # Require unique, relocated tables; never infer native offsets by field order.
    offset_tables = []
    needle = struct.pack('<Q', len(td))
    for start, data in segments:
        pos = 0
        while (pos := data.find(needle, pos)) >= 0:
            at = start + pos
            pos += 8
            if at % 8 or at + 8 not in reloc or at + 24 not in reloc:
                continue
            if u64(at + 16) == len(td):
                table = u64(at + 8)
                read(table, 8 * len(td))
                offset_tables.append(table)
    if len(offset_tables) != 1:
        raise ValueError('field-offset registration is not unique')
    field_offsets_pointer = u64(offset_tables[0] + ti * 8)
    field_offsets = struct.unpack('<' + str(td[ti][19]) + 'i',
                                  read(field_offsets_pointer, td[ti][19] * 4))
    field_names = [name(struct.unpack_from('<I', raw, fields + 12*i)[0])
                   for i in range(td[ti][9], td[ti][9] + td[ti][19])]
    rows = []
    decoder = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    for method_index in range(td[ti][10], td[ti][10] + td[ti][17]):
        method = md[method_index]
        address = u64(mod[2] + 8 * ((method[5] & 0xffffff) - 1))
        row = {'name': name(method[0]), 'token': hex(method[5]), 'main_offset': hex(address)}
        if name(method[0]) == 'Start' and address:
            end = min(a for a in address_names if a > address)
            calls = []
            for ins in decoder.disasm(read(address, end - address), address):
                if ins.mnemonic == 'bl':
                    target = int(ins.op_str.lstrip('#'), 0)
                    calls.append({'site': hex(ins.address), 'target': hex(target),
                                  'names': address_names.get(target, [])})
            row['direct_calls'] = calls
        rows.append(row)
    return {'metadata_sha256': hashlib.sha256(raw).hexdigest(), 'main_nso_sha256': ns['sha256'],
            'type': type_name, 'type_definition_index': ti, 'assembly': assembly,
            'codegen_module_main_offset': hex(mod[0]), 'method_pointer_count': mod[1],
            'methods': rows,
            'fields': field_names,
            'field_offsets_table_main_offset': hex(offset_tables[0]),
            'field_offsets_pointer_main_offset': hex(field_offsets_pointer),
            'field_offsets': [{'name': n, 'offset': hex(o)} for n, o in zip(field_names, field_offsets)],
            'limitations': 'Static call mapping only. Does not prove live execution or an exception.'}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('metadata', type=Path)
    ap.add_argument('image', type=Path)
    ap.add_argument('report', type=Path)
    ap.add_argument('--type', default='ManagerMenuPrincipal')
    args = ap.parse_args()
    print(json.dumps(inspect(args.metadata, args.image, args.report, args.type), indent=2))
