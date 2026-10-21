"""Same-run descriptor observations; absence is NOT a physical refund receipt."""
import unittest
from storage_retention import track


class RetentionTests(unittest.TestCase):
    def sample(self, size=200, text=' 1000, 2000, 2000, c07e, Native\n', ctx='17_1', uuid='run-A'):
        return dict(run_uuid=uuid, boot_id='boot', pid=17, starttime=42,
                    log_before=dict(dev=1, ino=2, size=size), t=1.0,
                    driver={ctx: dict(mem_allocs=text)})

    def test_present_then_absent_is_not_claimed_as_physical_free(self):
        a=self.sample();b=self.sample(text='Zone name: SAME_VA:\n');b['t']=2.0
        r=track([a,b], marker_end=100, addresses=['1000'])
        self.assertEqual([x['commits']['1000'] for x in r['observations']], [8192,None])
        self.assertIsNone(r['physical_refund_bytes'])

    def test_pre_marker_samples_do_not_count_as_post_upload(self):
        r=track([self.sample(size=50),self.sample()],marker_end=100,addresses=['1000'])
        self.assertEqual(len(r['observations']),1)

    def test_foreign_process_or_context_is_refused(self):
        for foreign in [self.sample(uuid='run-B'),self.sample(ctx='17_2')]:
            with self.assertRaises(ValueError):
                track([self.sample(),foreign],marker_end=100,addresses=['1000'])

    def test_missing_metadata_does_not_mean_descriptor_disappeared(self):
        s=self.sample();s['driver']['17_1']['mem_allocs']='[Errno 2] missing'
        with self.assertRaises(ValueError):
            track([s],marker_end=100,addresses=['1000'])
