"""Compile+run the observation-ledger contract extracted from the public overlay."""
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

from gl_allocation_inventory import source_tree_identity

ROOT = pathlib.Path(__file__).resolve().parents[1]
MARKER = 'diff --git a/native/lc2_life_events.h b/native/lc2_life_events.h'

FIXTURE = r'''
#define LC2_LIFE_BUDGET_EVENT_CAP 3
#include "lc2_life_events.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <unistd.h>
static struct lc2_life_texture_pair test_pair(const char *phase,uint64_t id,uint64_t owner,
        unsigned texture,unsigned renderbuffer) {
 return (struct lc2_life_texture_pair){.phase=phase,.timestamp_ns=1234,.nvn_id=id,.storage_owner=owner,
  .object=4660,.texture_name=texture,.renderbuffer_name=renderbuffer,.width=128,.height=64,
  .format=0x41,.levels=1,.guest_bytes=500,.charge_bytes=400,.pool_id=99,.pool_generation=8,
  .target=1,.depth=1,.samples=1,.cpu_write_generation=2,.owner_first=1};
}
int main(void) {
 assert(!lc2_life_events_on());
 lc2_life_events_storage(1,10,1,400,0);        /* disabled: no accounting */
 lc2_life_events_report_fd(1);
 setenv("LC2_LIFE_EVENTS","0",1);
 assert(!lc2_life_events_on());
 setenv("LC2_LIFE_EVENTS","1",1);
 setenv("LAMENTUM_RUN_UUID","test-budget-run",1);
 assert(lc2_life_events_on());
 lc2_life_events_budget("add",42,100,100,1,7);
 lc2_life_events_budget("add",43,50,150,2,8);
 lc2_life_events_budget("sub",43,20,130,2,9);
 lc2_life_events_budget("add",44,1,131,3,10); /* bounded ring overflow */
 assert(lc2_life_events_state()->budget_event_lines==3);
 assert(lc2_life_events_state()->budget_event_overflow==1);
 lc2_life_events_budget_floor(1234,2345,70304,2031356,131,150,3,3,1,"sampled",0);
 lc2_life_events_budget_floor(5678,0,70000,2000000,0,0,0,3,1,"mutex-busy",16);
 lc2_life_events_storage(1,10,1,400,0);
 lc2_life_events_storage(1,10,1,100,1);         /* second mip extends one image */
 assert(lc2_life_events_state()->retained_bytes==500);
 assert(lc2_life_events_state()->extends==1);
 struct lc2_life_event *alias_entry=lc2_life_event_find(10,1,1);assert(alias_entry);
 uint64_t alias_generation=alias_entry->generation;
 lc2_life_events_alias(10,1,alias_generation,1);
 lc2_life_events_alias(10,1,alias_generation,1);
 assert(alias_entry->alias_views==2 && lc2_life_events_state()->alias_views==2);
 lc2_life_events_alias(10,1,alias_generation,-1);
 assert(alias_entry->alias_views==1 && lc2_life_events_state()->alias_views==1);
 lc2_life_events_alias(10,1,alias_generation,-1);
 assert(alias_entry->alias_views==0 && lc2_life_events_state()->alias_views==0);
 lc2_life_events_delete(10,1,0);               /* zero views: the expected path */
 assert(lc2_life_events_state()->deletes==1);
 assert(lc2_life_events_state()->delete_with_views==0);
 lc2_life_events_storage(2,10,1,700,0);        /* same GL name, new generation */
 assert(lc2_life_events_state()->name_reuse==1);
 uint64_t generation_min=0,generation_max=0;
 assert(lc2_life_events_storage_generation(2,1,&generation_min,&generation_max));
 assert(generation_min==2 && generation_max==2);
 lc2_life_events_delete(10,1,2);               /* reported, never hidden */
 assert(lc2_life_events_state()->delete_with_views==1);
 lc2_life_events_respec(3,77,3,900);
 lc2_life_events_respec(3,77,3,400);           /* glBufferData replaces the store */
 assert(lc2_life_events_state()->respecs==1);  /* the first store was an allocation */
 lc2_life_events_respec(3,77,3,100);
 assert(lc2_life_events_state()->respecs==2);
 assert(lc2_life_events_state()->kind_bytes[3]==100);
 assert(lc2_life_events_state()->kind_live[3]==1);
 /* Texture owner join is by NVN id across current live GL storage generations. */
 lc2_life_events_storage(42,420,1,200,0);
 lc2_life_events_storage(42,420,1,50,1);          /* another mip of the same GL image */
 lc2_life_events_storage(42,421,1,80,0);          /* second image for the same NVN owner */
 lc2_life_events_storage(42,422,2,999,UINT_MAX);  /* renderbuffer is not texture payload */
 lc2_life_events_storage(43,430,1,300,0);
 uint64_t decoded=0;unsigned records=0;
 assert(lc2_life_events_texture_payload(42,&decoded,&records));
 assert(decoded==330 && records==2);
 assert(lc2_life_events_texture_payload(43,&decoded,&records));
 assert(decoded==300 && records==1);
 assert(lc2_life_events_storage_generation(42,1,&generation_min,&generation_max));
 assert(generation_min==1 && generation_max==1);
 assert(lc2_life_events_storage_payload(42,2,&decoded,&records));
 assert(decoded==999 && records==1);
 lc2_life_events_delete(420,1,0);
 assert(lc2_life_events_texture_payload(42,&decoded,&records));
 assert(decoded==80 && records==1);
 lc2_life_events_storage(44,420,1,100,0);      /* reused GL name has a new owner */
 assert(lc2_life_events_storage_generation(44,1,&generation_min,&generation_max));
 assert(generation_min==2 && generation_max==2);
 assert(lc2_life_events_texture_payload(42,&decoded,&records));
 assert(decoded==80 && records==1);
 assert(lc2_life_events_texture_payload(44,&decoded,&records));
 assert(decoded==100 && records==1);
 struct lc2_life_texture_pair pair=test_pair("initialize",42,42,7,0);
 lc2_life_events_texture_pair(&pair);
 assert(lc2_life_events_state()->tex_pair_lines==1);
 for(unsigned i=1;i<LC2_LIFE_TEXTURE_PAIR_CAP;i++)
  lc2_life_events_texture_pair(&pair);
 assert(lc2_life_events_state()->tex_pair_lines==LC2_LIFE_TEXTURE_PAIR_CAP);
 lc2_life_events_texture_pair(&pair);
 assert(lc2_life_events_state()->tex_pair_overflow==1);
 pair.phase="live-set";
 lc2_life_events_texture_live_pair(&pair);
 assert(lc2_life_events_state()->tex_live_pair_lines==1);
 assert(lc2_life_events_live_storage_fd(1,5678,128)>0);
 for(unsigned i=0;i<LC2_LIFE_EVENT_CAP+3;i++)lc2_life_events_storage(100+i,1000+i,1,1,0);
 assert(lc2_life_events_state()->overflow>=3);
 lc2_life_events_tex(0,1000,0,0,1);
 lc2_life_events_tex(1,250,0,0,1);
 lc2_life_events_tex(0,400,1,0,0);
 lc2_life_events_tex(0,90,0,1,0);
 assert(lc2_life_events_state()->tex_level0_bytes==1490);
 assert(lc2_life_events_state()->tex_mip_bytes==250);
 assert(lc2_life_events_state()->tex_scaled_bytes==400);
 assert(lc2_life_events_state()->tex_half_bytes==90);
 assert(lc2_life_events_state()->tex_charged_bytes==1250);
 assert(lc2_life_events_state()->tex_uncharged_bytes==490);
 lc2_life_events_tex_guest(1000);
 assert(lc2_life_events_state()->tex_guest_bytes==1000);
 /* M3-B: bounded default-off event ring, with write-after-call reporting. */
 setenv("LC2_M3B_TIMELINE","0",1);
 struct lc2_m3b_descriptor window_desc={.stage="bc-full-refresh",.owner_id=105,.object=4660,
  .gl_name=12,.storage_generation=3,.content_generation=7,.pool_id=8,.pool_generation=9,
  .compressed_input_bytes=2073600,.rgba_requested_bytes=8294400,.linear_requested_bytes=2073600,
  .staging_live_requested_peak_bytes=10368000,.gl_intent_bytes=8294400,
  .width=1920,.height=1080,.level=0,.format=0x44,.allocate=0,.storage_generation_known=1};
 assert(lc2_m3b_window_begin(&window_desc)==NULL);
 setenv("LC2_M3B_TIMELINE","1",1);
 setenv("LC2_M3B_MAX_EVENTS","4",1);
 struct lc2_m3b_window *window=lc2_m3b_window_begin(&window_desc);assert(window);
 lc2_m3b_decode_mark(window,100,150);
 lc2_m3b_gl_alloc_mark(window,160,170);
 lc2_m3b_upload_mark(window,180,190);
 lc2_m3b_window_finish(window,200);
 assert(lc2_m3b_mark("first-present",7));
 assert(lc2_m3b_mark("teardown",0));
 assert(lc2_m3b_window_begin(&window_desc)); /* unfinished owner window is incomplete at flush */
 assert(!lc2_m3b_mark("overflow",0));
 /* The stop-path formatter must agree with printf digit-for-digit: a stray leading
  * or trailing digit silently misreports every counter by 10x. */
 char expect[768];
 snprintf(expect,sizeof expect," storage-calls=%llu extends=%llu deletes=%llu delete-with-views=%llu name-reuse=%llu retained=%llu peak=%llu live=%llu alias-views=%llu overflow=%llu generation-history-overflow=%llu live-owner-overflow=%llu tex-bytes=%llu tex-live=%llu rb-bytes=%llu rb-live=%llu buf-bytes=%llu buf-live=%llu respecs=%llu tex-l0=%llu tex-mips=%llu tex-scaled=%llu tex-half=%llu tex-charged=%llu tex-uncharged=%llu tex-guest=%llu tex-pair-lines=%llu tex-pair-overflow=%llu tex-live-pair-lines=%llu tex-live-pair-overflow=%llu storage-event-lines=%llu storage-event-overflow=%llu delete-event-lines=%llu delete-event-overflow=%llu",
  (unsigned long long)lc2_life_events_state()->storage_calls,
  (unsigned long long)lc2_life_events_state()->extends,
  (unsigned long long)lc2_life_events_state()->deletes,
  (unsigned long long)lc2_life_events_state()->delete_with_views,
  (unsigned long long)lc2_life_events_state()->name_reuse,
  (unsigned long long)lc2_life_events_state()->retained_bytes,
  (unsigned long long)lc2_life_events_state()->peak_bytes,
  (unsigned long long)lc2_life_events_state()->live,
  (unsigned long long)lc2_life_events_state()->alias_views,
  (unsigned long long)lc2_life_events_state()->overflow,
  (unsigned long long)lc2_life_events_state()->generation_history_overflow,
  (unsigned long long)lc2_life_events_state()->live_owner_overflow,
  (unsigned long long)lc2_life_events_state()->kind_bytes[1],
  (unsigned long long)lc2_life_events_state()->kind_live[1],
  (unsigned long long)lc2_life_events_state()->kind_bytes[2],
  (unsigned long long)lc2_life_events_state()->kind_live[2],
  (unsigned long long)lc2_life_events_state()->kind_bytes[3],
  (unsigned long long)lc2_life_events_state()->kind_live[3],
  (unsigned long long)lc2_life_events_state()->respecs,
  (unsigned long long)lc2_life_events_state()->tex_level0_bytes,
  (unsigned long long)lc2_life_events_state()->tex_mip_bytes,
  (unsigned long long)lc2_life_events_state()->tex_scaled_bytes,
  (unsigned long long)lc2_life_events_state()->tex_half_bytes,
  (unsigned long long)lc2_life_events_state()->tex_charged_bytes,
  (unsigned long long)lc2_life_events_state()->tex_uncharged_bytes,
  (unsigned long long)lc2_life_events_state()->tex_guest_bytes,
  (unsigned long long)lc2_life_events_state()->tex_pair_lines,
  (unsigned long long)lc2_life_events_state()->tex_pair_overflow,
  (unsigned long long)lc2_life_events_state()->tex_live_pair_lines,
  (unsigned long long)lc2_life_events_state()->tex_live_pair_overflow,
  (unsigned long long)lc2_life_events_state()->storage_event_lines,
  (unsigned long long)lc2_life_events_state()->storage_event_overflow,
  (unsigned long long)lc2_life_events_state()->delete_event_lines,
  (unsigned long long)lc2_life_events_state()->delete_event_overflow);
 printf("EXPECT%s\n",expect);
 lc2_life_events_report_fd(1);
 return 0;
}
'''

