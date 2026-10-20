#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "lc2_guest_quota.h"
int main(void) {
    uint64_t bytes=0;
    assert(lc2_guest_quota_parse(NULL,&bytes)==0 && bytes==(1536ULL<<20));
    assert(lc2_guest_quota_parse("2048",&bytes)==0 && bytes==(2048ULL<<20));
    assert(lc2_guest_quota_parse("3072",&bytes)==0 && bytes==(3072ULL<<20));
    const char *bad[]={"","0","1535","3073","-1","3072x","99999999999999999999999"};
    for(unsigned i=0;i<sizeof(bad)/sizeof(*bad);i++) {
        bytes=123;assert(lc2_guest_quota_parse(bad[i],&bytes)<0 && bytes==123);
    }
    puts("guest quota: default, bounded virtual budgets and invalid inputs OK");
}
