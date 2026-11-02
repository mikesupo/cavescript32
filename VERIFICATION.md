# Verification status — 2.0-rc.1

Local environment: Python 3.12.14 on Linux, 2 November 2026.

- **40 automated tests passed**, including all 1,112,064 Unicode scalars,
  27 exact vectors, 2,000 seeded byte strings, all 98 original mappings,
  all 158 extension assignments and all 768 unassigned pairs.
- Nine version tests cover distinct rc1/draft1 envelopes, preserved draft fixture,
  default rc1 encoding, automatic old-frame decoding, explicit profile mismatch,
  no output/file clobber on mismatch and unknown future-header rejection.
- Separate review reran all 40 tests and checked compatibility with the original
  draft tool plus all three key-integrity failure paths. No blocking issue found.
- All 10 selected v1 source fixtures and the frozen draft1 key/example match their
  original source bytes. The RC assignment table and unassigned list are identical
  to draft1; only current metadata/header/hash differ.
- Official action refs/commit objects/action files were resolved read-only and
  immutable SHAs pinned. No CI result is inferred from that provenance check.

## Hosted cross-platform result

[Run 41382272362](https://github.com/mikesupo/cavescript32/actions/runs/41382272362) completed successfully for exact source commit
`e90cb6958e35b033cd2cae062af0330f29ffdc62` in [mikesupo/cavescript32](https://github.com/mikesupo/cavescript32).
All four jobs passed: Ubuntu/Linux, Windows and macOS with Python 3.12,
plus Ubuntu/Linux with Python 3.9. A pre-run verification compared all 49 remote
files byte-for-byte with the clean candidate before the run.

This is a hosted-runner result, not a claim that a particular user's Windows or
Mac computer was accessed or tested. The subsequent preferred-credit, optional-
contact and license-scope clarification changes only documentation/metadata and
checksums. Code, keys, tests, examples, baseline fixtures and workflow remain
byte-identical to the green source commit; no fresh CI run for that later
documentation-only revision is implied. The exact revision boundary is retained
rather than labeling every future commit “tested.”
