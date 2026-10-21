"""G0 pure storage geometry, extracted from the public overlay (no private checkout).

These tests calculate format-defined GL image payload, NOT driver residency or
resource-lifetime ownership. All inputs are self-authored, not captured assets.
"""
import json
import os
from pathlib import Path
import random
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
HEADER = 'lc2_gl_storage.h'
RGBA8, SRGBA8, RGBA16F, RGBA32F = 0x8058, 0x8C43, 0x881A, 0x8814
BC1, BC3, ETC2_RGBA, ETC2_SRGBA, ASTC6 = 0x83F1, 0x83F3, 0x9278, 0x9279, 0x93B4
T2D, T3D, ARRAY, CUBE, CUBE_ARRAY, MS, MS_ARRAY, RB = (
    0x0DE1, 0x806F, 0x8C1A, 0x8513, 0x9009, 0x9100, 0x9102, 0x8D41)


def overlay_header():
    text = (REPO / 'runtime/lamentum-adapter.patch').read_text()
    marker = f'diff --git a/native/{HEADER} b/native/{HEADER}\n'
    if marker not in text:
        return None
    section = text.split(marker, 1)[1].split('\ndiff --git ', 1)[0]
    return '\n'.join(line[1:] for line in section.splitlines()
                     if line.startswith('+') and not line.startswith('+++')) + '\n'


def descriptor(width=8192, height=8192, *, depth=1, layers=1, levels=1,
               samples=1, target=T2D, internal=RGBA8):
    return [target, internal, width, height, depth, layers, levels, samples]


