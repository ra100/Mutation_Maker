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

import itertools
import unittest

from mutation_maker.degenerate_codon import DegenerateTriplet, DegenerateTripletWithAminos, count_same_bases, CodonUsage

e_coli = CodonUsage("e-coli")


class DegenerateTripletTest(unittest.TestCase):
    def test_non_degenerate_triplets(self):
        test_cases = [
            ("AAA", ["AAA"]),
            ("NAA", ["AAA", "CAA", "TAA", "GAA"]),
            ("KAK", ["GAG", "GAT", "TAG", "TAT"]),
            ("WSY", ["AGC", "AGT", "TGC", "TGT", "ACC", "ACT", "TCC", "TCT"])
        ]

        for degenerate_codon, non_degenerate_codons in test_cases:
            non_deg_codons = DegenerateTriplet.get_all_non_degenerate_codons(degenerate_codon)

            self.assertEqual(set(non_deg_codons), set(non_degenerate_codons))

    def test_degenerate_codon_to_aminos(self):
        test_cases = [
            ("AAA", ["K"]),
            ("KAT", ["Y", "D"]),
            ("BGG", ["W", "R", "G"])
        ]

        for degenerate_codon, aminos in test_cases:
            generated_aminos = DegenerateTriplet.degenerate_codon_to_aminos(degenerate_codon,e_coli.table.forward_table)

            self.assertEqual(set(aminos), set(generated_aminos))

    def test_count_same_bases(self):
        self.assertEqual(1, count_same_bases("AAT", "TAG"))
        self.assertEqual(2, count_same_bases("AAT", "KAT"))
        self.assertEqual(2, count_same_bases("AAT", "TAT"))
        self.assertEqual(2, count_same_bases("RAT", "RAG"))
        # Here we just make sure it only counts exactly matching bases
        # and not degenerate bases.
        self.assertEqual(0, count_same_bases("AAT", "NNN"))


