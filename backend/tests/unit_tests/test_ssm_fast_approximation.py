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
from mutation_maker.mutation import AminoMutation
from mutation_maker.ssm_fast_approximation import grow_primers, grow_forward_primer, grow_reverse_primer

from mutation_maker.ssm_types import SSMPrimerSpec
from mutation_maker.temperature_calculator import TemperatureConfig


class SSMPrimerGrowthTest(unittest.TestCase):
    def test_grow_forward_primer(self):
        temp_calculator = TemperatureConfig().create_calculator()

        max_primer_size = 12
        sequence = "AAACCCGGGTTT"
        mutation = AminoMutation(0, "", "", "", 0)
        overlap = SSMPrimerSpec(0, 3, 0, 0)

        primer = grow_forward_primer(max_primer_size, 0, sequence, mutation, overlap, 10, temp_calculator)

        self.assertEqual(primer.three_end_temp, temp_calculator("CCCGGG"))
        self.assertEqual(primer.three_end_size, 6)
        self.assertEqual(primer.offset, 0)

    def test_grow_reverse_primer(self):
        temp_calculator = TemperatureConfig().create_calculator()

        max_primer_size = 12
        sequence = "AAACCCGGGTTTAAAGGGCCC"
        mutation = AminoMutation(10, "", "", "", 0)
        overlap = SSMPrimerSpec(10, 3, 0, 0)

        primer = grow_reverse_primer(max_primer_size, 0, sequence, mutation, overlap, 10, temp_calculator)

        self.assertEqual(primer.three_end_temp, temp_calculator("CCGGGT"))
        self.assertEqual(primer.three_end_size, 6)
        self.assertEqual(primer.offset, 4)

    def test_grow_reverse_offset(self):
        temp_calculator = TemperatureConfig().create_calculator()
        prefix = "TTTTTTTTTTAAAAAC"
        overlap = "CGCC"

        sequence = prefix + overlap
        print(sequence)

        rv_computed = grow_reverse_primer(30, 0, sequence, AminoMutation(len(prefix), "", "", "", 0),
                                          SSMPrimerSpec(len(prefix), len(overlap), 0, 0),
                                          25.0, temp_calculator)

        expected_rv = SSMPrimerSpec(offset=5, length=15, three_end_size=11, three_end_temp=28.0)

        self.assertEqual(expected_rv, rv_computed)

    def test_grow_primers(self):
        temp_calculator = TemperatureConfig().create_calculator()
        prefix = "TTTTTTTTTTAAAAAC"
        overlap = "CGCC"
        suffix = "AAAAACTTTTTTTTTT"

        temp_thresh_fw = 25.0
        temp_thresh_rv = 25.0
        overlaps = [
            SSMPrimerSpec(len(prefix), len(overlap), len(overlap), 0)
        ]

        mutations = [AminoMutation(len(prefix), "", "", "", 0)]

        sequence = prefix + overlap + suffix
        print(sequence)

        fw_computed, rv_computed = grow_primers(
            min(len(prefix), len(suffix)), 0, sequence, mutations,
            overlaps, temp_thresh_fw, temp_thresh_rv, temp_calculator
        )

        expected_fw = SSMPrimerSpec(offset=len(prefix), length=13, three_end_size=10, three_end_temp=29.0)
        expected_rv = SSMPrimerSpec(offset=5, length=15, three_end_size=11, three_end_temp=28.0)

        self.assertEqual(expected_fw, fw_computed[0])
        self.assertEqual(expected_rv, rv_computed[0])
