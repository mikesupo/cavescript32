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

The suite has not been claimed to pass on Windows/macOS or a hosted runner until
an actual run supplies that evidence. An unrun workflow is not a result. Private
Actions allowance must be checked before triggering; no paid overage authorized.
The purpose-written summary contains no private review correspondence or raw logs.
