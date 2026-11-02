# Manual CI and public-release hold

This source tree is a **private release candidate**, not a public registry update.
No published release, deployment or public mapping change follows automatically
from a test run. Windows/macOS results are pending until an actual run completes.

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

## Before public publication

1. Review results for the exact candidate commit, including Windows and macOS.
   Do not call an unrun matrix a pass. Record any intentionally unsupported platform.
2. Confirm final audience/visibility and explicit public-publication approval.
3. Finalize public version/profile naming and key metadata deliberately. Preserve
   both legacy v1 and draft1 compatibility; never silently change a pinned key.
4. Recheck mapping equality, license scope, checksums and the exact release assets.

The owner already confirmed no outside reservations and delegated the applied
MIT software/data and CC BY 4.0 documentation choice. Those decisions need not be
re-asked. Preserved v1/third-party exceptions remain, and font work stays separate.
