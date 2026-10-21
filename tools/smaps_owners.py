"""Read-only pathname attribution; RSS is not synonymous with image residency."""
import re
from collections import defaultdict

HEADER = re.compile(r'^([0-9a-f]+)-([0-9a-f]+)\s+(\S+)\s+([0-9a-f]+)\s+(\S+)\s+(\d+)\s*(.*)$')
FIELDS = ('Rss', 'Pss', 'Anonymous', 'Swap', 'Private_Clean', 'Private_Dirty')


def summarise(text):
    owners = defaultdict(lambda: dict(mappings=0, **{k: 0 for k in FIELDS}))
    current = None
    for line in text.splitlines():
        header = HEADER.match(line)
        if header:
            current = header[7] or '[anonymous]'
            owners[current]['mappings'] += 1
        elif current is not None:
            field = re.fullmatch(r'(\w+):\s+(\d+) kB', line)
            if field and field[1] in FIELDS:
                owners[current][field[1]] += int(field[2])
    return {'units': 'KiB', 'scope': 'one smaps read; non-atomic',
            'limitations': 'Pathname is not allocator identity; file VMAs can contain anonymous COW pages. Device mappings are not ordinary reclaimable files. No drop safety inferred.',
            'owners': [dict(path=path, **values) for path, values in
                       sorted(owners.items(), key=lambda pair: (-pair[1]['Rss'], pair[0]))],
            'totals': {key: sum(v[key] for v in owners.values()) for key in FIELDS}}
