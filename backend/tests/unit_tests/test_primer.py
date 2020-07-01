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

from mutation_maker.mutation import ConcreteTripletMutation
from mutation_maker.primer import Primer


class SSMSequenceTest(unittest.TestCase):

    def test_create_valid_primers(self):
        """
        Scenario desc : We provide parent sequence, direction, start of the primer
        and length of the primer. We expect valid primer.
        """
        Primer("ACGT", Primer.FORWARD, 0, 1)
        Primer("ACGT", Primer.FORWARD, 0, 4)
        Primer("ACGT", Primer.FORWARD, 1, 2)
        Primer("ACGT", Primer.REVERSE, 3, 1)
        Primer("ACGT", Primer.REVERSE, 3, 4)
        Primer("ACGT", Primer.REVERSE, 2, 2)
        self.assertTrue(True)

    def test_create_primer_without_parent_seq(self):
        """
        Scenario desc: We initialize Primer without
        parent sequence. We should get value error.
        """
        with self.assertRaises(ValueError) as context:
            Primer(None, Primer.FORWARD, 0, 1)
        self.assertTrue('Parent sequence must be defined to create primer' in str(context.exception))
        #TODO empty primer string is acceptable?
        # with self.assertRaises(ValueError) as context:
        #     Primer("", Primer.FORWARD, 0, 1)
        # self.assertTrue('Parent sequence must be defined to create primer' in str(context.exception))

    def test_create_primer_with_invalid_direction(self):
        """
        Scenario desc: We initialize Primer with invalid
        direction. We should get value error.
        """
        with self.assertRaises(ValueError) as context:
            Primer("ACGT", "", 0, 1)
        self.assertTrue('Direction must be either forward or reverse' in str(context.exception))

    def test_create_primer_without_direction(self):
        """
        Scenario desc: We initialize Primer without
        direction. We should get value error.
        """
        with self.assertRaises(ValueError) as context:
            Primer("ACGT", None, 0, 1)
        self.assertTrue('Primer direction must be specified' in str(context.exception))

    def test_create_primer_without_start(self):
        """
        Scenario desc: We initialize Primer without
        start. We should get value error.
        """
        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.REVERSE, None, 1)
        self.assertTrue('Primer start must be specified' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.FORWARD, None, 1)
        self.assertTrue('Primer start must be specified' in str(context.exception))

    def test_create_primer_with_invalid_start(self):
        """
        Scenario desc: We initialize Primer with invalid
        start values. We should get value error.
        """
        """Negative value"""
        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.REVERSE, -1, 1)
        self.assertTrue('Primer start is not in sequence' in str(context.exception))
        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.FORWARD, -1, 1)
        self.assertTrue('Primer start is not in sequence' in str(context.exception))

        """Start is bigger than length"""
        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.REVERSE, 4, 1)
        self.assertTrue('Primer start is not in sequence' in str(context.exception))
        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.FORWARD, 4, 1)
        self.assertTrue('Primer start is not in sequence' in str(context.exception))

    def test_create_primer_without_length(self):
        """
        Scenario desc: We initialize Primer without
        length. We should get value error.
        """
        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.REVERSE, 1, None)
        self.assertTrue('Primer length must be specified' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.FORWARD, 1, None)
        self.assertTrue('Primer length must be specified' in str(context.exception))

    def test_create_fw_primer_with_invalid_length_start(self):
        """
        Scenario desc: We initialize forward primer with invalid
        combination of length and start. We should get value error.
        """
        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.FORWARD, 3, 2)
        self.assertTrue('Primer end is not in sequence' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.FORWARD, 3, 3)
        self.assertTrue('Primer end is not in sequence' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.FORWARD, 2, 3)
        self.assertTrue('Primer end is not in sequence' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.FORWARD, 1, 4)
        self.assertTrue('Primer end is not in sequence' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.FORWARD, 0, 13)
        self.assertTrue('Primer end is not in sequence' in str(context.exception))

    def test_create_rv_primer_with_invalid_length_start(self):
        """
        Scenario desc: We initialize reverse primer with invalid
        combination of length and start. We should get value error.
        """
        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.REVERSE, 0, 2)
        self.assertTrue('Primer end is not in sequence' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.REVERSE, 0, 3)
        self.assertTrue('Primer end is not in sequence' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.REVERSE, 1, 3)
        self.assertTrue('Primer end is not in sequence' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.REVERSE, 1, 4)
        self.assertTrue('Primer end is not in sequence' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.REVERSE, 4, 13)
        self.assertTrue('Primer start is not in sequence' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.REVERSE, 3, 5)
        self.assertTrue('Primer end is not in sequence' in str(context.exception))

    def test_create_primer_with_zero_length(self):
        """
        Scenario desc: We initialize primer with 0 length.
        We should get value error.
        """
        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.REVERSE, 0, 0)
        self.assertTrue('Length must be greater than zero' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            Primer("ACGT", Primer.FORWARD, 2, 0)
        self.assertTrue('Length must be greater than zero' in str(context.exception))

    def test_primer_normal_order_start(self):
        """
        Scenario desc : We provide parent sequence, direction, start of the primer
        and length of the primer. We expect valid primer with correct normal order start.
        """
        self.assertEqual(0, Primer("ACGT", Primer.FORWARD, 0, 1).normal_start)
        self.assertEqual(0, Primer("ACGT", Primer.FORWARD, 0, 4).normal_start)
        self.assertEqual(1, Primer("ACGT", Primer.FORWARD, 1, 2).normal_start)
        self.assertEqual(3, Primer("ACGT", Primer.FORWARD, 3, 1).normal_start)

        self.assertEqual(3, Primer("ACGT", Primer.REVERSE, 3, 1).normal_start)
        self.assertEqual(0, Primer("ACGT", Primer.REVERSE, 3, 4).normal_start)
        self.assertEqual(1, Primer("ACGT", Primer.REVERSE, 2, 2).normal_start)

    def test_primer_normal_order_end(self):
        """
        Scenario desc : We provide parent sequence, direction, start of the primer
        and length of the primer. We expect valid primer with correct normal order end.
        """
        self.assertEqual(1, Primer("ACGT", Primer.FORWARD, 0, 1).normal_end)
        self.assertEqual(4, Primer("ACGT", Primer.FORWARD, 0, 4).normal_end)
        self.assertEqual(3, Primer("ACGT", Primer.FORWARD, 1, 2).normal_end)
        self.assertEqual(4, Primer("ACGT", Primer.FORWARD, 3, 1).normal_end)

        self.assertEqual(4, Primer("ACGT", Primer.REVERSE, 3, 1).normal_end)
        self.assertEqual(4, Primer("ACGT", Primer.REVERSE, 3, 4).normal_end)
        self.assertEqual(3, Primer("ACGT", Primer.REVERSE, 2, 2).normal_end)

    def test_primer_normal_order_sequence(self):
        """
        Scenario desc : We provide parent sequence, direction, start of the primer
        and length of the primer. We expect valid primer with correct normal order sequence.
        """
        self.assertEqual("A", Primer("ACGT", Primer.FORWARD, 0, 1).normal_order_sequence)
        self.assertEqual("ACGT", Primer("ACGT", Primer.FORWARD, 0, 4).normal_order_sequence)
        self.assertEqual("CG", Primer("ACGT", Primer.FORWARD, 1, 2).normal_order_sequence)
        self.assertEqual("T", Primer("ACGT", Primer.FORWARD, 3, 1).normal_order_sequence)
        #TODO sure it should not be reversed?
        self.assertEqual("T", Primer("ACGT", Primer.REVERSE, 3, 1).normal_order_sequence)
        self.assertEqual("ACGT", Primer("ACGT", Primer.REVERSE, 3, 4).normal_order_sequence)
        self.assertEqual("CG", Primer("ACGT", Primer.REVERSE, 2, 2).normal_order_sequence)


    def test_primer_compute_gc_content(self):
        """
        Scenario desc : Test gc content computation
        """
        self.assertEqual(100.0, Primer("GCGCGCGCG", Primer.FORWARD, 0, 9).get_gc_content())
        self.assertEqual(0, Primer("ATATATATA", Primer.FORWARD, 0, 9).get_gc_content())
        self.assertEqual(50.0, Primer("CGCGAAAA", Primer.REVERSE, 7, 8).get_gc_content())
        self.assertEqual(75.0, Primer("CCCCCCAA", Primer.REVERSE, 7, 8).get_gc_content())

    def test_primer_get_mutated_seq(self):
        """
        Scenario desc : Test mutation of primer.
        """
        self.assertEqual("GGTAAAAAA", Primer("AAAAAAAAA", Primer.FORWARD, 0, 9).get_mutated_sequence(0,"GGT"))
        self.assertEqual("AAGGTAAAA", Primer("AAAAAAAAA", Primer.FORWARD, 0, 9).get_mutated_sequence(2,"GGT"))
        self.assertEqual("AAAAGTTAA", Primer("AAAAAAAAA", Primer.REVERSE, 8, 9).get_mutated_sequence(4,"GTT"))
        self.assertEqual("AAAAAAGTT", Primer("AAAAAAAAA", Primer.REVERSE, 8, 9).get_mutated_sequence(6,"GTT"))

    def test_primer_get_gc_clamp(self):
        """
        Scenario desc : Test gc clamp computation in primer.
        """
        self.assertEqual(9, Primer("GCGCGCGCG", Primer.FORWARD, 0, 9).get_gc_clamp())
        self.assertEqual(9, Primer("GCGCGCGCG", Primer.REVERSE, 8, 9).get_gc_clamp())
        self.assertEqual(0, Primer("ATATATATA", Primer.FORWARD, 0, 9).get_gc_clamp())
        self.assertEqual(0, Primer("ATATATATA", Primer.REVERSE, 8, 9).get_gc_clamp())
        self.assertEqual(1, Primer("ATAC", Primer.FORWARD, 0, 4).get_gc_clamp())
        self.assertEqual(1, Primer("GTAC", Primer.FORWARD, 0, 4).get_gc_clamp())
        self.assertEqual(1, Primer("CTAA", Primer.REVERSE, 3, 4).get_gc_clamp())
        self.assertEqual(1, Primer("GTAC", Primer.REVERSE, 3, 4).get_gc_clamp())
        self.assertEqual(2, Primer("CCACCCAA", Primer.REVERSE, 7, 8).get_gc_clamp())
        self.assertEqual(2, Primer("CGCGAACC", Primer.FORWARD, 0, 8).get_gc_clamp())

    def test_primer_get_3_end_seq(self):
        """
        Scenario desc : Test getting 3 end sequence.
        """
        self.assertEqual("CGCGCG", Primer("GCGCGCGCG", Primer.FORWARD, 0, 9).get_three_end_sequence(
            ConcreteTripletMutation(0, "")))
        self.assertEqual("ATAT", Primer("ATATATATA", Primer.REVERSE, 8, 9).get_three_end_sequence(
            ConcreteTripletMutation(4, "")))
        self.assertEqual("AAA", Primer("CGCGAAAA", Primer.FORWARD, 0, 8).get_three_end_sequence(
            ConcreteTripletMutation(2, "")))
        self.assertEqual("CCCCCCA", Primer("CCCCCCAA", Primer.REVERSE, 7, 8).get_three_end_sequence(
            ConcreteTripletMutation(7, "")))

    def test_primer_compute_3_end_seq_size(self):
        """
        Scenario desc : Test computation of three end size from mutation.
        """
        self.assertEqual(1, Primer("ACGTACGTA", Primer.FORWARD, 0, 5).get_three_end_size_from_mutation(
            ConcreteTripletMutation(1, "")))
        self.assertEqual(2, Primer("ACGTACGTA", Primer.FORWARD, 0, 6).get_three_end_size_from_mutation(
            ConcreteTripletMutation(1, "")))
        self.assertEqual(2, Primer("ACGTACGTA", Primer.FORWARD, 1, 6).get_three_end_size_from_mutation(
            ConcreteTripletMutation(2, "")))

        self.assertEqual(1, Primer("ACGTACGTA", Primer.REVERSE, 7, 5).get_three_end_size_from_mutation(
            ConcreteTripletMutation(4, "")))
        self.assertEqual(2, Primer("ACGTACGTA", Primer.REVERSE, 7, 6).get_three_end_size_from_mutation(
            ConcreteTripletMutation(4, "")))
        self.assertEqual(2, Primer("ACGTACGTA", Primer.REVERSE, 6, 6).get_three_end_size_from_mutation(
            ConcreteTripletMutation(3, "")))
        self.assertEqual(4, Primer("AAAAAAAAA", Primer.REVERSE, 8, 9).get_three_end_size_from_mutation(
            ConcreteTripletMutation(4, "")))

    def test_primer_compute_5_end_seq_size(self):
        """
        Scenario desc : Test computation of five end size from mutation.
        """
        self.assertEqual(1, Primer("ACGTACGTA", Primer.FORWARD, 0, 5).get_five_end_size_from_mutation(
            ConcreteTripletMutation(1, "")))
        self.assertEqual(1, Primer("ACGTACGTA", Primer.FORWARD, 0, 6).get_five_end_size_from_mutation(
            ConcreteTripletMutation(1, "")))
        self.assertEqual(1, Primer("ACGTACGTA", Primer.FORWARD, 1, 6).get_five_end_size_from_mutation(
            ConcreteTripletMutation(2, "")))
        self.assertEqual(2, Primer("ACGTACGTA", Primer.FORWARD, 1, 7).get_five_end_size_from_mutation(
            ConcreteTripletMutation(3, "")))

        self.assertEqual(1, Primer("ACGTACGTA", Primer.REVERSE, 7, 5).get_five_end_size_from_mutation(
            ConcreteTripletMutation(4, "")))
        self.assertEqual(1, Primer("ACGTACGTA", Primer.REVERSE, 7, 6).get_five_end_size_from_mutation(
            ConcreteTripletMutation(4, "")))
        self.assertEqual(1, Primer("ACGTACGTA", Primer.REVERSE, 6, 6).get_five_end_size_from_mutation(
            ConcreteTripletMutation(3, "")))
        self.assertEqual(2, Primer("AAAAAAAAA", Primer.REVERSE, 7, 6).get_five_end_size_from_mutation(
            ConcreteTripletMutation(3, "")))

#TODO get overlap tests