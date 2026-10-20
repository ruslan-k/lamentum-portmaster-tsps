#!/usr/bin/env python3
"""Read-only derivation of SDK10.9's PRIVATE accessor -> HID mapping.

Input: owner's image directory (sdk.text.seg). No game payload is emitted.
Requires capstone; refuses a different SDK hash. Prints offsets, not game bytes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import capstone

SDK_SHA256 = 'ff614dae42158f50ffd1e8c28f268fcf85a56dcc8a97c020d960ce2f6ea9d421'


def inspect(image):
    raw = (image / 'sdk.text.seg').read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SDK_SHA256:
        raise ValueError('SDK identity mismatch; rederive symbols for this SDK')
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    # Attach: x19 is accessor this, x20 is SharedMemoryFormat*.
    # Decode the straight-line ten stlr stores after IPC succeeds.
    regs = {'x19': ('accessor', 0), 'x20': ('shared', 0)}
    stores = []
    for i in md.disasm(raw[0x2083f8:0x2084bc], 0x2083f8):
        operands = [x.strip() for x in i.op_str.split(',')]
        if i.mnemonic == 'mov' and operands[0].startswith('w'):
            regs['x' + operands[0][1:]] = ('constant', int(operands[1][1:], 0))
        elif i.mnemonic == 'movk':
            reg = 'x' + operands[0][1:]
            shift = int(operands[2].split('#')[1], 0)
            regs[reg] = ('constant', regs[reg][1] | (int(operands[1][1:], 0) << shift))
        elif i.mnemonic == 'add':
            dst, base, offset = operands
            kind, value = regs[base]
            delta = int(offset[1:], 0) if offset.startswith('#') else regs[offset][1]
            regs[dst] = (kind, value + delta)
        elif i.mnemonic == 'stlr':
            src, address = operands
            kind, shared_offset = regs[src]
            dst_kind, private_offset = regs[address.strip('[]')]
            assert kind == 'shared' and dst_kind == 'accessor'
            stores.append({'sdk_pc': hex(i.address), 'private_accessor_offset': hex(private_offset),
                           'shared_memory_offset': hex(shared_offset)})
    assert len(stores) == 10
    for index, store in enumerate(stores):
        assert int(store['private_accessor_offset'], 16) == 0x18 + 8 * index
        assert int(store['shared_memory_offset'], 16) == 0x9a00 + 0x5000 * index
    return {'sdk_text_sha256': digest, 'attach_sdk_offset': '0x208370',
            'pointer_table_owner': 'private SDK accessor, NOT HID shared-memory head',
            'stores': stores}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    print(json.dumps(inspect(parser.parse_args().image), indent=2))
