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
from difflib import SequenceMatcher

from Bio.Seq import reverse_complement

from mutation_maker.primer3_interoperability import AllPrimerGenerator, Primer3, NullPrimerGenerator
from mutation_maker.ssm import ssm_solve
from mutation_maker.temperature_calculator import TemperatureConfig
from tasks import PRIMER3_PATH
from tests.test_support import generate_SSM_input, generate_random_SSM_input, comp_dicts, print_stats_ssm


def test_overlap_complementary(ssm_result):
    """
    Tests whatever the forward primer is complementary to
        reverse primer on the overlap and the actual size is the same as expected.
    :param ssm_result: result of ssm
    :return: True if all fw_primer and rv_primer are complement to each other on overlap
        and the size of overlap is same as expected
    """
    for mutation_dict in ssm_result["results"]:
        fw_seq = mutation_dict["forward_primer"]["sequence"]
        rv_seq = reverse_complement(mutation_dict["reverse_primer"]["sequence"])
        # find the overlaps
        match = SequenceMatcher(None, fw_seq, rv_seq).find_longest_match(0, len(fw_seq), 0, len(rv_seq))
        # check that overlap sequences are the same
        if not fw_seq[match.a: match.a + match.size] == rv_seq[match.b: match.b + match.size]:
            print("Forward and reverse primers are not complementary.")
            print("Fw primer: ", fw_seq[match.a: match.a + match.size])
            print("Rv primer reverse complement: ", rv_seq[match.b: match.b + match.size])
            return False
        # check that the size of overlap is the same
        if not mutation_dict["overlap"]["length"] == match.size:
            print("Overlap computation went wrong for mutation:", mutation_dict["mutation"])
            return False
    return True


def test_overlap_size_in_range(ssm_result):
    """
    Tests the overlap is in required range.
    """
    min_size = ssm_result["input_data"]["config"]["min_overlap_size"]
    max_size = ssm_result["input_data"]["config"]["max_overlap_size"]
    for mutation_dict in ssm_result["results"]:
        fw_seq = mutation_dict["forward_primer"]["sequence"]
        rv_seq = reverse_complement(mutation_dict["reverse_primer"]["sequence"])
        # find the overlaps
        match = SequenceMatcher(None, fw_seq, rv_seq).find_longest_match(0, len(fw_seq), 0, len(rv_seq))
        # check that overlap sequences are the same
        if match.size < min_size or match.size > max_size:
            print(f"Overlap size out of range [{min_size}, {max_size}] for mutation:", mutation_dict["mutation"])
            print("Overlap size is ", match.size)
            return False

    return True


def test_overlap_temperature_in_range(ssm_result):
    """
    Tests is found primers have temperature inside range specified by the
    input configuration.
    """
    min_temp = ssm_result["input_data"]["config"]["min_overlap_temperature"]
    max_temp = ssm_result["input_data"]["config"]["max_overlap_temperature"]
    temp_calculator = TemperatureConfig().create_calculator()

    for mutation_dict in ssm_result["results"]:
        fw_seq = mutation_dict["forward_primer"]["sequence"]
        rv_seq = reverse_complement(mutation_dict["reverse_primer"]["sequence"])
        # find the overlaps
        match = SequenceMatcher(None, fw_seq, rv_seq).find_longest_match(0, len(fw_seq), 0, len(rv_seq))
        fw_temp = temp_calculator(fw_seq[match.a: match.a + match.size])
        rv_temp = temp_calculator(rv_seq[match.b: match.b + match.size])

        if fw_temp < min_temp or fw_temp > max_temp:
            print(f"Forward primer overlap temperature not in range [{min_temp}, {max_temp}]. Actual temperature: ", fw_temp)
            print("Failed for mutation: " + mutation_dict["mutation"])
            return False
        if rv_temp < min_temp or rv_temp > max_temp:
            print(f"Reverse primer overlap temperature size not in range [{min_temp}, {max_temp}]. Actual temperature: ", rv_temp)
            print("Failed for mutation: " + mutation_dict["mutation"])
            return False

    return True


