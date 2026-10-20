#define _GNU_SOURCE
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include "lc2_fileback.h"
int main(void) {
    const size_t size=16384;
    unsigned char *memory=mmap(NULL,size,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    assert(memory!=MAP_FAILED);
    unsigned char original[16384];
    for(size_t i=0;i<size;i++)original[i]=(unsigned char)(i*37+i/11);
    memcpy(memory,original,size);
    const char *temporary=getenv("TMPDIR");if(!temporary || !*temporary)temporary=".";
    char path[1024];snprintf(path,sizeof(path),"%s/lamentum-test-XXXXXX",temporary);
    int fd=mkstemp(path);assert(fd>=0);unlink(path);
    uint64_t cursor=0;
    assert(mprotect(memory+4096,4096,PROT_NONE)==0);
    errno=0;
    assert(lc2_fileback_snapshot(fd,&cursor,memory+17,12288,8192)==-1 && errno==EFAULT && cursor==0);
    assert(mprotect(memory+4096,4096,PROT_READ|PROT_WRITE)==0);
    assert(lc2_fileback_snapshot(fd,&cursor,memory+17,12288,8192)==8192);
    assert(cursor==8192);
    assert(lc2_fileback_overlaps((uintptr_t)memory+4096,4096));
    assert(!lc2_fileback_overlaps((uintptr_t)memory,4096));
    assert(!lc2_fileback_overlaps((uintptr_t)memory+12288,4096));
    assert(memcmp(memory,original,size)==0);
    unsigned char saved[8192];assert(pread(fd,saved,sizeof(saved),0)==sizeof(saved));
    assert(memcmp(saved,original+4096,sizeof(saved))==0);
    memory[5000]^=0xff;
    unsigned char value=0;assert(pread(fd,&value,1,904)==1);
    assert(value==original[5000]);
    assert(memory[5000]!=(unsigned char)original[5000]);
    assert(lc2_fileback_snapshot(fd,&cursor,memory,size,8192)==0);
    snprintf(path,sizeof(path),"%s/lamentum-test-XXXXXX",temporary);
    int extra=mkstemp(path);assert(extra>=0);assert(unlink(path)==0);
    uint64_t extra_cursor=0;
    assert(lc2_fileback_snapshot(extra,&extra_cursor,memory,4096,4096)==4096);
    assert(extra_cursor==4096 && cursor==8192 && memcmp(memory,original,4096)==0);
    assert(pread(extra,&value,1,0)==1 && value==original[0]);
    assert(pread(fd,&value,1,904)==1 && value==original[5000]);
    close(extra);close(fd);munmap(memory,size);
    puts("fileback: exact bytes, unaligned tails, COW independence and capacity guard OK");
    return 0;
}
