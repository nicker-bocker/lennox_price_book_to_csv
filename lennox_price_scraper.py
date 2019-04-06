import csv
import re
import math
from contextlib import suppress
import common

BRAND = "Lennox"
SAVE_FILE = 'lennox_results.csv'
INPUT_FILE = 'lennox_dna.txt'
FLAGS = re.MULTILINE | re.DOTALL

_cu_model_pattern = r'(?:XC|XP|SL|EL|14|16|ML)[-A-Z0-9]+-0(?:60|48|42|36|30|24|18)'

re_section = re.compile(fr'''
    (?P<seer>[1-2][0-9]\.?\d?)\s
    (?P<cu_model>{_cu_model_pattern})
    (?P<other>.*?)
    MOP.*?
    (?P<cu_mop>\d\d)
    .*?
    (?P<cu_mca>\d\d\.?\d?)
''', flags=FLAGS | re.VERBOSE)

re_hp = re.compile(r'''
    (?P<seer>[1-2][0-9]\.?\d?)\s
    (?P<junk>.*?)\s
    (?P<ahu_model>CB[-A-Z0-9]+)\s
    \$(?P<ahu_price>[^\s]+)\s
    (?P<ahu_dimensions>[^\s]+)\s
    (?P<filter_size>[^\s]+)\s
    (?P<coil_type>[^\s]+)\s
    (?P<fan_motor>[^\s]+)\s
    (?P<cat_heater>[^\s]+)\s
    (?P<heater_model>[^\s]+)\s
    \$(?P<heater_price>[^\s]+)\s
    (?P<cu_btu>[^\s]+)\s
    (?P<eer>[^\s]+)\s
    (?P<hspf>[^\s]+)\s
    \$(?P<system_price>[^\s]+)\s
    (?P<ahri>[^\s]+)
''', flags=FLAGS | re.VERBOSE)

re_gas = re.compile(r'''
    (?P<seer>[1-2][0-9]\.?\d?)\s
    (?P<junk>.*?)\s
    (?P<furnace_model>[-A-Z0-9]{9,})\s
    (?P<furnace_dimensions>[^\s]+)\s
    (?P<fan_motor>[^\s]+)\s
    (?P<afue>[^\s]+)\s
    (?P<gas_value>[^\s]+)\s
    (?P<furnace_btu>[^\s]+)\s
    \$(?P<furnace_price>[^\s]+)\s
    (?P<cat_coil>[^\s]+)\s                    #cat coil
    (?P<coil_model>[^\s]+)\s
    (?P<coil_position>[^\s]+)\s
    (?P<coil_dimensions>[^\s]+)\s
    \$(?P<coil_price>[^\s]+)\s
    (?P<cu_btu>[^\s]+)\s
    (?P<eer>[^\s]+)\s
    \$(?P<system_price>[^\s]+)\s
    (?P<ahri>[^\s]+)
''', flags=FLAGS | re.VERBOSE)

re_sc = re.compile(r'''
    (?P<seer>[1-2][0-9]\.?\d?)\s
    (?P<junk>.*?)\s
    (?P<ahu_model>CB[-A-Z0-9]+)\s
    \$(?P<ahu_price>[^\s]+)\s
    (?P<ahu_dimensions>[^\s]+)\s
    (?P<filter_size>[^\s]+)\s
    (?P<coil_type>[^\s]+)\s
    (?P<fan_motor>[^\s]+)\s
    (?P<cat_heater>[^\s]+)\s
    (?P<heater_model>[^\s]+)\s
    \$(?P<heater_price>[^\s]+)\s
    (?P<cu_btu>[^\s]+)\s
    (?P<eer>[^\s]+)\s
    \$(?P<system_price>[^\s]+)\s
    (?P<ahri>[^\s]+)
''', flags=FLAGS | re.VERBOSE)

PATTERNS = [
    ('HP-AHU', re_hp),
    ('SC-AHU', re_sc),
    ('SC-GAS', re_gas)
]


def main():
    dna = common.get_dna(INPUT_FILE)
    results = set()
    for section in re_section.finditer(dna):
        section_map = section.groupdict()
        cu_model = section_map['cu_model']
        cu_mop = section_map['cu_mop']
        cu_mca = section_map['cu_mca']
        section_text = ' '.join(map(str.strip, section.groups()))
        for type_name, pattern in PATTERNS:
            for line_match in pattern.finditer(section_text):
                sys_map = line_match.groupdict()
                sys_map.pop('junk')
                sys_map['cu_model'] = cu_model
                sys_map['cu_mop'] = cu_mop
                sys_map['cu_mca'] = cu_mca
                sys_map['brand'] = BRAND
                sys_map['type'] = type_name
                sys_map = {k: common.trycast(v) for k, v in sys_map.items()}
                prices = sum(p for k, p in sys_map.items()
                             if 'price' in k and 'system' not in k and p > 0)
                sys_map['cu_price'] = sys_map['system_price'] - prices
                size = round(sys_map['cooling_btu'] / 12000 / 0.5) * 0.5
                if math.isclose(size, 4.5):
                    size = 5
                sys_map['size'] = size
                results.add(tuple(sorted(sys_map.items())))

    results = [dict(t) for t in results]
    print(f'...writing {len(results)} results to {SAVE_FILE}')
    with open(SAVE_FILE, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=common.FIELDS)
        w.writeheader()
        w.writerows(results)


if __name__ == '__main__':
    main()