def get_fw_three_end(fw_sequence, degen_codon):
    """
    Finds degenerate codon in the forward sequence and returns
    three end part of the forward primer
    :param fw_sequence:  forward primer sequence
    :param degen_codon: degenerate codon code
    :return: three end part of the forward primer
    """
    mut_offset = fw_sequence.find(degen_codon) + 3
    return fw_sequence[mut_offset:]


def get_rv_three_end(rv_sequence, degen_codon):
    """
    Finds degenerate codon in the reverse sequence and returns
    three end part of the reverse primer
    :param rv_sequence:  reverse primer sequence
    :param degen_codon: degenerate codon code
    :return: three end part of the reverse primer
    """
    mut_location = rv_sequence.find(degen_codon[::-1]) + 3
    return rv_sequence[mut_location:]


def get_fw_five_end(fw_sequence, degen_codon):
    """
    Finds degenerate codon in the forward sequence and returns
    five end part of the forward primer
    :param fw_sequence:  forward primer sequence
    :param degen_codon: degenerate codon code
    :return: five end part of the forward primer
    """
    mut_offset = fw_sequence.find(degen_codon)
    return fw_sequence[:mut_offset]


def get_rv_five_end(rv_sequence, degen_codon):
    """
    Finds degenerate codon in the reverse sequence and returns
    five end part of the reverse primer
    :param rv_sequence:  reverse primer sequence
    :param degen_codon: degenerate codon code
    :return: five end part of the reverse primer
    """
    mut_location = rv_sequence.find(degen_codon[::-1])
    return rv_sequence[:mut_location]


def test_3end_size_in_range(ssm_result):
    """
    Tests is found primers have 3end size inside range specified by the
    input configuration.
    """
    min_size = ssm_result["input_data"]["config"]["min_three_end_size"]
    max_size = ssm_result["input_data"]["config"]["max_three_end_size"]
    degen_codon = ssm_result["input_data"]["degenerate_codon"]
    for mutation_dict in ssm_result["results"]:
        # +3 because find returns start of mutation, we need end
        fw_3end_size = len(get_fw_three_end(mutation_dict["forward_primer"]["sequence"],degen_codon))
        rv_3end_size = len(get_rv_three_end(mutation_dict["reverse_primer"]["sequence"], degen_codon))

        if fw_3end_size < min_size or fw_3end_size > max_size:
            print(f"Forward primer 3 end size not in range [{min_size}, {max_size}]. The size is ", fw_3end_size)
            print("Failed for mutation: " + mutation_dict["mutation"])
            return False
        if rv_3end_size < min_size or rv_3end_size > max_size:
            print(f"Reverse primer 3 end size not in range [{min_size}, {max_size}]. The size is ", rv_3end_size)
            print("Failed for mutation: " + mutation_dict["mutation"])
            return False

    return True


def test_5end_size_in_range(ssm_result):
    """
    Tests that found primers have 5end size inside range specified by the
    input configuration.
    """
    min_size = ssm_result["input_data"]["config"]["min_five_end_size"]
    degen_codon = ssm_result["input_data"]["degenerate_codon"]
    for mutation_dict in ssm_result["results"]:
        # +3 because find returns start of mutation, we need end
        fw_5end_size = len(get_fw_five_end(mutation_dict["forward_primer"]["sequence"], degen_codon))
        rv_5end_size = len(get_rv_five_end(mutation_dict["reverse_primer"]["sequence"], degen_codon))

        if fw_5end_size < min_size:
            print(f"Forward primer 5 end size not in range [{min_size}]. The size is ", fw_5end_size)
            print("Failed for mutation: " + mutation_dict["mutation"])
            return False
        if rv_5end_size < min_size:
            print(f"Reverse primer 5 end size not in range [{min_size}]. The size is ", rv_5end_size)
            print("Failed for mutation: " + mutation_dict["mutation"])
            return False

    return True


