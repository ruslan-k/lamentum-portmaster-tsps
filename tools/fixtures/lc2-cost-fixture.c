/* Self-authored CPU-only fixture; contains no game code/data or display/audio calls.
 * Exercise short-lived worker tails and nested work, then use the runtime's _exit path. */
#define _GNU_SOURCE
#include <stdio.h>
#include <pthread.h>
#include <assert.h>
#include "lc2_cost.h"
static void *worker(void *argument) {
    (void)argument;
    for(unsigned i=0;i<3;i++) {
        uint64_t parent=lc2_cost_enter(LC2_COST_WAIT);
        uint64_t child=lc2_cost_enter(LC2_COST_BC_DECODE);
        volatile uint64_t value=1;
        for(unsigned n=0;n<10000;n++)value=value*33+n;
        (void)value;
        lc2_cost_leave(LC2_COST_BC_DECODE,child);
        struct timespec delay={0,10000000};nanosleep(&delay,NULL);
        lc2_cost_leave(LC2_COST_WAIT,parent);
    }
    uint64_t token=lc2_cost_enter(LC2_COST_RELEASE);
    lc2_cost_leave(LC2_COST_RELEASE,token);
    return NULL;
}
int main(void) {
    alarm(8);
    struct timespec cpu,wall;
    assert(!clock_getres(CLOCK_THREAD_CPUTIME_ID,&cpu));
    assert(!clock_getres(CLOCK_MONOTONIC_RAW,&wall));
    dprintf(STDOUT_FILENO,"LC2_COST_FIXTURE_CLOCK fixture_pid=%ld cpu_resolution_ns=%lu wall_resolution_ns=%lu\n",
            (long)getpid(),(unsigned long)cpu.tv_nsec,(unsigned long)wall.tv_nsec);
    pthread_t threads[4];
    for(unsigned i=0;i<4;i++)assert(!pthread_create(&threads[i],NULL,worker,NULL));
    for(unsigned i=0;i<4;i++)assert(!pthread_join(threads[i],NULL));
    /* Retired TLS cannot flush itself here: this must use the bounded registry. */
    lc2_cost_report_fd(STDOUT_FILENO);
    _exit(0);
}
