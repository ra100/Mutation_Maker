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
Support functions for testing methods.
"""

from random import randint
from typing import List, NamedTuple

from Bio.Alphabet import IUPAC
from Bio.Data import CodonTable

from mutation_maker.basic_types import Offset, DNASequenceForMutagenesis
from mutation_maker.qclm_types import QCLMInput, QCLMSequences, QCLMConfig
from mutation_maker.ssm_types import SSMInput, SSMSequences, Plasmid, SSMConfig
from mutation_maker.pas_types import PASInput, PASSequences, PASConfig, PASMutation, PASMutationSite, \
    PASMutationFormattedInput
from mutation_maker.temperature_calculator import TemperatureConfig


# ======================================================================================================================#
#                              RECURSIVE DICTIONARY COMPARISON / JSON COMPARISON                                       #
# ======================================================================================================================#

def id_dict(obj):
    """
    Checks if object is a dictionary.
    :param obj:
    :return: obj is a dictionary True/False
    """
    return obj.__class__.__name__ == 'dict'


def contains_key_rec(v_key, v_dict):
    for curKey in v_dict:
        if curKey == v_key or (id_dict(v_dict[curKey]) and contains_key_rec(v_key, v_dict[curKey])):
            return True
    return False


def get_value_rec(v_key, v_dict):
    for curKey in v_dict:
        if curKey == v_key:
            return v_dict[curKey]
        elif id_dict(v_dict[curKey]) and get_value_rec(v_key, v_dict[curKey]):
            return contains_key_rec(v_key, v_dict[curKey])
    return None


def comp_dicts(d1, d2):
    """
    Compares recursively two dictionaries.
    :param d1: (nested) dictionary
    :param d2: (nested) dictionary
    :return: True if the dictionaries contents are the same.
    """
    # TODO sort?
    for key in d1:
        if contains_key_rec(key, d2):
            d2_value = get_value_rec(key, d2)
            if d1[key] == d2_value or key == "non_optimality" or key == "parameters_in_range":
                # print("values are equal, d1: " + str(d1[key]) + ", d2: " + str(d2_value))
                continue
            else:
                print("values are not equal for key " + key + ":\n"
                      "list1: " + str(d1[key]) + "\n" +
                      "list2: " + str(d2_value))
                return False

        else:
            print("dict d2 does not contain key: " + key)
            return False
    return True


# ======================================================================================================================#
#                                               STATISTICS                                                             #
# ======================================================================================================================#


def get_statistics_qclm(data, metrics=None):
    """
    Creates dictionary of statistic for mutation results.
    :param metrics:
    :param data: dictionary of results
    :return: dict
    """
    if metrics is None:
        metrics = ["length", "temperature", "gc_content"]
    statistics = {}

    for metric in metrics:
        statistics[metric] = dict()

    for mutation_dict in data:
        for primer in mutation_dict["primers"]:
            for key in statistics.keys():
                statistics[key][int(10*primer[key])] = statistics[key].get(primer[key], 0) + 1
    return statistics


def print_stats_ssm(results, metrics=None):
    """
    Creates dictionary of statistic for mutation results.
    :param metrics:
    :param results: list of dictionaries
    :return: dict of statiscs + non optimality score triplet (min, max, avg)
    """
    if metrics is None:
        metrics = ["length", "three_end_temperature", "gc_content", "parameters_in_range"]
    statistics = {}

    for metric in metrics:
        statistics[metric] = dict()
    statistics["overlap_tm"] = dict()

    # for key in comparative_tests.keys():
    #     comparative_tests[key] = collections.Counter([d["forward_primer"][key] for d in results])
    score = []

    for mutation_dict in results:
        for key in metrics:
            val = str(format(mutation_dict["forward_primer"][key], ".2f"))
            statistics[key][val] = statistics[key].get(val, 0) + 1
            val = str(format(mutation_dict["reverse_primer"][key], ".2f"))
            statistics[key][val] = statistics[key].get(val, 0) + 1

        score.append(mutation_dict["non_optimality"])
        val = mutation_dict["overlap"]["temperature"]
        statistics["overlap_tm"][val] = statistics["overlap_tm"].get(val, 0) + 1

    non_opt = (min(score), max(score), sum(score) / len(score))
    format_stats_ssm(statistics)
    print("Optimality score min: %.2f , max: %.2f, avg: %.2f" % non_opt)
    return statistics, non_opt


def format_stats(stats):
    print("=" * 18, " STATS ", "=" * 18)
    for metric in stats.keys():
        print(metric + ":")
        for key in sorted(stats[metric].keys()):
            print('{:>10}'.format(key/10) + ": " + 'x' * stats[metric][key])

def format_stats_ssm(stats):
    print("=" * 18, " STATS ", "=" * 18)
    for metric in stats.keys():
        if metric is "parameters_in_range":
            print('{:>10}'.format("Parameters in range: %.2f %%") %
                  (100 * stats[metric]["1.00"] / (stats[metric]["1.00"] + sum(stats[metric].values()))))
            continue
        print(metric + ":")
        for key in sorted(stats[metric].keys()):
            print('{:>10}'.format(key) + ": " + 'x' * stats[metric][key])


def print_stats_qclm(data):
    stats = get_statistics_qclm(data["results"])
    format_stats(stats)


# ======================================================================================================================#
#                                                SSM specific                                                          #
# ======================================================================================================================#

def sample_ssm_sequence():
    return SSMSequences(
            forward_primer="PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING",
            reverse_primer="PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING",
            gene_of_interest="PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING",
            plasmid=Plasmid(
                plasmid_sequence="PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
            )
        )


def generate_SSM_input(mut_ind=0, min_overlap_temp=57,
                       calculation_method="MaxMutationsCovered",
                       max_3_end_ranges=1, temp_conf_precision=0,
                       primer_growth=True, separateTM=False):
    """
    Generates input for SSM solver
    :param mut_ind: Mutations, for mutations with not good enough overlap choose index 4 or higher
    :param min_overlap_temp:
    :param calculation_method:
    :param max_3_end_ranges:
    :param temp_conf_precision:
    :return:
    """
    muts = [  # 0
        ["E160X", "T164X", "T205X", "F206X", "F228X", "V272X"],
        # 1
        ["E89X", "E386X", "E329X", "E12X", "E38X", "E61X", "E445X", "E36X", "E239X",
         "E158X", "E267X", "E373X", "E347X", "E405X", "E57X", "E140X", "E99X", "E250X",
         "E204X", "E5X", "E219X", "E91X", "E299X", "E70X", "E417X", "E40X", "E97X",
         "E300X", "E35X", "E185X", "E403X", "E254X", "E343X", "E157X", "E397X", "E272X",
         "E215X", "E325X", "E24X", "E131X", "E411X", "E253X", "E46X", "E297X", "E428X"],
        # 2
        ["E160X", "T164X", "T205X", "F206X", "F228X", "V272X", "P283X", "S286X", "W287X",
         "I334X", "H383X", "S408X", "E449X", "D450X", "K451X"],
        # 3
        ["E449X", "D450X", "K451X"],
        # Mutations which don't have primers with good enough overlap size
        # 4
        ["E160X", "E449X"],
        # 5
        ["E449X", "D450X", "K451X"],
        # 6
        ["E160X", "T164X"],
        # 7
        ["E160X", "H383X"],
        # 8
        ["E160X"],
        # 9
        # 3' end problems
        ["S117E", "S117E", "V213P", "R257R", "H285S", "H285H", "A290Y", "S561A"]#, "E570M", "E570G"]
    ]

    return SSMInput(
        sequences=sample_ssm_sequence(),
        config=SSMConfig(
            min_overlap_temperature=min_overlap_temp,
            # min_overlap_temperature=78,
            calculation_method=calculation_method,
            max_three_end_ranges=max_3_end_ranges,
            temperature_config=TemperatureConfig(precision=temp_conf_precision),
            use_fast_approximation_algorithm=primer_growth,
            exclude_flanking_primers=separateTM
        ),
        mutations=muts[mut_ind]
    )


def generate_random_ssm_mutations(sequence, start_end, no_sites, max_mut_per_site=4):
    """Generate random mutations sites for SSM"""
    mutations = []
    sites = []

    while len(sites) < no_sites:
        sites.append(randint(start_end[0] // 3 + 9, start_end[1] // 3 - 9))

    all_aminos = IUPAC.IUPACProtein.letters
    standard_table = CodonTable.unambiguous_dna_by_name["Standard"]

    for site in sorted(sites):
        codon = sequence[3 * site: 3 * (site + 1)]
        if codon not in standard_table.forward_table.keys():
            continue
        else:
            orig_amino = standard_table.forward_table[codon]

        for _ in range(randint(1, max_mut_per_site)):
            target_amino = all_aminos[randint(0, len(all_aminos) - 1)]
            mutations.append(orig_amino + str(site) + target_amino)

    return mutations


def generate_random_SSM_input(mut_cnt = 96, max_mut_per_site = 3, min_overlap_temp=57,
                              calculation_method="MaxMutationsCovered",
                              max_3_end_ranges=1, temp_conf_precision=0,
                              use_fast_approximation=True, exclude_fl_prim=False,
                              hairpins=False, separate=True):
    """
    Generates random input for SSM solver
    :param mut_ind: Mutations, for mutations with not good enough overlap choose index 4 or higher
    :param min_overlap_temp:
    :param calculation_method:
    :param max_3_end_ranges:
    :param temp_conf_precision:
    :return:
    """
    sequenece = sample_ssm_sequence()

    mutations = generate_random_ssm_mutations(*sequenece.get_full_sequence_with_offset(), mut_cnt, max_mut_per_site)

    return SSMInput(
        sequences=sequenece,
        config=SSMConfig(
            compute_hairpin_homodimer=hairpins,
            separate_forward_reverse_temperatures=separate,
            # min_overlap_temperature=min_overlap_temp,
            # min_overlap_temperature=78,
            calculation_method=calculation_method,
            # max_three_end_ranges=max_3_end_ranges,
            temperature_config=TemperatureConfig(precision=temp_conf_precision),
            use_fast_approximation_algorithm=use_fast_approximation,
            exclude_flanking_primers=exclude_fl_prim,
            min_five_end_size=randint(3, 12)
        ),
        mutations=mutations
    )


# ======================================================================================================================#
#                                               QCLM specific                                                          #
# ======================================================================================================================#

def generate_qclm_input(ind=3, non_overlapping_primers=False) -> QCLMInput:
    """
    Generates input for QCLM algorithm testing
    :param ind: index of mutations. We can pick from 3 different mutations list.
    :return:
    """

    mutations = []
    use_degenerate_codons = True
    if ind == 0:
        mutations = ["E52W", "E52L", "E52F", "E52A"]
    elif ind == 1:
        mutations = ["E52W", "E52I", "E53W", "E53I"]
    elif ind == 2:
        mutations = ["E52W", "E52L", "E52F", "E52A", "V73L", "V73G", "V73F", "V73I",
                     "V73S", "A165P", "A165E", "A165R", "A165K", "R169I", "R169K",
                     "R169L", "R169Y"]
    elif ind == 3:
        mutations = ["P269P", "P269D", "A271A", "A271R", "V272V", "V272N", "Q376Q", "Q376R", "M379M", "M379L",
                     "K383K", "K383T", "T408T", "T408S", "T408N", "H411H", "H411K", "H411P", "H411E", "L412L", "L412D"]
    # tricky test with many primers with neighbours !WARNING! takes a long of time
    elif ind == 4:
        mutations = ["G310C", "H348C", "I6C", "L9C", "S11C", "G15C", "A16C", "A20C", "E21C", "V26C", "G27C",
                     "L31C", "G32C"]
        use_degenerate_codons = False
    elif ind == 5:
        mutations = ["I6C", "L9C"]
        use_degenerate_codons = False
    elif ind == 6:
        mutations = ["I6C", "L9C", "S11C"]
        use_degenerate_codons = False
    elif ind == 7:
        mutations = ["Y67K", "Y67R", "T69F", "T69Y", "T124K", "T124R", "P135R", "F136R", "G284A"]
        use_degenerate_codons = False
    elif ind == 8:
        mutations = ["Y67K", "Y67R", "T69F", "T69Y", "T124K", "T124R", "P135R", "F136R", "G284A"]
        use_degenerate_codons = True

    elif ind == 9:
        mutations = ["F86W", "E91A", "V140R", "A141P", "L155E", "L155Q",
                     "T181V", "S199P", "P225E", "L227E", "L227T", "L227Q", "L227V"]
        use_degenerate_codons = True

    elif ind == 10:
        mutations = ["K52W", "K52L", "K52F", "K52A", "N73L", "N73G", "N73F", "N73I", "N73S", "T165P", "T165E",
                     "T165R", "T165K", "A169I", "A169K", "A169L", "A169Y"]
        use_degenerate_codons = True

    elif ind == 11:  # testing three/five prime end orientation
        mutations = ["Y67K", "Y67R", "T69F", "T69Y", "T124K", "T124R", "P135R", "F136R", "G284A"]
        use_degenerate_codons = False

    elif ind == 11:
        ## overlap mutations
        mutations = ["I55V", "I55F", "V69C", "V69T", "H83G", "H83N", "I122W", "I122F", "T134V", "T134G", "L136Y",
                     "V152I", "Q155L", "W156T", "W156S", "A192S", "I196R", "I199L", "F215L", "R273V"]
        use_degenerate_codons = False

    return QCLMInput(
        sequences=sample_qclm_sequences(ind),
        config=sample_qclm_config(ind, use_degeneracy_codon=use_degenerate_codons, non_overlapping_primers=non_overlapping_primers),
        mutations=mutations)


class MutationsForSite(NamedTuple):
    codon_index: int
    orig_amino: str
    target_amino: str


MIN_THREE_END_SIZE = 10
MIN_FIVE_END_SIZE = 10


def random_qclm_mutations(seq: QCLMSequences, no_sites=10, mutations_per_site=4) -> List[MutationsForSite]:
    """
    Generates random mutations for QCLM algorithm testing
    """

    first_codon = (len(seq.five_end_flanking_sequence) + MIN_FIVE_END_SIZE) // 3 + 1
    last_codon = (len(seq.gene_of_interest) - len(seq.three_end_flanking_sequence)
                  - MIN_THREE_END_SIZE) // 3 - 1

    sites = set()

    while len(sites) < no_sites:
        sites.add(randint(first_codon, last_codon))

    # sites = [231//3, 363//3, 447//3, 468//3, 477//3]

    result: List[MutationsForSite] = []
    for site in sorted(sites):
        mutations = set()
        aminos = IUPAC.IUPACProtein.letters
        no_aminos = len(aminos)

        codon = seq.gene_of_interest[3 * site : 3 * (site + 1)]
        standard_table = CodonTable.unambiguous_dna_by_name["Standard"]
        orig_amino = standard_table.forward_table[codon]

        while len(mutations) < mutations_per_site:
            amino = aminos[randint(0, no_aminos - 1)]
            if amino is not orig_amino:
                mutations.add(amino)

        for target_amino in mutations:
            result.append(MutationsForSite(site, orig_amino, target_amino))

    return sorted(result, key=lambda x: x.codon_index)


def sample_qclm_sequences(ind=0) -> QCLMSequences:
    if ind ==4:
        mutated_dna = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        three_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        five_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
    elif ind == 5 or ind == 6:
        mutated_dna = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        three_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        five_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
    elif ind in [7, 8]:
        mutated_dna = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        three_end_flanking = ""
        five_end_flanking = ""
    elif ind == 11:
        mutated_dna= "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        three_end_flanking = ""
        five_end_flanking = ""
    else:
        mutated_dna = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        three_end_flanking = ""
        five_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"

    return QCLMSequences(
        gene_of_interest=mutated_dna,
        five_end_flanking_sequence=five_end_flanking,
        three_end_flanking_sequence=three_end_flanking)


def sample_qclm_config(ind=0, use_primer3=True, use_degeneracy_codon=True,
                       non_overlapping_primers=False) -> QCLMConfig:
    return QCLMConfig(
        min_gc_content=40,
        max_gc_content=60,
        temp_range_size=5,
        min_temperature=75,
        use_degeneracy_codon=use_degeneracy_codon,
        use_primer3=use_primer3,
        non_overlapping_primers=non_overlapping_primers)


def LevensteinDist(seq1, seq2):
    """
    Dynamic programming solution for Levenstein distance of two sequences.
    seq1 -> represents rowumn
    seq2 -> represents col
    Returns levenstein distance of two sequences
    """
    # Create matrix of lev_distance
    # +1 because first row and first column are empty substrings
    lev_dist_mat = [[0 for row in range(len(seq2) + 1)] for col in range(len(seq1) + 1)]
    # initialize with number of insertion to row / column from the empty substring
    for row in range(0, len(seq1) + 1):
        lev_dist_mat[row][0] = row
    for col in range(0, len(seq2) + 1):
        lev_dist_mat[0][col] = col
    # compute distance for other substrings
    for row in range(1, len(seq1) + 1):
        for col in range(1, len(seq2) + 1):
            if seq1[row - 1] == seq2[col - 1]:
                match = 0
            else:
                match = 1

            lev_dist_mat[row][col] = min(lev_dist_mat[row - 1][col] + 1, lev_dist_mat[row][col - 1] + 1,
                                         lev_dist_mat[row - 1][col - 1] + match)
    return lev_dist_mat[-1][-1]

# ======================================================================================================================#
#                                               PAS specific                                                          #
# ======================================================================================================================#


def generate_pas_input(ind=1) -> PASInput:
    """
    Generates input for PAS algorithm testing
    :param ind: index of the test case.
    :return:
    """

    mutations = []
    use_degenerate_codons = True
    mutations = sample_pas_mutations(ind)
    if ind == 5:
        is_dna_seq=False
    else:
        is_dna_seq=True

    return PASInput(
        sequences=sample_pas_sequences(ind),
        is_dna_sequence=is_dna_seq,
        config=sample_pas_config(ind, use_degeneracy_codon=use_degenerate_codons),
        mutations=[PASMutationFormattedInput(mutants=mut.get_mutations_str_list(), position=mut.position, frequency=mut.mutations[0].frequency) for mut in mutations],
        is_mutations_as_codons=False)


def sample_pas_mutations(ind=1) -> [PASMutationSite]:
    if ind == 1:
        return [
                PASMutationSite(position=9,
                                mutations=[PASMutation(mutation="R,W", frequency=0.5)]),
                PASMutationSite(position=10,
                                mutations=[PASMutation(mutation="K,R", frequency=0.1)]),
                PASMutationSite(position=13,
                                mutations=[PASMutation(mutation="R,K", frequency=0.1)]),
                PASMutationSite(position=19,
                                mutations=[PASMutation(mutation="L", frequency=0.1)]),
                PASMutationSite(position=39,
                                mutations=[PASMutation(mutation="C", frequency=0.1)])]

    elif ind == 2:
        return [PASMutationSite(position=16,
                                mutations=[PASMutation(mutation="W,R", frequency=0.2)]),
                PASMutationSite(position=29,
                                mutations=[PASMutation(mutation="M,K", frequency=0.2)]),
                PASMutationSite(position=55,
                                mutations=[PASMutation(mutation="W,E", frequency=0.2)]),
                PASMutationSite(position=56,
                                mutations=[PASMutation(mutation="E", frequency=0.2)]),
                PASMutationSite(position=57,
                                mutations=[PASMutation(mutation="D", frequency=0.2)]),
                PASMutationSite(position=58,
                                mutations=[PASMutation(mutation="V", frequency=0.2)]),
                PASMutationSite(position=65,
                                mutations=[PASMutation(mutation="S", frequency=0.2)]),
                PASMutationSite(position=85,
                                mutations=[PASMutation(mutation="S", frequency=0.2)]),
            ]
    elif ind == 3:
        return [PASMutationSite(position=1,
                                mutations=[PASMutation(mutation="R,L", frequency=0.25)]),
                PASMutationSite(position=2,
                                mutations=[PASMutation(mutation="R", frequency=0.9)]),
                PASMutationSite(position=10,
                                mutations=[PASMutation(mutation="I,V,F,S,R,T", frequency=0.5)]),
                PASMutationSite(position=12,
                                mutations=[PASMutation(mutation="Y", frequency=0.1)]),
                PASMutationSite(position=30,
                                mutations=[PASMutation(mutation="L", frequency=0.1)]),
                PASMutationSite(position=36,
                                mutations=[PASMutation(mutation="A", frequency=0.1)]),
                PASMutationSite(position=39,
                                mutations=[PASMutation(mutation="L", frequency=0.1)]),
                PASMutationSite(position=63,
                                mutations=[PASMutation(mutation="H", frequency=0.1)]),
                PASMutationSite(position=66,
                                mutations=[PASMutation(mutation="L", frequency=0.1)]),
                PASMutationSite(position=73,
                                mutations=[PASMutation(mutation="A", frequency=0.1)]),
                PASMutationSite(position=84,
                                mutations=[PASMutation(mutation="R", frequency=0.1)]),
                PASMutationSite(position=87,
                                mutations=[PASMutation(mutation="G", frequency=0.1)]),
                PASMutationSite(position=90,
                                mutations=[PASMutation(mutation="N", frequency=0.1)])
                ]

    elif ind == 4:
        return [PASMutationSite(position=1,
                                     mutations=[PASMutation(mutation="A", frequency=0.5)])]
    elif ind == 5:
        return [
            PASMutationSite(position=9,
                            mutations=[PASMutation(mutation="R,W", frequency=0.5)]),
            PASMutationSite(position=10,
                            mutations=[PASMutation(mutation="K,R", frequency=0.1)]),
            PASMutationSite(position=13,
                            mutations=[PASMutation(mutation="R,K", frequency=0.1)]),
            PASMutationSite(position=19,
                            mutations=[PASMutation(mutation="L", frequency=0.1)]),
            PASMutationSite(position=39,
                            mutations=[PASMutation(mutation="C", frequency=0.1)])]

    elif ind == 6:
        """
        R17	H
        P34	I,V,F,S,R,T
        K246	M
        R254	P,G,D,A
        S255	D
        S256	L
        R286	L
        V351	M
        """

        return [PASMutationSite(position=17,
                         mutations=[PASMutation(mutation="H", frequency=0.24)]),
         PASMutationSite(position=34,
                         mutations=[PASMutation(mutation="I,V,F,S,R,T", frequency=0.24)]),
         # PASMutationSite(position=1,
         #                         mutations=[PASMutation(mutation="E", frequency=0.25)]),
         PASMutationSite(position=246,
                         mutations=[PASMutation(mutation="M", frequency=0.24)]),
         PASMutationSite(position=254,
                         mutations=[PASMutation(mutation="P,G,D,A", frequency=0.24)]),
         PASMutationSite(position=255,
                         mutations=[PASMutation(mutation="D", frequency=0.24)]),
         PASMutationSite(position=256,
                         mutations=[PASMutation(mutation="L", frequency=0.24)]),
         PASMutationSite(position=286,
                         mutations=[PASMutation(mutation="L", frequency=0.24)]),
         PASMutationSite(position=351,
                         mutations=[PASMutation(mutation="M", frequency=0.24)])]


def sample_pas_sequences(ind=1) -> PASSequences:
    if ind == 1:
        mutated_dna = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        three_end_flanking = ""
        five_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
    elif ind==2:
        mutated_dna = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        three_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        five_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
    elif ind==3:
        mutated_dna = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        three_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        five_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
    elif ind==4:
        mutated_dna = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        three_end_flanking = None
        five_end_flanking = None
    # AMINO ACID
    elif ind==5:
        mutated_dna = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        three_end_flanking = None
        five_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
    elif ind==6:
        mutated_dna = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        three_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
        five_end_flanking = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"

    return PASSequences(
        gene_of_interest=mutated_dna,
        five_end_flanking_sequence=five_end_flanking,
        three_end_flanking_sequence=three_end_flanking)


def sample_pas_config(ind=1, use_degeneracy_codon=True) -> PASConfig:
    if ind == 1:
        return PASConfig(
            min_oligo_len=30,
            max_oligo_len=70,
            min_gc_content=40,
            max_gc_content=60,
            min_overlap_tm=40,
            min_overlap_len=12,
            max_overlap_len=30,
            temp_range_size=10,
            max_overlap_tm=65,
            use_degeneracy_codon=use_degeneracy_codon,
            temperature_config=TemperatureConfig(calculation_type="NN"))


    if ind == 2:
        return PASConfig(
            min_gc_content=40,
            max_gc_content=60,
            temp_range_size=5,
            min_overlap_tm=40,
            max_overlap_tm=90,
            use_degeneracy_codon=False,
            temperature_config=TemperatureConfig(calculation_type="NEB_like"))

    if ind == 3:
        return PASConfig(
            min_gc_content=40,
            max_gc_content=60,
            temp_range_size=5,
            min_overlap_tm=53,
            max_overlap_tm=63,
            use_degeneracy_codon=use_degeneracy_codon,
            temperature_config=TemperatureConfig(calculation_type="NEB_like"))

    if ind == 4:
        return PASConfig(
            min_gc_content=40,
            max_gc_content= 60,
            min_oligo_size= 30,
            max_oligo_size= 90,
            min_overlap_length= 15,
            opt_overlap_length= 21,
            max_overlap_length= 30,
            min_overlap_tm= 54,
            opt_overlap_tm= 56,
            max_overlap_tm= 64,
            organism= "e-coli",
            use_degeneracy_codon=use_degeneracy_codon,
            temperature_config=TemperatureConfig(calculation_type="NEB_like"))

    if ind == 5:
        return PASConfig(
            min_oligo_len=30,
            max_oligo_len=70,
            min_gc_content=40,
            max_gc_content=60,
            min_overlap_tm=40,
            min_overlap_len=12,
            max_overlap_len=30,
            temp_range_size=10,
            max_overlap_tm=65,
            organism= "e-coli",
            is_dna_sequence=False,
            use_degeneracy_codon=use_degeneracy_codon,

            temperature_config=TemperatureConfig(calculation_type="NN"))


    return PASConfig(
        min_gc_content=40,
        max_gc_content=60,
        temp_range_size=5,
        min_overlap_tm=30,
        max_overlap_tm=60,
        use_degeneracy_codon=use_degeneracy_codon,
        temperature_config=TemperatureConfig(calculation_type="NEB_like"))


def sample_pas_gene(ind=1) ->DNASequenceForMutagenesis:
    """
    Generates gene sequence for testing purposes
    :param ind:
    :return:
    """
    sequence, goi_offset = sample_ssm_sequence(ind).get_full_sequence_with_offset()
    mutations_offsets = [Offset(goi_offset + mut.position * 3) for mut in sample_pas_mutations(ind)]
    return DNASequenceForMutagenesis(sequence, mutations_offsets)
