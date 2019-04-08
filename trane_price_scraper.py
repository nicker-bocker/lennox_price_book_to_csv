import csv
import re

import common

BRAND = "Trane"
SAVE_FILE = 'trane_results.csv'
INPUT_FILE = 'trane_dna.txt'
FLAGS = re.MULTILINE | re.DOTALL

model_pattern = r'[0-9A-Z*]{6,}'

re_section_header = re.compile(fr'''
    (?P<size>[1-5]\.?\d?)\sTon\s
    (?P<cu_model>{model_pattern})\s
  \$(?P<cu_price>\d+)\s
    (?P<cu_dimensions>.*?)\sMax\sAmp:\s
    (?P<cu_mop>\d\d)\sMCA:\s
    (?P<cu_mca>\d+\.?\d?).*?LIQ=
    (?P<cu_liq>[^"]+).*?GAS=
    (?P<cu_gas>[^"]+).*
''', flags=FLAGS | re.VERBOSE)

re_hp = re.compile(fr'''
    (?P<ahu_model>{model_pattern})\s
    (?P<ahu_dimensions>.*?)
    (?:\s\$(?P<ahu_price>\d+))\s
    (?P<heater_model>{model_pattern})\s
    \$(?P<heater_price>\d+)\s
    (?P<seer>[1-2][0-9]\.?\d?\d?)\s
    (?P<eer>\d+\.?\d?\d?)\s
    (?P<hspf>\d+\.?\d?\d?)\s
    (?P<cu_btu>\d+)\s
    (?P<ahri>\d+)\s
    \$(?P<system_price>\d+)
''', flags=FLAGS | re.VERBOSE)

re_sc = re.compile(fr'''
    (?P<ahu_model>{model_pattern})\s
    (?P<ahu_dimensions>.*?)
    (?:\s\$(?P<ahu_price>\d+))\s
    (?P<heater_model>{model_pattern})\s
    \$(?P<heater_price>\d+)\s
    (?P<seer>[1-2][0-9]\.?\d?\d?)\s
    (?P<eer>\d+\.?\d?\d?)\s
    (?P<cu_btu>\d+)\s
    (?P<ahri>\d+)\s
    \$(?P<system_price>\d+)
''', flags=FLAGS | re.VERBOSE)

re_gas = re.compile(fr'''
    (?P<furnace_model>{model_pattern})\s
    (?P<furnace_dimensions>.*?)
    (?:\s\$(?P<furnace_price>\d+))\s
    (?P<coil_model>{model_pattern})\s
    \$(?P<coil_price>\d+)\s
    (?P<seer>[1-2][0-9]\.?\d?\d?)\s
    (?P<eer>\d+\.?\d?\d?)\s
    (?P<cu_btu>\d+)\s
    (?P<ahri>\d+)\s
    \$(?P<system_price>\d+)
''', flags=FLAGS | re.VERBOSE)

PATTERNS = [
    ('HP-AHU', re_hp),
    ('SC-AHU', re_sc),
    ('SC-GAS', re_gas)
]


def get_re_dict(text, patterns):
    for t, p in patterns:
        m = p.search(text)
        if m:
            return {'type': t, **m.groupdict()}


def main():
    with open(INPUT_FILE) as f:
        file_txt = f.read().replace(',', '')
    file_txt = file_txt.split('\n')
    results = set()
    cu_map = None
    working_re = None
    for line in file_txt:
        m = re_section_header.match(line)
        if m:
            cu_map = m.groupdict()
            continue

        if line.startswith('Furnace'):
            working_re = PATTERNS[2:]
            continue
        elif line.startswith('Air Handler'):
            working_re = PATTERNS[:2]
            continue

        if cu_map is None or working_re is None:
            continue
        if cu_map['cu_model'].startswith('M'):
            cu_map = working_re = None
            continue

        sys_map = get_re_dict(line, working_re)
        if sys_map is None:
            continue
        sys_map = {**cu_map, **sys_map}
        sys_map['brand'] = BRAND
        sys_map = {k: common.trycast(v) for k, v in sys_map.items()}
        results.add(tuple(sorted(sys_map.items())))
    results = [dict(t) for t in results]
    print(f'...writing {len(results)} results to {SAVE_FILE}')
    with open(SAVE_FILE, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=common.FIELDS)
        w.writeheader()
        w.writerows(results)



if __name__ == '__main__':
    main()

    # test = 'TUD1C080A9H41B 40" x 21" x 28" $875 4MXCC009AC6HCA $449 15.0 12.5 45500 10257726 $3,058'
    # # test = '2 Ton 4TWX8024A1000* $2,549 50"H x 37"W x 34"D Max Amp: 25 MCA: 15 Line Connections: LIQ=3/8", GAS=5/8"'
    # test = test.replace(',', '')
    # from pprint import pprint
    #
    # m = re_gas.search(test)
    # print(m)
    # pprint(m.groupdict())
