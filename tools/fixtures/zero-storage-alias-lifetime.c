#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lc2_life_events.h"

typedef int GLint;
struct nvn_pool;
struct nvn_texture_builder {
    uint64_t device,pool,offset,packaged;
    uint32_t flags,target,width,height,depth,levels,samples,format,depth_mode,stride,packaged_layout,gl_name,swizzle[4];
};
struct zero_texture_storage;
struct nvn_pool {uint32_t flags;uint64_t object,address,size;unsigned live,retired;};
struct nvn_texture {
    struct nvn_texture_builder b;uint64_t size;struct nvn_pool *pool;
    unsigned host_scaled,host_width,host_height;uint64_t levels[14];
    unsigned host_half,packaged_lazy,host_upload_type,zero_backend_deferred,normal_guarded,normal_unmaterialized;
    struct zero_texture_storage *zero_storage;unsigned name,depth_buffer;uint64_t id,object;unsigned live;
};
static struct nvn_texture nvn_textures[4096];
static const char nvn_caller[]="fixture";
static uint64_t nvn_gl_share_group_id(void){return 1;}
static void stop(const char *why,const char *caller,uint64_t value,unsigned code){
    (void)why;(void)caller;(void)value;(void)code;abort();
}
#include "zero_texture_storage.h"

static void init_texture(struct nvn_texture *t,struct nvn_pool *p,uint64_t id,
        unsigned format,unsigned name,unsigned depth,uint64_t offset) {
    memset(t,0,sizeof(*t));t->id=id;t->object=id;t->pool=p;t->size=UINT64_C(0x384000);
    t->host_scaled=1;t->host_width=640;t->host_height=360;t->name=name;t->depth_buffer=depth;
    t->b.device=7;t->b.pool=p->object;t->b.offset=offset;t->b.flags=8;t->b.target=1;
    t->b.width=1280;t->b.height=720;t->b.depth=1;t->b.levels=1;t->b.samples=0;
    t->b.format=format;t->b.depth_mode=0;t->b.swizzle[0]=2;t->b.swizzle[1]=3;
    t->b.swizzle[2]=4;t->b.swizzle[3]=5;
}

static void record_storage(uint64_t id,unsigned name,unsigned kind) {
    struct lc2_life_storage_key key={.share_group=1,.name=name,.kind=kind,
        .target=kind==1?0x0de1:0x8d41};
    lc2_life_events_storage_key(id,&key,64);
}

int main(void) {
    setenv("LC2_LIFE_EVENTS","1",1);
    struct nvn_pool pool={.flags=0xa4,.object=9,.address=0x20000000,.size=0x800000,.live=1};
    struct nvn_texture *owner=&nvn_textures[0];
    init_texture(owner,&pool,100,0x25,101,0,0);record_storage(100,101,1);
    zero_texture_storage_publish(owner);owner->live=1;
    struct lc2_life_event *texture=lc2_life_event_find_group(1,101,1,1);
    assert(texture && owner->zero_storage->gl_generation==texture->generation);
    struct nvn_texture view;init_texture(&view,&pool,102,0x25,0,0,0);
    assert(zero_texture_storage_join(&view));
    assert(texture->alias_views==1 && lc2_life_events_state()->alias_views==1);
    assert(zero_texture_storage_release(&view)==0);
    assert(texture->alias_views==0 && lc2_life_events_state()->alias_views==0);

    struct nvn_texture *depth_owner=&nvn_textures[1];
    init_texture(depth_owner,&pool,200,0x35,0,202,0x400000);record_storage(200,202,2);
    zero_texture_storage_publish(depth_owner);depth_owner->live=1;
    struct lc2_life_event *renderbuffer=lc2_life_event_find_group(1,202,2,1);
    assert(renderbuffer && depth_owner->zero_storage->gl_generation==renderbuffer->generation);
    struct nvn_texture depth_view;init_texture(&depth_view,&pool,201,0x35,0,0,0x400000);
    assert(zero_texture_storage_join(&depth_view));
    assert(renderbuffer->alias_views==1 && lc2_life_events_state()->alias_views==1);
    assert(zero_texture_storage_release(&depth_view)==0);
    assert(renderbuffer->alias_views==0 && lc2_life_events_state()->alias_views==0);
    return 0;
}
