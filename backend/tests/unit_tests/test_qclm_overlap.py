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

"""
Unit tests for QCLM overlapping primers. For this the non-overlapping solution parameters was introduced.

"""
import random
import unittest

from mutation_maker.qclm import qclm_solve
from tests.test_support import generate_qclm_input

def num_only(string: str):
    return "".join([s for s in string if s.isdigit()])

def extract_position_from_key(key: str):
    return [int(num_only(s)) for s in key.split("-")]

def count_overlaps(primers_postions):
    cnt_overlaps = 0
    for key in primers_postions.keys():
        # we look if we have overlap with any other primer
        for other_key in primers_postions.keys():
            if other_key != key and primers_postions[other_key][0] < primers_postions[key][0] < primers_postions[other_key][1]:
                cnt_overlaps += 1
                continue
        # if any([primers_postions[other_key][0] > primers_postions[key][0] < primers_postions[other_key][1] for other_key in primers_postions.keys() if other_key!=key]):
        #     cnt_overlaps += 1
    print("The solution has {} number of overlapping primers".format(cnt_overlaps))
    return cnt_overlaps


def extract_muations(qclm_result):
    mut_positions = set()
    # here we store primers start and enc positions, as a key we use mutations, which the primer is covering
    primers_postions = {}
    for res in qclm_result["results"]:
        # we create key from just mutation positions therefore [1:-1]
        key = "-".join(res["mutations"])
        key_pos = "-".join([num_only(m) for m in res["mutations"]])
        print(key, res["primers"])
        for primer in res["primers"]:
            st = int(primer["start"])
            end = int(primer["start"]) + int(primer["length"])
            # we can have multiple primers for 1 mutation set, therefore we store just the minimal start and maximal end
            if key_pos in primers_postions.keys():
                st = min(st, primers_postions[key_pos][0])
                end = max(end, primers_postions[key_pos][1])
            primers_postions[key_pos] = (st, end)
        mut_positions.update(set(extract_position_from_key(key)))

    return mut_positions,primers_postions


