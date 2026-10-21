/* Self-authored G0 host fixture. No GL, game content or device state.
 * Input: target internalformat width height depth layers levels realized-samples.
 * JSON output is format-defined payload, never GPU physical residency.
 */
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include "lc2_gl_storage.h"
int main(void) {
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
