# Manual CI and release-candidate boundaries

This source tree presents **2.0-rc.1**, a release candidate, not a stable or
ratified registry. A test run does not change the original v1 public reading key.
[Run 41382272362](https://github.com/mikesupo/cavescript32/actions/runs/41382272362) passed the four-job matrix for exact source commit
`e90cb6958e35b033cd2cae062af0330f29ffdc62`. Later credit/documentation changes leave code, keys, tests and
workflow unchanged but do not claim a new CI run for their own revision.

## Bounded manual workflow

`.github/workflows/tests.yml` has only `workflow_dispatch`, `contents: read`, no
saved checkout credentials, no secrets, no upload/release/deploy step and no retry
loop. It defines four jobs: Ubuntu/Windows/macOS with Python 3.12, plus Ubuntu
with Python 3.9. Each job has a five-minute timeout. The workflow is not automatic
on push or pull request. Trigger only within confirmed existing included private-
Actions allowance; do not enable paid overage or repeat runs without authority.

Pinned official actions, resolved 2 November 2026:
- `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (official v7 ref)
- `actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` (official v7 ref)

Verification used each official repository's tag-ref API, resolved commit object
and `action.yml` fetched at the exact commit. Both commit objects reported a
verified signature. This verifies identity/provenance, not a complete security
audit of action internals. `.github/action-pins.json` records the public evidence.
No account identifiers, tokens or private evidence captures are included.

## Before a stable release or future profile change

1. Review results for the exact candidate commit, including Windows and macOS.
   Do not call an unrun matrix a pass. Record any intentionally unsupported platform.
2. Deliberately identify the release audience, version and status; making source
   public is not equivalent to declaring a stable registry.
3. Finalize public version/profile naming and key metadata deliberately. Preserve
   both legacy v1 and draft1 compatibility; never silently change a pinned key.
4. Recheck mapping equality, license scope, checksums and the exact release assets.

The pinned key and CLI retain their original private-preparation status wording
as part of the frozen RC artifact. Repository visibility is separate; do not
silently edit a pinned key just to change a display label.

The owner already confirmed no outside reservations and delegated the applied
MIT software/data and CC BY 4.0 documentation choice. Those decisions need not be
re-asked. Preserved v1/third-party exceptions remain, and font work stays separate.