class LifeEventTests(unittest.TestCase):
    def test_alias_views_are_scoped_to_object_generation(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        block = patch.split(MARKER, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in block.splitlines()
                             if line.startswith('+') and not line.startswith('+++')) + '\n'
        source = r'''
#include "lc2_life_events.h"
#include <assert.h>
int main(void) {
 setenv("LC2_LIFE_EVENTS","1",1);
 struct lc2_life_events_state *s=lc2_life_events_state();
 assert(sizeof(struct lc2_life_event)==64); /* alias_views occupies prior alignment padding */
 const struct lc2_life_storage_key a={.share_group=1,.name=42,.kind=1,.target=0x0de1};
 const struct lc2_life_storage_key b={.share_group=1,.name=43,.kind=1,.target=0x0de1};
 lc2_life_events_storage_key(11,&a,64);lc2_life_events_storage_key(12,&b,96);
 struct lc2_life_event *ea=lc2_life_event_find_group(1,42,1,1);
 struct lc2_life_event *eb=lc2_life_event_find_group(1,43,1,1);
 assert(ea && eb && ea->generation==1 && eb->generation==1);
 uint64_t old_generation=ea->generation;
 lc2_life_events_alias_group(1,42,1,old_generation,1);
 lc2_life_events_alias_group(1,42,1,old_generation,1);
 lc2_life_events_alias_group(1,43,1,eb->generation,1);
 assert(ea->alias_views==2 && eb->alias_views==1 && s->alias_views==3);
 lc2_life_events_alias_group(1,42,1,old_generation,-1);
 assert(ea->alias_views==1 && eb->alias_views==1 && s->alias_views==2);
 lc2_life_events_delete_key(&a,0); /* alias ledger detects caller's missing view count */
 assert(s->delete_with_views==1);
 lc2_life_events_storage_key(13,&a,128);
 struct lc2_life_event *reused=lc2_life_event_find_group(1,42,1,1);
 assert(reused && reused->generation==2 && reused->alias_views==0);
 uint64_t before=s->overflow;
 lc2_life_events_alias_group(1,42,1,old_generation,-1); /* stale generation */
 assert(s->overflow==before+1 && reused->alias_views==0 && s->alias_views==2);
 lc2_life_events_alias_group(1,42,1,reused->generation,1);
 assert(reused->alias_views==1 && s->alias_views==3);
 lc2_life_events_alias_group(1,42,1,reused->generation,-1);
 assert(reused->alias_views==0 && s->alias_views==2);
 before=s->overflow;
 lc2_life_events_alias_group(1,42,1,reused->generation,-1); /* underflow is fail-closed */
 assert(s->overflow==before+1 && reused->alias_views==0 && s->alias_views==2);
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            (p/'lc2_life_events.h').write_text(header)
            (p/'aliases.c').write_text(source)
            built=subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I',d,
                                  str(p/'aliases.c'),'-o',str(p/'aliases')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            ran=subprocess.run([str(p/'aliases')],capture_output=True,text=True)
            self.assertEqual(ran.returncode,0,ran.stderr)

    def test_zero_storage_join_release_updates_generation_scoped_aliases(self):
        patch=(ROOT/'runtime/lamentum-adapter.patch').read_text()
        adapter_src=pathlib.Path(os.environ.get('LAMENTUM_ADAPTER_SRC',ROOT.parent/'adapter-src'))
        required=os.environ.get('LAMENTUM_REQUIRE_ZERO_STORAGE_ALIAS_TEST')=='1'
        if not adapter_src.is_dir():
            if required:self.fail(f'required adapter source missing: {adapter_src}')
            self.skipTest(f'adapter source unavailable: {adapter_src}')
        overlay=subprocess.run(['git','-C',str(adapter_src),'diff','--binary'],capture_output=True)
        self.assertEqual(overlay.returncode,0,overlay.stderr.decode(errors='replace'))
        self.assertEqual(overlay.stdout,(ROOT/'runtime/lamentum-adapter.patch').read_bytes())
        fixture=ROOT/'tools/fixtures/zero-storage-alias-lifetime.c'
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            built=subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',
                '-Wno-unused-function','-Wno-unused-variable','-Wno-unused-parameter',
                '-I',str(adapter_src/'native'),str(fixture),'-o',str(p/'aliases')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            ran=subprocess.run([str(p/'aliases')],capture_output=True,text=True)
            self.assertEqual(ran.returncode,0,ran.stderr)

    def test_identical_gl_names_in_distinct_share_groups_have_independent_lifetimes(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        block = patch.split(MARKER, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in block.splitlines()
                             if line.startswith('+') and not line.startswith('+++')) + '\n'
        source = r'''
#include "lc2_life_events.h"
#include <assert.h>
int main(void) {
 setenv("LC2_LIFE_EVENTS","1",1);
 struct lc2_life_events_state *s=lc2_life_events_state();
 const struct lc2_life_storage_key a={.share_group=1,.name=42,.kind=1,.target=0x0de1};
 const struct lc2_life_storage_key b={.share_group=2,.name=42,.kind=1,.target=0x0de1};
 lc2_life_events_storage_key(11,&a,64);
 lc2_life_events_storage_key(22,&b,96);
 uint64_t lo=0,hi=0,bytes=0;unsigned records=0;
 assert(s->live==2 && s->generation_history_overflow==0 && s->live_owner_overflow==0);
 assert(lc2_life_events_storage_generation(11,1,&lo,&hi) && lo==1 && hi==1);
 assert(lc2_life_events_storage_generation(22,1,&lo,&hi) && lo==1 && hi==1);
 lc2_life_events_delete_key(&a,0);
 assert(s->live==1);
 assert(lc2_life_events_storage_payload(22,1,&bytes,&records) && bytes==96 && records==1);
 lc2_life_events_storage_key(33,&a,128);
 assert(lc2_life_events_storage_generation(33,1,&lo,&hi) && lo==2 && hi==2);
 assert(lc2_life_events_storage_generation(22,1,&lo,&hi) && lo==1 && hi==1);
 assert(s->live==2 && s->name_reuse==1);
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            (p/'lc2_life_events.h').write_text(header)
            (p/'share_groups.c').write_text(source)
            built=subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I',d,
                                  str(p/'share_groups.c'),'-o',str(p/'share_groups')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            ran=subprocess.run([str(p/'share_groups')],capture_output=True,text=True)
            self.assertEqual(ran.returncode,0,ran.stderr)

    def test_1024_create_delete_pairs_and_24_reuses_preserve_generations(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        block = patch.split(MARKER, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in block.splitlines()
                             if line.startswith('+') and not line.startswith('+++')) + '\n'
        source = r'''
#include "lc2_life_events.h"
#include <assert.h>
int main(void) {
 setenv("LC2_LIFE_EVENTS","1",1);
 struct lc2_life_events_state *s=lc2_life_events_state();
 for(uint64_t i=1;i<=1024;i++) {
  const struct lc2_life_storage_key key={.share_group=7,.name=i,.kind=1,.target=0x0de1};
  lc2_life_events_storage_key(i,&key,64);
  lc2_life_events_delete_key(&key,0);
 }
 assert(s->deletes==1024 && s->live==0);
 assert(s->generation_history_overflow==0 && s->live_owner_overflow==0);
 assert(s->storage_event_overflow>0 && s->delete_event_overflow>0);
 for(uint64_t i=0;i<24;i++) {
  const struct lc2_life_storage_key key={.share_group=7,.name=1,.kind=1,.target=0x0de1};
  lc2_life_events_storage_key(2000+i,&key,64);
  lc2_life_events_delete_key(&key,0);
 }
 uint64_t last=0;
 for(unsigned i=0;i<LC2_LIFE_GENERATION_CAP;i++)
  if(s->generations[i].share_group==7 && s->generations[i].name==1 && s->generations[i].kind==1)
   last=s->generations[i].last_generation;
 assert(last==25 && s->name_reuse==24);
 assert(s->deletes==1048 && s->live==0);
 assert(s->generation_history_overflow==0 && s->live_owner_overflow==0);
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            (p/'lc2_life_events.h').write_text(header)
            (p/'churn.c').write_text(source)
            built=subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I',d,
                                  str(p/'churn.c'),'-o',str(p/'churn')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            ran=subprocess.run([str(p/'churn')],capture_output=True,text=True)
            self.assertEqual(ran.returncode,0,ran.stderr)

    def test_generation_history_supports_more_than_1024_distinct_and_reused_keys(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        block = patch.split(MARKER, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in block.splitlines()
                             if line.startswith('+') and not line.startswith('+++')) + '\n'
        source = r'''
#include "lc2_life_events.h"
#include <assert.h>
int main(void) {
 unsigned reused=99;
 for(uint64_t i=1;i<=1200;i++) {
  assert(lc2_life_generation_next(7,i,1,&reused)==1);
  assert(reused==0);
 }
 for(uint64_t i=1;i<=1200;i++) {
  assert(lc2_life_generation_next(7,i,1,&reused)==2);
  assert(reused==1);
 }
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            (p/'lc2_life_events.h').write_text(header)
            (p/'generation.c').write_text(source)
            built=subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I',d,
                                  str(p/'generation.c'),'-o',str(p/'generation')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            ran=subprocess.run([str(p/'generation')],capture_output=True,text=True)
            self.assertEqual(ran.returncode,0,ran.stderr)

    def test_generation_and_live_owner_exhaustion_are_separate_failures(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        block = patch.split(MARKER, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in block.splitlines()
                            if line.startswith('+') and not line.startswith('+++')) + '\n'
        source = r'''
#include "lc2_life_events.h"
#include <assert.h>
#include <string.h>
int main(void) {
 struct lc2_life_events_state *s=lc2_life_events_state();unsigned reused=0;
 for(uint64_t i=1;i<=LC2_LIFE_GENERATION_CAP;i++)
  assert(lc2_life_generation_next(7,i,1,&reused)==1);
 assert(lc2_life_generation_next(7,LC2_LIFE_GENERATION_CAP+1,1,&reused)==0);
 assert(s->generation_history_overflow==1 && s->live_owner_overflow==0);
 memset(s,0,sizeof(*s));
 s->generations[0]=(struct lc2_life_generation_history){.share_group=7,.name=1,.kind=1,.last_generation=UINT64_MAX};
 assert(lc2_life_generation_next(7,1,1,&reused)==0);
 assert(s->generation_history_overflow==1 && s->live_owner_overflow==0);
 memset(s,0,sizeof(*s));setenv("LC2_LIFE_EVENTS","1",1);
 for(unsigned i=1;i<=LC2_LIFE_EVENT_CAP;i++)lc2_life_events_storage(i,i,1,1,0);
 assert(s->generation_history_overflow==0 && s->live_owner_overflow==0);
 lc2_life_events_storage(LC2_LIFE_EVENT_CAP+1,LC2_LIFE_EVENT_CAP+1,1,1,0);
 assert(s->generation_history_overflow==0 && s->live_owner_overflow==1);
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            (p/'lc2_life_events.h').write_text(header)
            (p/'exhaustion.c').write_text(source)
            built=subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I',d,
                                  str(p/'exhaustion.c'),'-o',str(p/'exhaustion')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            ran=subprocess.run([str(p/'exhaustion')],capture_output=True,text=True)
            self.assertEqual(ran.returncode,0,ran.stderr)

    def test_observation_contract(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        self.assertIn(MARKER, patch)
        block = patch.split(MARKER, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(l[1:] for l in block.splitlines() if l.startswith('+') and not l.startswith('+++')) + '\n'
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / 'lc2_life_events.h').write_text(header)
            (p / 'test.c').write_text(FIXTURE)
            r = subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-I', d,
                                str(p / 'test.c'), '-o', str(p / 'test')], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = subprocess.run([str(p / 'test')], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            out = r.stdout
            m3b_windows = [line for line in out.splitlines() if line.startswith('LC2_M3B_WINDOW ')]
            m3b_marks = [line for line in out.splitlines() if line.startswith('LC2_M3B_MARK ')]
            self.assertEqual(len(m3b_windows), 1)
            self.assertIn('run-id=test-budget-run', m3b_windows[0])
            self.assertIn('stage=bc-full-refresh', m3b_windows[0])
            self.assertIn('decode-start-ns=100 decode-end-ns=150 decode-wall-ns=50', m3b_windows[0])
            self.assertIn('gl-alloc-wall-ns=10', m3b_windows[0])
            self.assertIn('gl-upload-wall-ns=10', m3b_windows[0])
            self.assertIn('owner-id=105 owner-generation=105 generation-basis=nvn-object-id object=0x1234', m3b_windows[0])
            self.assertIn('storage-generation=3 storage-generation-known=1 content-generation=7', m3b_windows[0])
            self.assertIn('source-compressed-bytes=2073600 rgba-requested-bytes=8294400', m3b_windows[0])
            self.assertIn('linear-requested-bytes=2073600 staging-live-requested-peak-bytes=10368000', m3b_windows[0])
            self.assertIn('gl-error=unobserved-in-window driver-allocation=unknown', m3b_windows[0])
            self.assertIn('mali-residency=unknown completion=unobserved', m3b_windows[0])
            self.assertEqual(len(m3b_marks), 2)
            self.assertTrue(any('name=first-present value=7' in line for line in m3b_marks))
            m3b_summary = next(line for line in out.splitlines() if line.startswith('LC2_M3B_SUMMARY '))
            self.assertIn('configured=4 claimed=5 final-claimed=5 emitted=3 incomplete=1 active=1 dropped=1 format-errors=0 complete=0', m3b_summary)
            self.assertIn('LC2_LIFE_SUMMARY', out)
            self.assertIn('share-group=per-record', out)
            self.assertIn('delete-with-views=1', out)
            self.assertIn('name-reuse=2', out)
            pairs = [line for line in out.splitlines() if line.startswith('LC2_TEXTURE_PAIR ')]
            self.assertEqual(len(pairs), 128)
            self.assertTrue(any('id=42 object-generation=42 storage-owner=42 storage-token=42 object=4660 texture=7 renderbuffer=0 '
                                'size=128x64 format=0x41 levels=1 target=1 depth=1 samples=1 '
                                'guest-bytes=500 charge-bytes=400 pool-id=99 pool-generation=8 cpu-write-generation=2 '
                                'source-write-generation=untracked alias-parent=0 storage-owner-first=1 '
                                'gl-texture-bytes=80 gl-texture-records=1 gl-texture-generation-min=1 gl-texture-generation-max=1 '
                                'gl-renderbuffer-bytes=999 gl-renderbuffer-records=1 gl-renderbuffer-generation-min=1 '
                                'gl-renderbuffer-generation-max=1 storage-status=recorded' in line for line in pairs))
            self.assertTrue(any(line.startswith('LC2_GL_STORAGE_EVENT ') and
                                'event=extend owner=42 gl-name=420 kind=1 storage-generation=1 bytes=50 total-bytes=250 subresource=1' in line
                                for line in out.splitlines()))
            self.assertTrue(any(line.startswith('LC2_GL_STORAGE_DELETE ') and
                                'owner=42 gl-name=420 kind=1 storage-generation=1 bytes=250' in line
                                for line in out.splitlines()))
            self.assertTrue(any(line.startswith('LC2_GL_STORAGE_EVENT ') and
                                'owner=44 gl-name=420 kind=1 storage-generation=2' in line
                                for line in out.splitlines()))
            self.assertTrue(any(line.startswith('LC2_TEXTURE_LIVE_PAIR ') and 'phase=live-set' in line
                                for line in out.splitlines()))
            self.assertTrue(any(line.startswith('LC2_GL_STORAGE_LIVE ') and 'generation=2' in line
                                for line in out.splitlines()))
            budget_events = [line for line in out.splitlines() if line.startswith('LC2_TEXTURE_BUDGET_EVENT ')]
            self.assertEqual(len(budget_events), 3)
            expected_budget = [
                'action=add texture-id=42 delta-bytes=100 live-bytes=100 charge-count=1 caller=7',
                'action=add texture-id=43 delta-bytes=50 live-bytes=150 charge-count=2 caller=8',
                'action=sub texture-id=43 delta-bytes=20 live-bytes=130 charge-count=2 caller=9',
            ]
            for line, fields in zip(budget_events, expected_budget):
                self.assertIn('run-id=test-budget-run', line)
                self.assertRegex(line, 't-ns=[0-9]+')
                self.assertIn(fields, line)
            floor = next(line for line in out.splitlines() if line.startswith('LC2_TEXTURE_BUDGET_FLOOR ')
                         and 'floor-check-t-ns=1234' in line)
            self.assertIn('floor-available-kib=70304 floor-swap-free-kib=2031356', floor)
            self.assertIn('live-bytes=131 peak-bytes=150 charge-count=3 event-lines=3 event-overflow=1 status=sampled', floor)
            busy = next(line for line in out.splitlines() if line.startswith('LC2_TEXTURE_BUDGET_FLOOR ')
                        and 'floor-check-t-ns=5678' in line)
            self.assertIn('status=mutex-busy lock-rc=16', busy)
            self.assertFalse(any('STOP status=' in line for line in out.splitlines()
                                 if line.startswith('LC2_TEXTURE_BUDGET_FLOOR ')))
            self.assertEqual(out.count('LC2_LIFE_SUMMARY'), 1)
            expected = [l for l in out.splitlines() if l.startswith('EXPECT')]
            summary = [l for l in out.splitlines() if l.startswith('LC2_LIFE_SUMMARY')]
            self.assertEqual(len(expected), 1)
            self.assertTrue(summary[0].endswith(expected[0][len('EXPECT'):]), (summary, expected))

    def test_redefining_same_texture_level_replaces_not_adds(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        block = patch.split(MARKER, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in block.splitlines()
                            if line.startswith('+') and not line.startswith('+++')) + '\n'
        source = r'''
#include "lc2_life_events.h"
#include <assert.h>
int main(void) {
 setenv("LC2_LIFE_EVENTS","1",1);
 lc2_life_events_storage(42,77,1,100,0);
 lc2_life_events_storage(42,77,1,250,0);
 assert(lc2_life_events_state()->retained_bytes==250);
 assert(lc2_life_events_state()->respecs==1);
 assert(lc2_life_events_state()->extends==0);
 lc2_life_events_storage(42,77,1,50,1);
 assert(lc2_life_events_state()->retained_bytes==300);
 assert(lc2_life_events_state()->extends==1);
 lc2_life_events_storage(42,77,1,0,0);
 assert(lc2_life_events_state()->retained_bytes==50);
 assert(lc2_life_event_find(77,1,1)->mips==2);
 assert(lc2_life_events_state()->respecs==2);
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / 'lc2_life_events.h').write_text(header)
            (p / 'test.c').write_text(source)
            built = subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-I', d,
                                    str(p / 'test.c'), '-o', str(p / 'test')], capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            ran = subprocess.run([str(p / 'test')], capture_output=True, text=True)
            self.assertEqual(ran.returncode, 0, ran.stderr)

    def test_storage_key_distinguishes_share_groups_and_cube_faces(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        block = patch.split(MARKER, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in block.splitlines()
                            if line.startswith('+') and not line.startswith('+++')) + '\n'
        source = r'''
#include "lc2_life_events.h"
#include <assert.h>
int main(void) {
 setenv("LC2_LIFE_EVENTS","1",1);
 struct lc2_life_storage_key a={.share_group=1,.name=9,.kind=1,.target=0x8515,.face=0,.level=0,.layer=0};
 struct lc2_life_storage_key b=a;b.face=1;
 struct lc2_life_storage_key c=a;c.share_group=2;
 lc2_life_events_storage_key(7,&a,100);
 lc2_life_events_storage_key(7,&a,200);
 lc2_life_events_storage_key(7,&b,100);
 lc2_life_events_storage_key(7,&c,50);
 assert(lc2_life_events_state()->retained_bytes==350);
 assert(lc2_life_events_state()->live==2);
 uint64_t bytes=0;unsigned records=0;
 struct lc2_life_storage_key v={.share_group=1,.name=17,.kind=3,.target=0x8892,.face=0,.level=0,.layer=0};
 lc2_life_events_respec_key(8,&v,100);
 lc2_life_events_respec_key(8,&v,80);
 assert(lc2_life_events_state()->retained_bytes==430);
 assert(lc2_life_events_state()->live==3);
 assert(lc2_life_events_storage_payload(8,3,&bytes,&records));
 assert(bytes==80 && records==1);
 lc2_life_events_delete_key(&v,0);
 assert(lc2_life_events_storage_payload(8,3,&bytes,&records));
 assert(bytes==0 && records==0);
 assert(lc2_life_events_state()->retained_bytes==350);
 lc2_life_events_delete_key(&a,0);
 assert(lc2_life_events_texture_payload(7,&bytes,&records));
 assert(bytes==50 && records==1);
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / 'lc2_life_events.h').write_text(header)
            (p / 'test.c').write_text(source)
            built = subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-I', d,
                                    str(p / 'test.c'), '-o', str(p / 'test')], capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            ran = subprocess.run([str(p / 'test')], capture_output=True, text=True)
            self.assertEqual(ran.returncode, 0, ran.stderr)
            self.assertIn('share-group=verified share-group-id=1 target=0x8515 face=0 level=0 layer=0', ran.stdout)
            self.assertIn('share-group=verified share-group-id=1 target=0x8515 face=1 level=0 layer=0', ran.stdout)
            self.assertIn('share-group=verified share-group-id=2 target=0x8515 face=0 level=0 layer=0', ran.stdout)
            self.assertIn('event=respec owner=8 gl-name=17 kind=3 storage-generation=1 bytes=80', ran.stdout)
            self.assertIn('share-group=verified share-group-id=1 target=0x8892 face=0 level=0 layer=0', ran.stdout)
            self.assertIn('share-group=verified share-group-id=1', ran.stdout)

    def test_live_table_recycles_after_more_than_512_create_delete_cycles(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        block = patch.split(MARKER, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in block.splitlines()
                            if line.startswith('+') and not line.startswith('+++')) + '\n'
        source = r'''
#include "lc2_life_events.h"
#include <assert.h>
int main(void) {
 setenv("LC2_LIFE_EVENTS","1",1);
 for(unsigned i=0;i<LC2_LIFE_EVENT_CAP+24;i++) {
  lc2_life_events_storage(7,99,1,1,0);
  uint64_t min=0,max=0;
  assert(lc2_life_events_storage_generation(7,1,&min,&max));
  assert(min==i+1 && max==i+1);
  lc2_life_events_delete(99,1,0);
 }
 struct lc2_life_events_state *s=lc2_life_events_state();
 assert(s->overflow==0 && s->live==0 && s->retained_bytes==0);
 assert(s->name_reuse==LC2_LIFE_EVENT_CAP+23);
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / 'lc2_life_events.h').write_text(header)
            (p / 'test.c').write_text(source)
            built = subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-I', d,
                                    str(p / 'test.c'), '-o', str(p / 'test')], capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            ran = subprocess.run([str(p / 'test')], capture_output=True, text=True)
            self.assertEqual(ran.returncode, 0, ran.stderr)

    def test_owner_event_ring_preserves_order_and_reports_overflow(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        block = patch.split(MARKER, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in block.splitlines()
                            if line.startswith('+') and not line.startswith('+++')) + '\n'
        source = r'''
#define LC2_LIFE_OWNER_EVENT_CAP 3
#include "lc2_life_events.h"
#include <assert.h>
int main(void) {
 assert(!lc2_life_events_owner("initialize-start",280,280,0,0,77,1,0,1,"owner-unresolved"));
 setenv("LC2_LIFE_EVENTS","1",1);
 setenv("LAMENTUM_RUN_UUID","owner-test",1);
 assert(lc2_life_events_owner("initialize-start",280,280,0,0,77,1,0,1,"owner-unresolved"));
 assert(lc2_life_events_owner("budget-add",280,280,0,2097152,77,1,0,1,"budget-id-only"));
 assert(lc2_life_events_owner("initialize",280,280,280,2097152,77,1,0,1,"pair-emitted"));
 assert(!lc2_life_events_owner("retire",280,280,280,0,77,1,0,1,"capacity-exceeded"));
 lc2_life_events_owner_report_fd(1);
 assert(!lc2_life_events_owner("late",280,280,280,0,77,1,0,1,"closed"));
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / 'lc2_life_events.h').write_text(header)
            (p / 'test.c').write_text(source)
            built = subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-I', d,
                                    str(p / 'test.c'), '-o', str(p / 'test')], capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            ran = subprocess.run([str(p / 'test')], capture_output=True, text=True)
            self.assertEqual(ran.returncode, 0, ran.stderr)
            events = [line for line in ran.stdout.splitlines()
                      if line.startswith('LC2_TEXTURE_OWNER_EVENT ')]
            self.assertEqual(len(events), 3)
            self.assertIn('run-id=owner-test event-seq=1', events[0])
            self.assertIn('phase=initialize-start nvn-id=280 object-generation=280', events[0])
            self.assertIn('storage-owner=0 storage-owner-status=unresolved', events[0])
            self.assertIn('source-write-generation=untracked status=owner-unresolved', events[0])
            self.assertIn('phase=budget-add', events[1])
            self.assertIn('charge-bytes=2097152', events[1])
            self.assertIn('phase=initialize nvn-id=280 object-generation=280', events[2])
            self.assertIn('storage-owner=280 storage-owner-status=resolved', events[2])
            summary = next(line for line in ran.stdout.splitlines()
                           if line.startswith('LC2_TEXTURE_OWNER_EVENTS_SUMMARY '))
            self.assertIn('claimed=4 final-claimed=4 emitted=3 incomplete=0 active=0 dropped=1 format-errors=0 complete=0', summary)


    def test_texture_owner_generation_tracks_nvn_identity_separately_from_gl_storage(self):
        """Compile the source-bound identity/emitter seam; this is not a GL/game run."""
        adapter_src = pathlib.Path(os.environ.get('LAMENTUM_ADAPTER_SRC', ROOT.parent / 'adapter-src'))
        required = os.environ.get('LAMENTUM_REQUIRE_ZERO_STORAGE_ALIAS_TEST') == '1'
        if not adapter_src.is_dir():
            if required:
                self.fail(f'required adapter source missing: {adapter_src}')
            self.skipTest(f'adapter source unavailable: {adapter_src}')
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_bytes()
        diff = subprocess.run(['git', '-C', str(adapter_src), 'diff', '--binary'], capture_output=True)
        self.assertEqual(diff.returncode, 0, diff.stderr.decode(errors='replace'))
        self.assertEqual(diff.stdout, patch)
        policy = json.loads((ROOT / 'tools/gl_storage_callsite_policy.json').read_text())
        self.assertEqual(source_tree_identity(adapter_src)['sha256'], policy['source_tree_sha256'])

        textures = (adapter_src / 'native/nvn_textures.h').read_text()
        self.assertIn('.id=zero_next_object_id()', textures)
        self.assertIn('lc2_life_events_owner("initialize-start",t->id,t->id,0,0,pool->object,pool->generation,', textures)
        self.assertIn('lc2_life_events_owner("alias-resolve",t->id,t->id,storage_owner->id,', textures)
        self.assertIn('.nvn_id=t->id,.storage_owner=storage_owner->id', textures)
        memory = (adapter_src / 'native/nvn_memory.h').read_text()
        start = memory.index('static uint64_t nvn_next_object_id;')
        end = memory.index('static struct nvn_pool *nvn_pool_find', start)
        id_generator = memory[start:end]
        patch_text = patch.decode()
        block = patch_text.split(MARKER, 1)[1].split('diff --git ', 1)[0]
        events = '\n'.join(line[1:] for line in block.splitlines()
                            if line.startswith('+') and not line.startswith('+++')) + '\n'
        source = r'''
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
static uint64_t nvn_caller=1;
static void stop(const char *reason,uint64_t caller,uint64_t detail,unsigned code) {
    (void)reason;(void)caller;(void)detail;(void)code;abort();
}
''' + id_generator + r'''
#include "lc2_life_events.h"
struct mock_texture {uint64_t object,id;};
static struct mock_texture make_texture(uint64_t object) {
    return (struct mock_texture){.object=object,.id=zero_next_object_id()};
}
static void record_texture(uint64_t id) {
    const struct lc2_life_storage_key key={.share_group=1,.name=7,.kind=1,.target=0x0de1};
    lc2_life_events_storage_key(id,&key,64);
    struct lc2_life_texture_pair pair={.phase="initialize",.timestamp_ns=100,
        .nvn_id=id,.storage_owner=id,.texture_name=7,.width=4,.height=4,.levels=1,
        .guest_bytes=64,.charge_bytes=64,.pool_id=9,.pool_generation=1,.owner_first=1};
    lc2_life_events_texture_pair(&pair);
}
int main(void) {
    setenv("LC2_LIFE_EVENTS","1",1);setenv("LAMENTUM_RUN_UUID","nvn-generation-test",1);
    struct mock_texture first=make_texture(100),second=make_texture(101);
    assert(first.id==1 && second.id==2);
    assert(lc2_life_events_owner("initialize-start",first.id,first.id,0,0,9,1,0,1,"owner-unresolved"));
    record_texture(first.id);
    uint64_t min=0,max=0;
    assert(lc2_life_events_storage_generation(first.id,1,&min,&max) && min==1 && max==1);
    const struct lc2_life_storage_key key={.share_group=1,.name=7,.kind=1,.target=0x0de1};
    lc2_life_events_delete_key(&key,0);
    assert(lc2_life_events_owner("retire-start",first.id,first.id,first.id,64,9,1,0,1,"retire-started"));
    assert(lc2_life_events_owner("initialize-start",second.id,second.id,0,0,9,1,0,1,"owner-unresolved"));
    record_texture(second.id);
    assert(lc2_life_events_storage_generation(second.id,1,&min,&max) && min==2 && max==2);
    lc2_life_events_owner_report_fd(1);
    return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / 'lc2_life_events.h').write_text(events)
            (p / 'owner_generation.c').write_text(source)
            built = subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-function',
                                    '-I',str(p),'-I',str(adapter_src/'native'),
                                    str(p/'owner_generation.c'),'-o',str(p/'owner_generation')],
                                   capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            ran = subprocess.run([str(p/'owner_generation')],capture_output=True,text=True)
            self.assertEqual(ran.returncode,0,ran.stderr)
        owner_events = [line for line in ran.stdout.splitlines() if line.startswith('LC2_TEXTURE_OWNER_EVENT ')]
        first_owner_events = [line for line in owner_events if 'nvn-id=1 ' in line]
        second_owner_events = [line for line in owner_events if 'nvn-id=2 ' in line]
        self.assertTrue(first_owner_events and second_owner_events)
        self.assertTrue(all('object-generation=1' in line for line in first_owner_events))
        self.assertTrue(all('object-generation=2' in line for line in second_owner_events))
        pairs = [line for line in ran.stdout.splitlines() if line.startswith('LC2_TEXTURE_PAIR ')]
        self.assertEqual(len(pairs),2)
        self.assertIn('id=1 object-generation=1 storage-owner=1',pairs[0])
        self.assertIn('id=2 object-generation=2 storage-owner=2',pairs[1])
        gl_events = [line for line in ran.stdout.splitlines() if line.startswith('LC2_GL_STORAGE_EVENT ')]
        self.assertIn('owner=1 gl-name=7 kind=1 storage-generation=1',gl_events[0])
        self.assertIn('owner=2 gl-name=7 kind=1 storage-generation=2',gl_events[-1])


if __name__ == '__main__':
    unittest.main()
