# Changelog

## 2.0-rc.1 — private candidate, 2 November 2026

- New current key/version/header/status with all 256 assignments unchanged.
- Preserve frozen draft1 key/hash and exact draft1 decoding/encoding compatibility.
- Default encode emits rc1; auto decode recognizes only exact rc1/draft1 envelopes.
  Explicit profile mismatch rejects even where payload mappings coincide.
- Retain all 98 v1 meanings and explicit headerless `--profile v1` compatibility.
- Add nine version-compatibility tests to the existing 31-test suite (40 total).
- Record current source-check/owner-reservation status in the new key; old key
  remains an immutable historical artifact, not the current status record.
- Clean repository includes ten immutable v1 source fixtures; full prior archives
  remain preserved separately. No PDFs, correspondence or private audit captures.
- MIT current software/data; CC BY 4.0 documentation, with explicit archival and
  third-party exceptions. Font remains separate.
- Pin official checkout/setup-python commits; bounded four-job manual CI only.
  No hosted result, public mapping change or publication is implied.

## 2.0-draft.1 — private prototype, 1 November 2026

Preserved 98 v1 assignments and proposed 158 additional byte assignments. Its
frozen key is retained exactly for interoperability. Earlier full private packages
and their validation records are not rewritten by this repository candidate.
