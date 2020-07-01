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

from mutation_maker.ssm_types import SSMSequences, Plasmid
from tests.test_support import generate_SSM_input

fw_primer_short = "AAT"
rv_primer_short = "GGC"
goi_short = "AAA"
plasmid_seq_short = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
full_seq_short = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
offset_short = 6


fw_primer_2 = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
rv_primer_2 = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"


fw_primer = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
rv_primer = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
gene_of_interest = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
plasmid_seq = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
full_seq = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
five_end = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
three_end ="PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"


class SSMSequenceTest(unittest.TestCase):

    def test_ssm_sequence_simple_valid(self):
        """
        Scenario desc: check offset computation and g.o.i. look-up in simple sequence.
        :return:
        """
        sequences=SSMSequences(
            forward_primer=fw_primer_short,
            reverse_primer=rv_primer_short,
            gene_of_interest="AAA",
            plasmid=Plasmid(
                plasmid_sequence=plasmid_seq_short
            ))
        result_full_seq, offsets = sequences.get_full_sequence_with_offset()

        self.assertEqual(result_full_seq, "AATGTCAAACCCTTTGCC")
        self.assertEqual(offsets, (6, 9))

    def test_ssm_sequence_simple_valid_rev(self):
        """
        Scenario desc: check offset computation and g.o.i. look-up in simple sequence.
        This time the forward primer is after reverse primer in sequence.
        :return:
        """
        sequences=SSMSequences(
            forward_primer="GCC",
            reverse_primer="TTT",
            gene_of_interest="GTC",
            plasmid=Plasmid(
                plasmid_sequence="AATGTCAAACCCTTTGCC"
            ))
        result_full_seq, offsets = sequences.get_full_sequence_with_offset()

        self.assertEqual(result_full_seq, "GCCAATGTCAAA")
        self.assertEqual(offsets, (6, 9))

    def test_ssm_sequence_valid_cyclic_seq(self):
        """
        Scenario desc: check offset computation and g.o.i. look-up in cyclic sequence.
        Sequence has same start/end so here we look more at creating the full sequence.
        """
        sequences=SSMSequences(
            forward_primer="AAT",
            reverse_primer="GGC",
            gene_of_interest="CCC",
            plasmid=Plasmid(
                plasmid_sequence="AAA" + plasmid_seq_short + "AAA"
            ))
        result_full_seq, offsets = sequences.get_full_sequence_with_offset()

        self.assertEqual(result_full_seq, "AATGTCAAACCCTTTGCC")
        self.assertEqual(offsets, (9, 12))

    def test_ssm_sequence_complex_valid(self):
        """
        Scenario desc: Checking creation of full sequence and finding the offset for
        long sequence (length=1747)
        """
        sequences=SSMSequences(
            forward_primer=fw_primer,
            reverse_primer=rv_primer,
            gene_of_interest=gene_of_interest,
            plasmid=Plasmid(
                plasmid_sequence=plasmid_seq
            ))
        result_full_seq, offsets = sequences.get_full_sequence_with_offset()

        self.assertEqual(result_full_seq, full_seq)
        self.assertEqual(offsets, (316, 1747))

    def test_ssm_sequence_wrong_fw_primer(self):
        """
        Scenario desc: Forward primer is not found in sequence. We expect error.
        """
        sequences = SSMSequences(
            forward_primer="GGG",
            reverse_primer=rv_primer_short,
            gene_of_interest=goi_short,
            plasmid=Plasmid(
                plasmid_sequence=plasmid_seq_short
            ))
        with self.assertRaises(ValueError) as context:
            sequences.get_full_sequence_with_offset()
        self.assertTrue('Forward primer was not found in plasmid' in str(context.exception))

    def test_ssm_sequence_missing_goi(self):
        """
        Scenario desc: Gene of interest is not found in sequence. We expect error.
        """
        sequences = SSMSequences(
            forward_primer=fw_primer_short,
            reverse_primer=rv_primer_short,
            gene_of_interest="GGG",
            plasmid=Plasmid(
                plasmid_sequence=plasmid_seq_short
            ))
        with self.assertRaises(ValueError) as context:
            sequences.get_full_sequence_with_offset()
        self.assertTrue('Gene of interest was not found in plasmid' in str(context.exception))

    def test_ssm_sequence_goi_outside_primers(self):
        """
        Scenario desc: Gene of interest is not found between forward
        and revers primer. We expect error.
        Plasmid sequence: AAT GTC AAA CCC TTT GCC
        Forward primer: AAT
        Reverse primer: AAA (reverse is TTT)
        Gene of interest: GCC (which is after TTT)
        Sequence specified by primers should be: AAT GTC AAA CCC TTT
        """
        sequences = SSMSequences(
            forward_primer=fw_primer_short,
            reverse_primer="AAA",
            gene_of_interest="GCC",
            plasmid=Plasmid(
                plasmid_sequence=plasmid_seq_short
            ))
        with self.assertRaises(ValueError) as context:
            sequences.get_full_sequence_with_offset()
        self.assertTrue('Gene of interest was not found in plasmid' in str(context.exception))

    def test_ssm_sequence_wrong_rv_primer(self):
        """
        Scenario desc: Complement to reverse primer is not found in sequence. We expect error.
        """
        sequences = SSMSequences(
            forward_primer=fw_primer_short,
            reverse_primer="CCC",
            gene_of_interest=goi_short,
            plasmid=Plasmid(
                plasmid_sequence=plasmid_seq_short
            ))
        with self.assertRaises(ValueError) as context:
            sequences.get_full_sequence_with_offset()
        self.assertTrue('Reverse primer was not found in plasmid' in str(context.exception))

    def test_ssm_sequence_wrong_multiple_goi(self):
        """
        Scenario desc: Gene of interest is found multiple times in the plasmid. We expect error.
        """
        sequences = SSMSequences(
            forward_primer=fw_primer_short,
            reverse_primer=rv_primer_short,
            gene_of_interest=goi_short,
            plasmid=Plasmid(
                plasmid_sequence=plasmid_seq_short+goi_short
            ))
        with self.assertRaises(ValueError) as context:
            sequences.get_full_sequence_with_offset()
        self.assertTrue('Gene of interest position is ambiguous' in str(context.exception))

    def test_ssm_sequence_wrong_multiple_goi(self):
        """
        Scenario desc: Gene of interest is found multiple times in the plasmid. We expect error.
        """
        sequences = SSMSequences(
            forward_primer=fw_primer_short,
            reverse_primer=rv_primer_short,
            gene_of_interest=goi_short,
            plasmid=Plasmid(
                plasmid_sequence=plasmid_seq_short+goi_short
            ))
        with self.assertRaises(ValueError) as context:
            sequences.get_full_sequence_with_offset()
        self.assertTrue('Gene of interest position is ambiguous' in str(context.exception))


