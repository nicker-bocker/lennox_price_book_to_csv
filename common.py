import re
import contextlib

def trycast(val):
    for cast in (int, float, str, lambda x: x):
        with contextlib.suppress(ValueError):
            return cast(val)


def get_dna(file):
    with open(file) as f:
        contents = f.read()
        contents = re.sub(r'v.\sspeed', 'variable', contents, flags=re.IGNORECASE)
        contents = re.sub(r'[?,]', '', contents)
        contents = contents.replace('\n', ' ')
    return contents

FIELDS = [
    "brand", "type", "size", "seer", "eer", "hspf", 'ahri', 'afue',
    'cu_btu', 'cu_model', 'cu_family', 'cu_price', 'cu_mop', 'cu_mca', 'cu_dimensions', 'cu_liq', 'cu_gas',
    'ahu_model', 'ahu_family', 'ahu_price', 'ahu_dimensions', 'fan_motor', 'ahu_valve', 'ahu_valve_price'
    'filter_size',
    'cat_coil', 'coil_type', 'coil_model', 'coil_position','coil_dimensions', 'coil_price',
    'cat_heater', 'heater_model','heater_price',
    'furnace_model', 'furnace_family', 'furnace_dimensions', 'furnace_btu','furnace_price', 'furnace_position', 'gas_value',
    'system_price'
]