#include <assert.h>
#include <stdio.h>
#include "lc2_cbuf_units.h"
int main(void) {
    assert(lc2_cbuf_unit(16,2,0,0)==15);
    assert(lc2_cbuf_unit(16,2,0,1)==14);
    assert(lc2_cbuf_unit(16,2,0,2)==13);
    assert(lc2_cbuf_unit(16,14,0,2)==-1);
    assert(lc2_cbuf_unit(16,2,3,0)==12);
    assert(lc2_cbuf_unit(16,13,3,0)==-1);
    assert(lc2_cbuf_unit(0,0,0,0)==-1);
    assert(lc2_cbuf_unit(16,0,16,0)==-1);
    unsigned used=0;
    for(unsigned i=0;i<14;i++) {int unit=lc2_cbuf_unit(16,2,0,i);assert(unit>=2&&unit<16);assert(!(used&(1U<<unit)));used|=1U<<unit;}
    assert(lc2_cbuf_unit(16,2,0,14)==-1);
    puts("cbuf units: distinct buffers, low/high reservations and exhaustion OK");
}
