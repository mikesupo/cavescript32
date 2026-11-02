# Expected fixture results

`READ.cave` -> READ (no source newline).
`cafe.cave` -> café; `--inspect` -> `"caf\u00e9"` plus one inspection LF.
`emoji.cave` -> U+1F469 U+1F3FD U+200D U+1F4BB (15 UTF-8 bytes).
`empty.cave` -> zero decoded bytes.
`multilingual.cave` -> exact bytes in `multilingual.txt`, including source LF.
These frames now use the rc1 header; each matching `.txt` is unchanged source data.

`draft1-cafe.cave` is the byte-identical old draft1 frame and decodes automatically
or with `--profile utf8-draft1`. Explicit `--profile utf8-rc1` must reject it.
`legacy_READ.cave` is headerless v1 and requires `--profile v1` under default use.

All 27 scalar/byte/body vectors remain unchanged in `reference/test-vectors.json`.
The multilingual fixtures are encoding examples, not validated translations or
font/shaping tests. Visual appearance, especially bidi text, is not a byte oracle.
