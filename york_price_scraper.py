import csv
import re
from itertools import islice
from pathlib import Path

import common
from common import System
from common import trycast

BRAND = "York"
SAVE_FILE = 'york_results.csv'
INPUT_FILE = 'york_dna.txt'
FLAGS = re.MULTILINE | re.DOTALL
DIR = Path('./york/')


class Parser:
    files = []

    def iter_files(self):
        for f in self.files:
            p = DIR / (f + '.csv')
            if p.exists():
                with open(p) as opened:
                    reader = csv.reader(opened)
                    yield reader

    def _table_sections(self, rows):
        start = None
        end = None
        chunks = []
        cu_pattern = re.compile(r'([1-5]\.?\d?)\sTon.*', re.I)
        for i, row in enumerate(rows):
            if row:
                m = cu_pattern.match(row[0])
                if m:
                    if start is not None:
                        chunks.append((start, end + 1))
                    start = i
                elif row[1] or row[6]:
                    end = i
        if start is not None and end is not None:
            chunks.append((start, end + 1))
        return chunks

    def parse(self):
        pass


class HpParser(Parser):
    files = [
        'YHE', 'YHE - Front Return', 'YHE - Pancake', 'YHG', 'YHM',
        'Affinity YZT', 'Affinity YZV'
    ]

    def parse(self):
        all_systems = []
        for table in self.iter_files():
            rows = list(table)

            def cns(item):
                return trycast(item.strip().replace('$', '').replace(',', ''))

            rows = [[cns(i) for i in row] for row in rows]
            sections = self._table_sections(rows)
            for section in sections:
                wrows = list(islice(rows, *section))
                for row in wrows:
                    sys = System()
                    sys.brand = BRAND
                    sys.type = 'HP-AHU'
                    sys.size, sys.cu_model, *_, sys.cu_price = wrows[0][:6]
                    sys.size = cu_pattern.match(sys.size).group(1)
                    sys.cu_dimensions = wrows[1][4]
                    sys.cu_mop = wrows[2][4]
                    if len(wrows) > 3:
                        sys.cu_gas, sys.cu_liq = re.split(r'\s?x\s?', wrows[3][4], flags=re.I)
                    row = row[6:]
                    try:
                        (
                            sys.seer, sys.eer, sys.hspf,
                            sys.ahu_model, sys.ahu_price,
                            sys.ahu_dimensions, sys.ahu_family, sys.ahu_valve, sys.ahu_valve_price,
                            sys.heater_model, _, sys.heater_price, sys.cu_btu,
                            sys.system_price, sys.ahri, *_
                        ) = row
                    except ValueError:
                        print('!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!')
                        print(row)
                    if sys.seer:
                        all_systems.append(sys.to_dict())
        return all_systems


