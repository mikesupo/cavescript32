#!/usr/bin/env python3
"""Recompute the proposed deterministic allocation without changing any files."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def expected_assignments(baseline):
    old = {entry['ascii']: entry['pair'] for entry in baseline['characters']}
    free = [f'S{i:02}+S{j:02}' for i in range(32) for j in range(32)
            if f'S{i:02}+S{j:02}' not in old.values()]
    new = dict(zip((b for b in range(256) if b not in old), free))
    return {b: old.get(b, new.get(b)) for b in range(256)}


def main():
    baseline = json.loads((ROOT / 'baseline/v1.0/reference/cavescript32-v1.0-key.json').read_bytes())
    draft = json.loads((ROOT / 'reference/cavescript32-v2.0-rc.1-utf8-key.json').read_bytes())
    actual = {entry['byte']: entry['pair'] for entry in draft['assignments']}
    if expected_assignments(baseline) != actual:
        raise SystemExit('FAIL: draft differs from deterministic allocation')
    lock = json.loads((ROOT / 'baseline/BASELINE_LOCK.json').read_bytes())
    for name, expected in lock['files'].items():
        path = ROOT / 'baseline/v1.0' / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit(f'FAIL: baseline changed: {name}')
    print(f'PASS: 98 preserved + 158 unchanged extension assignments = 256 byte assignments; 768 unassigned; {len(lock["files"])} baseline source fixtures unchanged.')


if __name__ == '__main__':
    main()
