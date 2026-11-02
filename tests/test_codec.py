"""No third-party dependencies: python3 -m unittest discover -s tests -v."""
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cavescript32 as c
from tools.check_allocation import expected_assignments

KEY = json.loads((ROOT / 'reference/cavescript32-v2.0-rc.1-utf8-key.json').read_bytes())
V1 = json.loads((ROOT / 'baseline/v1.0/reference/cavescript32-v1.0-key.json').read_bytes())
B2P = {entry['byte']: entry['pair'] for entry in KEY['assignments']}
spec = importlib.util.spec_from_file_location('original_v1_decoder', ROOT / 'baseline/v1.0/first-program/cavescript_run.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)


def byte_body(data):
    return ' '.join(B2P[b] for b in data)


def cli(*args, data=b''):
    return subprocess.run([sys.executable, str(ROOT / 'cavescript32.py'), *map(str, args)],
                          input=data, capture_output=True, cwd=ROOT)


class KeyTests(unittest.TestCase):
    def test_frozen_baseline_hashes(self):
        lock = json.loads((ROOT / 'baseline/BASELINE_LOCK.json').read_bytes())
        self.assertEqual(len(lock['files']), 10)
        for name, digest in lock['files'].items():
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256((ROOT / 'baseline/v1.0' / name).read_bytes()).hexdigest(), digest)

    def test_key_and_counts(self):
        self.assertEqual(KEY['signs'], V1['signs'])
        self.assertEqual(len(KEY['signs']), 32)
        self.assertEqual(len(B2P), 256)
        self.assertEqual(len(set(B2P.values())), 256)
        self.assertEqual(set(B2P), set(range(256)))
        self.assertEqual(len(KEY['unassigned_pairs']), 768)
        self.assertEqual(sum(e['origin'] == 'v1.0-preserved' for e in KEY['assignments']), 98)
        self.assertEqual(sum(e['origin'] == 'private-draft-addition' for e in KEY['assignments']), 158)
        for e in KEY['assignments']:
            self.assertEqual(e['pair'], f'S{e["signs"][0]:02}+S{e["signs"][1]:02}')
            self.assertEqual(e['hex'], f'{e["byte"]:02X}')

    def test_deterministic_allocation(self):
        self.assertEqual(B2P, expected_assignments(V1))
        all_pairs = {f'S{i:02}+S{j:02}' for i in range(32) for j in range(32)}
        self.assertEqual(set(KEY['unassigned_pairs']), all_pairs - set(B2P.values()))

    def test_all_98_v1_assignments_unchanged(self):
        self.assertEqual(old.reading_key(), {e['pair']: e['character'] for e in V1['characters']})
        for e in V1['characters']:
            with self.subTest(byte=e['ascii']):
                self.assertEqual(B2P[e['ascii']], e['pair'])
                self.assertEqual(c.decode(e['pair'], profile='v1'), e['character'])
                self.assertEqual(c.decode(e['pair'], profile=c.RC_PROFILE), e['character'])
                self.assertEqual(c.encode_body(e['character'], profile=c.RC_PROFILE), e['pair'])

    def test_original_decoder_rejects_all_158_additions(self):
        for e in KEY['assignments']:
            if e['origin'] == 'private-draft-addition':
                with self.subTest(byte=e['byte']), self.assertRaises(ValueError):
                    old.decode(e['pair'])

    def test_all_768_unassigned_rejected(self):
        for pair in KEY['unassigned_pairs']:
            with self.subTest(pair=pair), self.assertRaises(c.CaveScriptError):
                c.decode(pair, profile=c.RC_PROFILE)

    def test_first_program_unchanged(self):
        folder = ROOT / 'baseline/v1.0/first-program'
        body = (folder / 'marks_cavescript32.txt').read_text(encoding='utf-8')
        source = (folder / 'marks.py').read_bytes()
        self.assertEqual(c.decode(body, profile='v1').encode(), source)
        self.assertEqual(c.decode(body, profile=c.RC_PROFILE).encode(), source)
        self.assertEqual(old.decode(body).encode(), source)


