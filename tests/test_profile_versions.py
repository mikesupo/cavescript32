"""Release-candidate and frozen-draft profile interoperability."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cavescript32 as c
from test_codec import cli


class VersionCompatibilityTests(unittest.TestCase):
    def test_frozen_draft_key_and_identical_mapping(self):
        path = ROOT / 'reference/cavescript32-v2.0-draft.1-utf8-key.json'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         'a4454dbad16b487d84c94207036355823488132782df52e589dc01ce5456d65b')
        draft = json.loads(path.read_bytes())
        current = json.loads((ROOT / 'reference/cavescript32-v2.0-rc.1-utf8-key.json').read_bytes())
        self.assertEqual(current['assignments'], draft['assignments'])
        self.assertEqual(current['unassigned_pairs'], draft['unassigned_pairs'])
        self.assertEqual(current['signs'], draft['signs'])
        self.assertEqual(current['header'], c.HEADER)
        self.assertEqual(draft['header'], c.DRAFT_HEADER)
        self.assertNotEqual(current['version'], draft['version'])
        self.assertEqual(current['mapping_sha256'], hashlib.sha256(json.dumps(
            [[e['byte'], e['pair']] for e in current['assignments']], separators=(',', ':')).encode()).hexdigest())

    def test_default_emits_rc1_not_draft1(self):
        self.assertEqual(c.VERSION, '2.0-rc.1')
        self.assertEqual(c.CURRENT_PROFILE, c.RC_PROFILE)
        self.assertEqual(c.DRAFT_PROFILE, 'utf8-draft1')
        self.assertTrue(c.encode('A').startswith(c.HEADER + '\n'))
        self.assertFalse(c.encode('A').startswith(c.DRAFT_HEADER + '\n'))

    def test_both_frames_auto_decode_all_vectors(self):
        for vector in json.loads((ROOT / 'reference/test-vectors.json').read_bytes()):
            source = vector['source']
            for profile in (c.RC_PROFILE, c.DRAFT_PROFILE):
                with self.subTest(case=vector['name'], profile=profile):
                    frame = c.encode(source, profile=profile)
                    self.assertEqual(c.decode(frame), source)
                    self.assertEqual(c.decode(frame, profile=profile), source)
                    self.assertEqual(c.encode_body(source, profile=profile), vector['body'])

    def test_exact_draft_fixture_still_readable_and_reproducible(self):
        fixture = (ROOT / 'examples/draft1-cafe.cave').read_bytes()
        self.assertEqual(c.decode(fixture.decode('ascii')), 'café')
        self.assertEqual(c.encode('café', profile=c.DRAFT_PROFILE).encode('ascii'), fixture)
        result = cli(ROOT / 'examples/draft1-cafe.cave')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'café'.encode())

    def test_explicit_mismatches_reject_before_output(self):
        for frame_profile, requested in ((c.RC_PROFILE, c.DRAFT_PROFILE),
                                         (c.DRAFT_PROFILE, c.RC_PROFILE)):
            frame = c.encode('café', profile=frame_profile)
            with self.subTest(requested=requested), self.assertRaises(c.CaveScriptError):
                c.decode(frame, profile=requested)
            result = cli('--profile', requested, data=frame.encode())
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b'')
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / 'output.txt'
                result = cli('--profile', requested, '-o', path, data=frame.encode())
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(path.exists())
                path.write_bytes(b'keep')
                result = cli('--profile', requested, '-o', path, '--force', data=frame.encode())
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(path.read_bytes(), b'keep')

    def test_both_profiles_accept_lf_and_crlf_headers(self):
        for profile in (c.RC_PROFILE, c.DRAFT_PROFILE):
            source = 'é\r\n\x00\ufeff👩🏽\u200d💻'
            body = c.encode_body(source, profile=profile)
            for line_ending in ('\n', '\r\n'):
                frame = c.HEADERS[profile] + line_ending + body
                self.assertEqual(c.decode(frame), source)
                self.assertEqual(c.decode(frame, profile=profile), source)

    def test_unknown_future_versions_are_not_guessed(self):
        for version in ('2.0-rc.2', '2.0', '3.0', '2.0-draft.2'):
            frame = f'#!CaveScript32 version={version} profile=UTF-8\nS28+S19\n'
            for profile in ('auto', c.RC_PROFILE, c.DRAFT_PROFILE):
                with self.subTest(version=version, profile=profile), self.assertRaises(c.CaveScriptError):
                    c.decode(frame, profile=profile)

    def test_bare_bodies_require_explicit_profile(self):
        body = c.encode('café', framed=False)
        with self.assertRaises(c.CaveScriptError):
            c.decode(body)
        for profile in (c.RC_PROFILE, c.DRAFT_PROFILE):
            self.assertEqual(c.decode(body, profile=profile), 'café')
        with self.assertRaises(c.CaveScriptError):
            c.decode(body, profile='v1')

    def test_explicit_draft_encoding_cli(self):
        result = cli('--encode', '--profile', c.DRAFT_PROFILE, data='café'.encode())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (ROOT / 'examples/draft1-cafe.cave').read_bytes())
        result = cli('--encode', data='café'.encode())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (ROOT / 'examples/cafe.cave').read_bytes())


if __name__ == '__main__':
    unittest.main()
