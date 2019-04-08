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



class System:
    __slots__ = [
        "brand", "type", "size", "seer", "eer", "hspf", 'ahri', 'afue',
        'cu_btu', 'cu_model', 'cu_family', 'cu_price', 'cu_mop', 'cu_mca', 'cu_dimensions', 'cu_liq', 'cu_gas',
        'ahu_model', 'ahu_family', 'ahu_price', 'ahu_dimensions', 'fan_motor', 'ahu_valve', 'ahu_valve_price',
        'filter_size',
        'cat_coil', 'coil_type', 'coil_model', 'coil_position','coil_dimensions', 'coil_price',
        'cat_heater', 'heater_model','heater_price',
        'furnace_model', 'furnace_family', 'furnace_dimensions', 'furnace_btu','furnace_price', 'furnace_position', 'gas_value',
        'system_price'
    ]

    def to_dict(self):
        return {k: getattr(self, k) for k in sorted(self.__slots__) if hasattr(self, k)}


FIELDS = System.__slots__


# class System:
#     def __init__(self, **kwargs):
#         self.brand = None
#         self.type = None
#         self.size = None
#         self.seer = None
#         self.eer=None
#         self.hspf=None
#         self.ahri=None
#         self.afue=None
#         self.cu_btu=None
#         self.cu_model=None
#         self.cu_family=None
#         self.cu_price=None
#         self.cu_mop=None
#         self.cu_mca=None
#         self.cu_dimensions=None
#         self.cu_liq', 'cu_gas',
#         'ahu_model', 'ahu_family', 'ahu_price', 'ahu_dimensions', 'fan_motor', 'ahu_valve', 'ahu_valve_price'
#                                                                                             'filter_size',
#         'cat_coil', 'coil_type', 'coil_model', 'coil_position', 'coil_dimensions', 'coil_price',
#         'cat_heater', 'heater_model', 'heater_price',
#         'furnace_model', 'furnace_family', 'furnace_dimensions', 'furnace_btu', 'furnace_price', 'furnace_position',
#         'gas_value',
#         'system_price'
#         ])