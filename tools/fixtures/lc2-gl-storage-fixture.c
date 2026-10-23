/* Self-authored G0 host fixture. No GL, game content or device state.
 * Input: target internalformat width height depth layers levels realized-samples.
 * JSON output is format-defined payload, never GPU physical residency.
 */
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include "lc2_gl_storage.h"
static void admission_contract(void) {
    uint32_t resolved=123;
    assert(lc2_gl_storage_resolve_upload(0x1908,0x1908,0x1401,&resolved)==LC2_GL_STORAGE_OK && resolved==0x8058);
    assert(lc2_gl_storage_resolve_upload(0x1908,0x1908,0x1406,&resolved)==LC2_GL_STORAGE_OK && resolved==0x8814);
    resolved=123;
    assert(lc2_gl_storage_resolve_upload(0x1909,0x1909,0x1401,&resolved)==LC2_GL_STORAGE_OK && resolved==0x8229);
    assert(lc2_gl_storage_resolve_upload(0x190a,0x190a,0x1401,&resolved)==LC2_GL_STORAGE_OK && resolved==0x822b);
    assert(lc2_gl_storage_resolve_upload(0x8c42,0x1908,0x1401,&resolved)==LC2_GL_STORAGE_OK && resolved==0x8c43);
    assert(lc2_gl_storage_resolve_upload(0x1908,0x1908,0x8d61,&resolved)==LC2_GL_STORAGE_OK && resolved==0x881a);
    resolved=123;
    assert(lc2_gl_storage_resolve_upload(0x1908,0x1908,0xdead,&resolved)==LC2_GL_STORAGE_FORMAT && resolved==123);
    struct lc2_gl_storage_desc depth={0x8d41,0x81a6,3,2,1,1,1,1};
    struct lc2_gl_storage_layout depth_plan;
    assert(lc2_gl_storage_calculate(&depth,&depth_plan)==LC2_GL_STORAGE_OK && depth_plan.bytes==24);
    struct lc2_gl_admission_result out={0};
    unsigned status=lc2_gl_storage_admission(8ULL<<20,2ULL<<20,4,112ULL*1024,14ULL*1024,96,&out);
    assert(status==LC2_GL_ADMISSION_OK);
    assert(out.required_available_bytes==110ULL<<20 && out.required_cma_bytes==14ULL<<20);
    status=lc2_gl_storage_admission(8ULL<<20,2ULL<<20,4,112ULL*1024,13ULL*1024,96,&out);
    assert(status==LC2_GL_ADMISSION_CMAFREE);
    status=lc2_gl_storage_admission(8ULL<<20,2ULL<<20,4,109ULL*1024,14ULL*1024,96,&out);
    assert(status==LC2_GL_ADMISSION_MEMAVAILABLE);
    status=lc2_gl_storage_admission(8ULL<<20,2ULL<<20,4,109ULL*1024,13ULL*1024,96,&out);
    assert((status&(LC2_GL_ADMISSION_MEMAVAILABLE|LC2_GL_ADMISSION_CMAFREE))==
           (LC2_GL_ADMISSION_MEMAVAILABLE|LC2_GL_ADMISSION_CMAFREE));
    struct lc2_gl_admission_result unchanged=out;
    status=lc2_gl_storage_admission(UINT64_MAX,1,4,UINT64_MAX,UINT64_MAX,96,&out);
    assert(status==LC2_GL_ADMISSION_OVERFLOW);
    assert(!memcmp(&unchanged,&out,sizeof(out)));
    assert(lc2_gl_storage_admission(1,1,1,1,1,1,NULL)==LC2_GL_ADMISSION_INVALID);
}
int main(int argc,char **argv) {
    if(argc==2 && !strcmp(argv[1],"--admission-contract")){admission_contract();return 0;}
    struct lc2_gl_storage_desc d;
    int count;
    while((count=scanf("%"SCNu32" %"SCNu32" %"SCNu32" %"SCNu32" %"SCNu32" %"SCNu32" %"SCNu32" %"SCNu32,
            &d.target,&d.internal_format,&d.width,&d.height,&d.depth,&d.layers,&d.levels,&d.samples))!=EOF) {
        if(count!=8)return 2;
        struct lc2_gl_storage_layout plan,before;
        memset(&plan,0xa5,sizeof(plan));memcpy(&before,&plan,sizeof(plan));
        enum lc2_gl_storage_status status=lc2_gl_storage_calculate(&d,&plan);
        if(status!=LC2_GL_STORAGE_OK) {
            assert(!memcmp(&before,&plan,sizeof(plan)));
            printf("{\"status\":\"%s\",\"output_unchanged\":true}\n",
                status==LC2_GL_STORAGE_FORMAT?"format":status==LC2_GL_STORAGE_DESCRIPTOR?"descriptor":"overflow");
            continue;
        }
        printf("{\"status\":\"ok\",\"bytes\":%"PRIu64",\"levels\":[",plan.bytes);
        for(unsigned i=0;i<plan.levels;i++) {
            const struct lc2_gl_storage_level *p=&plan.level[i];
            printf("%s{\"width\":%u,\"height\":%u,\"depth\":%u,\"slices\":%"PRIu64
                   ",\"offset\":%"PRIu64",\"bytes\":%"PRIu64"}",
                   i?",":"",p->width,p->height,p->depth,p->slices,p->offset,p->bytes);
        }
        puts("]}");
    }
    return 0;
}
