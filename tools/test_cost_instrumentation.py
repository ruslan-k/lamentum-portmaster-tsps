import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from cost_report import summarize

REPO = Path(__file__).resolve().parents[1]


def cost_header():
    patch = (REPO / 'runtime/lamentum-adapter.patch').read_text()
    section = patch.split('diff --git a/native/lc2_cost.h b/native/lc2_cost.h\n', 1)[1].split('\ndiff --git ', 1)[0]
    return '\n'.join(line[1:] for line in section.splitlines() if line.startswith('+') and not line.startswith('+++')) + '\n'


def build_run(source, enabled: str | None = '1'):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / 'lc2_cost.h').write_text(cost_header())
        if '#define _GNU_SOURCE' not in source:
            source = '#define _GNU_SOURCE\n' + source
        (root / 'driver.c').write_text(source)
        result = subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-pthread',
                                 '-I', str(root), str(root / 'driver.c'), '-o', str(root / 'driver')],
                                text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(result.stderr)
        env = dict(os.environ)
        env.pop('EXPECT_OFF', None)
        env.pop('LC2_SVC_COST', None)
        if enabled is not None:
            env['LC2_SVC_COST'] = enabled
        out = subprocess.run([str(root / 'driver')], env=env, capture_output=True, text=True, timeout=15)
        if out.returncode:
            raise AssertionError((out.returncode, out.stderr, out.stdout))
        return out.stdout


FAKE_CLOCK = r'''
#include <time.h>
#include <errno.h>
#include <assert.h>
struct tick {clockid_t clock; long ns; int failed;};
static struct tick ticks[] = {
 {CLOCK_MONOTONIC_RAW,10000,0},{CLOCK_THREAD_CPUTIME_ID,1000,0},
 {CLOCK_MONOTONIC_RAW,11000,0},{CLOCK_THREAD_CPUTIME_ID,1200,0},
 {CLOCK_MONOTONIC_RAW,12000,0},{CLOCK_THREAD_CPUTIME_ID,1500,0},
 {CLOCK_THREAD_CPUTIME_ID,1700,0},{CLOCK_MONOTONIC_RAW,14000,0},
 {CLOCK_THREAD_CPUTIME_ID,2200,0},{CLOCK_MONOTONIC_RAW,16000,0},
 {CLOCK_THREAD_CPUTIME_ID,4000,0},{CLOCK_MONOTONIC_RAW,20000,0}};
static unsigned next_tick;
static int fake_clock(clockid_t clock,struct timespec *out) {
 assert(next_tick<sizeof(ticks)/sizeof(ticks[0]));
 struct tick t=ticks[next_tick++];assert(t.clock==clock);
 if(t.failed){errno=EIO;return -1;}
 out->tv_sec=0;out->tv_nsec=t.ns;return 0;
}
#define LC2_COST_CLOCK fake_clock
#include "lc2_cost.h"
'''


