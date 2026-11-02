# CaveScript32 · UTF-8 release candidate

**2.0-rc.1 · private test candidate · not a published registry or public release**

CaveScript32 uses two ordered signs per cell. This reference implementation reads
and writes text pair IDs such as `S00+S00`, not pictures, handwriting or font glyphs.
It preserves all **98 v1 assignments**, carries the same **256 byte assignments**
as `2.0-draft.1`, and rejects the remaining **768 unassigned pairs**.

The release-candidate key has current status/provenance and a new header/hash.
**No pair was reassigned.** The original draft key remains byte-for-byte intact for
compatibility; its historical metadata does not override the current RC record.
The owner confirmed no outside reservations on 2 November 2026. This declaration
is distinct from the checks against published v1 records and is not a claim of
independent global-registry certification. Publication remains on hold.

## Quick start

Python 3.9+ syntax target; no third-party packages. Local verification used Python
3.12.14/Linux. Cross-platform CI is prepared, but no Windows/macOS or hosted-CI
pass is claimed by these files before an actual result exists.

```sh
# Default mode is decode, never execute. Expected: READ
python3 cavescript32.py examples/READ.cave

# Safe ASCII inspection. Expected JSON string: "caf\u00e9"
python3 cavescript32.py examples/cafe.cave --inspect

# Existing v1 file; no edits required. Expected: READ
python3 cavescript32.py examples/legacy_READ.cave --profile v1

# Existing draft-1 frame is recognized automatically. Expected: café
python3 cavescript32.py examples/draft1-cafe.cave

# Exact-byte file round trip; output paths must not already exist.
python3 cavescript32.py examples/multilingual.cave -o decoded.txt
python3 cavescript32.py decoded.txt --encode -o encoded.cave
python3 cavescript32.py encoded.cave -o checked.txt

python3 -m unittest discover -s tests -v
python3 tools/check_allocation.py
```

On Windows use `py -3` in place of `python3` if that is the installed launcher.
See [WINDOWS_TEST.md](WINDOWS_TEST.md). Use `-o` rather than shell text redirection
for byte comparisons; shell/editor encoding and newline conversions are outside
the codec. Missing Python is not permission to install or create new access.

## Version and compatibility rules

| Mode | Identification | Behavior |
|---|---|---|
| Current default encode | `utf8-rc1` | Emits the exact RC header below |
| Default decode (`auto`) | Exact rc1 **or** draft1 frame | Dispatches by header; no guessing |
| `--profile v1` | Headerless original body only | Same 98 original meanings |
| `--profile utf8-draft1` | Matching draft1 frame or explicit bare body | Original draft semantics |
| `--profile utf8-rc1` | Matching rc1 frame or explicit bare body | RC semantics |

Current envelope:

```text
#!CaveScript32 version=2.0-rc.1 profile=UTF-8
```

Frozen draft envelope, still readable:

```text
#!CaveScript32 version=2.0-draft.1 profile=UTF-8
```

An explicit profile rejects a different header even though the mappings are
identical. Unknown/future headers fail. Bare input needs an explicit profile.
Bare encoding requires `--encode --bare --profile PROFILE`. To deliberately write
an old draft file, use `--encode --profile utf8-draft1`.

The archived v1 decoder rejects every new byte pair and both v2 headers. The old
draft-1 decoder is **not** claimed to recognize the RC header; compatibility here
means the **new RC decoder reads old draft-1 files**. No silent downgrade occurs.

## What multilingual means

One pair carries one UTF-8 byte, not necessarily a character or visible glyph.
A scalar uses one to four cells; joined emoji and other graphemes can use many.
Strict UTF-8 rejects overlong, surrogate, out-of-range, isolated-continuation and
truncated sequences. Exact code points, source BOMs, NUL, CR/LF/CRLF, combining
marks, joiners and bidi controls are preserved—no normalization or translation.

This is **not a font**, translation, shaping/bidi-display engine, image recognizer,
compression, encryption, error correction or LLM-token optimization. Font work
stays separate. A valid pair can change into another valid pair undetected.

## Safety

The root-level codec has no execution option and never executes decoded content.
The immutable original v1 decoder kept solely as a compatibility fixture still
has its original opt-in `--run`; do not use it for untrusted text. Source text may
contain commands, markup, terminal escapes or bidi controls. Prefer `--inspect`
or a non-executing viewer; never pipe decoded text into an interpreter.

The whole input is validated before any output is written. This prevents partial
decoded output on malformed input, not partial files from disk errors or interrupted
writes. Existing files are protected unless `--force` is explicitly supplied.

## Licenses and provenance

**MIT:** current software/tests/tools/configuration, both v2 keys and fixture data.
**CC BY 4.0:** current documentation. See [LICENSE](LICENSE), full official texts
in `LICENSES/`, and the exact [LICENSE_SCOPE.json](LICENSE_SCOPE.json).
Ten original v1 text/code/key fixtures retain their original bytes and notices;
no blanket relicense of archived code or third-party content is asserted.
No drawing assets, font files, PDFs, correspondence, account data or entire private
archive are included in this repository. Original full archives are preserved
separately, unchanged. See [baseline/README.md](baseline/README.md) and [NOTICE.md](NOTICE.md).

## Tests and release hold

The suite has **40 tests**, including all 1,112,064 Unicode scalar values, all 98
v1 assignments, all 158 extension pairs, all 768 unassigned pairs, 27 source vectors,
2,000 seeded byte strings, profile mismatches and exact draft1 compatibility.
The manual CI template is pinned to verified official action commits, with only
`contents: read`, no persisted credentials, no secrets/deployment/publishing and
four jobs capped at five minutes each. Do not trigger until existing included
private-Actions allowance is confirmed; no paid overage or repeated runs are
implicitly authorized. See [CI_AND_RELEASE.md](CI_AND_RELEASE.md).

No public mapping or release is changed by this candidate. Publication requires
separate approval after the intended platform results and final release review.
