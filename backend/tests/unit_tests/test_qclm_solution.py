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

from mutation_maker.basic_types import AminoAcid, Offset
from mutation_maker.qclm_solution import PrimerSpec, DNASequenceForMutagenesis
from mutation_maker.site_split import SiteSequenceAminos

base_sequence = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"


class PrimerSpecTest(unittest.TestCase):
    def test_get_sequence_zero_offset_primer(self):
        primer_spec = PrimerSpec(0, 6, ["AAA"])

        mutated_sequence = DNASequenceForMutagenesis(base_sequence, [Offset(0)])
        mutagenic_primer = primer_spec.get_sequence(mutated_sequence)

        self.assertEqual(mutagenic_primer, "AAATTT")

        mutated_sequence2 = DNASequenceForMutagenesis(base_sequence, [Offset(1)])
        mutagenic_primer2 = primer_spec.get_sequence(mutated_sequence2)

        self.assertEqual(mutagenic_primer2, "GAAATT")

    def test_get_sequence_offset_primer_no_mutation(self):
        primer_spec = PrimerSpec(2, 7, [])
        mutated_sequence = DNASequenceForMutagenesis(base_sequence, [])
        mutagenic_primer = primer_spec.get_sequence(mutated_sequence)

        self.assertEqual(mutagenic_primer, "GTTTAAA")

    def test_get_sequence_offset_primer(self):
        primer_spec = PrimerSpec(2, 7, ["WWW"])
        # It is important to note here that the offset is absolute,
        # in another words, it is relative to the start of the whole DNA sequence,
        # not relative ot the start of the primer.
        mutated_sequence = DNASequenceForMutagenesis(base_sequence, [Offset(3)])
        mutagenic_primer = primer_spec.get_sequence(mutated_sequence)

        self.assertEqual(mutagenic_primer, "GWWWAAA")

    def test_get_sequence_primer_in_the_middle(self):
        primer_spec = PrimerSpec(6, 7, ["TTT"])
        mutated_sequence = DNASequenceForMutagenesis(base_sequence, [Offset(0), Offset(9), Offset(18)])
        mutagenic_primer = primer_spec.get_sequence(mutated_sequence)

        self.assertEqual(mutagenic_primer, "AAATTTG")

    def test_merge_amino_sequences(self):
        subset1 = SiteSequenceAminos(tuple([
            frozenset({AminoAcid("F"), AminoAcid("L")}),
            frozenset({AminoAcid("S")})
        ]))

        subset2 = SiteSequenceAminos(tuple([
            frozenset({AminoAcid("I")}),
            frozenset({AminoAcid("N"), AminoAcid("K")})
        ]))

        merged = SiteSequenceAminos.merge_amino_sequences([subset1, subset2])

        self.assertEqual(merged[0], {"F", "L", "I"})
        self.assertEqual(merged[1], {"S", "N", "K"})