class CostInstrumentationTests(unittest.TestCase):
    def test_no_clock_reads_and_no_report_when_off_or_unset_or_zero(self):
        source = FAKE_CLOCK + r'''
int main(void) {
 uint64_t token=lc2_cost_enter(LC2_COST_WAIT);assert(!token);
 lc2_cost_leave(LC2_COST_WAIT,token);lc2_cost_report_fd(1);
 assert(!next_tick && !lc2_cost_next);return 0;
}
'''
        for value in (None, '0', '2'):
            self.assertEqual(build_run(source, value), '')

    def test_all_short_lived_threads_and_sub_4096_tails_survive_exit(self):
        out = build_run((REPO / 'tools/fixtures/lc2-cost-fixture.c').read_text())
        report = summarize(out)
        self.assertTrue(report['coverage_complete'])
        self.assertEqual(report['reporting_threads'], 4)
        self.assertEqual(len(report['rows']), 12)
        self.assertEqual(report['classes']['svc0x1a-wait']['completed'], 12)
        self.assertEqual(report['classes']['bc-decode']['completed'], 12)
        self.assertEqual(report['classes']['svc0x1b-release']['completed'], 4)
        self.assertTrue(all(row['tid_starttime'] > 0 for row in report['rows']))
        self.assertFalse(report['profiler_overhead_qualified'])

    def test_true_exclusive_time_subtracts_direct_child_inclusive_time(self):
        source = FAKE_CLOCK + r'''
int main(void) {
 uint64_t a=lc2_cost_enter(LC2_COST_WAIT);
 uint64_t b=lc2_cost_enter(LC2_COST_AUDOUT7);
 uint64_t c=lc2_cost_enter(LC2_COST_BC_DECODE);
 lc2_cost_leave(LC2_COST_BC_DECODE,c);lc2_cost_leave(LC2_COST_AUDOUT7,b);
 lc2_cost_leave(LC2_COST_WAIT,a);assert(next_tick==12);
 lc2_cost_report_fd(1);return 0;
}
'''
        report = summarize(build_run(source))
        rows = {r['class_name']: r for r in report['rows']}
        self.assertEqual(rows['svc0x1a-wait']['cpu_exclusive_ns'], (4000-1000)-(2200-1200))
        self.assertEqual(rows['audout-cmd7']['cpu_exclusive_ns'], (2200-1200)-(1700-1500))
        self.assertEqual(sum(r['cpu_exclusive_ns'] for r in rows.values()), 4000-1000)
        self.assertEqual(sum(r['wall_exclusive_ns'] for r in rows.values()), 20000-10000)
        self.assertTrue(report['coverage_complete'])

    def test_raw_wall_never_gets_replaced_by_cpu_and_zero_is_a_valid_clock(self):
        source = FAKE_CLOCK.replace('10000,0', '0,0', 1).replace('1000,0', '0,0', 1)
        # Use only one enter/leave with a deliberately shorter raw-wall interval.
        source = source.replace('{CLOCK_MONOTONIC_RAW,11000,0},{CLOCK_THREAD_CPUTIME_ID,1200,0}',
                                '{CLOCK_THREAD_CPUTIME_ID,500,0},{CLOCK_MONOTONIC_RAW,100,0}', 1)
        source += r'''
int main(void) {uint64_t t=lc2_cost_enter(LC2_COST_WAIT);assert(t);
 lc2_cost_leave(LC2_COST_WAIT,t);lc2_cost_report_fd(1);return 0;}
'''
        row = summarize(build_run(source))['rows'][0]
        self.assertEqual(row['cpu_inclusive_ns'], 500)
        self.assertEqual(row['wall_inclusive_ns'], 100)
        self.assertEqual(row['wall_lt_cpu'], 1)

    def test_failed_clock_is_invalid_not_zero_cost_and_preserves_errno(self):
        source = FAKE_CLOCK.replace('10000,0', '10000,1', 1)
        source = source.replace('{CLOCK_MONOTONIC_RAW,11000,0},{CLOCK_THREAD_CPUTIME_ID,1200,0}',
                                '{CLOCK_THREAD_CPUTIME_ID,1500,0},{CLOCK_MONOTONIC_RAW,12000,0}', 1)
        source += r'''
int main(void) {errno=EDOM;uint64_t t=lc2_cost_enter(LC2_COST_WAIT);assert(errno==EDOM);
 errno=ERANGE;lc2_cost_leave(LC2_COST_WAIT,t);assert(errno==ERANGE);
 lc2_cost_report_fd(1);assert(errno==ERANGE);return 0;}
'''
        report = summarize(build_run(source))
        self.assertFalse(report['coverage_complete'])
        self.assertEqual(report['rows'][0]['invalid'], 1)
        self.assertEqual(report['rows'][0]['valid'], 0)

    def test_inflight_and_registry_overflow_are_explicit_incomplete_coverage(self):
        source = r'''
#define LC2_COST_THREADS 1
#include "lc2_cost.h"
#include <assert.h>
#include <pthread.h>
static void *worker(void *unused) {(void)unused;
 uint64_t t=lc2_cost_enter(LC2_COST_RELEASE);lc2_cost_leave(LC2_COST_RELEASE,t);return NULL;}
int main(void) {uint64_t t=lc2_cost_enter(LC2_COST_WAIT);assert(t);
 pthread_t p;assert(!pthread_create(&p,NULL,worker,NULL));assert(!pthread_join(p,NULL));
 lc2_cost_report_fd(1);return 0;}
'''
        text = build_run(source)
        report = summarize(text)
        self.assertIn('overflow=1', text)
        self.assertFalse(report['coverage_complete'])
        self.assertEqual(report['rows'][0]['entered'], 1)
        self.assertEqual(report['rows'][0]['completed'], 0)

    def test_nesting_overflow_invalidates_parent_instead_of_reporting_false_exclusive(self):
        text = build_run(r'''
#define LC2_COST_DEPTH 1
#include "lc2_cost.h"
#include <assert.h>
int main(void) {uint64_t a=lc2_cost_enter(LC2_COST_WAIT);
 uint64_t b=lc2_cost_enter(LC2_COST_BC_DECODE);assert(!b);
 lc2_cost_leave(LC2_COST_BC_DECODE,b);lc2_cost_leave(LC2_COST_WAIT,a);
 lc2_cost_report_fd(1);return 0;}
''')
        report = summarize(text)
        self.assertFalse(report['coverage_complete'])
        self.assertEqual(report['rows'][0]['nesting_errors'], 1)
        self.assertEqual(report['rows'][0]['invalid'], 1)

    def test_busy_snapshot_is_bounded_and_explicit_not_a_hang_or_false_zero(self):
        text = build_run(r'''
#include "lc2_cost.h"
int main(void) {uint64_t a=lc2_cost_enter(LC2_COST_WAIT);lc2_cost_leave(LC2_COST_WAIT,a);
 LC2_COST_STORE(&lc2_cost_slots[0].rows[LC2_COST_WAIT].seq,1);
 lc2_cost_report_fd(1);return 0;}
''')
        report = summarize(text)
        self.assertFalse(report['coverage_complete'])
        self.assertEqual(report['snapshot_footer']['incomplete_snapshots'], '1')
        self.assertTrue(report['aggregate_is_lower_bound'])

    def test_tid_reuse_is_a_distinct_generation_not_an_overwritten_class(self):
        source = r'''
#include "lc2_cost.h"
int main(void) {uint64_t a=lc2_cost_enter(LC2_COST_WAIT);lc2_cost_leave(LC2_COST_WAIT,a);
 lc2_cost_report_fd(1);return 0;}
'''
        lines = build_run(source).splitlines()
        begin = next(l for l in lines if l.startswith('LC2_COST_V2_BEGIN ')).replace('slots=1', 'slots=2')
        row = next(l for l in lines if l.startswith('LC2_COST_V2 '))
        start = int(dict(w.split('=', 1) for w in row.split()[1:])['tid_starttime'])
        reused = row.replace('tid_starttime=%d' % start, 'tid_starttime=%d' % (start+1))
        end = next(l for l in lines if l.startswith('LC2_COST_V2_END ')).replace('rows=1', 'rows=2')
        report = summarize('\n'.join((begin, row, reused, end)))
        self.assertEqual(report['reporting_threads'], 2)
        self.assertEqual(report['classes']['svc0x1a-wait']['completed'], 2)
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            summarize('\n'.join((begin, row, row, end)))

    def test_stat_comm_parser_uses_last_parenthesis(self):
        source = r'''
#include "lc2_cost.h"
#include <assert.h>
int main(void) {uint64_t n=0;
 assert(lc2_cost_parse_start("7 (name ) with spaces) R 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 4242 20",&n));
 assert(n==4242);assert(!lc2_cost_parse_start("7 broken",&n));return 0;}
'''
        build_run(source)

    def test_cumulative_snapshots_are_not_added_and_missing_report_is_not_zero(self):
        source = r'''
#include "lc2_cost.h"
int main(void) {uint64_t t=lc2_cost_enter(LC2_COST_WAIT);lc2_cost_leave(LC2_COST_WAIT,t);
 lc2_cost_report_fd(1);lc2_cost_report_fd(1);return 0;}
'''
        text = build_run(source)
        report = summarize(text)
        self.assertEqual(report['complete_snapshots'], 2)
        self.assertEqual(report['classes']['svc0x1a-wait']['completed'], 1)
        self.assertEqual(summarize('LC2_COST class=bc-decode calls=0\n')['status'], 'no_complete_report')
        with self.assertRaisesRegex(ValueError, 'GENERATION_AMBIGUOUS'):
            summarize(text + text)
        # A truncated final report cannot establish complete coverage.
        incomplete = summarize(text + 'LC2_COST_V2_BEGIN report=3 slots=1\n')
        self.assertFalse(incomplete['coverage_complete'])


if __name__ == '__main__':
    unittest.main()
