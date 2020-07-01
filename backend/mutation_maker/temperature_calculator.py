#    Copyright (c) 2020 Merck Sharp & Dohme Corp. a subsidiary of Merck & Co., Inc., Kenilworth, NJ, USA.
#
#    This file is part of the Mutation Maker, An Open Source Oligo Design Software For Mutagenesis and De Novo Gene Synthesis Experiments.
#
#    Mutation Maker is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from functools import partial
from typing import List, Tuple, NamedTuple

from Bio.SeqUtils import MeltingTemp
from jsonobject import (StringProperty, IntegerProperty, FloatProperty, JsonObject)
from primer3 import calcHairpin, calcHomodimer, calcTm, calcHeterodimer

gc_value_sets = ["Chester_1993", "QuickChange", "Schildkraut_1965", "Wetmur_Melting_1991",
                 "Wetmur_RNA_1991", "Wetmur_DNA_RNA_1991", "Primer3", "Ahsen_2001"]
nn_tables = ["SantaLucia_1997", "SantaLucia_2004", "Breselauer_1986", "Sugimoto_1996"]
salt_corrections = ["No", "Schildkraut_1965", "Wetmur_1991", "SantaLucia_1996", "SantaLucia_1998",
                    "SantaLucia_DeltaS_1998", "Owczarzy_2004", "Owczarzy_2008"]


def create_default_qclm_temperature_config():
    return TemperatureConfig(
        calculation_type="GC",
        gc_value_set="QuickChange",
        salt_correction="No",
        na=0,
        k=50,
        tris=20,
        mg=2,
        dntp=0.2,
        dnca1=500,
        precision=1)

def create_default_pas_temperature_config():
    return TemperatureConfig(
        calculation_type="GC",
        gc_value_set="QuickChange",
        salt_correction="No",
        na=0,
        k=50,  # = monovalent cation concentration
        tris=20,
        mg=2,  # = divalent cation concentration
        dntp=0.2,  # DNTP concentration
        dnca1=500,
        precision=1)


def get_all_temp_ranges_between(minimum, maximum, range_size, increment) -> List[Tuple[float, float]]:
    if maximum <= minimum:
        return []
    if (maximum - minimum) <= range_size:
        return [(minimum, maximum)]
    ranges = []
    i = 0
    actual_min = minimum
    actual_max = actual_min + range_size
    while actual_max <= maximum:
        ranges.append((actual_min, actual_max))
        i = i + 1
        actual_min = (i * increment) + minimum
        actual_max = actual_min + range_size
    return ranges


class TemperatureCalculator:
    def __init__(self, calculation_method, precision: int, cached: bool = True):
        self.calculation_method = calculation_method
        self.precision = precision
        self.precision_increment = 1 / (10**precision)
        self.cached = cached
        self.cache = {}

    def __call__(self, primer: str) -> float:
        if len(primer) > 0:
            if self.cached:
                if primer in self.cache:
                    return self.cache[primer]
            temp = self.calculation_method(primer)
            temp = round(temp, self.precision)
            if self.cached:
                self.cache[primer] = temp
            return temp
        else:
            # TODO remove and let raise exception
            return -float("inf")
        raise ValueError("Cannot calculate temperature of empty primer")


class PrimerDimerCalculator():
    def __init__(self,monovalent: float, divalent: float, dntp: float, cached: bool = True):
        self.cached = cached
        self.cache_homo = {}
        self.cache_hairpin = {}
        self.cache_hetero = {}
        self.mv = monovalent
        self.dv = divalent
        self.dntp = dntp

    def homodimer(self, primer: str) -> float:
        """
        Cached homodimer computation with Primer3 library.
        :param primer: [str] primer sequence
        :return: melting temperature
        """
        if len(primer) > 0:
            if self.cached:
                if primer in self.cache_homo:
                    return self.cache_homo[primer]
            temp = calcHomodimer(primer, self.mv, self.dv, self.dntp).tm
            if self.cached:
                self.cache_homo[primer] = temp
            return temp
        else:
            return 0

    def hairpin(self, primer: str) -> float:
        """
        Cached hair pin computation with Primer3 library.
        :param primer: [str] primer sequence
        :return: melting temperature
        """
        if len(primer) > 0:
            if self.cached:
                if primer in self.cache_hairpin:
                    return self.cache_hairpin[primer]
            temp = calcHairpin(primer, self.mv, self.dv, self.dntp).tm
            if self.cached:
                self.cache_hairpin[primer] = temp
            return temp
        else:
            return 0

    def heterodimer(self, primer: str, other_primer: str) -> float:
        """
        Cached heterodimer computation with Primer3 library.

        :param primer: [str] primer sequence
        :return: melting temperature
        """
        if len(primer) > 0:
            key = primer + '_' + other_primer
            if self.cached:
                if key in self.cache_hetero:
                    return self.cache_hetero[key]
            temp = calcHeterodimer(primer, other_primer, self.mv, self.dv, self.dntp).tm
            if self.cached:
                self.cache_hetero[key] = temp
            return temp
        else:
            return 0


