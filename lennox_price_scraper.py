import csv
import re
from contextlib import suppress

BRAND = "Lennox"

FLAGS = re.MULTILINE | re.DOTALL

_cu_model_pattern = r'(?:XC|XP|SL|EL|14|16|ML)[-A-Z0-9]+-0(?:60|48|42|36|30|24|18)'

re_section = re.compile(fr'''
    (?P<seer>[1-2][0-9]\.?\d?)\s
    (?P<cu_model>{_cu_model_pattern})
    (?P<other>.*?)
    MOP.*?
    (?P<cu_mop_mca>\d\d\s/\s\d+\.?\d?)
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
    (?P<cooling_btu>[^\s]+)\s
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
    (?P<cooling_btu>[^\s]+)\s
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
    (?P<cooling_btu>[^\s]+)\s
    (?P<eer>[^\s]+)\s
    \$(?P<system_price>[^\s]+)\s
    (?P<ahri>[^\s]+)
''', flags=FLAGS | re.VERBOSE)

PATTERNS = [
    ('HP-AHU', re_hp),
    ('SC-AHU', re_sc),
    ('SC-GAS', re_gas)
]

FIELDS = [
    "brand", "type", "size", "seer", "eer", "hspf", 'ahri', 'afue',
    'cooling_btu', 'cu_model', 'cu_price', 'cu_mop_mca',
    'ahu_model', 'ahu_price', 'ahu_dimensions', 'fan_motor', 'txv',
    'filter_size', 'cat_coil', 'coil_type', 'coil_model', 'coil_position',
    'coil_dimensions', 'coil_price', 'cat_heater', 'heater_model',
    'heater_price', 'furnace_model', 'furnace_dimensions', 'furnace_btu',
    'furnace_price', 'furnace_position', 'gas_value', 'system_price'
]


def trycast(val):
    for cast in (int, float, str, lambda x: x):
        with suppress(ValueError):
            return cast(val)


def get_dna():
    with open('lennox_dna.txt') as f:
        contents = f.read()
        contents = re.sub(r'v.\sspeed', 'variable', contents, flags=re.IGNORECASE)
        contents = re.sub(r'[?,\n]', '', contents)
    return contents


def main():
    dna = get_dna()
    results = set()
    for section in re_section.finditer(dna):
        sd = section.groupdict()
        cu_model = sd['cu_model']
        cu_mop_mca = sd['cu_mop_mca']
        section_text = ' '.join(map(str.strip, section.groups()))
        for type_name, p in PATTERNS:
            for line_match in p.finditer(section_text):
                xd = line_match.groupdict()
                xd.pop('junk')
                xd['cu_model'] = cu_model
                xd['cu_mop_mca'] = cu_mop_mca
                xd['brand'] = BRAND
                xd['type'] = type_name
                xd = {k: trycast(v) for k, v in xd.items()}
                prices = sum(p for k, p in xd.items()
                             if 'price' in k and 'system' not in k and p)
                xd['cu_price'] = xd['system_price'] - prices
                size = round(xd['cooling_btu'] / 12000 / 0.5) * 0.5
                if size == 4.5:
                    size = 5
                xd['size'] = size
                results.add(tuple(sorted(xd.items())))

    results = [dict(t) for t in results]
    with open('all_results.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(results)


if __name__ == '__main__':
    main()
