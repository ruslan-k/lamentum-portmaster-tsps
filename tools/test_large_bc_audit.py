import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class LargeBcAuditTests(unittest.TestCase):
    def test_actual_added_c_logger_is_bounded_opt_in_and_keeps_mip_metadata(self):
        patch = (Path(__file__).resolve().parents[1] / 'runtime/lamentum-adapter.patch').read_text()
        added = '\n'.join(line[1:] for line in patch.splitlines() if line.startswith('+') and not line.startswith('+++'))
        begin = added.index('static void lc2_large_bc_reserve_audit(')
        end = added.index('/* LC2_LARGE_BC_AUDIT_END */', begin)
        logger = added[begin:end]
        source = r'''
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
struct nvn_texture_builder { uint64_t offset; unsigned flags,target,width,height,depth,levels,format,samples,swizzle[4]; };
struct nvn_pool { uint64_t object,address,size,generation; uint32_t flags; };
struct nvn_texture { uint64_t object,id,size,levels[14],cpu_generation,t2_budget_bytes;
 struct nvn_texture_builder b; struct nvn_pool *pool;
 unsigned name,depth_buffer,lc2_bc_pending,draws,composition_target_seen,references; };
static struct {int texture_limit;} nvn_device={16384};
static uint64_t nvn_caller=0x123;
static void *eglGetCurrentContext(void){return (void*)0x456;}
''' + logger + r'''
int main(void){
 struct nvn_pool p={.object=7,.address=0x3000,.size=0x9000,.generation=11,.flags=0xa4};
 struct nvn_texture t={.id=295,.object=0x1000,.size=0x8000,.pool=&p,.name=9,.lc2_bc_pending=1,
  .b={.width=8192,.height=8192,.depth=1,.levels=2,.target=1,.format=0x44},.levels={0,0x4000}};
 lc2_large_bc_reserve_audit(&t,&t,4,16,0x1401,0,268435456);
 lc2_large_bc_reserve_audit(&t,&t,4,16,0x1401,0,268435456);
 for(unsigned i=0;i<5;i++){t.id=296+i;lc2_large_bc_reserve_audit(&t,&t,4,16,0x1401,0,268435456);}
 puts("FIXTURE_BUDGET_REJECT: no GL allocation function exists in this fixture");
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            exe = str(Path(directory) / 'logger')
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-x', 'c', '-o', exe, '-'],
                           input=source, text=True, capture_output=True, check=True)
            for setting in ('0', '1'):
                env = dict(os.environ, LC2_LARGE_BC_AUDIT=setting)
                out = subprocess.check_output([exe], env=env, text=True)
                if setting == '0':
                    self.assertNotIn('LC2_BC_RESERVE_AUDIT ', out)
                else:
                    self.assertEqual(out.count('LC2_BC_RESERVE_AUDIT '), 4)
                    self.assertEqual(out.count('LC2_BC_AUDIT_LEVEL '), 8)
                    self.assertIn('mip-decoded-bytes=335544320', out)
                    self.assertIn('source-offset=16384', out)
                    self.assertLess(out.index('LC2_BC_RESERVE_AUDIT '), out.index('FIXTURE_BUDGET_REJECT'))


if __name__ == '__main__':
    unittest.main()
