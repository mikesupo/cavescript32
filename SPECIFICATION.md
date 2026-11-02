# CaveScript32 2.0-rc.1 / UTF-8

Release-candidate specification, first prepared privately on 2 November 2026.
The pinned key/CLI retain that preparation label; it is not repository access
control or a claim of a stable public registry. MUST/MUST NOT below
mean conformance to this candidate, not proof of a published standard.

## Assignments and provenance

There are 32 signs and 1,024 ordered pairs. Retain all 98 v1 assignments exactly:
ASCII 32–126 plus TAB=9, LF=10, CR=13. Enumerate remaining byte values 0–255 in
ascending order; assign them to the first 158 unused pairs ordered by left sign,
then right sign (0–31 each). Byte 0 maps to S00+S00 and byte 255 to S05+S08.
The other 768 pairs MUST remain unassigned/rejected. This is a lookup table,
not arithmetic interpretation of sign numbers. No escape/header pair is added.

The complete 256 assignments, sign list and unassigned list are identical to the
frozen `2.0-draft.1` key. The RC key updates only version/status/provenance/license
metadata and includes a canonical assignment digest. Current published v1 JSON,
tables and original decoder were checked against the retained baseline; all 98
match. The owner separately confirmed no outside reservations on 2 November.
This is not independent global-registry verification or publication authority.

## Unicode semantics

Encode a sequence of Unicode scalar values (U+0000–U+10FFFF excluding surrogates)
as strict UTF-8, then map each byte to one ordered pair. Decode every pair to its
byte, then decode the complete byte sequence as strict UTF-8. Malformed cells,
unassigned pairs and invalid UTF-8 MUST fail before decoded output is emitted.
No automatic replacement, ignored errors, surrogate pass/escape, overlong form,
encoded surrogate, out-of-range scalar or truncated sequence is allowed. Literal
U+FFFD is valid source data. All bytes have pairs, but not all byte strings are
valid UTF-8; this is a text profile, not an arbitrary binary format.

No normalization, case folding, transliteration, translation, trimming, BOM
stripping or newline rewriting. Preserve exact controls, NUL, CR/LF/CRLF, source
BOM, combining marks, variation selectors, joiners, noncharacters, private-use
scalars and bidi data. Acceptance of data is not safe display or language validation.
One scalar takes one to four byte cells; a grapheme may take many more.

## Envelopes and grammar

Canonical RC header, external to the sign-pair space:
`#!CaveScript32 version=2.0-rc.1 profile=UTF-8`

Frozen draft header, also recognized:
`#!CaveScript32 version=2.0-draft.1 profile=UTF-8`

A frame MUST start with one exact header at byte zero followed by LF; the decoder
also accepts CRLF as that terminator. No BOM or leading whitespace. Termination
is required even for empty input. Canonical body: exact `Sdd+Sdd` tokens, uppercase
S, two decimal digits each 00–31, separated by ASCII spaces, with a final layout
LF if nonempty. Empty canonical source is header + LF only.

The UTF-8 body may use only ASCII SPACE/TAB/CR/LF/VT/FF between tokens. No Unicode
whitespace, comments, punctuation, partial tokens or additional headers. Layout
whitespace is not source whitespace: source LF is the byte pair S23+S08.

Default `auto` decoding dispatches only these two exact headers. Explicit
`utf8-rc1` or `utf8-draft1` accepts its own matching frame or a bare body and MUST
reject the other profile's header. Unknown/future headers MUST NOT be guessed.
Default encoding emits rc1. Explicit draft1 encoding retains the old envelope.
CLI bare encoding requires an explicit `--profile`; bare auto decoding always
fails. In the Python API, `encode_body` requires a profile, while
`encode(..., framed=False)` retains the documented current-profile default unless
a profile is supplied explicitly.
External protocols carrying bare bodies must supply exact profile identification.

`v1` is explicit and headerless only. Its 98 meanings and original Unicode-
whitespace layout tolerance remain unchanged. That legacy tolerance is not
extended to either UTF-8 profile. V1 encoding fails on unsupported source text.

## Integrity and migration

The implementation pins separate full-file hashes for the RC, frozen draft1 and
v1 keys. Both v2 tables MUST remain identical in this candidate; an integrity
mismatch fails closed. Hashes detect accidental change, not authenticated origin.
The canonical assignment digest uses UTF-8 JSON of ordered `[byte,pair]` arrays,
with separators `,` and `:` and no extra whitespace; metadata edits do not change
that digest. The full-file key hash does change with version/status metadata.

New decoder reads old v1 (explicitly) and draft1 (by exact header). Old v1 rejects
v2 headers and all 158 extension pairs. Old draft1 is not claimed to read the RC
header. Preserve source files and explicitly re-encode when migrating; do not
silently replace headers or strip them to make a file appear compatible.
Any future mapping or semantics change needs a distinct profile/version/header.
A later public release must finalize its identity and documentation deliberately;
this candidate does not automatically ratify a public mapping.

## Limits and safety

No decoded-code execution, network interpretation or URL opening in the codec.
The retained original v1 decoder still contains its historical opt-in execution
option and is used only as a decode fixture by these tests. Raw decoded data may
be unsafe in terminals/interpreters; use ASCII JSON `--inspect` or file output.
Validate all input before writing, but no transactional/atomic I/O guarantee.

Read cells in logical order: left sign then right sign, cells left-to-right and
rows top-to-bottom. Do not reverse source sequences to imitate bidi appearance.
Shaping, isolation in UI labels, fonts and visual layout are renderer concerns,
not validated by these byte tests. The format has no checksum, encryption, error
correction or guaranteed corruption detection. Font development remains separate;
no translation, compression, tokenizer advantage or ancient meaning is claimed.
