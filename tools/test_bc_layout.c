#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "zero_bc_layout.h"
#include "zero_bc.h"
int main(void) {
    struct zero_bc_level m;
    assert(zero_bc_level_layout(8192,4096,16,0,&m));
    assert(m.size==33554432 && m.blocks_x==2048 && m.blocks_y==1024);
    unsigned char *seen=calloc(m.size/16,1);assert(seen);
    size_t checked=0;
    for(unsigned y=0;y<m.blocks_y;y++)for(unsigned x=0;x<m.blocks_x;x++) {
        size_t address=zero_bc_block_address(&m,x,y);
        assert(address%16==0 && address+16<=m.size);
        assert(!seen[address/16]);seen[address/16]=1;checked++;
    }
    free(seen);
    assert(zero_bc_level_layout(8192,8192,16,13,&m));
    assert(m.width==1 && m.height==1);
    assert(!zero_bc_level_layout(8192,8192,16,14,&m));
    assert(!zero_bc_level_layout(16384,4096,16,0,&m));
    /* Synthetic BC3 input: compare full decode with 128-row tiled slices. */
    const unsigned w=8192,h=132;
    assert(zero_bc_level_layout(w,h,16,0,&m));
    size_t linear_bytes=(size_t)(w/4)*(h/4)*16,rgba_bytes=(size_t)w*h*4;
    unsigned char *linear=malloc(linear_bytes),*tiled=calloc(m.size,1);
    unsigned char *full=malloc(rgba_bytes),*striped=malloc(rgba_bytes);
    assert(linear&&tiled&&full&&striped);
    for(size_t k=0;k<linear_bytes;k++)linear[k]=(unsigned char)(k*37+k/19);
    assert(zero_bc_blocks_copy(&m,tiled,m.size,linear,linear_bytes,0,0,w/4,h/4,1));
    assert(zero_bc_decode(0x44,full,rgba_bytes,linear,linear_bytes,w,h,w/4*16));
    for(unsigned y=0;y<h;y+=128) {
        unsigned rows=h-y;if(rows>128)rows=128;
        size_t n=(size_t)(w/4)*(rows/4)*16;
        assert(zero_bc_blocks_copy(&m,tiled,m.size,linear,n,0,y/4,w/4,rows/4,0));
        assert(zero_bc_decode(0x44,striped+(size_t)y*w*4,(size_t)rows*w*4,linear,n,w,rows,w/4*16));
    }
    assert(memcmp(full,striped,rgba_bytes)==0);
    free(linear);free(tiled);free(full);free(striped);
    printf("BC3 8192x4096: %zu unique in-range blocks; mip13, guards and stripe equivalence OK\n",checked);
    return 0;
}