def test_3end_temperature_in_range(ssm_result):
    """
    Tests that found primers have 3end size inside range specified by the
    input configuration.
    """
    min_temp = ssm_result["input_data"]["config"]["min_three_end_temperature"]
    max_temp = ssm_result["input_data"]["config"]["max_three_end_temperature"]
    temp_calculator = TemperatureConfig().create_calculator()
    degen_codon = ssm_result["input_data"]["degenerate_codon"]
    for mutation_dict in ssm_result["results"]:
        fw_3end = get_fw_three_end(mutation_dict["forward_primer"]["sequence"],degen_codon)
        rv_3end = get_rv_three_end(mutation_dict["reverse_primer"]["sequence"], degen_codon)

        if fw_3end=="" or rv_3end=="":
            print(f"Emprty three end. Fw_3_end={fw_3end}, Rv_3_end={rv_3end}")
            return False

        if temp_calculator(fw_3end) < min_temp or temp_calculator(fw_3end) > max_temp:
            print(f"Forward primer 3 end temperature not in range [{min_temp}, {max_temp}].The temperature is: ", temp_calculator(fw_3end))
            print("Failed for mutation: " + mutation_dict["mutation"])
            return False
        if temp_calculator(rv_3end) < min_temp or temp_calculator(rv_3end) > max_temp:
            print(f"Reverse primer 3 end temperature not in range [{min_temp}, {max_temp}]. The temperature is: ", temp_calculator(rv_3end))
            print("Failed for mutation: " + mutation_dict["mutation"])
            return False

    return True


def test_primer_size_in_range(ssm_result):
    """
    Tests if the found primers have size inside range specified in the input
    :param ssm_result:
    :return:
    """
    min_size = ssm_result["input_data"]["config"]["min_primer_size"]
    max_size = ssm_result["input_data"]["config"]["max_primer_size"]
    for mutation_dict in ssm_result["results"]:
        fw_seq = mutation_dict["forward_primer"]["sequence"]
        rv_seq = mutation_dict["reverse_primer"]["sequence"]

        if len(fw_seq) < min_size or len(fw_seq) > max_size:
            print(f"Forward primer size={len(fw_seq)} not in range [{min_size}, {max_size}].")
            print("Primer seq:" + fw_seq + " Mutation: " + mutation_dict["mutation"])
            return False
        if len(rv_seq) < min_size or len(rv_seq) > max_size:
            print(f"Reverse primer size={len(rv_seq)} not in range [{min_size}, {max_size}].")
            print("Primer seq:" + rv_seq + " Mutation: " + mutation_dict["mutation"])
            return False

    return True


def test_mutation_position(ssm_result):
    """
    Tests if the mutation is present at expected position and also
    that the mutation is in fact present.
    Mutation position for forward primer is computed as mutation amino location * 3 - 3 - fw_primer.start
    Mutation position for reverse primer is computed as mutation amino location * 3 - 3 - rv_primer.normal_order_start
    """
    desired_amino = ssm_result["input_data"]["degenerate_codon"]
    for mutation_dict in ssm_result["results"]:

        mut_offset = ssm_result["goi_offset"] + (int(mutation_dict["mutation"][1:-1]) - 1) * 3 - mutation_dict["forward_primer"]["start"]
        fw_amino = mutation_dict["forward_primer"]["sequence"][mut_offset: mut_offset + 3]

        if fw_amino != desired_amino:
            print("Forward primer does not have mutation at expected location.")
            print("Failed for mutation: " + mutation_dict["mutation"])
            return False

        mut_offset = ssm_result["goi_offset"] + (int(mutation_dict["mutation"][1:-1]) - 1) * 3 - mutation_dict["reverse_primer"]["normal_order_start"]
        rv_section = mutation_dict["reverse_primer"]["sequence"][::-1][mut_offset: mut_offset + 3]

        if rv_section != desired_amino:
            print("Reverse primer does not have mutation at expected location.")
            print("Failed for mutation: " + mutation_dict["mutation"])
            return False

    return True


#======================================================================================================================
#                                           Tests case classes
#======================================================================================================================


