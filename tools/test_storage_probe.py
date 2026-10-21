"""Standalone C tests for metadata parsing/delta, not GPU allocation evidence."""
import subprocess
import tempfile
from pathlib import Path
import unittest

PATCH = Path(__file__).resolve().parents[1] / 'runtime/lamentum-adapter.patch'


class StorageProbeTests(unittest.TestCase):
    def test_native_metadata_hex_and_growth_are_not_size_guesses(self):
        added = '\n'.join(line[1:] for line in PATCH.read_text().splitlines()
                          if line.startswith('+') and not line.startswith('+++'))
        self.assertIn('/* LC2_STORAGE_PROBE_BEGIN */', added, 'missing bounded storage probe')
        header = added.split('/* LC2_STORAGE_PROBE_BEGIN */',1)[1].split('/* LC2_STORAGE_PROBE_END */',1)[0]
        source = r'''
#include "lc2_storage_probe.h"
int main(void) {
 struct lc2_storage_row r={0};
 if(!lc2_storage_parse(" 5ef3e00000, 3564000, 3564000, c07e, Native", &r))return 1;
 if(r.va!=0x5ef3e00000ULL || r.commit!=0x3564000ULL || !r.native)return 2;
 struct lc2_storage_row old[2]={{r.va,r.commit,1},{0x1234,99,1}};
 if(lc2_storage_previous(old,2,r.va)!=r.commit)return 3;
 if(lc2_storage_previous(old,2,0x9999)!=0)return 4;
 if(lc2_storage_parse("Zone name: SAME_VA:",&r))return 5;
 if(!lc2_storage_parse(" 1000, 8000, 2000, c23e, Imported UMM",&r) || r.native)return 6;
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory);(p/'test.c').write_text(source);(p/'lc2_storage_probe.h').write_text(header)
            build=subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-function',
                                  '-I',str(p),str(p/'test.c'),'-o',str(p/'test')],capture_output=True,text=True)
            self.assertEqual(build.returncode,0,build.stderr)
            run=subprocess.run([str(p/'test')],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
