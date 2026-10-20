#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "lc2_hid109.h"

struct sample { uint64_t number, buttons; int32_t lx, ly, rx, ry; uint32_t attributes, reserved; };

int main(void) {
    uint8_t block[LC2_HID109_BLOCK_STRIDE];
    memset(block, 0, sizeof block);
    struct sample s = {7, 0x2, 100, -100, 0, 0, 1, 0};
    _Static_assert(sizeof s == LC2_HID109_SAMPLE, "sample ABI");

    unsigned tail = lc2_hid109_publish(block, 11, &s, sizeof s);
    assert(tail == 1);
    uint64_t v = 0;
    memcpy(&v, block + LC2_HID109_TAIL, 8); assert(v == 1);
    memcpy(&v, block + LC2_HID109_COUNT, 8); assert(v == 1);
    const uint8_t *slot = block + LC2_HID109_RING + tail * LC2_HID109_SLOT;
    memcpy(&v, slot, 8); assert(v == 11);
    struct sample got; memcpy(&got, slot + 8, sizeof got);
    assert(got.number == 7 && got.buttons == 0x2 && got.lx == 100 && got.ly == -100);
    assert(got.attributes == 1 && got.reserved == 0);

    for (unsigned i = 0; i < 16; i++) tail = lc2_hid109_publish(block, 12 + i, &s, sizeof s);
    assert(tail == 0);
    memcpy(&v, block + LC2_HID109_COUNT, 8); assert(v == LC2_HID109_SLOTS);
    memcpy(&v, block + LC2_HID109_RING, 8); assert(v == 27);

    assert(LC2_HID109_RING + LC2_HID109_SLOTS * LC2_HID109_SLOT <= LC2_HID109_BLOCK_STRIDE);
    assert(lc2_hid109_block_offset(0) == 0x1000);
    assert(lc2_hid109_block_offset(9) == 0x3400);
    assert(lc2_hid109_block_offset(9) + LC2_HID109_BLOCK_STRIDE <= 0x9a00);
    puts("hid109: slot layout, wrap, saturation and block bounds OK");
}