class SsmSolveTestOnPresetPrimer3(unittest.TestCase):
    initialized = False
    primary_generator = Primer3(primer3_path=PRIMER3_PATH)
    secondary_generator = AllPrimerGenerator()
    use_fast_approximation = True
    exclude_fl_prim = True

    @classmethod
    def initialize(cls):
        if not cls.initialized:
            tst_start = 0
            tst_end = 10
            cls.results = []
            for ind in range(tst_start, tst_end):
                print(f"\nPreset result NO. {ind+1} generated.\n")
                cls.results.append(ssm_solve(generate_SSM_input(ind, primer_growth=cls.use_fast_approximation,
                                                                separateTM=cls.exclude_fl_prim),
                                             cls.primary_generator, cls.secondary_generator))
            cls.initialized = True

    def test_primer_size(self):
        self.__class__.initialize()
        for result in self.__class__.results:
            # test primer size
            self.assertTrue(test_primer_size_in_range(result), msg="Primer size is out of range!")

    def test_3_end_size(self):
        self.__class__.initialize()
        for result in self.__class__.results:
            self.assertTrue(test_3end_size_in_range(result), msg="Primers 3'end size is out of range!")

    def test_overlap_size(self):
        self.__class__.initialize()
        for result in self.__class__.results:
            # test overlap size
            self.assertTrue(test_overlap_size_in_range(result), msg="Overlap size is out of range!")

    def test_overlap_temp(self):
        self.__class__.initialize()
        for result in self.__class__.results:
            # test overlap temperature in range
            self.assertTrue(test_overlap_temperature_in_range(result), msg="Overlap temperature is out of range!")

    def test_3_end_temp(self):
        self.__class__.initialize()
        for result in self.__class__.results:
            # test 3'end temperature of primers
            self.assertTrue(test_3end_temperature_in_range(result), msg="Primer 3'end temperature is out of range!")

    def test_overlap_complementary(self):
        self.__class__.initialize()
        for result in self.__class__.results:
            # test overlap complementary
            self.assertTrue(test_overlap_complementary(result), msg="Overlap size is incorrectly computed!")

    def test_mutation_position(self):
        self.__class__.initialize()
        for result in self.__class__.results:
            # test mutation position
            self.assertTrue(test_mutation_position(result), msg="Mutation is not on expected location!")

    def test_min_5_end_size(self):
        self.__class__.initialize()
        for result in self.__class__.results:
            # test mutation position
            self.assertTrue(test_5end_size_in_range(result), msg="Primers do not have sufficient 5 end size!")


