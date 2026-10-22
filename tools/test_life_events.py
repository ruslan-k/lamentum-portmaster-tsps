"""Compile+run the observation-ledger contract extracted from the public overlay."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MARKER = 'diff --git a/native/lc2_life_events.h b/native/lc2_life_events.h'

FIXTURE = r'''
#include "lc2_life_events.h"
#include <assert.h>
#include <stdio.h>
#include <unistd.h>
int main(void) {
 assert(!lc2_life_events_on());
 lc2_life_events_storage(1,10,1,400);          /* disabled: no accounting */
 lc2_life_events_report_fd(1);
 setenv("LC2_LIFE_EVENTS","0",1);
 assert(!lc2_life_events_on());
 setenv("LC2_LIFE_EVENTS","1",1);
 assert(lc2_life_events_on());
 lc2_life_events_storage(1,10,1,400);
 lc2_life_events_storage(1,10,1,100);          /* second mip extends one image */
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
 lc2_life_events_storage(2,10,1,700);          /* same GL name, new generation */
 assert(lc2_life_events_state()->name_reuse==1);
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
 lc2_life_events_storage(42,420,1,200);
 lc2_life_events_storage(42,420,1,50);           /* another mip of the same GL image */
 lc2_life_events_storage(42,421,1,80);           /* second image for the same NVN owner */
 lc2_life_events_storage(42,422,2,999);         /* renderbuffer is not texture payload */
 lc2_life_events_storage(43,430,1,300);
 uint64_t decoded=0;unsigned records=0;
 assert(lc2_life_events_texture_payload(42,&decoded,&records));
 assert(decoded==330 && records==2);
 assert(lc2_life_events_texture_payload(43,&decoded,&records));
 assert(decoded==300 && records==1);
 assert(lc2_life_events_storage_payload(42,2,&decoded,&records));
 assert(decoded==999 && records==1);
 lc2_life_events_delete(420,1,0);
 assert(lc2_life_events_texture_payload(42,&decoded,&records));
 assert(decoded==80 && records==1);
 lc2_life_events_storage(44,420,1,100);        /* reused GL name has a new owner */
 assert(lc2_life_events_texture_payload(42,&decoded,&records));
 assert(decoded==80 && records==1);
 assert(lc2_life_events_texture_payload(44,&decoded,&records));
 assert(decoded==100 && records==1);
 lc2_life_events_texture_pair("initialize",42,42,4660,7,0,128,64,0x41,1,500,400);
 assert(lc2_life_events_state()->tex_pair_lines==1);
 for(unsigned i=1;i<LC2_LIFE_TEXTURE_PAIR_CAP;i++)
  lc2_life_events_texture_pair("initialize",42,42,4660,7,0,128,64,0x41,1,500,400);
 assert(lc2_life_events_state()->tex_pair_lines==LC2_LIFE_TEXTURE_PAIR_CAP);
 lc2_life_events_texture_pair("overflow",42,42,4660,7,0,128,64,0x41,1,500,400);
 assert(lc2_life_events_state()->tex_pair_overflow==1);
 for(unsigned i=0;i<LC2_LIFE_EVENT_CAP+3;i++)lc2_life_events_storage(100+i,1000+i,1,1);
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
 /* The stop-path formatter must agree with printf digit-for-digit: a stray leading
  * or trailing digit silently misreports every counter by 10x. */
 char expect[768];
 snprintf(expect,sizeof expect," storage-calls=%llu extends=%llu deletes=%llu delete-with-views=%llu name-reuse=%llu retained=%llu peak=%llu live=%llu alias-views=%llu overflow=%llu tex-bytes=%llu tex-live=%llu rb-bytes=%llu rb-live=%llu buf-bytes=%llu buf-live=%llu respecs=%llu tex-l0=%llu tex-mips=%llu tex-scaled=%llu tex-half=%llu tex-charged=%llu tex-uncharged=%llu tex-guest=%llu tex-pair-lines=%llu tex-pair-overflow=%llu",
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
  (unsigned long long)lc2_life_events_state()->tex_pair_overflow);
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
            self.assertIn('LC2_LIFE_SUMMARY', out)
            self.assertIn('share-group=unverified', out)
            self.assertIn('delete-with-views=1', out)
            self.assertIn('name-reuse=2', out)
            pairs = [line for line in out.splitlines() if line.startswith('LC2_TEXTURE_PAIR ')]
            self.assertEqual(len(pairs), 128)
            self.assertTrue(any('id=42 storage-owner=42 object=4660 texture=7 renderbuffer=0 '
                                'size=128x64 format=0x41 levels=1 guest-bytes=500 charge-bytes=400 '
                                'gl-texture-bytes=80 gl-texture-records=1 gl-renderbuffer-bytes=999 '
                                'gl-renderbuffer-records=1 storage-status=recorded' in line for line in pairs))
            self.assertEqual(out.count('LC2_LIFE_SUMMARY'), 1)
            expected = [l for l in out.splitlines() if l.startswith('EXPECT')]
            summary = [l for l in out.splitlines() if l.startswith('LC2_LIFE_SUMMARY')]
            self.assertEqual(len(expected), 1)
            self.assertTrue(summary[0].endswith(expected[0][len('EXPECT'):]), (summary, expected))

if __name__ == '__main__':
    unittest.main()
