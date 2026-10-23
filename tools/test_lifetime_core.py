"""Compile and execute the portable lifetime contract from the actual overlay."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class LifetimeCoreTests(unittest.TestCase):
    def test_storage_only_commit_has_no_completion_or_refund_path(self):
        patch=(ROOT/'runtime/lamentum-adapter.patch').read_text()
        marker='diff --git a/native/lc2_lifetime.h b/native/lc2_lifetime.h'
        self.assertIn(marker,patch)
        block=patch.split(marker,1)[1].split('diff --git ',1)[0]
        header='\n'.join(line[1:] for line in block.splitlines()
                          if line.startswith('+') and not line.startswith('+++'))+'\n'
        fixture=r'''
#include "lc2_lifetime.h"
#include <assert.h>
int main(void) {
 struct lc2_lifetime l={0};uint64_t token;
 const struct lc2_life_identity identity={.share_group_epoch=1,.name=13,.kind=1};
 assert(lc2_life_begin_storage_only(&l,&identity,128,&token));
 assert(lc2_life_find(&l,token)->timeline==0);
 assert(lc2_life_commit_gl_result(&l,token,0));
 assert(l.retained_bytes==128 && l.reserved_bytes==0);
 assert(!lc2_life_use(&l,token,1,1));
 assert(lc2_life_retire(&l,token));
 assert(!lc2_life_can_delete(&l,token));
 assert(!lc2_life_deleted(&l,token,1));
 assert(l.retained_bytes==128);
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            (p/'lc2_lifetime.h').write_text(header)
            (p/'test.c').write_text(fixture)
            built=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-I',d,
                                  str(p/'test.c'),'-o',str(p/'test')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            ran=subprocess.run([str(p/'test')],capture_output=True,text=True)
            self.assertEqual(ran.returncode,0,ran.stderr)

    def test_unknown_gl_result_keeps_pending_charge_and_blocks_reuse(self):
        patch=(ROOT/'runtime/lamentum-adapter.patch').read_text()
        marker='diff --git a/native/lc2_lifetime.h b/native/lc2_lifetime.h'
        self.assertIn(marker,patch)
        block=patch.split(marker,1)[1].split('diff --git ',1)[0]
        header='\n'.join(line[1:] for line in block.splitlines()
                          if line.startswith('+') and not line.startswith('+++'))+'\n'
        fixture=r'''
#include "lc2_lifetime.h"
#include <assert.h>
int main(void) {
 struct lc2_lifetime l={0};uint64_t old,unknown,reused;
 const struct lc2_life_identity identity={.share_group_epoch=1,.name=9,.kind=1};
 assert(lc2_life_begin_scoped(&l,&identity,1,100,&old));
 assert(lc2_life_commit_gl_result(&l,old,0));
 assert(lc2_life_begin_scoped(&l,&identity,1,200,&unknown));
 assert(lc2_life_mark_unknown(&l,unknown));
 assert(lc2_life_find(&l,old)->live);
 assert(lc2_life_find(&l,unknown)->pending && lc2_life_find(&l,unknown)->outcome_unknown && !lc2_life_find(&l,unknown)->lost);
 assert(l.retained_bytes==100 && l.reserved_bytes==200);
 assert(!lc2_life_commit_gl_result(&l,unknown,0));
 assert(!lc2_life_use(&l,unknown,1,1) && !lc2_life_can_delete(&l,unknown));
 assert(!lc2_life_begin_scoped(&l,&identity,1,300,&reused));
 assert(l.retained_bytes==100 && l.reserved_bytes==200);
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            (p/'lc2_lifetime.h').write_text(header)
            (p/'test.c').write_text(fixture)
            built=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-I',d,
                                  str(p/'test.c'),'-o',str(p/'test')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            ran=subprocess.run([str(p/'test')],capture_output=True,text=True)
            self.assertEqual(ran.returncode,0,ran.stderr)

    def test_gl_error_code_rolls_back_only_failed_respec_intent(self):
        patch=(ROOT/'runtime/lamentum-adapter.patch').read_text()
        marker='diff --git a/native/lc2_lifetime.h b/native/lc2_lifetime.h'
        self.assertIn(marker,patch)
        block=patch.split(marker,1)[1].split('diff --git ',1)[0]
        header='\n'.join(line[1:] for line in block.splitlines()
                          if line.startswith('+') and not line.startswith('+++'))+'\n'
        fixture=r'''
#include "lc2_lifetime.h"
#include <assert.h>
#include <stdint.h>
static uint32_t mock_gl_storage(uint32_t error) { return error; }
int main(void) {
 struct lc2_lifetime l={0};uint64_t old,replacement,failed;
 const struct lc2_life_identity identity={.share_group_epoch=1,.name=9,.kind=1};
 assert(lc2_life_begin_scoped(&l,&identity,1,100,&old));
 assert(lc2_life_commit_gl_result(&l,old,mock_gl_storage(0))); /* GL_NO_ERROR */
 assert(l.retained_bytes==100 && l.reserved_bytes==0);
 assert(lc2_life_begin_scoped(&l,&identity,1,200,&failed));
 assert(l.retained_bytes==100 && l.reserved_bytes==200);
 assert(!lc2_life_commit_gl_result(&l,failed,mock_gl_storage(0x0505))); /* GL_OUT_OF_MEMORY */
 assert(l.retained_bytes==100 && l.reserved_bytes==0);
 assert(lc2_life_find(&l,old)->live && lc2_life_find(&l,failed)==NULL);
 assert(lc2_life_begin_scoped(&l,&identity,1,300,&replacement));
 assert(lc2_life_commit_gl_result(&l,replacement,mock_gl_storage(0)));
 assert(l.retained_bytes==400 && l.reserved_bytes==0);
 assert(lc2_life_find(&l,old)->object_generation==lc2_life_find(&l,replacement)->object_generation);
 assert(!lc2_life_can_delete(&l,old)); /* the old name still owns the replacement */
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            (p/'lc2_lifetime.h').write_text(header)
            (p/'test.c').write_text(fixture)
            built=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-I',d,
                                  str(p/'test.c'),'-o',str(p/'test')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            ran=subprocess.run([str(p/'test')],capture_output=True,text=True)
            self.assertEqual(ran.returncode,0,ran.stderr)

    def test_lost_share_group_epoch_tombstones_are_not_recycled(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        marker = 'diff --git a/native/lc2_lifetime.h b/native/lc2_lifetime.h'
        self.assertIn(marker, patch)
        block = patch.split(marker, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in block.splitlines()
                            if line.startswith('+') and not line.startswith('+++')) + '\n'
        fixture = r'''
#include "lc2_lifetime.h"
#include <assert.h>
int main(void) {
 struct lc2_lifetime l={0};uint64_t token;
 const struct lc2_life_identity old={.share_group_epoch=77,.name=1,.kind=1};
 assert(lc2_life_begin_scoped(&l,&old,1,1,&token));
 assert(lc2_life_commit(&l,token,1));
 assert(lc2_life_retire(&l,token) && lc2_life_detach(&l,token));
 assert(lc2_life_can_delete(&l,token) && lc2_life_deleted(&l,token,1));
 lc2_life_share_group_lost(&l,77);
 for(uint64_t i=0;i<LC2_LIFE_CAP-1;i++) {
  const struct lc2_life_identity other={.share_group_epoch=1000+i,.name=i+1,.kind=1};
  assert(lc2_life_begin_scoped(&l,&other,1,1,&token));
  assert(lc2_life_commit(&l,token,1));
 }
 const struct lc2_life_identity reused={.share_group_epoch=77,.name=2,.kind=1};
 assert(!lc2_life_begin_scoped(&l,&reused,1,1,&token));
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            (p/'lc2_lifetime.h').write_text(header)
            (p/'test.c').write_text(fixture)
            built=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-I',d,
                                  str(p/'test.c'),'-o',str(p/'test')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            ran=subprocess.run([str(p/'test')],capture_output=True,text=True)
            self.assertEqual(ran.returncode,0,ran.stderr)

    def test_context_epochs_scope_identical_names_and_context_loss(self):
        patch = (ROOT / 'runtime/lamentum-adapter.patch').read_text()
        marker = 'diff --git a/native/lc2_lifetime.h b/native/lc2_lifetime.h'
        self.assertIn(marker, patch)
        block = patch.split(marker, 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in block.splitlines()
                            if line.startswith('+') and not line.startswith('+++')) + '\n'
        fixture = r'''
#include "lc2_lifetime.h"
#include <assert.h>
int main(void) {
 struct lc2_lifetime l={0};uint64_t shared_a,shared_b,local_a,local_b,local_new,stale;
 const struct lc2_life_identity shared={.share_group_epoch=1,.name=7,.kind=1};
 const struct lc2_life_identity ctx_a={.share_group_epoch=1,.context_epoch=11,.name=7,.kind=3};
 const struct lc2_life_identity ctx_b={.share_group_epoch=1,.context_epoch=12,.name=7,.kind=3};
 const struct lc2_life_identity ctx_new={.share_group_epoch=1,.context_epoch=13,.name=7,.kind=3};
 assert(lc2_life_begin_scoped(&l,&shared,1,64,&shared_a));
 assert(lc2_life_commit(&l,shared_a,1));
 assert(lc2_life_begin_scoped(&l,&shared,1,64,&shared_b));
 assert(lc2_life_commit(&l,shared_b,1));
 assert(lc2_life_find(&l,shared_a)->object_generation==lc2_life_find(&l,shared_b)->object_generation);
 assert(lc2_life_begin_scoped(&l,&ctx_a,1,32,&local_a));
 assert(lc2_life_commit(&l,local_a,1));
 assert(lc2_life_begin_scoped(&l,&ctx_b,1,48,&local_b));
 assert(lc2_life_commit(&l,local_b,1));
 assert(lc2_life_find(&l,local_a)->object_generation!=lc2_life_find(&l,local_b)->object_generation);
 uint64_t retained=l.retained_bytes;
 lc2_life_context_lost(&l,1,11);
 assert(lc2_life_find(&l,local_a)->lost);
 assert(!lc2_life_find(&l,local_b)->lost && !lc2_life_find(&l,shared_a)->lost);
 assert(l.retained_bytes==retained);
 assert(!lc2_life_use(&l,local_a,1,1));
 assert(lc2_life_use(&l,local_b,1,1) && lc2_life_use(&l,shared_a,1,1));
 assert(!lc2_life_begin_scoped(&l,&ctx_a,1,8,&stale));
 assert(lc2_life_begin_scoped(&l,&ctx_new,1,16,&local_new));
 assert(lc2_life_commit(&l,local_new,1));
 assert(lc2_life_find(&l,local_new)->object_generation!=lc2_life_find(&l,local_a)->object_generation);
 assert(l.retained_bytes==retained+16);
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / 'lc2_lifetime.h').write_text(header)
            (p / 'test.c').write_text(fixture)
            built = subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-I',d,
                                    str(p/'test.c'),'-o',str(p/'test')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            ran = subprocess.run([str(p/'test')],capture_output=True,text=True)
            self.assertEqual(ran.returncode,0,ran.stderr)

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
 lc2_life_share_group_lost(&l,1);
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
