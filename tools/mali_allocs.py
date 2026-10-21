"""Parse Mali mem_allocs metadata, not GPU memory contents.

Commit-size sums are descriptor totals, not alias-deduplicated physical residency.
Keep gpu_memory raw unless target-driver units/semantics have been established.
"""
import re
from collections import Counter

ROW = re.compile(r'\s*([0-9a-fA-F]+),\s*([0-9a-fA-F]+),\s*([0-9a-fA-F]+),\s*([0-9a-fA-F]+),\s*(.+)')


def summarise(text):
    totals = Counter()
    rows = 0
    for line in text.splitlines():
        match = ROW.fullmatch(line)
        if match:
            rows += 1
            totals[match[5]] += int(match[3], 16)
    return {'rows': rows, 'commit_descriptor_bytes_by_type': dict(totals),
            'deduplicated_physical_residency': None}
