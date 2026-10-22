"""Execute the real T2 pre-allocation wrapper extracted from the public overlay."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATCH = ROOT / 'runtime/lamentum-adapter.patch'

PREFIX = r'''
#include <assert.h>
#include <errno.h>
#include <setjmp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "lc2_gl_storage.h"
struct t2_meminfo {unsigned long available_kib,swap_total_kib,swap_free_kib,cma_free_kib;unsigned cma_known;};
static struct {unsigned floor_mib;} t2_memwatch;
struct t2_storage_admission_stats {volatile uint64_t checks,allowed,refused;volatile unsigned margin_known,margin_mib;};
static struct t2_storage_admission_stats t2_storage_admission;
static struct t2_meminfo sample;
static int sample_error,reports,stop_status;
static char stop_reason[96],log_buffer[2048];static size_t log_size;
static jmp_buf stop_env;
static void t2_memwatch_configure(void) {}
static int t2_meminfo_read(struct t2_meminfo *out) {
    if(sample_error)return -1;
    *out=sample;return sample.available_kib?0:-1;
}
static const char *lc2_life_events_run_id(void){return "fixture-run";}
static uint64_t lc2_life_events_now_ns(void){return 1234;}
static void lc2_life_write(int fd,const char *data,size_t size) {
    (void)fd;assert(size<sizeof(log_buffer)-log_size);
    memcpy(log_buffer+log_size,data,size);log_size+=size;log_buffer[log_size]=0;
}
static void t2_storage_admission_report(void){reports++;}
static void t2_storage_admit(uint64_t,uint64_t,uint64_t,uint64_t);
static void stop(const char *why,uint64_t caller,uint64_t detail,int status) {
    (void)caller;(void)detail;snprintf(stop_reason,sizeof(stop_reason),"%s",why);
    stop_status=status;longjmp(stop_env,1);
}
static void reset_case(unsigned long available,unsigned long cma,unsigned cma_known) {
    memset(&t2_storage_admission,0,sizeof(t2_storage_admission));
    sample=(struct t2_meminfo){.available_kib=available,.cma_free_kib=cma,.cma_known=cma_known};
    sample_error=0;reports=0;stop_status=0;stop_reason[0]=0;log_size=0;log_buffer[0]=0;
}
static int admit(uint64_t gl_bytes,uint64_t scratch_bytes) {
    if(!setjmp(stop_env)){t2_storage_admit(gl_bytes,scratch_bytes,7,99);return 0;}
    return 1;
}
'''

SUFFIX = r'''
int main(void) {
    const uint64_t gl=8ULL<<20,scratch=2ULL<<20;
    t2_memwatch.floor_mib=96;
    reset_case(112UL*1024,14UL*1024,1);
    unsetenv("T2_STORAGE_MARGIN_MIB");
    assert(admit(gl,scratch)==1 && !strcmp(stop_reason,"T2_STORAGE_ADMISSION") && stop_status==26);
    assert(strstr(log_buffer,"reason=policy-unset") && t2_storage_admission.checks==1 &&
           t2_storage_admission.refused==1 && t2_storage_admission.allowed==0 && reports==1);

    setenv("T2_STORAGE_MARGIN_MIB","4",1);
    reset_case(112UL*1024,14UL*1024,1);
    assert(admit(gl,scratch)==0 && t2_storage_admission.checks==1 &&
           t2_storage_admission.allowed==1 && t2_storage_admission.refused==0 && log_size==0);

    reset_case(112UL*1024,13UL*1024,1);
    assert(admit(gl,scratch)==1 && strstr(log_buffer,"reason=cmafree-margin") &&
           strstr(log_buffer,"required-cma-bytes=14680064"));

    reset_case(109UL*1024,14UL*1024,1);
    assert(admit(gl,scratch)==1 && strstr(log_buffer,"reason=memavailable-floor") &&
           strstr(log_buffer,"required-available-bytes=115343360"));

    reset_case(112UL*1024,0,0);
    assert(admit(gl,scratch)==1 && strstr(log_buffer,"reason=meminfo-unavailable") &&
           strstr(log_buffer,"cma-known=0"));

    setenv("T2_STORAGE_MARGIN_MIB","0",1);
    reset_case(112UL*1024,14UL*1024,1);
    assert(admit(gl,scratch)==1 && strstr(log_buffer,"reason=policy-invalid"));

    setenv("T2_STORAGE_MARGIN_MIB","4",1);
    t2_memwatch.floor_mib=0;
    reset_case(112UL*1024,14UL*1024,1);
    assert(admit(gl,scratch)==1 && strstr(log_buffer,"reason=floor-disabled"));

    t2_memwatch.floor_mib=96;
    reset_case(112UL*1024,14UL*1024,1);
    assert(admit(UINT64_MAX,1)==1 && strstr(log_buffer,"reason=size-overflow") &&
           strstr(log_buffer,"requirements-known=0"));
    puts("T2_STORAGE_ADMISSION_WRAPPER_OK");return 0;
}
'''


def overlay_added_file(patch, name):
    marker = f'diff --git a/native/{name} b/native/{name}\n'
    if marker not in patch:
        raise AssertionError(f'{name} missing from overlay')
    block = patch.split(marker, 1)[1].split('\ndiff --git ', 1)[0]
    return '\n'.join(line[1:] for line in block.splitlines()
                      if line.startswith('+') and not line.startswith('+++')) + '\n'


def overlay_added_function(patch, path, signature):
    marker = f'diff --git a/{path} b/{path}\n'
    if marker not in patch:
        raise AssertionError(f'{path} missing from overlay')
    block = patch.split(marker, 1)[1].split('\ndiff --git ', 1)[0]
    added = '\n'.join(line[1:] for line in block.splitlines()
                       if line.startswith('+') and not line.startswith('+++'))
    start = added.find(signature)
    if start < 0:
        raise AssertionError(f'{signature} missing from {path} overlay additions')
    brace = added.find('{', start)
    if brace < 0:
        raise AssertionError(f'{signature} body missing')
    depth = 0
    in_string = False
    escaped = False
    for pos in range(brace, len(added)):
        ch = added[pos]
        if in_string:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return added[start:pos + 1] + '\n'
    raise AssertionError(f'{signature} body is not brace-balanced')


class T2AdmissionTests(unittest.TestCase):
    def test_margin_meminfo_floor_and_overflow_fail_closed(self):
        patch = PATCH.read_text()
        header = overlay_added_file(patch, 'lc2_gl_storage.h')
        function = overlay_added_function(patch, 'native/t2_memwatch.h',
                                          'static void t2_storage_admit(')
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / 'lc2_gl_storage.h').write_text(header)
            (root / 'fixture.c').write_text(PREFIX + function + SUFFIX)
            binary = root / 'admission'
            built = subprocess.run(['cc', '-std=gnu11', '-D_POSIX_C_SOURCE=200809L',
                                    '-Wall', '-Wextra', '-Werror', '-I', str(root),
                                    str(root / 'fixture.c'), '-o', str(binary)],
                                   capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            ran = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
            self.assertEqual(ran.returncode, 0, ran.stderr)
            self.assertIn('T2_STORAGE_ADMISSION_WRAPPER_OK', ran.stdout)


if __name__ == '__main__':
    unittest.main()
