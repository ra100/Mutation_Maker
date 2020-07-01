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

import random
import unittest

from Bio.Seq import reverse_complement

from mutation_maker.pas_types import PASOligoOutput, PASSequences


class TestPASOligoOutput(unittest.TestCase):

    def test_reverse_complement_sequence(self):
        sequence = ''.join([random.choice(["A","C","T","G"]) for _ in range(100)])

        json_obj = PASOligoOutput(sequence=sequence, mix_ratio = 0.2, mutations = [], reds=[], blues=[])

        json_obj.make_reverse_complement()

        self.assertEqual(json_obj.sequence, reverse_complement(sequence))


    def test_reverse_complement_reindexing(self):
        sequence = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        mix_ratio = 0.4
        mutations = [1]
        reds = [3]
        blues = [9]

        json_obj = PASOligoOutput(sequence=sequence, mix_ratio = mix_ratio, mutations = mutations, reds=reds, blues=blues)

        json_obj.make_reverse_complement()

        self.assertEqual(json_obj.sequence, reverse_complement(sequence))

        # check reds reversed correctly
        red = json_obj.sequence[json_obj.reds[0]:json_obj.reds[0]+3]
        self.assertEqual(red,"AGA")

        # check blues reversed correctly
        blue = json_obj.sequence[json_obj.blues[0]:json_obj.blues[0]+3]
        self.assertEqual(blue, "GCG")

class TestPASSequences(unittest.TestCase):

    def test_get_full_sequence_with_offset(self):
        PASSequences(gene_of_interest="PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING")