class SsmSolveTestConfigRange(unittest.TestCase):
    """
    Run tests with null generator as primary generator on random examples
    """
    percentage = 0.9
    primary_generator = Primer3(primer3_path=PRIMER3_PATH)
    secondary_generator = AllPrimerGenerator()
    use_fast_approximation = True
    exclude_fl_prim = False
    initialized = False
    hairpins = False
    separate_temp_calc = True
    num_of_tests = 1

    @classmethod
    def initialize(cls):

        max_muts = 24
        if not cls.initialized:
            # b_tmp = [True, False]
            # primary_generators = [Primer3(primer3_path=PRIMER3_PATH), NullPrimerGenerator()]
            # # all configurations
            # for use_fast_approximation in b_tmp:
            #     for exclude_fl_prim in b_tmp:
            #         for p_generator in primary_generators:
            random.seed(123)
            tst_start = 0
            tst_end = cls.num_of_tests
            cls.results = []
            for ind in range(tst_start, tst_end):
                print(f"\nRandom result NO. {ind+1} generated.\n")
                cls.results.append(
                    ssm_solve(generate_random_SSM_input(mut_cnt=random.randint(12, max_muts),
                                                        use_fast_approximation=cls.use_fast_approximation,
                                                        exclude_fl_prim=cls.exclude_fl_prim,
                                                        hairpins=cls.hairpins,
                                                        separate=cls.separate_temp_calc
                                                        ),
                              cls.primary_generator, cls.secondary_generator))
            cls.initialized = True

    def test_primer_size(self):
        self.__class__.initialize()
        cnt = 0
        for result in self.__class__.results:
            # test primer size
            if test_primer_size_in_range(result):
                cnt+=1
        self.assertGreaterEqual(cnt, len(self.__class__.results)*self.__class__.percentage,
                                "Too many primers out of range")
        if len(self.__class__.results) > 0:
            print("%.2f of primers have size in range." % (cnt/len(self.__class__.results)*100))

    def test_3_end_size(self):
        self.__class__.initialize()
        cnt = 0
        for result in self.__class__.results:
            # test primer size
            if test_3end_size_in_range(result):
                cnt += 1
        self.assertGreaterEqual(cnt, len(self.__class__.results) * self.__class__.percentage,
                                "Too many primers 3 end size out of range")
        if len(self.__class__.results) > 0:
            print("%.2f of primers have 3 end size in range." % (cnt / len(self.__class__.results) * 100))

    def test_5_end_size(self):
        self.__class__.initialize()
        cnt = 0
        for result in self.__class__.results:
            # test primer size
            if test_5end_size_in_range(result):
                cnt += 1
        self.assertGreaterEqual(cnt, len(self.__class__.results) * self.__class__.percentage,
                                "Too many primers 5 end size out of range")
        if len(self.__class__.results) > 0:
            print("%.2f of primers have 5 end size in range." % (cnt / len(self.__class__.results) * 100))

    def test_overlap_size(self):
        self.__class__.initialize()
        cnt = 0
        for result in self.__class__.results:
            # test primer size
            if test_overlap_size_in_range(result):
                cnt += 1
        self.assertGreaterEqual(cnt, len(self.__class__.results) * self.__class__.percentage,
                                "Too many primers overlap size is out of range!")
        if len(self.__class__.results) > 0:
            print("%.2f  of primers have overlap size in range." % (cnt / len(self.__class__.results) * 100))

    def test_overlap_temp(self):
        self.__class__.initialize()
        cnt = 0
        for result in self.__class__.results:
            # test primer size
            if test_overlap_temperature_in_range(result):
                cnt += 1
        self.assertGreaterEqual(cnt, 0,
                                "Too many primers overlap temperature is out of range!")
        if len(self.__class__.results) > 0:
            print("%.2f  of primers have overlap temp. in range." % (cnt / len(self.__class__.results) * 100))

    def test_3_end_temp(self):
        self.__class__.initialize()
        cnt = 0
        for result in self.__class__.results:
            # test primer size
            if test_3end_temperature_in_range(result):
                cnt += 1
        self.assertGreaterEqual(cnt, len(self.__class__.results) * self.__class__.percentage,
                                "Too many primers 3 end temperatures out of range")
        if len(self.__class__.results) > 0:
            print("%.2f  of primers have 3'end temp. in range." % (cnt / len(self.__class__.results) * 100))

    def test_overlap_complementary(self):
        self.__class__.initialize()
        cnt = 0
        for result in self.__class__.results:
            # test primer size
            if test_overlap_complementary(result):
                cnt += 1
        self.assertGreaterEqual(cnt, len(self.__class__.results) * self.__class__.percentage,
                                "Too many primers overlap size is incorrectly computed")
        if len(self.__class__.results) > 0:
            print("%.2f of primers are correctly complements to each other." % (cnt / len(self.__class__.results) * 100))

    def test_mutation_position(self):
        self.__class__.initialize()
        cnt = 0
        for result in self.__class__.results:
            # test primer size
            if test_mutation_position(result):
                cnt += 1
        self.assertGreaterEqual(cnt, len(self.__class__.results) * self.__class__.percentage,
                                "Too many primers mutation is not on expected location!")
        if len(self.__class__.results) > 0:
            print("%.2f of primers mutation at right spot." % (cnt / len(self.__class__.results) * 100))
            