class NEB_like_calculator():
    def __init__(self, calculation_method="", precision: int = 0, cached: bool = True):
        self.calculation_method = calculation_method
        self.precision = precision
        self.precision_increment = 1 / (10**precision)
        self.cached = cached
        self.cache = {}


    def __call__(self, primer: str) -> float:
        """
        We created NEB like calculation method from here:
        According to the article: https://tmcalculator.neb.com/#!/help
        we offset our results by 3 and it yields similar results as default NEB calculator
        for Q5 product group + High Fidelity.

        :param primer: [str] primer sequence
        :return: melting temperature
        """
        if len(primer) > 0:
            if self.cached:
                if primer in self.cache:
                    return self.cache[primer]
            temp = calcTm(
                            primer,
                            dna_conc=(500 / 6) * 7,  # primer is assumed 6x template
                            mv_conc=(60 + 20),
                            dv_conc=2,
                            tm_method='santalucia',
                            salt_corrections_method='owczarzy') + 3 # +3 because NEB documentation recommends it and it is fairly close
            temp = round(temp, self.precision)
            if self.cached:
                self.cache[primer] = temp
            return temp
        else:
            # TODO remove and let raise exception
            return -float("inf")
        raise ValueError("Cannot calculate temperature of empty primer")


class HeteroDimerCalculator:
    """ Computes melting temperatures for hetero dimers -> primers binding to others"""

    def __init__(self, monovalent: float, divalent: float, dntp: float):
        # Arguments have the same meaning as in the primer3 library
        self.mv = monovalent
        self.dv = divalent
        self.dntp = dntp

    def __call__(self, primer_seq, other_primer_seq: str) -> float:
        return calcHeterodimer(primer_seq, other_primer_seq, self.mv, self.dv, self.dntp).tm


class SelfBindingTemps(NamedTuple):
    """ Melting temperatures for forming a hairpin or homodimer """
    hairpin_tm: float
    homodimer_tm: float


class SelfBindingCalculator:
    """ Computes melting temperatures for hairpins and primer dimers"""

    def __init__(self, monovalent: float, divalent: float, dntp: float):
        # Arguments have the same meaning as in the primer3 library
        self.mv = monovalent
        self.dv = divalent
        self.dntp = dntp

    def __call__(self, primer_seq: str) -> SelfBindingTemps:
        hairpin_tm = calcHairpin(primer_seq, self.mv, self.dv, self.dntp).tm
        homodimer_tm = calcHomodimer(primer_seq, self.mv, self.dv, self.dntp).tm
        return SelfBindingTemps(hairpin_tm, homodimer_tm)


class TemperatureConfig(JsonObject):
    calculation_type = StringProperty(required=True, choices=["Wallace", "GC", "NN", "NEB_like"], default="NN")
    gc_value_set = StringProperty(choices=gc_value_sets, default="QuickChange")
    nn_table = StringProperty(choices=nn_tables, default="SantaLucia_1997")
    salt_correction = StringProperty(choices=salt_corrections, default="Owczarzy_2004")
    dnac1 = FloatProperty(default=500)
    dnac2 = FloatProperty(default=25)
    na = FloatProperty(default=50)
    k = FloatProperty(default=50)
    tris = FloatProperty(default=20)
    mg = FloatProperty(default=2)
    dntp = FloatProperty(default=0.2)
    # TODO: this isn't really being used in SSM anymore, check if it is needed in QCLM and remove it
    precision = IntegerProperty(default=0)

    def create_calculator(self, cached=True):
        if self.calculation_type == "Wallace":
            return self.create_wallace_calculator(cached)
        if self.calculation_type == "GC":
            return self.create_gc_calculator(cached)
        if self.calculation_type == "NN":
            return self.create_nn_calculator(cached)
        if self.calculation_type == "NEB_like":
            return self.create_neb_calculator(cached)

    def create_wallace_calculator(self, cached):
        return TemperatureCalculator(MeltingTemp.Tm_Wallace, self.precision, cached)

    def create_gc_calculator(self, cached):
        valueset_id = self.get_gc_valueset_id()
        saltcorrection_id = self.get_salt_correction_id()
        calc_func = partial(MeltingTemp.Tm_GC, valueset=valueset_id, saltcorr=saltcorrection_id,
                            Na=self.na, K=self.k, Tris=self.tris, Mg=self.mg, dNTPs=self.dntp,
                            strict=False)
        return TemperatureCalculator(calc_func, self.precision, cached)

    def create_nn_calculator(self, cached):
        table = self.get_nn_table()
        saltcorrection_id = self.get_salt_correction_id()
        calc_func = partial(MeltingTemp.Tm_NN, nn_table=table, saltcorr=saltcorrection_id,
                            Na=self.na, K=self.k, Tris=self.tris, Mg=self.mg, dnac1=self.dnac1,
                            dnac2=self.dnac2, dNTPs=self.dntp)
        return TemperatureCalculator(calc_func, self.precision, cached)

    def create_neb_calculator(self, cached):
        return NEB_like_calculator(cached)

    def get_gc_valueset_id(self):
        return gc_value_sets.index(self.gc_value_set) + 1

    def get_salt_correction_id(self):
        return salt_corrections.index(self.salt_correction)

    def get_nn_table(self):
        if self.nn_table == "Breselauer_1986":
            return MeltingTemp.DNA_NN1
        if self.nn_table == "Sugimoto_1996":
            return MeltingTemp.DNA_NN2
        if self.nn_table == "SantaLucia_1997":
            return MeltingTemp.DNA_NN3
        if self.nn_table == "SantaLucia_2004":
            return MeltingTemp.DNA_NN4
