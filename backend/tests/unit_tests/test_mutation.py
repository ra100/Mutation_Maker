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

from mutation_maker.mutation import parse_codon_mutation, MutationSite


class MutationTest(unittest.TestCase):
    def test_parse_valid_mut(self):
        mutation = parse_codon_mutation("A51F")
        self.assertEqual("A51F",mutation.original_string)
        self.assertEqual("A",mutation.old_amino)
        self.assertEqual("F", mutation.new_amino)
        self.assertEqual(150, mutation.position)

    def test_parse_invalid_orig_amino(self):
        with self.assertRaises(ValueError) as context:
            mutation = parse_codon_mutation("*51F")
        self.assertTrue("Original amino acid is not valid" in str(context.exception))

    def test_parse_invalid_new_amino(self):
        with self.assertRaises(ValueError) as context:
            mutation = parse_codon_mutation("A51*")
        self.assertTrue("Target amino acid is not valid" in str(context.exception))

    def test_parse_invalid_position(self):
        with self.assertRaises(ValueError) as context:
            mutation = parse_codon_mutation("A*F")
        self.assertTrue("Position" in str(context.exception))

        with self.assertRaises(ValueError) as context:
            mutation = parse_codon_mutation("A0F")
        self.assertTrue("Position" in str(context.exception))

        with self.assertRaises(ValueError) as context:
            mutation = parse_codon_mutation("A-12F")
        self.assertTrue("positive number" in str(context.exception))


class MutationSiteTest(unittest.TestCase):

    def test_valid_mutation_site(self):
        mutation1 = parse_codon_mutation("A51F")
        mutation2 = parse_codon_mutation("A51M")
        lst = [mutation1, mutation2]

        mut_site = MutationSite(lst)

        self.assertEqual(150, mut_site.position)
        self.assertEqual("A", mut_site.old_amino)
        self.assertIn("F", mut_site.new_aminos)
        self.assertIn("M", mut_site.new_aminos)

    def test_mutation_site_different_positions(self):
        mutation1 = parse_codon_mutation("A51F")
        mutation2 = parse_codon_mutation("A52M")
        lst = [mutation1, mutation2]

        with self.assertRaises(ValueError) as context:
            mut_site = MutationSite(lst)
        self.assertTrue("must be on same position" in str(context.exception))

    def test_mutation_site_diff_original_aminos(self):
        mutation1 = parse_codon_mutation("A51F")
        mutation2 = parse_codon_mutation("M51M")
        lst = [mutation1, mutation2]

        with self.assertRaises(ValueError) as context:
            mut_site = MutationSite(lst)
        self.assertTrue("must have same amin" in str(context.exception))

    def test_get_mutation_string(self):
        mutation1 = parse_codon_mutation("A51F")
        mutation2 = parse_codon_mutation("A51M")
        lst = [mutation1, mutation2]

        mut_site = MutationSite(lst)

        self.assertEqual("A51A", mut_site.get_mutation_string("A"))
        self.assertEqual("A51F", mut_site.get_mutation_string("F"))
        self.assertEqual("A51M", mut_site.get_mutation_string("M"))