class DegenerateTripletWithAminosTest(unittest.TestCase):
    def test_parse_from_codon_string(self):
        triplet = DegenerateTripletWithAminos.parse_from_codon_string("BGG",e_coli.table.forward_table)

        self.assertEqual({"C", "T", "G"}, triplet.base1.bases)
        self.assertEqual({"G"}, triplet.base2.bases)
        self.assertEqual({"G"}, triplet.base3.bases)

        self.assertEqual({"W", "R", "G"}, set(triplet.aminos))

    def test_set_cover_with_degenerate_code(self):
        codon1 = DegenerateTripletWithAminos.parse_from_codon_string("TTT",e_coli.table.forward_table)
        codon2 = DegenerateTripletWithAminos.parse_from_codon_string("CTT",e_coli.table.forward_table)

        degenerate = DegenerateTripletWithAminos.set_cover_with_degenerate_code([
            codon1, codon2
        ])

        self.assertEqual(str(degenerate.pop()), "YTT")

    def test_set_cover_with_degenerate_code_no_single_solution(self):
        degenerate = DegenerateTripletWithAminos.set_cover_with_degenerate_code([
            DegenerateTripletWithAminos.parse_from_codon_string(codon,e_coli.table.forward_table)
            for codon in ["TTT", "CTT", "ATT", "ACG"]
        ])

        self.assertEqual(set(str(deg) for deg in degenerate), {"HTT", "ACG"})

    def test_degenerate_union_decode(self):
        codons = ["TTT", "TTA", "ATT", "GTT", "ACT", "AAT", "GAT", "GGG"]

        original_aminos = set(e_coli.table.forward_table[codon] for codon in codons)

        degenerate_codons = DegenerateTripletWithAminos.set_cover_with_degenerate_code([
            DegenerateTripletWithAminos.parse_from_codon_string(codon,e_coli.table.forward_table)
            for codon in codons
        ])

        decoded_aminos_per_degenerate_codon = [
            set(DegenerateTriplet.degenerate_codon_to_aminos(str(deg_codon),e_coli.table.forward_table))
            for deg_codon in degenerate_codons
        ]

        # Before checking the decoding we just quickly check if the
        # set cover is disjoint.
        for a, b in itertools.combinations(decoded_aminos_per_degenerate_codon, 2):
            self.assertEqual(len(a.intersection(b)), 0)

        all_decoded_aminos = set.union(*decoded_aminos_per_degenerate_codon)

        self.assertEqual(original_aminos, all_decoded_aminos)

    def test_multi_site_set_cover(self):
        test_cases = [
            (
                [{"AAA"}, {"GGG"}],
                [{"AAA"}, {"GGG"}]
            ),
            (
                [{"AAA", "GAA"}, {"GGG", "GGT"}],
                [{"RAA"}, {"GGK"}]
            ),
            (
                # In this case each site has only one degenerate solution
                [{"AAA", "GAA", "CCC", "TTT"}, {"GGG", "CGG", "TTT", "AAA"}],
                [{"RAA", "CCC", "TTT"}, {"SGG", "TTT", "AAA"}]
            ),
            (
                # In this case the second site doesn't have any degenerate solutions
                [{"AAA", "GAA", "CCC", "CCA"}, {"GGG", "CCC", "TTT", "AAA"}],
                [{"AAA", "GAA", "CCC", "CCA"}, {"GGG", "CCC", "TTT", "AAA"}]
            )
        ]

        for test_case in test_cases:
            solution = DegenerateTripletWithAminos.stringified_multi_site_set_cover(test_case[0], e_coli.table.forward_table)
            self.assertEqual(test_case[1], solution)

    def test_site_separate_set_cover(self):
        test_cases = [
            (
                [{"AAA"}, {"GGG"}],
                [{"AAA"}, {"GGG"}]
            ),
            (
                [{"AAA", "GAA"}, {"GGG", "GGT"}],
                [{"RAA"}, {"GGK"}]
            ),
            (
                # In this case each site has only one degenerate solution
                [{"AAA", "GAA", "CCC", "TTT"}, {"GGG", "CGG", "TTT", "AAA"}],
                [{"RAA", "CCC", "TTT"}, {"SGG", "TTT", "AAA"}]
            ),
            (
                # In this case the second site doesn't have any degenerate solutions
                [{"AAA", "GAA", "CCC", "CCA"}, {"GGG", "CCC", "TTT", "AAA"}],
                [{"RAA", "CCM"}, {"GGG", "CCC", "TTT", "AAA"}]
            )
        ]

        for test_case in test_cases:
            solution = DegenerateTripletWithAminos.stringified_site_separate_set_cover(test_case[0],e_coli.table.forward_table)
            self.assertEqual(test_case[1], solution)

    def test_create_subsets_for_primers(self):
        test_cases = [
            (
                [["AAA"], ["GGG"]],
                [["AAA", "GGG"]]
            ),
            (
                [["AAA", "GAA"], ["GGG", "GGT"]],
                [['AAA', 'GGG'], ['AAA', 'GGT'], ['GAA', 'GGG'], ['GAA', 'GGT']]
            )
        ]

        for test_case in test_cases:
            result = DegenerateTripletWithAminos.create_subsets_for_primers(test_case[0])

            self.assertEqual(test_case[1], result)

        uneven_test_case = [["AAA", "GGG"], ["CCC"]]

        uneven_result = DegenerateTripletWithAminos.create_subsets_for_primers(uneven_test_case)

        self.assertIn(["AAA", "CCC"], uneven_result)
        self.assertIn(["GGG", "CCC"], uneven_result)

    def test_degenerate_union_in_two_bases(self):
        codon1 = DegenerateTripletWithAminos.parse_from_codon_string("RAT",e_coli.table.forward_table)
        codon2 = DegenerateTripletWithAminos.parse_from_codon_string("RAG",e_coli.table.forward_table)

        degenerate_codon = codon1.union(codon2)

        self.assertEqual("RAK", str(degenerate_codon))

    def test_find_two_similar(self):

        bag = set()
        amino1 = DegenerateTripletWithAminos.parse_from_codon_string("TTT",e_coli.table.forward_table)
        bag.add(amino1)
        amino2 = DegenerateTripletWithAminos.parse_from_codon_string("TTA",e_coli.table.forward_table)
        bag.add(amino2)
        bag.add(DegenerateTripletWithAminos.parse_from_codon_string("CCC",e_coli.table.forward_table))

        res = DegenerateTripletWithAminos.find_two_similar(bag)

        self.assertIsNotNone(res)
        self.assertEqual(2, len(res))
        self.assertIn(amino1, res)
        self.assertIn(amino2, res)
