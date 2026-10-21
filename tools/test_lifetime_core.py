"""Compile and execute the portable lifetime contract from the actual overlay."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class LifetimeCoreTests(unittest.TestCase):
    def test_generation_alias_and_completion_contract(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        marker = 'diff --git a/native/lc2_lifetime.h b/native/lc2_lifetime.h'
        self.assertIn(marker, patch)
        block = patch.split(marker, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(l[1:] for l in block.splitlines() if l.startswith('+') and not l.startswith('+++')) + '\n'
        fixture = r'''
#include "lc2_lifetime.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
 struct lc2_lifetime l={0}; uint64_t a,b,c;
 assert(!lc2_life_begin(&l,0,1,1,1,100,&a));
 assert(lc2_life_begin(&l,7,1,1,1,100,&a));
 assert(l.reserved_bytes==100 && !lc2_life_can_delete(&l,a));
 assert(!lc2_life_begin(&l,7,1,1,1,100,&b)); /* pending name cannot replace */
 assert(lc2_life_commit(&l,a,0)); /* failed GL allocation rolls back intent */
 assert(l.reserved_bytes==0 && l.retained_bytes==0);
 assert(lc2_life_begin(&l,7,1,1,1,100,&a));
 assert(lc2_life_commit(&l,a,1));
 assert(lc2_life_begin(&l,7,2,1,1,50,&b)); /* same name, different share group */
 assert(lc2_life_commit(&l,b,1));
 assert(lc2_life_begin(&l,7,1,2,1,25,&c)); /* same name, renderbuffer namespace */
 assert(lc2_life_commit(&l,c,1));
 assert(l.retained_bytes==175);
 assert(lc2_life_attach(&l,a));
 assert(lc2_life_use(&l,a,1,9));
 assert(!lc2_life_use(&l,a,2,10)); /* foreign timeline must not qualify */
 assert(lc2_life_retire(&l,a));
 assert(!lc2_life_can_delete(&l,a));
 assert(lc2_life_detach(&l,a));
 assert(!lc2_life_can_delete(&l,a)); /* another view remains */
 assert(lc2_life_detach(&l,a));
 assert(!lc2_life_can_delete(&l,a)); /* GPU reader remains */
 assert(!lc2_life_complete(&l,1,9,0)); /* lost/failed fence */
 assert(!lc2_life_can_delete(&l,a));
 assert(lc2_life_complete(&l,1,8,1));
 assert(!lc2_life_can_delete(&l,a));
 assert(lc2_life_complete(&l,1,9,1));
 assert(lc2_life_can_delete(&l,a));
 assert(!lc2_life_complete(&l,1,8,1)); /* no completion regression */
 assert(!lc2_life_deleted(&l,a,0));
 assert(l.retained_bytes==175);
 assert(lc2_life_deleted(&l,a,1));
 assert(l.retained_bytes==75);
 assert(!lc2_life_use(&l,a,1,10)); /* stale generation */
 uint64_t reused;
 assert(lc2_life_begin(&l,7,1,1,1,200,&reused));
 assert(reused!=a && lc2_life_commit(&l,reused,1));
 assert(!lc2_life_use(&l,reused,1,9)); /* a completed serial cannot name a new reader */
 assert(lc2_life_use(&l,reused,1,10));
 /* Respecification keeps the old storage charged, even with same GL name. */
 uint64_t replacement;
 assert(lc2_life_begin(&l,7,1,1,1,300,&replacement));
 assert(lc2_life_commit(&l,replacement,1));
 assert(l.retained_bytes==575);
 assert(lc2_life_retire(&l,reused));
 assert(lc2_life_detach(&l,reused));
 assert(!lc2_life_can_delete(&l,reused)); /* glDelete would delete replacement too */
 assert(lc2_life_find(&l,replacement)->object_generation==lc2_life_find(&l,reused)->object_generation);
 assert(lc2_life_find(&l,reused)->object_generation!=a);
 lc2_life_context_lost(&l,1);
 assert(!lc2_life_can_delete(&l,reused));
 assert(!lc2_life_deleted(&l,reused,1));
 assert(l.retained_bytes==575); /* loss is not a physical refund */
 assert(!lc2_life_use(&l,replacement,1,10));
 assert(!lc2_life_begin(&l,999,1,1,1,10,&a)); /* lost group identity cannot be reused */
 struct lc2_lifetime full={0};
 for(unsigned i=0;i<LC2_LIFE_CAP;i++)assert(lc2_life_begin(&full,i+1,1,1,1,1,&a));
 assert(!lc2_life_begin(&full,9999,1,1,1,1,&a));
 assert(full.reserved_bytes==LC2_LIFE_CAP);
 struct lc2_lifetime overflow={0};
 assert(lc2_life_begin(&overflow,1,1,1,1,UINT64_MAX,&a));
 assert(!lc2_life_begin(&overflow,2,1,1,1,1,&b));
 assert(overflow.reserved_bytes==UINT64_MAX);
 puts("lifetime-contract PASS");
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / 'lc2_lifetime.h').write_text(header)
            (p / 'test.c').write_text(fixture)
            r = subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=undefined', '-fsanitize-undefined-trap-on-error', '-fno-sanitize-recover=all', '-I', d, str(p/'test.c'), '-o', str(p/'test')], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = subprocess.run([str(p/'test')], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout.strip(), 'lifetime-contract PASS')

if __name__ == '__main__':
    unittest.main()
