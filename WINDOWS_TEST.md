# Windows test — rc1 source tree

The hosted Windows/Python 3.12 job passed in [run 41382272362](https://github.com/mikesupo/cavescript32/actions/runs/41382272362) for commit
`e90cb6958e35b033cd2cae062af0330f29ffdc62`. That is not a claim about a personal Windows computer. The optional
local steps below use an already obtained source tree and existing Python;
they create no access, install nothing and change no execution policy.

Open PowerShell in this repository folder. If `py` is absent but an existing
`python --version` reports Python 3.9+, substitute `python` for `py -3` consistently.
If no suitable interpreter exists, stop and report that; no install is authorized.

```powershell
py -3 --version
py -3 -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Tests failed: retain complete output.' }
py -3 tools\check_allocation.py
if ($LASTEXITCODE -ne 0) { throw 'Assignment/baseline check failed.' }
py -3 cavescript32.py examples\legacy_READ.cave --profile v1 --inspect
if ($LASTEXITCODE -ne 0) { throw 'V1 check failed.' }
py -3 cavescript32.py examples\draft1-cafe.cave --inspect
if ($LASTEXITCODE -ne 0) { throw 'Draft1 compatibility failed.' }
py -3 cavescript32.py examples\cafe.cave --inspect
if ($LASTEXITCODE -ne 0) { throw 'RC1 check failed.' }
```

Expected: `Ran 40 tests ... OK`; allocation reports 98 preserved + 158 unchanged
extension assignments = 256, 768 unassigned, **10 baseline source fixtures**
unchanged. Inspection yields `"READ"`, then `"caf\u00e9"` twice.

For a byte-level round trip, use fresh output names:

```powershell
py -3 cavescript32.py examples\multilingual.cave -o windows-decoded.txt
if ($LASTEXITCODE -ne 0) { throw 'Decode failed.' }
py -3 cavescript32.py windows-decoded.txt --encode -o windows-roundtrip.cave
if ($LASTEXITCODE -ne 0) { throw 'Encode failed.' }
py -3 cavescript32.py windows-roundtrip.cave -o windows-roundtrip.txt
if ($LASTEXITCODE -ne 0) { throw 'Round-trip decode failed.' }
py -3 -c "from pathlib import Path; expected=Path('examples/multilingual.txt').read_bytes(); assert Path('windows-decoded.txt').read_bytes()==expected; assert Path('windows-roundtrip.txt').read_bytes()==expected; print('PASS: exact UTF-8 bytes')"
if ($LASTEXITCODE -ne 0) { throw 'Byte comparison failed.' }
```

Do not use PowerShell `>`/text pipelines or editors to perform exact-byte source
comparisons; those layers may translate encoding/newlines. No `--run` is needed
or present in the new codec. Return OS/Python version, complete failures if any,
and pass/fail/not-run for suite, allocation and exact-byte comparison. A console
glyph/display problem is distinct from a failed byte comparison.