class QCLMCoverageTest(unittest.TestCase):

    def test_non_overlap_false(self):
        """
        If everything works with new overlap parameter off
        For specified input we expect to find some overlaps
        :return:
        """
        qclm_data = generate_qclm_input(11)
        qclm_data.config.non_overlapping_primers = False
        exp = set()

        for mut in qclm_data.mutations:
            exp.update(set(extract_position_from_key(mut)))

        random.seed(121)
        result = qclm_solve(qclm_data)
        print(result)
        mut_positions = set()
        # here we store primers start and enc positions, as a key we use mutations, which the primer is covering
        primers_postions = {}
        for res in result["results"]:
            # we create key from just mutation positions therefore [1:-1]
            key = "-".join(res["mutations"])
            key_pos = "-".join([m[1:-1] for m in res["mutations"]])
            print(key, res["primers"])
            for primer in res["primers"]:
                st = int(primer["start"])
                end = int(primer["start"]) + int(primer["length"])
                # we can have multiple primers for 1 mutaiton set, therefore we store just the minimal start and maximal end
                if key_pos in primers_postions.keys():
                    st = min(st, primers_postions[key_pos][0])
                    end = max(end, primers_postions[key_pos][1])
                primers_postions[key_pos] = (st, end)
            mut_positions.update(set(extract_position_from_key(key)))

        # determine overlaps
        cnt_overlaps = 0
        for pair in primers_postions.values():
            # we look if we have overlap with any other primer
            if any([other[0] > pair[0] < other[1] for other in primers_postions.values()]):
                cnt_overlaps += 1
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))

        if len(mut_positions) != len(exp):
            print(len(mut_positions), len(exp))

        # we should have 0 overlaps
        self.assertEqual(len(mut_positions), len(exp))

    def test_non_overlap_true(self):
        """
        If everything works with new overlap parameter off
        For specified input we expect not to find any overlap
        :return:
        """
        qclm_data = generate_qclm_input(11)
        qclm_data.config.non_overlapping_primers = True
        exp = set()

        for mut in qclm_data.mutations:
            exp.update(set(extract_position_from_key(mut)))

        random.seed(121)
        result = qclm_solve(qclm_data)
        print(result)
        mut_positions = set()
        # here we store primers start and enc positions, as a key we use mutations, which the primer is covering
        primers_postions = {}
        for res in result["results"]:
            # we create key from just mutation positions therefore [1:-1]
            key = "-".join(res["mutations"])
            key_pos = "-".join([m[1:-1] for m in res["mutations"]])
            print(key, res["primers"])
            for primer in res["primers"]:
                st = int(primer["start"])
                end = int(primer["start"]) + int(primer["length"])
                # we can have multiple primers for 1 mutaiton set, therefore we store just the minimal start and maximal end
                if key_pos in primers_postions.keys():
                    st = min(st, primers_postions[key_pos][0])
                    end = max(end, primers_postions[key_pos][1])
                primers_postions[key_pos] = (st, end)
            mut_positions.update(set(extract_position_from_key(key)))

        # determine overlaps
        cnt_overlaps = 0
        for pair in primers_postions.values():
            # we look if we have overlap with any other primer
            if any([other[0] > pair[0] < other[1] for other in primers_postions.values()]):
                cnt_overlaps += 1
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))

        if len(mut_positions) != len(exp):
            print(len(mut_positions), len(exp))

        # we should have 0 overlaps
        self.assertEqual(cnt_overlaps, 0)


    def test_non_overlap_true1(self):
        """
        If everything works with new overlap parameter off
        For specified input we expect not to find any overlap
        :return:
        """
        qclm_data = generate_qclm_input(1)
        qclm_data.config.non_overlapping_primers = True
        exp = set()

        for mut in qclm_data.mutations:
            exp.update(set(extract_position_from_key(mut)))

        random.seed(121)
        result = qclm_solve(qclm_data)
        print(result)

        mut_positions, primers_postions = extract_muations(result)

        # determine overlaps
        cnt_overlaps = count_overlaps(primers_postions)
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))

        if len(mut_positions) != len(exp):
            print(len(mut_positions), len(exp))

        # we should have 0 overlaps
        self.assertEqual(cnt_overlaps, 0)

    def test_non_overlap_true2(self):
        """
        If everything works with new overlap parameter off
        For specified input we expect not to find any overlap
        :return:
        """
        qclm_data = generate_qclm_input(2)
        qclm_data.config.non_overlapping_primers = True
        exp = set()

        for mut in qclm_data.mutations:
            exp.update(set(extract_position_from_key(mut)))

        random.seed(121)
        result = qclm_solve(qclm_data)
        print(result)

        mut_positions, primers_postions = extract_muations(result)

        # determine overlaps
        cnt_overlaps = count_overlaps(primers_postions)
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))

        if len(mut_positions) != len(exp):
            print(len(mut_positions), len(exp))

        # we should have 0 overlaps
        self.assertEqual(cnt_overlaps, 0)

    def test_non_overlap_true3(self):
        """
        If everything works with new overlap parameter off
        For specified input we expect not to find any overlap
        :return:
        """
        qclm_data = generate_qclm_input(3)
        qclm_data.config.non_overlapping_primers = True
        exp = set()

        for mut in qclm_data.mutations:
            exp.update(set(extract_position_from_key(mut)))

        random.seed(121)
        result = qclm_solve(qclm_data)
        print(result)

        mut_positions, primers_postions = extract_muations(result)

        # determine overlaps
        cnt_overlaps = count_overlaps(primers_postions)
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))

        if len(mut_positions) != len(exp):
            print(len(mut_positions), len(exp))

        # we should have 0 overlaps
        self.assertEqual(cnt_overlaps, 0)

    # def test_non_overlap_true4(self):
    #     """
    #     If everything works with new overlap parameter off
    #     For specified input we expect not to find any overlap
    #     :return:
    #     """
    #     qclm_data = generate_qclm_input(4)
    #     qclm_data.config.non_overlapping_primers = True
    #     exp = set()
    #
    #             for mut in qclm_data.mutations:
    #             exp.update(set(extract_position_from_key(mut)))
    #
    #         random.seed(121)
    #         result = qclm_solve(qclm_data)
    #         print(result)
    #
    #         mut_positions, primers_postions = extract_muations(result)
    #
    #         # determine overlaps
    #         cnt_overlaps = count_overlaps(primers_postions)
    #         print("The solution has {} number of overlapping primers".format(cnt_overlaps))
    #
    #         if len(mut_positions) != len(exp):
    #             print(len(mut_positions), len(exp))
    #
    #         # we should have 0 overlaps
    #         self.assertEqual(cnt_overlaps, 0)

    def test_non_overlap_true5(self):
        """
        If everything works with new overlap parameter off
        For specified input we expect not to find any overlap
        :return:
        """
        qclm_data = generate_qclm_input(5)
        qclm_data.config.non_overlapping_primers = True
        exp = set()

        for mut in qclm_data.mutations:
            exp.update(set(extract_position_from_key(mut)))

        random.seed(121)
        result = qclm_solve(qclm_data)
        print(result)

        mut_positions, primers_postions = extract_muations(result)

        # determine overlaps
        cnt_overlaps = count_overlaps(primers_postions)
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))

        if len(mut_positions) != len(exp):
            print(len(mut_positions), len(exp))

        # we should have 0 overlaps
        self.assertEqual(cnt_overlaps, 0)


    def test_non_overlap_true6(self):
        """
        If everything works with new overlap parameter off
        For specified input we expect not to find any overlap
        :return:
        """
        qclm_data = generate_qclm_input(6)
        qclm_data.config.non_overlapping_primers = True
        exp = set()

        for mut in qclm_data.mutations:
            exp.update(set(extract_position_from_key(mut)))

        random.seed(121)
        result = qclm_solve(qclm_data)
        print(result)

        mut_positions, primers_postions = extract_muations(result)

        # determine overlaps
        cnt_overlaps = count_overlaps(primers_postions)
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))

        if len(mut_positions) != len(exp):
            print(len(mut_positions), len(exp))

        # we should have 0 overlaps
        self.assertEqual(cnt_overlaps, 0)


    def test_non_overlap_true7(self):
        """
        If everything works with new overlap parameter off
        For specified input we expect not to find any overlap
        :return:
        """
        qclm_data = generate_qclm_input(7)
        qclm_data.config.non_overlapping_primers = True
        exp = set()

        for mut in qclm_data.mutations:
            exp.update(set(extract_position_from_key(mut)))

        random.seed(121)
        result = qclm_solve(qclm_data)
        print(result)

        mut_positions, primers_postions = extract_muations(result)

        # determine overlaps
        cnt_overlaps = count_overlaps(primers_postions)
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))

        if len(mut_positions) != len(exp):
            print(len(mut_positions), len(exp))

        # we should have 0 overlaps
        self.assertEqual(cnt_overlaps, 0)


    def test_non_overlap_true8(self):
        """
        If everything works with new overlap parameter off
        For specified input we expect not to find any overlap
        :return:
        """
        qclm_data = generate_qclm_input(8)
        qclm_data.config.non_overlapping_primers = True
        exp = set()

        for mut in qclm_data.mutations:
            exp.update(set(extract_position_from_key(mut)))

        random.seed(121)
        result = qclm_solve(qclm_data)
        print(result)

        mut_positions, primers_postions = extract_muations(result)

        # determine overlaps
        cnt_overlaps = count_overlaps(primers_postions)
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))

        if len(mut_positions) != len(exp):
            print(len(mut_positions), len(exp))

        # we should have 0 overlaps
        self.assertEqual(cnt_overlaps, 0)


    def test_non_overlap_true9(self):
        """
        If everything works with new overlap parameter off
        For specified input we expect not to find any overlap
        :return:
        """
        qclm_data = generate_qclm_input(9)
        qclm_data.config.non_overlapping_primers = True
        exp = set()

        for mut in qclm_data.mutations:
            exp.update(set(extract_position_from_key(mut)))

        random.seed(121)
        result = qclm_solve(qclm_data)
        print(result)

        mut_positions, primers_postions = extract_muations(result)

        # determine overlaps
        cnt_overlaps = count_overlaps(primers_postions)
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))

        if len(mut_positions) != len(exp):
            print(len(mut_positions), len(exp))

        # we should have 0 overlaps
        self.assertEqual(cnt_overlaps, 0)


    def test_non_overlap_true10(self):
        """
        If everything works with new overlap parameter off
        For specified input we expect not to find any overlap
        :return:
        """
        qclm_data = generate_qclm_input(10)
        qclm_data.config.non_overlapping_primers = True
        exp = set()

        for mut in qclm_data.mutations:
            exp.update(set(extract_position_from_key(mut)))

        random.seed(121)
        result = qclm_solve(qclm_data)
        print(result)

        mut_positions, primers_postions = extract_muations(result)

        # determine overlaps
        cnt_overlaps = count_overlaps(primers_postions)
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))

        if len(mut_positions) != len(exp):
            print(len(mut_positions), len(exp))

        # we should have 0 overlaps
        self.assertEqual(cnt_overlaps, 0)


    def test_non_overlap_true11(self):
        """
        If everything works with new overlap parameter off
        For specified input we expect not to find any overlap
        :return:
        """
        qclm_data = generate_qclm_input(11)
        qclm_data.config.non_overlapping_primers = True
        exp = set()

        for mut in qclm_data.mutations:
            exp.update(set(extract_position_from_key(mut)))

        random.seed(121)
        result = qclm_solve(qclm_data)
        print(result)

        mut_positions, primers_postions = extract_muations(result)

        # determine overlaps
        cnt_overlaps = count_overlaps(primers_postions)
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))

        if len(mut_positions) != len(exp):
            print(len(mut_positions), len(exp))

        # we should have 0 overlaps
        self.assertEqual(cnt_overlaps, 0)



class QCLMNonOverlapTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(QCLMNonOverlapTest, self).__init__(*args, **kwargs)

    def runTest(self, non_overlap_flag, ind):
        self.non_overlap_flag = non_overlap_flag
        self.qclm_data = generate_qclm_input(ind)
        self.qclm_data.config.non_overlapping_primers = self.non_overlap_flag
        random.seed(121)
        self.qclm_result = qclm_solve(self.qclm_data)

        self.exp = set()
        for mut in self.qclm_data.mutations:
            self.exp.update(set(extract_position_from_key(mut)))

        mut_positions = set()
        # here we store primers start and enc positions, as a key we use mutations, which the primer is covering
        primers_postions = {}
        for res in self.qclm_result["results"]:
            # we create key from just mutation positions therefore [1:-1]
            key = "-".join(res["mutations"])
            key_pos = "-".join([m[1:-1] for m in res["mutations"]])
            print(key, res["primers"])
            for primer in res["primers"]:
                st = int(primer["start"])
                end = int(primer["start"]) + int(primer["length"])
                # we can have multiple primers for 1 mutaiton set, therefore we store just the minimal start and maximal end
                if key_pos in primers_postions.keys():
                    st = min(st, primers_postions[key_pos][0])
                    end = max(end, primers_postions[key_pos][1])
                primers_postions[key_pos] = (st, end)
            mut_positions.update(set(extract_position_from_key(key)))

        # determine overlaps
        cnt_overlaps = 0
        for pair in primers_postions.values():
            # we look if we have overlap with any other primer
            if any([other[0] > pair[0] < other[1] for other in primers_postions.values()]):
                cnt_overlaps += 1
        print("The solution has {} number of overlapping primers".format(cnt_overlaps))


        if len(mut_positions) != len(self.xp):
            print(len(mut_positions), len(self.exp))

        # we should have 0 overlaps if the flag is on
        if self.non_overlap_flag:
            self.assertEqual(cnt_overlaps, 0)

        if len(mut_positions) != len(self.exp):
            print("Not full coverage ERROR: {}".format(str(len(mut_positions)/len(self.exp))))