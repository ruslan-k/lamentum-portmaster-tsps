"""Compile+run the observation-ledger contract extracted from the public overlay."""
import pathlib
import subprocess
import tempfile
import unittest

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
 lc2_life_events_alias(10,1,1);
 lc2_life_events_alias(10,1,1);
 assert(lc2_life_events_state()->alias_views==2);
 lc2_life_events_alias(10,1,-1);
 assert(lc2_life_events_state()->alias_views==1);
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
 snprintf(expect,sizeof expect," storage-calls=%llu extends=%llu deletes=%llu delete-with-views=%llu name-reuse=%llu retained=%llu peak=%llu live=%llu alias-views=%llu overflow=%llu tex-bytes=%llu tex-live=%llu rb-bytes=%llu rb-live=%llu buf-bytes=%llu buf-live=%llu respecs=%llu tex-l0=%llu tex-mips=%llu tex-scaled=%llu tex-half=%llu tex-charged=%llu tex-uncharged=%llu tex-guest=%llu tex-pair-lines=%llu tex-pair-overflow=%llu tex-live-pair-lines=%llu tex-live-pair-overflow=%llu storage-event-lines=%llu storage-event-overflow=%llu delete-event-lines=%llu delete-event-overflow=%llu",
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

if __name__ == '__main__':
    unittest.main()
