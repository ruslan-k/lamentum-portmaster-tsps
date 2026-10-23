#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "zero_bc_layout.h"
#include "zero_bc.h"
static void check_bc3_stripe(unsigned w,unsigned h) {
    struct zero_bc_level m;assert(zero_bc_level_layout(w,h,16,0,&m));
    size_t blocks=(size_t)m.blocks_x*m.blocks_y*16,pixels=(size_t)w*h*4;
    unsigned char *linear_source=malloc(blocks),*tiled=calloc(m.size,1),*linear_full=malloc(blocks);
    unsigned char *full=malloc(pixels),*striped=malloc(pixels);
    assert(linear_source&&tiled&&linear_full&&full&&striped);
    for(size_t i=0;i<blocks;i++)linear_source[i]=(unsigned char)(i*53+i/29);
    assert(zero_bc_blocks_copy(&m,tiled,m.size,linear_source,blocks,0,0,m.blocks_x,m.blocks_y,1));
    assert(zero_bc_blocks_copy(&m,tiled,m.size,linear_full,blocks,0,0,m.blocks_x,m.blocks_y,0));
    assert(zero_bc_decode(0x44,full,pixels,linear_full,blocks,w,h,(size_t)m.blocks_x*16));
    for(unsigned y=0;y<h;y+=128) {
        unsigned rows=h-y;if(rows>128)rows=128;
        size_t row_blocks=(size_t)m.blocks_x*((rows+3)/4),row_bytes=row_blocks*16;
        unsigned char *linear=malloc(row_bytes);assert(linear);
        assert(zero_bc_blocks_copy(&m,tiled,m.size,linear,row_bytes,0,y/4,m.blocks_x,(rows+3)/4,0));
        assert(zero_bc_decode(0x44,striped+(size_t)y*w*4,(size_t)rows*w*4,
                              linear,row_bytes,w,rows,(size_t)m.blocks_x*16));
        free(linear);
    }
    assert(memcmp(full,striped,pixels)==0);
    free(linear_source);free(tiled);free(linear_full);free(full);free(striped);
}
static void check_inplace(unsigned format,unsigned width,unsigned height,unsigned seed) {
    struct zero_bc_level m;unsigned block_bytes=zero_bc_bytes(format);
    assert(zero_bc_level_layout(width,height,block_bytes,0,&m));
    size_t compressed=(size_t)m.blocks_x*m.blocks_y*block_bytes;
    size_t stride=(size_t)m.blocks_x*block_bytes;
    size_t bpp=zero_bc_float(format)?16:4;
    size_t rgba=(size_t)width*height*bpp;
    size_t capacity=compressed>rgba?compressed:rgba;
    unsigned char *source=malloc(compressed),*reference=malloc(rgba),*work=malloc(capacity+32);
    unsigned char *tiled=calloc(m.size,1);
    assert(source&&reference&&work&&tiled);
    for(size_t i=0;i<compressed;i++)source[i]=(unsigned char)(i*37U+(i>>8)+seed);
    assert(zero_bc_decode(format,reference,rgba,source,compressed,width,height,stride));
    assert(zero_bc_blocks_copy(&m,tiled,m.size,source,compressed,0,0,m.blocks_x,m.blocks_y,1));
    memset(work,0xa5,capacity+32);
    assert(zero_bc_blocks_copy(&m,tiled,m.size,work,capacity,0,0,m.blocks_x,m.blocks_y,0));
    assert(zero_bc_decode_in_place(format,work,capacity,width,height,stride));
    assert(memcmp(reference,work,rgba)==0);
    for(size_t i=capacity;i<capacity+32;i++)assert(work[i]==0xa5);
    memcpy(work,source,compressed);
    assert(!zero_bc_decode_in_place(format,work,capacity-1,width,height,stride));
    assert(!zero_bc_decode_in_place(format,work,capacity,width,height,stride+block_bytes));
    assert(memcmp(work,source,compressed)==0);
    free(source);free(reference);free(work);free(tiled);
}
int main(void) {
    assert(zero_bc_should_stripe(16,4097,0,0));
    assert(!zero_bc_should_stripe(16,4096,0,0));
    assert(zero_bc_should_stripe(16,1920,0,1));
    assert(!zero_bc_should_stripe(16,768,0,1));
    assert(!zero_bc_should_stripe(16,1920,1,1));
    assert(!zero_bc_should_stripe(0,1920,0,1));
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
    unsigned char *staging=malloc(linear_bytes),*reference=calloc(m.size,1);
    assert(staging&&reference);memcpy(staging,linear,linear_bytes);
    assert(zero_bc_blocks_copy(&m,reference,m.size,staging,linear_bytes,0,0,w/4,h/4,1));
    assert(memcmp(reference,tiled,m.size)==0 && memcmp(staging,linear,linear_bytes)==0);
    free(reference);free(staging);
    assert(zero_bc_decode(0x44,full,rgba_bytes,linear,linear_bytes,w,h,w/4*16));
    for(unsigned y=0;y<h;y+=128) {
        unsigned rows=h-y;if(rows>128)rows=128;
        size_t n=(size_t)(w/4)*(rows/4)*16;
        assert(zero_bc_blocks_copy(&m,tiled,m.size,linear,n,0,y/4,w/4,rows/4,0));
        assert(zero_bc_decode(0x44,striped+(size_t)y*w*4,(size_t)rows*w*4,linear,n,w,rows,w/4*16));
    }
    assert(memcmp(full,striped,rgba_bytes)==0);
    free(linear);free(tiled);free(full);free(striped);
    check_bc3_stripe(1920,1080);
    for(unsigned format=0x41;format<=0x50;format++)check_inplace(format,7,5,format);
    check_inplace(0x44,3600,2160,81);
    check_inplace(0x44,3600,3600,92);
    printf("in-place equivalence OK\n");
    printf("BC3 layout and 8192x132/1920x1080 stripe equivalence OK blocks=%zu\n",checked);
    return 0;
}