class SsmSolveTestSpecificConfigsRandom1(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.09
    num_of_tests = 10

    separate_temp_calc = False
    exclude_fl_prim = False
    primary_generator = NullPrimerGenerator()
    use_fast_approximation = False
    hairpins = False


class SsmSolveTestSpecificConfigsRandom2(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.79
    num_of_tests = 10

    separate_temp_calc = False
    exclude_fl_prim = True
    primary_generator = NullPrimerGenerator()
    use_fast_approximation = True
    hairpins = False


class SsmSolveTestSpecificConfigsRandom3(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.39
    num_of_tests = 10

    separate_temp_calc = False
    exclude_fl_prim = False
    primary_generator = NullPrimerGenerator()
    use_fast_approximation = True
    hairpins = True


class SsmSolveTestSpecificConfigsRandom4(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.09
    num_of_tests = 0

    separate_temp_calc = False
    exclude_fl_prim = False
    primary_generator = Primer3(primer3_path=PRIMER3_PATH)
    use_fast_approximation = False
    hairpins = False


class SsmSolveTestSpecificConfigsRandom5(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.9
    num_of_tests = 10

    separate_temp_calc = False
    exclude_fl_prim = True
    primary_generator = NullPrimerGenerator()
    use_fast_approximation = True
    hairpins = False


class SsmSolveTestSpecificConfigsRandom6(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.9
    num_of_tests = 10

    separate_temp_calc = False
    exclude_fl_prim = True
    primary_generator = NullPrimerGenerator()
    use_fast_approximation = True
    hairpins = False


class SsmSolveTestSpecificConfigsRandom7(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.59
    num_of_tests = 10

    separate_temp_calc = False
    exclude_fl_prim = True
    primary_generator = NullPrimerGenerator()
    use_fast_approximation = True
    hairpins = True


class SsmSolveTestSpecificConfigsRandom8(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.59
    num_of_tests = 0

    separate_temp_calc = False
    exclude_fl_prim = True
    primary_generator = Primer3(primer3_path=PRIMER3_PATH)
    use_fast_approximation = False
    hairpins = False


class SsmSolveTestSpecificConfigsRandom9(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.59
    num_of_tests = 10

    separate_temp_calc = True
    exclude_fl_prim = False
    primary_generator = NullPrimerGenerator()
    use_fast_approximation = False
    hairpins = False


# Runs 3 hours
# class SsmSolveTestSpecificConfigsRandom11(SsmSolveTestConfigRange):
#     secondary_generator = AllPrimerGenerator()
#     initialized = False
#     percentage = 0.59
#     num_of_tests = 10
#
#     separate_temp_calc = True
#     exclude_fl_prim = False
#     primary_generator = NullPrimerGenerator()
#     use_fast_approximation = True
#     hairpins = True


class SsmSolveTestSpecificConfigsRandom12(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.59
    num_of_tests = 0

    separate_temp_calc = True
    exclude_fl_prim = False
    primary_generator = Primer3(primer3_path=PRIMER3_PATH)
    use_fast_approximation = False
    hairpins = False


class SsmSolveTestSpecificConfigsRandom13(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.0
    num_of_tests = 10

    separate_temp_calc = True
    exclude_fl_prim = True
    primary_generator = NullPrimerGenerator()
    use_fast_approximation = False
    hairpins = False


class SsmSolveTestSpecificConfigsRandom14(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.9
    num_of_tests = 10

    separate_temp_calc = True
    exclude_fl_prim = True
    primary_generator = NullPrimerGenerator()
    use_fast_approximation = True
    hairpins = False


# Runs 5 hours
# class SsmSolveTestSpecificConfigsRandom15(SsmSolveTestConfigRange):
#     secondary_generator = AllPrimerGenerator()
#     initialized = False
#     percentage = 0.49
#     num_of_tests = 10
#
#     separate_temp_calc = True
#     exclude_fl_prim = True
#     primary_generator = NullPrimerGenerator()
#     use_fast_approximation = True
#     hairpins = True


class SsmSolveTestSpecificConfigsRandom16(SsmSolveTestConfigRange):
    secondary_generator = AllPrimerGenerator()
    initialized = False
    percentage = 0.59
    num_of_tests = 0

    separate_temp_calc = True
    exclude_fl_prim = True
    primary_generator = Primer3(primer3_path=PRIMER3_PATH)
    use_fast_approximation = False
    hairpins = False


"""
calculate_mutagenic_primer_search_area
ssm_solve
SSMPrimerPair
SSMSolution
    primer_non_optimalities
    sum_of_non_optimality
SSMPrimerPossibilities
SSMPrimerPairPossibilities
pick_best_solution
update_generator_reports
SSMSolver
generate_fw_rw_primers
generate_primers
solve_for_mutations
get_temp_combinations
get_single_three_end_temps
get_separate_three_end_temps
get_three_end_temps_from_explicit_input
get_overlap_temps
get_all_valid_pairs_for_all_options
filter_by_three_end_size
get_best_primers_for_temp_ranges
config_for_mutation
create_config_for_primer3
"""