"""B1 pre-refusal owner receipt: bounded, opt-in, no guest memory reads.

The receipt has to exist BEFORE the budget refusal, must fire at most once per
owner, and must never dereference guest memory (the refusal happens under memory
pressure). These tests compile the real function out of the public overlay
against stubs, so the contract is executable rather than prose.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
MARK_START = '/* LC2_BC_OWNER_RECEIPT_BEGIN */'
MARK_END = '/* LC2_BC_OWNER_RECEIPT_END */'


def overlays():
    text = (REPO / 'runtime/lamentum-adapter.patch').read_text()
    added = '\n'.join(line[1:] for line in text.splitlines()
                      if line.startswith('+') and not line.startswith('+++'))
    return text, added


def receipt_body(added):
    if MARK_START not in added or MARK_END not in added:
        return None
    return added.split(MARK_START, 1)[1].split(MARK_END, 1)[0]


class OwnerReceiptTests(unittest.TestCase):
    def compile_and_run(self, body, calls, vary=False):
        source = r'''
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
struct nvn_texture_builder {uint64_t offset;unsigned width,height,depth,levels,target,format,flags,samples,swizzle[4];};
struct nvn_pool {uint64_t object,address,size,generation;unsigned flags;};
struct nvn_texture {uint64_t object,id,size,t2_budget_bytes;unsigned lc2_bc_pending,t2_page;
  struct nvn_texture_builder b;struct nvn_pool *pool;unsigned name,depth_buffer,draws,composition_target_seen,references;};
static uint64_t nvn_caller=0x1234;
struct {uint64_t live_bytes,peak_bytes,count;} t2_texture_budget={1<<20,2<<20,7};
static int mutex_locks;
static void t2_texture_budget_lock(void){mutex_locks++;}
static void t2_texture_budget_unlock(void){}
static int emitted;
static void lc2_bc_receipt_emit(const char *text,unsigned long long owner){printf("%llu:%s\n",owner,text);emitted++;}
''' + body + r'''
int main(int argc,char **argv) {
  (void)argc;
  struct nvn_pool pool={.object=0xabc,.address=0x100000,.size=0x400000,.generation=3,.flags=0};
  struct nvn_texture t={.object=0x77,.id=295,.size=0x18000000,.lc2_bc_pending=1,.pool=&pool,.name=4,
    .b={.width=8192,.height=8192,.depth=1,.levels=1,.target=1,.format=0x45,.samples=1,
        .swizzle={2,3,4,5}}};
  struct nvn_texture view=t;view.id=296;view.object=0x78;
  unsigned calls=(unsigned)atoi(argv[1]);
  int vary=argc>2 && argv[2][0]=='v';
  for(unsigned i=0;i<calls;i++) {view.id=296+i;if(vary)t.id=295+i;
    lc2_bc_owner_receipt(&view,&t,16,0x1401,4,(uint64_t)256<<20);}
  printf("emitted=%d overflow=%u locks=%d\n",emitted,lc2_bc_receipts.overflow,mutex_locks);
  return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_file = root / 'receipt.c'
            source_file.write_text(source)
            binary = root / 'receipt'
            flags = os.environ.get('LC2_RECEIPT_TEST_CFLAGS', '').split()
            built = subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', *flags,
                                    str(source_file), '-o', str(binary)],
                                   text=True, capture_output=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            ran = subprocess.run([str(binary), str(calls)] + (['vary'] if vary else []), capture_output=True, text=True, timeout=20,
                                 env=dict(os.environ, LC2_BC_OWNER_RECEIPT='1'))
            self.assertEqual(ran.returncode, 0, ran.stderr)
            return ran.stdout

    def test_receipt_is_opt_in_and_silent_when_disabled(self):
        _, added = overlays()
        body = receipt_body(added)
        self.assertIsNotNone(body, 'B1 pre-refusal owner receipt missing from overlay')
        assert body is not None
        self.assertIn('LC2_BC_OWNER_RECEIPT', body)
        source = r'''
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
struct nvn_texture_builder {uint64_t offset;unsigned width,height,depth,levels,target,format,flags,samples,swizzle[4];};
struct nvn_pool {uint64_t object,address,size,generation;unsigned flags;};
struct nvn_texture {uint64_t object,id,size,t2_budget_bytes;unsigned lc2_bc_pending,t2_page;
  struct nvn_texture_builder b;struct nvn_pool *pool;unsigned name,depth_buffer,draws,composition_target_seen,references;};
static uint64_t nvn_caller;
struct {uint64_t live_bytes,peak_bytes,count;} t2_texture_budget;
static int mutex_locks;static void t2_texture_budget_lock(void){mutex_locks++;}static void t2_texture_budget_unlock(void){}
static int emitted;static void lc2_bc_receipt_emit(const char *text,unsigned long long owner){(void)text;(void)owner;emitted++;}
''' + body + r'''
int main(void){struct nvn_texture t={.id=295,.b={.width=8192,.height=8192,.levels=1,.target=1,.format=0x45}};
lc2_bc_owner_receipt(&t,&t,16,0x1401,4,1);printf("emitted=%d\n",emitted);return 0;}
'''
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'off.c').write_text(source)
            binary = root / 'off'
            built = subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                                    str(root / 'off.c'), '-o', str(binary)],
                                   text=True, capture_output=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            for value, expected in (('0', 0), ('', 0), ('1', 1)):
                env = dict(os.environ)
                env.pop('LC2_BC_OWNER_RECEIPT', None)
                if value:
                    env['LC2_BC_OWNER_RECEIPT'] = value
                ran = subprocess.run([str(binary)], capture_output=True, text=True, timeout=20, env=env)
                self.assertEqual(ran.returncode, 0, ran.stderr)
                self.assertIn('emitted=%d' % expected, ran.stdout,
                              'LC2_BC_OWNER_RECEIPT=%r must mean enabled only when "1"' % value)

    def test_receipt_fires_once_per_owner_and_records_every_required_field(self):
        _, added = overlays()
        body = receipt_body(added)
        assert body is not None
        first = self.compile_and_run(body, 3)
        self.assertEqual(first.count('295:'), 1, first)
        self.assertIn('LC2_BC_OWNER_RECEIPT owner-id=%llu %s', added,
                      'the real emitter must name the owner in its prefix')
        for field in ('mode=pre-refusal', 'view-id=296', 'owner-object=0x77',
                      'levels=1', 'width=8192', 'height=8192', 'format=0x45', 'block-bytes=16',
                      'upload-type=0x1401', 'output-bpp=4', 'prospective-charge-bytes=268435456',
                      'level=0', 'decoded-bytes=268435456', 'caller=0x1234',
                      'immutable=unproven', 'source-hash=not-read',
                      'gl-allocation=not-attempted', 'guest-memory-read=none'):
            self.assertIn(field, first, field)
        self.assertIn('emitted=1', first)

    def test_receipt_bounded_and_never_reads_guest_memory(self):
        _, added = overlays()
        body = receipt_body(added)
        assert body is not None
        self.assertNotIn('nvn_pointer(', body, 'receipt must not dereference guest memory')
        self.assertNotIn('memcmp(', body)
        many = self.compile_and_run(body, 40, vary=True)
        self.assertIn('overflow=1', many, 'bounded receipt must flag overflow, not grow unbounded')
        self.assertLessEqual(many.count(':'), 16, many)

    def test_receipt_precedes_the_budget_charge_in_the_admission_path(self):
        patch, added = overlays()
        admission = added.split('static void lc2_bc_reserve_first_use(', 1)[1]
        admission = admission.split('LC2_BC_RESERVE_FIRST_USE_END', 1)[0]
        self.assertIn('lc2_bc_owner_receipt(', admission)
        self.assertLess(admission.index('lc2_bc_owner_receipt('),
                        admission.index('t2_texture_budget_add('),
                        'the receipt must be emitted before the charge can refuse')


if __name__ == '__main__':
    unittest.main()
