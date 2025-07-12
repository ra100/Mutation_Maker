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

import unittest

from mutation_maker.temperature_calculator import get_all_temp_ranges_between, TemperatureConfig


class CalculatorTest(unittest.TestCase):
    def test_get_ranges(self):
        start = 64
        end = 72
        rng = 5

        ranges = get_all_temp_ranges_between(start, end, rng, 1)
        self.assertEqual(4, len(ranges))
        self.assertEqual((64, 69), ranges[0])
        self.assertEqual((67, 72), ranges[-1])

    def test_get_ranges_prec_1(self):
        start = 64
        end = 72
        rng = 5

        ranges = get_all_temp_ranges_between(start, end, rng, 0.1)
        self.assertEqual(31, len(ranges))
        self.assertEqual((64, 69), ranges[0])
        self.assertEqual((67, 72), ranges[-1])

    def test_get_ranges_prec_2(self):
        start = 64
        end = 72
        rng = 5
        ranges = get_all_temp_ranges_between(start, end, rng, 0.01)
        self.assertEqual(301, len(ranges))
        self.assertEqual((64, 69), ranges[0])
        self.assertEqual((67, 72), ranges[-1])

    def test_get_ranges_prec_shorter(self):
        start = 64
        rng = 5

        ranges = get_all_temp_ranges_between(start, 71, rng, 1)
        self.assertEqual(3, len(ranges))
        self.assertEqual((64, 69), ranges[0])
        self.assertEqual((66, 71), ranges[-1])

    def test_get_ranges_single(self):
        start = 64
        rng = 5

        ranges = get_all_temp_ranges_between(start, 69, rng, 1)
        self.assertEqual(1, len(ranges))
        self.assertEqual((64, 69), ranges[0])
        self.assertEqual((64, 69), ranges[-1])

    def test_temperature_calc_empty_prim(self):
        # TODO fix this, we should implement try chat around all calls in PAS workflow
        pass
        # temp_calculator = TemperatureConfig().create_calculator()
        # with self.assertRaises(ValueError) as context:
        #     temp_calculator("")
        # self.assertIn("empty primer", str(context.exception))

    def test_temperature_calc_valid_input(self):
        temp_calculator = TemperatureConfig().create_calculator()
        self.assertEqual(64, temp_calculator("CTCTCTCTCTCTCTCTCTCT"))

    def test_temperature_calc_valid_input_complements(self):
        temp_calculator = TemperatureConfig().create_calculator()
        self.assertEqual(64, temp_calculator("CTCTCTCTCTCTCTCTCTCT"))
        self.assertEqual(temp_calculator("GAGAGAGAGAGAGAGAGAGA"), temp_calculator("CTCTCTCTCTCTCTCTCTCT"))

    def test_gc_calc_valid_input(self):
        gc_calculator = TemperatureConfig(calculation_type="GC").create_calculator()
        self.assertEqual(68, gc_calculator("CTCTCTCTCTCTCTCTCTCT"))

    def test_gc_calc_valid_input_complement(self):
        temp_calculator = TemperatureConfig(calculation_type="GC").create_calculator()
        self.assertEqual(68, temp_calculator("CTCTCTCTCTCTCTCTCTCT"))
        self.assertEqual(temp_calculator("GAGAGAGAGAGAGAGAGAGA"), temp_calculator("CTCTCTCTCTCTCTCTCTCT"))

    def test_wallace_calc_valid_input(self):
        wl_calculator = TemperatureConfig(calculation_type="Wallace").create_calculator()
        self.assertEqual(60, wl_calculator("CTCTCTCTCTCTCTCTCTCT"))

    def test_wallace_calc_valid_input_complement(self):
        wl_calculator = TemperatureConfig(calculation_type="Wallace").create_calculator()
        self.assertEqual(60, wl_calculator("CTCTCTCTCTCTCTCTCTCT"))
        self.assertEqual(wl_calculator("GAGAGAGAGAGAGAGAGAGA"), wl_calculator("CTCTCTCTCTCTCTCTCTCT"))


    def test_NEB_like_calculation(self):
        # Test NEB-like calculation with actual DNA sequences
        # Using sequences with varying GC content and lengths to test the calculator
        temperature_pairs = {
            "ATGCGTACGTAGCTAGCTAGCTAGCTAGC": (70, 76),  # Mixed sequence ~73°C
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAA": (50, 58),   # Low GC content ~54°C
            "CCCCCCCCCCCCCCCCCCCCCCCCCCCCC": (95, 105),  # High GC content ~100°C
            "ATCGATCGATCGATCGATCGATCGATCG": (68, 76),   # Alternating ~72°C
            "GCGCGCGCGCGCGCGCGCGCGCGCGCGC": (95, 105),  # High GC alternating ~99°C
            "ATATATATATATATATATATATATATA": (39, 47),   # Low GC alternating ~43°C
            "ATGCGTACGTAGCTAGCTAGCTAGC": (66, 74),      # Shorter sequence ~70°C
            "ATGCGTACGTAGCTAGCTAGCTAGCTAGCATGCGTACG": (75, 83),  # Longer sequence ~79°C
        }

        nc = TemperatureConfig(calculation_type="NEB_like").create_calculator()
        for sequence, (min_temp, max_temp) in temperature_pairs.items():
            calculated_temp = nc(sequence)
            print("Sequence: '{}' , expected range: {}-{}, calculated tm: {}".format(
                sequence, min_temp, max_temp, calculated_temp))
            self.assertTrue(min_temp <= calculated_temp <= max_temp,
                          f"Temperature {calculated_temp} not in expected range [{min_temp}, {max_temp}] for sequence {sequence}")