class ScParser(Parser):
    files = [
        'Affinity YXV', 'YFK', 'YCG - Front Return', 'YCG',
        'YCE', 'YCE - Front Return', 'YCE - Pancake',
    ]

    def parse(self):
        cu_pattern = re.compile(r'([1-5]\.?\d?)\sTon.*', re.I)
        all_systems = []
        for table in self.iter_files():
            rows = list(table)

            def cns(item):
                return trycast(item.strip().replace('$', '').replace(',', ''))

            rows = [[cns(i) for i in row] for row in rows]
            sections = self._table_sections(rows)
            for section in sections:
                wrows = list(islice(rows, *section))
                for row in wrows:
                    sys = System()
                    sys.brand = BRAND
                    sys.type = 'SC_AHU'
                    sys.size, sys.cu_model, *_, sys.cu_price = wrows[0][:6]
                    sys.size = cu_pattern.match(sys.size).group(1)
                    sys.cu_dimensions = wrows[1][4]
                    sys.cu_mop = wrows[2][4]
                    if len(wrows) > 3:
                        try:
                            sys.cu_gas, sys.cu_liq = re.split(r'\s?x\s?', wrows[3][4], flags=re.I)
                        except ValueError:
                            pass

                    row = row[6:]
                    row = [r for r in row if r]

                    if len(row) == 11:
                        try:
                            (
                                sys.seer,
                                sys.ahu_model, sys.ahu_price,
                                sys.ahu_dimensions, sys.ahu_family, _, sys.ahu_valve,
                                sys.heater_model, sys.cu_btu,
                                sys.system_price, sys.ahri, *_
                            ) = row
                        except ValueError:
                            print('!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!')
                            print(row)
                    elif len(row) == 12:
                        try:
                            (
                                sys.seer,
                                sys.ahu_model, sys.ahu_price,
                                sys.ahu_dimensions, sys.ahu_family, sys.ahu_valve, sys.ahu_valve_price,
                                sys.heater_model, sys.heater_price, sys.cu_btu,
                                sys.system_price, sys.ahri, *_
                            ) = row
                        except ValueError:
                            print('!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!')
                            print(row)
                    elif len(row) == 13:
                        try:
                            (
                                sys.seer,
                                sys.ahu_model, sys.ahu_price,
                                sys.ahu_dimensions, sys.ahu_family, sys.ahu_valve, sys.ahu_valve_price,
                                sys.heater_model, _, sys.heater_price, sys.cu_btu,
                                sys.system_price, sys.ahri, *_
                            ) = row
                        except ValueError:
                            print('!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!')
                            print(row)
                    elif len(row) == 14:
                        try:
                            (
                                sys.seer,
                                sys.ahu_model, sys.ahu_price,
                                sys.ahu_dimensions, sys.ahu_family, sys.ahu_valve, sys.ahu_valve_price,
                                sys.heater_model, _, sys.heater_price, sys.cu_btu, _,
                                sys.system_price, sys.ahri, *_
                            ) = row
                        except ValueError:
                            print('!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!')
                            print(row)
                    d = sys.to_dict()
                    if 'seer' in d and d['seer']:
                        all_systems.append(d)
        return all_systems


class GasParser(Parser):
    files = ['YCE-Gas', 'YCG-GAS']

    def parse(self):
        cu_pattern = re.compile(r'([1-5]\.?\d?)\sTon.*', re.I)
        all_systems = []
        for table in self.iter_files():
            rows = list(table)

            def cns(item):
                return trycast(item.strip().replace('$', '').replace(',', ''))

            rows = [[cns(i) for i in row] for row in rows]
            sections = self._table_sections(rows)
            for section in sections:
                wrows = list(islice(rows, *section))
                for row in wrows:
                    sys = System()
                    sys.brand = BRAND
                    sys.type = 'SC_GAS'
                    sys.size, sys.cu_model, *_, sys.cu_price = wrows[0][:5]
                    sys.size = cu_pattern.match(sys.size).group(1)
                    sys.cu_dimensions = wrows[1][4]
                    sys.cu_mop = wrows[2][4]
                    if len(wrows) > 3:
                        try:
                            sys.cu_gas, sys.cu_liq = re.split(r'\s?x\s?', wrows[3][4], flags=re.I)
                        except ValueError:
                            pass

                    row = row[5:]
                    row = [r for r in row if r != '' and r is not None]
                    if len(row) == 12:
                        try:
                            (
                                sys.seer,
                                sys.furnace_model, sys.furnace_price,
                                sys.furnace_dimensions, sys.furnace_family,
                                sys.coil_model, sys.coil_price, sys.coil_dimensions,
                                sys.ahu_valve, sys.ahu_valve_price, sys.cu_btu,
                                sys.system_price, sys.ahri, *_
                            ) = row
                        except ValueError:
                            print('!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!')
                            print(row)
                    if len(row) == 13:
                        try:
                            (
                                sys.seer,
                                sys.furnace_model, sys.furnace_price,
                                sys.furnace_dimensions, sys.furnace_family,
                                sys.coil_model, sys.coil_price, sys.coil_dimensions,
                                sys.ahu_valve, sys.ahu_valve_price, sys.cu_btu,
                                sys.system_price, sys.ahri, *_
                            ) = row
                        except ValueError:
                            print('!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!')
                            print(row)
                    d = sys.to_dict()
                    if 'seer' in d and d['seer']:
                        all_systems.append(d)
        return all_systems


def main():
    parsers = [HpParser, ScParser, GasParser]
    results = []
    for P in parsers:
        res = P().parse()
        results.extend(res)

    with open(SAVE_FILE, 'w', newline='') as f:
        w = csv.DictWriter(f, common.FIELDS)
        w.writeheader()
        w.writerows(results)


if __name__ == '__main__':
    main()
