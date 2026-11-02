"""Decode CaveScript32 v1.0; execute only with explicit --run.
Key: https://suposystem.ai/cavescript/
Original decoder: Claude. Release revision: ChatGPT, 2026-10-15.
"""
import argparse
from pathlib import Path

KEY = "28.19=65 12.19=66 17.07=67 16.13=68 00.27=69 08.23=70 26.08=71 21.15=72 03.11=73 23.21=74 14.24=75 20.11=76 19.02=77 15.27=78 09.06=79 15.03=80 14.21=81 14.20=82 01.14=83 21.21=84 27.09=85 05.29=86 21.28=87 19.11=88 23.11=89 22.03=90 28.26=97 04.14=98 29.19=99 21.20=100 24.10=101 11.07=102 24.17=103 16.01=104 27.25=105 25.05=106 26.13=107 27.06=108 09.04=109 24.26=110 00.31=111 28.30=112 23.30=113 17.28=114 29.29=115 21.23=116 31.08=117 05.13=118 26.16=119 21.00=120 31.17=121 08.14=122 27.23=48 19.07=49 30.11=50 16.30=51 06.03=52 22.31=53 07.00=54 11.22=55 03.02=56 02.20=57 22.09=SP 18.16=33 11.19=34 19.26=35 28.27=36 21.17=37 22.21=38 15.30=39 30.29=40 11.14=41 15.08=42 30.27=43 01.07=44 31.01=45 26.09=46 20.25=47 18.13=58 08.25=59 19.15=60 24.13=61 02.08=62 03.25=63 06.14=64 16.12=91 29.17=92 23.12=93 28.03=94 17.00=95 06.16=96 04.08=123 20.12=124 23.02=125 27.08=126 23.08=LF 29.00=TAB 27.03=CR"
SPECIAL = {'SP': ' ', 'LF': '\n', 'TAB': '\t', 'CR': '\r'}


def reading_key():
    pairs = {}
    for item in KEY.split():
        pair, value = item.split('=')
        a, b = pair.split('.')
        pairs[f'S{a}+S{b}'] = SPECIAL[value] if value in SPECIAL else chr(int(value))
    return pairs


def decode(text):
    pairs = reading_key()
    source, bad, cell = [], [], 0
    for row, line in enumerate(text.splitlines(), 1):
        for column, token in enumerate(line.split(), 1):
            cell += 1
            if token not in pairs:
                bad.append(f'cell {cell} (row {row}, token {column}): {token}')
            else:
                source.append(pairs[token])
    if bad:
        raise ValueError('Unreadable cells:\n' + '\n'.join(bad))
    return ''.join(source)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inscription', type=Path)
    parser.add_argument('--run', action='store_true', help='execute the decoded Python after displaying it')
    args = parser.parse_args()
    try:
        source = decode(args.inscription.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(1, f'{error}\n')
    print('--- decoded ---')
    print(source, end='')
    if args.run:
        print('--- running ---', flush=True)
        exec(compile(source, '<CaveScript32 inscription>', 'exec'),
             {'__name__': '__main__', '__file__': str(args.inscription)})


if __name__ == '__main__':
    main()
