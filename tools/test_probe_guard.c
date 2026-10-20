#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "lc2_probe_guard.h"
int main(void) {
    assert(lc2_probe_guard(160,0)==1);
    assert(lc2_probe_guard(156,0x80000000U)==1);
    assert(lc2_probe_guard(160,0x40000000U)==1);
    assert(lc2_probe_guard(160,0x7fc01234U)==1);
    assert(lc2_probe_guard(160,0x3f800000U)==0);
    assert(lc2_probe_guard(155,0)==-1);
    puts("probe guard: disabled/enabled, NaN, signed zero and short cbuf OK");
}
