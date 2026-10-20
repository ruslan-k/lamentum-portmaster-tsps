#define _GNU_SOURCE
#include <assert.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include "lc2_hid_watch.h"
static void handler(int sig, siginfo_t *info, void *context) {
    (void)context;
    if (sig == SIGSEGV && lc2_hid_watch_fault((uintptr_t)info->si_addr, 0x1234)) return;
    _exit(99);
}
int main(void) {
    size_t page = lc2_hid_watch_page();
    unsigned char *p=mmap(NULL,3*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    assert(p!=MAP_FAILED);
    p[0]=17;p[page]=29;p[2*page]=43;
    struct sigaction sa={0};sa.sa_sigaction=handler;sa.sa_flags=SA_SIGINFO;
    sigemptyset(&sa.sa_mask);assert(sigaction(SIGSEGV,&sa,NULL)==0);
    assert(!lc2_hid_watch_arm((uintptr_t)p+1,3*page));
    assert(!lc2_hid_watch_arm((uintptr_t)p,0));
    assert(lc2_hid_watch_arm((uintptr_t)p,3*page));
    assert(!lc2_hid_watch_fault((uintptr_t)p-1,0));
    assert(!lc2_hid_watch_fault((uintptr_t)p+3*page,0));
    volatile unsigned char *v=p;
    assert(v[page]==29);assert(lc2_hid_watch_hits==1);
    assert(v[page]==29);assert(lc2_hid_watch_hits==1);
    /* Once restored, do not swallow another fault (e.g. a forbidden write). */
    assert(!lc2_hid_watch_fault((uintptr_t)p+page,0));
    assert(v[0]==17);assert(lc2_hid_watch_hits==2);
    assert(v[2*page]==43);assert(lc2_hid_watch_hits==3);
    assert(munmap(p,3*page)==0);
    puts("hid-watch: real SIGSEGV restore, per-page first access, bounds PASS");
    return 0;
}
