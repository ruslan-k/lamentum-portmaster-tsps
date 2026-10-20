#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define LC2_MAIN_BASE UINT64_C(0x8005000)
struct line {unsigned used;};
typedef struct {struct {uint64_t regs[31],sp,pc;} uc_mcontext;} ucontext_t;
static uintptr_t low,high;
static unsigned events;
static int accessible(uint64_t p,uint64_t n,unsigned permission) {
    (void)permission;return p>=low && p<=high && n<=high-p;
}
static void stop(const char *s,uint64_t pc,uint64_t v,int code) {
    (void)pc;(void)v;(void)code;fprintf(stderr,"unexpected stop %s\n",s);abort();
}
static void text(struct line *l,const char *s) {(void)l;(void)s;}
static void hex(struct line *l,uint64_t n) {(void)l;(void)n;}
static void location(struct line *l,uint64_t n) {(void)l;(void)n;}
static void emit(struct line *l) {(void)l;events++;}
static void trace_frames(ucontext_t *c) {(void)c;}
#define PROT_READ 1
#define PROT_WRITE 2
#include "lc2_menu_trace.h"
int main(void) {
    unsigned char stack[1024];low=(uintptr_t)stack;high=low+sizeof stack;
    assert(setenv("LC2_MENU_TRACE","0",1)==0);lc2_menu_trace_configure();
    assert(lc2_menu_site(LC2_MAIN_BASE+0x16cb4c0)==-1);
    assert(setenv("LC2_MENU_TRACE","1",1)==0);lc2_menu_trace_configure();
    for(unsigned i=0;i<5;i++) {
        memset(stack,0,sizeof stack);ucontext_t ctx={0};
        for(unsigned r=0;r<31;r++)ctx.uc_mcontext.regs[r]=0x123000+r;
        ctx.uc_mcontext.regs[30]=LC2_MAIN_BASE+0x16cb670;
        uint64_t sp=low+512,pc=LC2_MAIN_BASE+lc2_menu_sites[i].offset;
        ctx.uc_mcontext.sp=sp;ctx.uc_mcontext.pc=pc;
        assert(lc2_menu_trace_entry(pc,lc2_menu_sites[i].opcode));
        assert(lc2_menu_trace_handle(pc,lc2_menu_sites[i].opcode,&ctx));
        assert(ctx.uc_mcontext.pc==pc+4);
        if(i==0 || i==1)assert(ctx.uc_mcontext.sp==sp-(i==0?0x80:0xb0));
        else if(i==2) {
            assert(ctx.uc_mcontext.sp==sp-0x30);
            uint64_t value;memcpy(&value,(void *)(uintptr_t)(sp-0x30),8);assert(value==0x123015);
        } else {
            assert(ctx.uc_mcontext.sp==sp-16);uint64_t pair[2];
            memcpy(pair,(void *)(uintptr_t)(sp-16),16);
            assert(pair[0]==0x12301d && pair[1]==ctx.uc_mcontext.regs[30]);
        }
        for(unsigned r=0;r<30;r++)assert(ctx.uc_mcontext.regs[r]==0x123000+r);
    }
    assert(events==5);
    assert(!lc2_menu_trace_entry(LC2_MAIN_BASE+4,0));
    puts("menu-trace: all five original prologues replayed, registers preserved, off=0 PASS");
}