class TextTests(unittest.TestCase):
    def test_27_multilingual_vectors(self):
        vectors = json.loads((ROOT / 'reference/test-vectors.json').read_bytes())
        self.assertEqual(len(vectors), 27)
        for v in vectors:
            with self.subTest(case=v['name']):
                self.assertEqual(v['source'].encode().hex(), v['utf8_hex'])
                self.assertEqual(c.encode_body(v['source'], profile=c.RC_PROFILE), v['body'])
                self.assertEqual(c.decode(v['body'], profile=c.RC_PROFILE), v['source'])
                self.assertEqual(c.decode(c.encode(v['source'])), v['source'])

    def test_no_normalization(self):
        self.assertNotEqual(c.encode('é'), c.encode('e\u0301'))
        for value in ('é', 'e\u0301', 'A\u030A', 'Å', '👩🏽\u200d💻'):
            self.assertEqual(c.decode(c.encode(value)), value)

    def test_empty(self):
        self.assertEqual(c.encode(''), c.HEADER + '\n')
        self.assertEqual(c.decode(c.HEADER + '\n'), '')
        self.assertEqual(c.decode('', profile='v1'), '')
        self.assertEqual(c.decode('', profile=c.RC_PROFILE), '')

    def test_newlines_controls_bom_and_bidi(self):
        text = '\ufeff\ufffdA\r\nB\rC\n\t\x00\x1b[31m\u202eabc\u202c\u2067שלום\u2069'
        self.assertEqual(c.decode(c.encode(text)), text)

    def test_whitespace_is_layout_not_source(self):
        body = c.encode_body('AB\nC', profile=c.RC_PROFILE)
        for whitespace in (' ', '\t', '\r', '\n', '\v', '\f', ' \r\n\t'):
            self.assertEqual(c.decode_body(whitespace + whitespace.join(body.split()) + whitespace,
                                           profile=c.RC_PROFILE), 'AB\nC')

    def test_v1_legacy_unicode_layout(self):
        body = '\u00a0'.join(c.encode_body('AB', profile='v1').split())
        self.assertEqual(c.decode(body, profile='v1'), old.decode(body))
        with self.assertRaises(c.CaveScriptError):
            c.decode(body, profile=c.RC_PROFILE)

    def test_surrogates_not_scalar_source(self):
        for value in ('\ud800', '\udfff', 'A\ud800B'):
            with self.subTest(value=ascii(value)), self.assertRaises(c.CaveScriptError):
                c.encode(value)

    def test_v1_rejects_unsupported_text(self):
        for text in ('café', '\x00', '你好'):
            with self.subTest(text=text), self.assertRaises(c.CaveScriptError):
                c.encode_body(text, profile='v1')

    def test_all_unicode_scalars(self):
        total = 0
        for start in range(0, 0x110000, 4096):
            value = ''.join(chr(n) for n in range(start, min(start + 4096, 0x110000))
                            if not 0xD800 <= n <= 0xDFFF)
            self.assertEqual(c.decode(c.encode(value)), value)
            total += len(value)
        self.assertEqual(total, 1112064)


class RejectTests(unittest.TestCase):
    def test_malformed_pairs(self):
        for value in ('S0+S00', 's00+s00', 'S32+S00', 'S00+S32', 'S99+S99',
                      'S00-S00', 'S00 + S00', 'S00+S00S00+S01', 'S00+', 'S00',
                      'S００+S００', 'S00+S00,', 'S00+S00\x00', '#comment',
                      'S00+S00\x1cS00+S00', '\ufeffS00+S00', 'S00+S00\u00a0S00+S00'):
            with self.subTest(value=ascii(value)), self.assertRaises(c.CaveScriptError):
                c.decode(value, profile=c.RC_PROFILE)

    def test_strict_invalid_utf8(self):
        invalid = [b'\x80', b'\xbf', b'\xc0\xaf', b'\xc1\xbf', b'\xe0\x80\xaf',
                   b'\xf0\x80\x80\xaf', b'\xed\xa0\x80', b'\xed\xbf\xbf',
                   b'\xf4\x90\x80\x80', b'\xf5\x80\x80\x80', b'\xff',
                   b'\xc2', b'\xe2\x82', b'\xf0\x9f\x98', b'\xc2A',
                   b'\xe2A\x80', b'\xf0\x9fA\x80', b'A\x80B']
        for value in invalid:
            with self.subTest(hex=value.hex()), self.assertRaises(c.CaveScriptError):
                c.decode(byte_body(value), profile=c.RC_PROFILE)

    def test_every_single_byte_against_utf8_oracle(self):
        for byte in range(256):
            if byte < 128:
                self.assertEqual(c.decode(B2P[byte], profile=c.RC_PROFILE), chr(byte))
            else:
                with self.assertRaises(c.CaveScriptError):
                    c.decode(B2P[byte], profile=c.RC_PROFILE)

    def test_2000_seeded_byte_strings_against_utf8_oracle(self):
        rng = random.Random(20261101)
        for i in range(2000):
            data = bytes(rng.randrange(256) for _ in range(rng.randrange(13)))
            try:
                expected = data.decode('utf-8', errors='strict')
            except UnicodeDecodeError:
                with self.subTest(case=i), self.assertRaises(c.CaveScriptError):
                    c.decode(byte_body(data), profile=c.RC_PROFILE)
            else:
                self.assertEqual(c.decode(byte_body(data), profile=c.RC_PROFILE), expected)

    def test_header_identity_and_mismatch(self):
        body = B2P[65]
        for header in ('#!CaveScript32 version=2.0 profile=UTF-8',
                       '#!CaveScript32 version=2.0-draft.2 profile=UTF-8',
                       '#!CaveScript32 version=2.0-draft.1 profile=ASCII',
                       c.HEADER + ' ', c.HEADER + '\r\r', '\ufeff' + c.HEADER,
                       ' ' + c.HEADER, c.HEADER.lower()):
            with self.subTest(header=ascii(header)), self.assertRaises(c.CaveScriptError):
                c.decode(header + '\n' + body)
        with self.assertRaises(c.CaveScriptError):
            c.decode(c.encode('A'), profile='v1')
        self.assertEqual(c.decode(c.HEADER + '\r\n' + body), 'A')
        with self.assertRaises(c.CaveScriptError):
            c.decode(c.HEADER)
        with self.assertRaises(c.CaveScriptError):
            c.decode(c.HEADER + '\n' + c.HEADER + '\n' + body)

    def test_bare_requires_explicit_profile(self):
        for body in ('', B2P[65]):
            with self.assertRaises(c.CaveScriptError):
                c.decode(body)
        with self.assertRaises(c.CaveScriptError):
            c.decode(B2P[65], profile='utf8')
        with self.assertRaises(c.CaveScriptError):
            c.encode('A', profile='v1')

    def test_valid_to_valid_corruption_is_not_detected(self):
        self.assertEqual(c.decode('S14+S20', profile='v1'), 'R')
        self.assertEqual(c.decode('S14+S21', profile='v1'), 'Q')