class SSMPlasmidTest(unittest.TestCase):
    def test_plasmid_get_three_end(self):
        plasmid = Plasmid(plasmid_sequence=plasmid_seq)
        self.assertEqual(plasmid.get_three_end(gene_of_interest, rv_primer), three_end)

    def test_plasmid_get_five_end(self):
        """
        Scenarion desc: Finding five end sub sequence in plasmid sequence.
        """
        plasmid = Plasmid(plasmid_sequence=plasmid_seq)
        self.assertEqual(plasmid.get_five_end(gene_of_interest, fw_primer), five_end)

    def test_plasmid_check_occurance_not_present(self):
        """
        Scenario desc: The gene of interest is not found in plasmid we report an error.
        :return:
        """
        plasmid = Plasmid(plasmid_sequence="TATAGCTTCTG")
        with self.assertRaises(ValueError) as context:
            plasmid.check_sequence_occurrences("TTGCF", "test")
        self.assertTrue('not found' in str(context.exception))

    def test_plasmid_check_occurance_ambiguos(self):
        """
         Scenario desc: The gene of interest is found multiple times in the plasmid sequence.
         We return an error that goi is ambiguous.
        """
        plasmid = Plasmid(plasmid_sequence="GTATAGCTTCTGTAT")
        with self.assertRaises(ValueError) as context:
            plasmid.check_sequence_occurrences("GTA", "test")
        self.assertTrue('ambiguous' in str(context.exception))

    @staticmethod
    def test_plasmid_check_occurrence_correct():
        plasmid = Plasmid(plasmid_sequence="TATAGCTTCTG")
        plasmid.check_sequence_occurrences("TTC", "test")


class SsmInputTest(unittest.TestCase):
    def test_parse_mutations(self):
        goi_position = 316
        ssm_in = generate_SSM_input()
        parsed_mutations = ssm_in.parse_mutations(goi_position)
        self.assertTrue(len(parsed_mutations) == len(ssm_in.mutations))
        for specified, parsed in zip(
                        sorted(ssm_in.mutations),
                        sorted(parsed_mutations, key=lambda k: k.original_string)):
            self.assertEqual(specified, parsed.original_string)
            expected = (int(specified[1:-1]) - 1) * 3 + goi_position
            self.assertEqual(expected, parsed.position)
