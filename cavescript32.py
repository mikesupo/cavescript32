#!/usr/bin/env python3
"""CaveScript32 UTF-8 private release-candidate codec; decode by default, never execute.

Python 3.9+ standard library. Default decoding requires an exact rc1 or draft1 header.
Use --profile v1 to read an unchanged, headerless v1 inscription.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

VERSION = '2.0-rc.1'
RC_PROFILE = 'utf8-rc1'
CURRENT_PROFILE = RC_PROFILE
DRAFT_PROFILE = 'utf8-draft1'
HEADER = '#!CaveScript32 version=2.0-rc.1 profile=UTF-8'
DRAFT_HEADER = '#!CaveScript32 version=2.0-draft.1 profile=UTF-8'
HEADERS = {RC_PROFILE: HEADER, DRAFT_PROFILE: DRAFT_HEADER}
KEY_SHA256 = '848c76a7c5fa5273ea6a4faf602803649cc8c322128133ba2f0216136d7a5cb2'
DRAFT_KEY_SHA256 = 'a4454dbad16b487d84c94207036355823488132782df52e589dc01ce5456d65b'
BASELINE_SHA256 = '3f2bc7b53c4fcc7c4409e5aff929a70b5639b7948a2abe32c27eac668be0e211'
ROOT = Path(__file__).resolve().parent
PAIR = re.compile(r'S(?:[0-2][0-9]|3[01])\+S(?:[0-2][0-9]|3[01])\Z', re.ASCII)
LAYOUT = ' \t\n\r\v\f'


class CaveScriptError(ValueError):
    """Invalid or incompatible inscription, source text, or key."""


def _tables():
    current_raw = (ROOT / 'reference/cavescript32-v2.0-rc.1-utf8-key.json').read_bytes()
    draft_raw = (ROOT / 'reference/cavescript32-v2.0-draft.1-utf8-key.json').read_bytes()
    baseline = (ROOT / 'baseline/v1.0/reference/cavescript32-v1.0-key.json').read_bytes()
    for name, raw, digest in (('rc1', current_raw, KEY_SHA256),
                              ('draft1', draft_raw, DRAFT_KEY_SHA256),
                              ('v1 baseline', baseline, BASELINE_SHA256)):
        if hashlib.sha256(raw).hexdigest() != digest:
            raise CaveScriptError(f'{name} key integrity mismatch; restore the matching unmodified package.')
    key, draft = json.loads(current_raw), json.loads(draft_raw)
    old = {entry['pair']: entry['ascii'] for entry in json.loads(baseline)['characters']}
    current = {entry['pair']: entry['byte'] for entry in key['assignments']}
    prior = {entry['pair']: entry['byte'] for entry in draft['assignments']}
    if (len(current) != 256 or set(current.values()) != set(range(256))
            or any(current.get(pair) != value for pair, value in old.items())
            or current != prior or key['unassigned_pairs'] != draft['unassigned_pairs']
            or key['header'] != HEADER or draft['header'] != DRAFT_HEADER):
        raise CaveScriptError('Inconsistent rc1/draft1 key or v1 baseline.')
    return current, old


def _profile_table(profile):
    if profile not in ('v1', RC_PROFILE, DRAFT_PROFILE):
        raise CaveScriptError('Choose v1, utf8-rc1 or utf8-draft1 explicitly for a bare body.')
    current, old = _tables()
    return old if profile == 'v1' else current


def decode_body(body, *, profile):
    """Decode a headerless body under an explicitly selected profile.

    v1 accepts the original decoder's Unicode-whitespace layout; both UTF-8 profiles
    accept ASCII layout only. Source text whitespace is encoded in cells.
    """
    table = _profile_table(profile)
    if profile != 'v1' and not body.isascii():
        raise CaveScriptError('The UTF-8 token body must be ASCII (no BOM or Unicode whitespace).')
    output = bytearray()
    tokens = body.split() if profile == 'v1' else re.findall(r'[^ \t\n\r\v\f]+', body)
    for cell, token in enumerate(tokens, 1):
        if PAIR.fullmatch(token) is None:
            raise CaveScriptError(f'Malformed pair at cell {cell}; expected S00+S00 through S31+S31.')
        if token not in table:
            raise CaveScriptError(f'Unassigned pair {token} at cell {cell} for profile {profile}.')
        output.append(table[token])
    try:
        return bytes(output).decode('utf-8', errors='strict')
    except UnicodeDecodeError as exc:
        raise CaveScriptError(
            f'Invalid UTF-8 at byte {exc.start} (cell {exc.start + 1}): {exc.reason}.') from exc


def encode_body(text, *, profile):
    """Encode exact scalar sequence; no normalization or newline conversion."""
    reverse = {value: pair for pair, value in _profile_table(profile).items()}
    try:
        data = text.encode('utf-8', errors='strict')
    except UnicodeEncodeError as exc:
        raise CaveScriptError(f'Non-scalar source character at index {exc.start}.') from exc
    for position, byte in enumerate(data):
        if byte not in reverse:
            raise CaveScriptError(f'Unsupported v1 byte at source UTF-8 byte {position}; use utf8-rc1 or utf8-draft1.')
    return ' '.join(reverse[byte] for byte in data)


def encode(text, *, profile=CURRENT_PROFILE, framed=True):
    """Encode text; the default is a header-bearing private rc1 inscription."""
    body = encode_body(text, profile=profile)
    if framed and profile == 'v1':
        raise CaveScriptError('No framed v1 format is defined; select framed=False explicitly.')
    if framed:
        return HEADERS[profile] + '\n' + (body + '\n' if body else '')
    return body


def decode(inscription, *, profile='auto'):
    """Decode exact rc1/draft1 frame or explicitly selected unframed profile.

    Metadata dispatch is exact; identical mappings never justify profile guessing.
    No content is executed, and unknown/future profile headers are rejected.
    """
    if profile not in ('auto', 'v1', RC_PROFILE, DRAFT_PROFILE):
        raise CaveScriptError('Unknown profile.')
    if inscription.startswith('#!'):
        line, separator, body = inscription.partition('\n')
        if line.endswith('\r'):
            line = line[:-1]
        header_profile = next((name for name, header in HEADERS.items() if line == header), None)
        if not separator or header_profile is None:
            raise CaveScriptError('Unknown, malformed, or unterminated version/profile header.')
        if profile != 'auto' and profile != header_profile:
            raise CaveScriptError(f'Header/profile mismatch: frame is {header_profile}, requested {profile}.')
        return decode_body(body, profile=header_profile)
    if profile == 'auto':
        raise CaveScriptError('Missing version/profile header. For a legacy body, choose --profile v1 explicitly.')
    return decode_body(inscription, profile=profile)


def _read(path):
    return sys.stdin.buffer.read() if path == '-' else Path(path).read_bytes()


def _write(path, data, force):
    if path == '-':
        sys.stdout.buffer.write(data)
    else:
        with open(path, 'wb' if force else 'xb') as output:
            output.write(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?', default='-', help='input file, or - for stdin')
    parser.add_argument('-o', '--output', default='-', help='output file, or - for stdout')
    parser.add_argument('--encode', action='store_true', help='encode UTF-8 source text instead of decoding')
    parser.add_argument('--profile', choices=('auto', 'v1', RC_PROFILE, DRAFT_PROFILE), default='auto')
    parser.add_argument('--bare', action='store_true', help='encode without header; requires explicit profile')
    parser.add_argument('--inspect', action='store_true', help='decode to an ASCII-escaped JSON string for safe inspection')
    parser.add_argument('--force', action='store_true', help='allow replacing the output file')
    parser.add_argument('--version', action='version', version=f'CaveScript32 {VERSION} PRIVATE RELEASE CANDIDATE')
    args = parser.parse_args(argv)
    if args.bare and (not args.encode or args.profile == 'auto'):
        parser.error('--bare requires --encode and an explicit --profile')
    if args.inspect and args.encode:
        parser.error('--inspect is decode-only')
    try:
        source = _read(args.input).decode('utf-8', errors='strict')
        if args.encode:
            profile = CURRENT_PROFILE if args.profile == 'auto' else args.profile
            result = encode(source, profile=profile, framed=not args.bare).encode('ascii')
        else:
            result_text = decode(source, profile=args.profile)
            result = (json.dumps(result_text, ensure_ascii=True) + '\n').encode('ascii') if args.inspect else result_text.encode('utf-8')
        # Only write after the entire source, inscription and UTF-8 have passed.
        _write(args.output, result, args.force)
    except (OSError, UnicodeError, CaveScriptError) as exc:
        # ascii() avoids echoing untrusted control or bidi characters to a terminal.
        parser.exit(1, f'Error: {ascii(str(exc))}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