class CLITests(unittest.TestCase):
    def test_default_is_decode_only(self):
        with tempfile.TemporaryDirectory() as temp:
            sentinel = Path(temp) / 'must_not_exist'
            source = f'open({str(sentinel)!r}, "w").write("executed")\n'
            result = cli(data=c.encode(source).encode())
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, source.encode())
            self.assertFalse(sentinel.exists())
            self.assertNotEqual(cli('--run', data=c.encode(source).encode()).returncode, 0)

    def test_cli_exact_binary_io(self):
        source = '\ufeffcafé\r\n\t你好\x00\r\n👩🏽\u200d💻'.encode()
        encoded = cli('--encode', data=source)
        self.assertEqual(encoded.returncode, 0, encoded.stderr)
        decoded = cli(data=encoded.stdout)
        self.assertEqual(decoded.returncode, 0, decoded.stderr)
        self.assertEqual(decoded.stdout, source)

    def test_cli_bare_and_legacy(self):
        encoded = cli('--encode', '--profile', 'v1', '--bare', data=b'READ')
        self.assertEqual(encoded.returncode, 0)
        decoded = cli('--profile', 'v1', data=encoded.stdout)
        self.assertEqual(decoded.stdout, b'READ')
        self.assertNotEqual(cli('--encode', '--bare', data=b'READ').returncode, 0)
        self.assertNotEqual(cli(data=encoded.stdout).returncode, 0)

    def test_cli_inspection_escapes_controls(self):
        text = '\x1b[31m\u202eשלום\x00'
        result = cli('--inspect', data=c.encode(text).encode())
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.isascii())
        self.assertEqual(json.loads(result.stdout), text)
        self.assertNotIn(b'\x1b', result.stdout)
        self.assertNotEqual(cli('--encode', '--inspect', data=b'A').returncode, 0)

    def test_failures_have_no_partial_output(self):
        for data in ((c.HEADER + '\n' + B2P[65] + ' BAD').encode(),
                     (c.HEADER + '\n' + byte_body(b'A\x80')).encode(), b'\xff'):
            result = cli(data=data)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b'')
        self.assertNotEqual(cli('--encode', data=b'\xc0\xaf').returncode, 0)

    def test_output_file_protection(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'result.txt'
            output.write_bytes(b'keep')
            result = cli('-o', output, data=c.encode('new').encode())
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), b'keep')
            result = cli('-o', output, '--force', data=c.encode('new').encode())
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), b'new')
            result = cli('-o', output, '--force', data=b'invalid')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), b'new')

    def test_missing_file_no_output(self):
        result = cli(ROOT / 'no-such-input-file.cave')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b'')

    def test_all_examples_expected(self):
        for name in ('READ', 'cafe', 'emoji', 'empty', 'multilingual'):
            with self.subTest(example=name):
                expected = (ROOT / f'examples/{name}.txt').read_bytes()
                result = cli(ROOT / f'examples/{name}.cave')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected)


if __name__ == '__main__':
    unittest.main()
