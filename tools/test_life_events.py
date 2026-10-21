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
 for(unsigned i=0;i<LC2_LIFE_EVENT_CAP+3;i++)lc2_life_events_storage(100+i,1000+i,1,1);
 assert(lc2_life_events_state()->overflow>=3);
 /* The stop-path formatter must agree with printf digit-for-digit: a stray leading
  * or trailing digit silently misreports every counter by 10x. */
 char expect[512];
 snprintf(expect,sizeof expect," storage-calls=%llu extends=%llu deletes=%llu delete-with-views=%llu name-reuse=%llu retained=%llu peak=%llu live=%llu alias-views=%llu overflow=%llu tex-bytes=%llu tex-live=%llu rb-bytes=%llu rb-live=%llu buf-bytes=%llu buf-live=%llu respecs=%llu",
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
  (unsigned long long)lc2_life_events_state()->respecs);
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
            self.assertIn('name-reuse=1', out)
            self.assertEqual(out.count('LC2_LIFE_SUMMARY'), 1)
            expected = [l for l in out.splitlines() if l.startswith('EXPECT')]
            summary = [l for l in out.splitlines() if l.startswith('LC2_LIFE_SUMMARY')]
            self.assertEqual(len(expected), 1)
            self.assertTrue(summary[0].endswith(expected[0][len('EXPECT'):]), (summary, expected))

if __name__ == '__main__':
    unittest.main()