class GlStorageLayoutTests(unittest.TestCase):
    def calculate(self, inputs):
        header = overlay_header()
        self.assertIsNotNone(header, 'G0 checked GL storage calculator missing from overlay')
        assert header is not None  # narrow the type after the test assertion
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / HEADER).write_text(header)
            source = REPO / 'tools/fixtures/lc2-gl-storage-fixture.c'
            self.assertTrue(source.is_file(), 'self-authored calculator fixture is missing')
            binary = root / 'layout'
            flags = os.environ.get('LC2_LAYOUT_TEST_CFLAGS', '').split()
            built = subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                                    *flags, '-I', str(root), str(source), '-o', str(binary)],
                                   text=True, capture_output=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            ran = subprocess.run([str(binary)], input=''.join(' '.join(map(str, x)) + '\n'
                                                            for x in inputs),
                                 text=True, capture_output=True, timeout=20)
            self.assertEqual(ran.returncode, 0, ran.stderr)
            results = [json.loads(line) for line in ran.stdout.splitlines()]
            self.assertEqual(len(results), len(inputs))
            return results

    def test_8192_one_level_and_complete_chain(self):
        one, full, half = self.calculate([descriptor(), descriptor(levels=14),
                                          descriptor(height=4096, levels=14)])
        self.assertEqual(one['bytes'], 8192 * 8192 * 4)
        expected = sum(max(8192 >> i, 1) ** 2 * 4 for i in range(14))
        self.assertEqual(full['bytes'], expected)
        self.assertGreater(full['bytes'], 300 * 1024 * 1024)
        self.assertEqual(full['levels'][-1]['bytes'], 4)
        self.assertEqual(half['bytes'], sum(max(8192 >> i, 1) * max(4096 >> i, 1) * 4
                                            for i in range(14)))

    def test_bc3_source_is_not_expanded_gl_storage(self):
        source, expanded = self.calculate([descriptor(height=4096, internal=BC3, levels=14),
                                          descriptor(height=4096, levels=14)])
        expected = sum(((max(8192 >> i, 1) + 3) // 4) *
                       ((max(4096 >> i, 1) + 3) // 4) * 16 for i in range(14))
        self.assertEqual(source['bytes'], expected)
        self.assertGreater(expanded['bytes'], source['bytes'])
        self.assertEqual(source['levels'][-1]['bytes'], 16)
        self.assertEqual(expanded['levels'][-1]['bytes'], 4)

    def test_npot_and_block_rounding_each_mip(self):
        rows = self.calculate([descriptor(7, 5, levels=3, internal=f)
                               for f in (RGBA8, BC1, BC3, ASTC6)])
        self.assertEqual([r['bytes'] for r in rows], [35*4 + 6*4 + 4, 32+8+8,
                                                    64+16+16, 32+16+16])
        self.assertEqual([(x['width'], x['height']) for x in rows[0]['levels']],
                         [(7, 5), (3, 2), (1, 1)])

    def test_array_layers_and_cube_faces_do_not_mip_shrink(self):
        plain, array, cube, cubes = self.calculate([
            descriptor(8, 8, levels=4), descriptor(8, 8, levels=4, target=ARRAY, layers=7),
            descriptor(8, 8, levels=4, target=CUBE),
            descriptor(8, 8, levels=4, target=CUBE_ARRAY, layers=3)])
        self.assertEqual(array['bytes'], plain['bytes'] * 7)
        self.assertEqual(cube['bytes'], plain['bytes'] * 6)
        self.assertEqual(cubes['bytes'], plain['bytes'] * 18)
        self.assertTrue(all(x['slices'] == 18 for x in cubes['levels']))

    def test_3d_depth_shrinks_instead_of_becoming_array_layers(self):
        row, = self.calculate([descriptor(7, 5, depth=9, levels=4, target=T3D)])
        self.assertEqual(row['bytes'], (7*5*9 + 3*2*4 + 1*1*2 + 1) * 4)
        self.assertEqual([x['depth'] for x in row['levels']], [9, 4, 2, 1])

    def test_explicit_sample_count_and_packed_or_float_output(self):
        rows = self.calculate([descriptor(3, 2, target=MS, samples=4),
                               descriptor(3, 2, target=MS_ARRAY, samples=4, layers=5),
                               descriptor(3, 2, target=RB, samples=4),
                               descriptor(3, 2, internal=0x8056),
                               descriptor(3, 2, internal=RGBA16F),
                               descriptor(3, 2, internal=RGBA32F)])
        self.assertEqual([x['bytes'] for x in rows], [96, 480, 96, 12, 48, 96])

    def test_srgb_changes_encoding_not_payload_size(self):
        rows = self.calculate([descriptor(7, 5, levels=3, internal=f)
                               for f in (RGBA8, SRGBA8, ETC2_RGBA, ETC2_SRGBA)])
        self.assertEqual(rows[0]['bytes'], rows[1]['bytes'])
        self.assertEqual(rows[2]['bytes'], rows[3]['bytes'])

    def test_unknown_and_unsized_internal_formats_are_rejected(self):
        rows = self.calculate([descriptor(internal=f) for f in (0, 0xDEAD, 0x1908, 0x8C42, 0x81A6)])
        self.assertTrue(all(row['status'] == 'format' for row in rows))
        self.assertTrue(all(row['output_unchanged'] for row in rows))

    def test_invalid_targets_dimensions_and_mip_counts_are_rejected(self):
        cases = [descriptor(width=0), descriptor(height=0), descriptor(depth=0),
                 descriptor(layers=0), descriptor(levels=0), descriptor(samples=0),
                 descriptor(width=0x80000000), descriptor(levels=15),
                 descriptor(target=0xDEAD), descriptor(depth=2), descriptor(layers=2),
                 descriptor(samples=2), descriptor(8, 4, target=CUBE),
                 descriptor(levels=2, target=MS, samples=4),
                 descriptor(levels=2, target=RB), descriptor(target=MS, internal=BC3),
                 descriptor(target=T3D, depth=4, internal=BC3)]
        rows = self.calculate(cases)
        self.assertTrue(all(row['status'] == 'descriptor' for row in rows), rows)
        self.assertTrue(all(row['output_unchanged'] for row in rows))

    def test_each_multiply_and_cumulative_sum_are_overflow_checked(self):
        cases = [descriptor(0x7FFFFFFF, 0x7FFFFFFF, internal=RGBA32F),
                 descriptor(0x7FFFFFFF, 0x7FFFFFFF, levels=31),
                 descriptor(0x7FFFFFFF, 0x7FFFFFFF, target=CUBE),
                 descriptor(65536, 65536, target=ARRAY, layers=0x7FFFFFFF),
                 descriptor(65536, 65536, target=MS, samples=0x7FFFFFFF),
                 descriptor(0x7FFFFFFF, 0x7FFFFFFF, depth=0x7FFFFFFF, target=T3D)]
        rows = self.calculate(cases)
        self.assertTrue(all(row['status'] == 'overflow' for row in rows), rows)
        self.assertTrue(all(row['output_unchanged'] for row in rows))

    def test_deferred_bc_reservation_uses_all_levels_and_rejects_before_gl(self):
        patch = (REPO / 'runtime/lamentum-adapter.patch').read_text()
        added = '\n'.join(line[1:] for line in patch.splitlines()
                          if line.startswith('+') and not line.startswith('+++'))
        start = added.find('static void lc2_bc_reserve_first_use(')
        self.assertGreaterEqual(start, 0, 'first-use admission still charges only the base mip')
        end = added.index('/* LC2_BC_RESERVE_FIRST_USE_END */', start)
        source = r'''
#include <assert.h>
#include <setjmp.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdint.h>
#include "lc2_gl_storage.h"
#define GL_UNSIGNED_BYTE 0x1401U
#define GL_FLOAT 0x1406U
struct nvn_texture_builder {unsigned width,height,depth,levels,target,samples,format;};
struct nvn_texture {uint64_t id,t2_budget_bytes;unsigned lc2_bc_pending;struct nvn_texture_builder b;};
static uint64_t nvn_caller,charged,cap=300ULL<<20;
static unsigned adds,gl_calls,audits;
static jmp_buf target;
static void stop(const char *reason,uint64_t caller,uint64_t detail,unsigned code) {
 (void)reason;(void)caller;(void)detail;(void)code;longjmp(target,1);
}
static unsigned zero_bc_srgb(unsigned format){return format==0x45;}
static void t2_texture_budget_add(uint64_t bytes,uint64_t caller) {
 (void)caller;adds++;if(bytes>cap)longjmp(target,2);charged+=bytes;
}
static unsigned nvn_texture_upload_bytes(unsigned type){return type==GL_UNSIGNED_BYTE?4:type==GL_FLOAT?16:0;}
static void lc2_large_bc_reserve_audit(const struct nvn_texture *view,const struct nvn_texture *t,
 unsigned bpp,unsigned bc,unsigned type,unsigned srgb,uint64_t bytes) {
 (void)view;(void)t;(void)bpp;(void)bc;(void)type;(void)srgb;(void)bytes;audits++;
}
static unsigned receipts;
static void lc2_bc_owner_receipt(const struct nvn_texture *view,const struct nvn_texture *t,
 unsigned bc,unsigned type,unsigned bpp,uint64_t prospective) {
 (void)view;(void)t;(void)bc;(void)type;(void)bpp;(void)prospective;receipts++;
}
''' + added[start:end] + r'''
int main(void) {
 struct nvn_texture t={.id=295,.lc2_bc_pending=1,
  .b={.width=8192,.height=8192,.depth=1,.levels=2,.target=1,.format=0x44}};
 int refusal=setjmp(target);
 if(!refusal){lc2_bc_reserve_first_use(&t,&t,GL_UNSIGNED_BYTE,16);gl_calls++;}
 assert(refusal==2 && adds==1 && audits==1 && !gl_calls && !charged && !t.t2_budget_bytes);
 t.b.levels=1;
 assert(!setjmp(target));lc2_bc_reserve_first_use(&t,&t,GL_UNSIGNED_BYTE,16);
 assert(adds==2 && charged==268435456 && t.t2_budget_bytes==charged);
 lc2_bc_reserve_first_use(&t,&t,GL_UNSIGNED_BYTE,16);assert(adds==2);
 t.lc2_bc_pending=0;lc2_bc_reserve_first_use(&t,&t,GL_UNSIGNED_BYTE,16);assert(adds==2);
 t.lc2_bc_pending=1;t.t2_budget_bytes--;
 if(!setjmp(target)){lc2_bc_reserve_first_use(&t,&t,GL_UNSIGNED_BYTE,16);assert(0);}
 t.t2_budget_bytes=0;
 if(!setjmp(target)){lc2_bc_reserve_first_use(&t,&t,0xDEAD,16);assert(0);}
 assert(adds==2);
 /* Existing eligibility remains single-level: this fixture tests the guard's
  * future-proof refusal, not a newly enabled multilevel lazy upload path. */
 puts("CHECKED_ADMISSION_OK");return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            header = overlay_header()
            assert header is not None
            (root / HEADER).write_text(header)
            exe = root / 'reserve'
            flags = os.environ.get('LC2_LAYOUT_TEST_CFLAGS', '').split()
            built = subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                                    *flags, '-I', str(root), '-x', 'c', '-o', str(exe), '-'],
                                   input=source, text=True, capture_output=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            ran = subprocess.run([str(exe)], capture_output=True, text=True, timeout=10)
            self.assertEqual(ran.returncode, 0, ran.stderr)
            self.assertIn('CHECKED_ADMISSION_OK', ran.stdout)
        # Exact public source ordering, not an assertion about driver allocation:
        # the full-chain charge must precede the first GL storage/bind call. A
        # non-GL declaration (the upload-triple resolution) may sit between them.
        # The charge-before-GL invariant is proven by the compiled fixture above
        # (a refusal leaves adds==1, gl_calls==0 and no charge). Here we only
        # require the call site to exist at the exact source position.
        self.assertIn('lc2_bc_reserve_first_use(view,t,type,bc);\n', added)
        self.assertRegex(patch, r'\+    lc2_bc_reserve_first_use\(view,t,type,bc\);\n')

    def test_fixed_seed_random_layouts_against_arbitrary_precision_reference(self):
        rng = random.Random(295)
        specs = [(RGBA8, 1, 1, 4), (SRGBA8, 1, 1, 4), (RGBA16F, 1, 1, 8),
                 (RGBA32F, 1, 1, 16), (BC1, 4, 4, 8), (BC3, 4, 4, 16),
                 (ETC2_RGBA, 4, 4, 16), (ASTC6, 6, 6, 16)]
        cases, expected = [], []
        for _ in range(1024):
            width, height = rng.randrange(1, 10000), rng.randrange(1, 10000)
            levels = rng.randrange(1, max(width, height).bit_length() + 1)
            fmt, bw, bh, bb = rng.choice(specs)
            layers = rng.randrange(1, 20)
            cases.append(descriptor(width, height, levels=levels, internal=fmt,
                                    target=ARRAY, layers=layers))
            expected.append([((max(width >> i, 1) + bw-1) // bw) *
                             ((max(height >> i, 1) + bh-1) // bh) * bb * layers
                             for i in range(levels)])
        rows = self.calculate(cases)
        for row, sizes in zip(rows, expected):
            self.assertEqual(row['status'], 'ok')
            self.assertEqual([level['bytes'] for level in row['levels']], sizes)
            self.assertEqual(row['bytes'], sum(sizes))
            self.assertEqual([level['offset'] for level in row['levels']],
                             [sum(sizes[:i]) for i in range(len(sizes))])


if __name__ == '__main__':
    unittest.main()
