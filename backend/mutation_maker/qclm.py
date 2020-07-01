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
import math
from pprint import pprint
import time

import numpy as np
import random
from typing import Dict, List, Set, Tuple, Mapping, Sequence

from Bio.Seq import _translate_str
from Bio.SeqUtils import GC
from Bio.Data import CodonTable

from mutation_maker.basic_types import PrimerSpec
from mutation_maker.codon_usage_table import Organism
from mutation_maker.qclm_solution import DNASequenceForMutagenesis, Offset, AminoAcid, Codon, \
    QCLMPrimers, QCLMSolution, ScoredPrimer
from mutation_maker.site_split import SiteSplits, SiteSequence, SiteSet
from mutation_maker.primer_scoring import PrimerScoring
from mutation_maker.degenerate_codon import DegenerateTriplet, DegenerateTripletWithAminos, CodonUsage
from mutation_maker.mutation import MutationSite, QCLMMutationSiteSequence
from mutation_maker.qclm_types import QCLMConfig, QCLMInput, QCLMMutationOutput, QCLMOutput, \
    QCLMSequences, SetOfMutationSiteSequences
from mutation_maker.temperature_calculator import TemperatureCalculator, HeteroDimerCalculator
from mutation_maker.qclm_types import (PrimerOutput)
from mutation_maker.pas_degeneracy_recursion import Degeneracy
from mutation_maker.degeneracy_lookup import lookup
from mutation_maker.usage_table import UsageTable


def calculate_mutagenic_primer_search_area(mutation: QCLMMutationSiteSequence,
                                           qclm_config: QCLMConfig) -> Tuple[int, int]:
    min_start = mutation.position - qclm_config.max_five_end_size
    search_area_length = (
            qclm_config.max_five_end_size +
            mutation.length +
            qclm_config.max_three_end_size
    )

    if min_start < 0:
        search_area_length = search_area_length + min_start
        min_start = 0

    return min_start, search_area_length


def qclm_solve(workflow_input: QCLMInput):
    solver = QCLMSolver(workflow_input.sequences, workflow_input.config)

    mutations = workflow_input.parse_mutations(solver.goi_offset)
    output = solver.solve(workflow_input, mutations)
    return output.to_json()


def get_replace_wildtype_codons(mutations, codons_for_sites, sequence):
    """
    From translated codons from site we extract wild-type codons
    and return the list of wild-type codons in the same order as mutation sites.
    Because codons are selected randomly also for wild-type amino, we need to replace it with actual
    codon from the sequence.
    The order is important as we will remove in the end primers containing only wild-types in case
    a single primer has more than 1 (this means 2,3,4...) mutation sites.
    :param mutations: ordered mutations by the position
    :param codons_for_sites:
    :return:
    """
    wt_codons = []
    table = CodonTable.ambiguous_dna_by_id[1]
    new_codons_for_site = []
    for mutation, codons in zip(mutations, codons_for_sites):
        new_site_codons = set()
        for codon in codons:
            if mutation.old_amino == _translate_str(codon, table):
                wt_codon = sequence[mutation.position: mutation.position+3]
                wt_codons.append(wt_codon)
                new_site_codons.add(wt_codon)
            else:
                new_site_codons.add(codon)

        new_codons_for_site.append(new_site_codons)

    return wt_codons, new_codons_for_site



# noinspection PyMethodMayBeStatic
def get_wildtype_codons(mutations, codons_for_sites):
    """
    From translated codons from site we extract wild-type codons
    and return the list of wild-type codons in the same order as mutation sites.
    The order is important as we will remove in the end primers containing only wild-types in case
    a single primer has more than 1 (this means 2,3,4...) mutation sites.
    :param mutations: ordered mutations by the position
    :param codons_for_sites:
    :return:
    """
    wt_codons = []
    table = CodonTable.ambiguous_dna_by_id[1]
    for mutation, codons in zip(mutations, codons_for_sites):
        for codon in codons:
            if mutation.old_amino == _translate_str(codon, table):
                wt_codons.append(codon)
    return wt_codons

def non_deg_codon_transformation(codon):
    """Returns a list of normal codons from the degenerate one"""
    list_of_nucs = [list(lookup[str(nuc)].bases) for nuc in codon]
    return [''.join(element) for element in itertools.product(*list_of_nucs)]

def get_wildtype_codons_degenerate(mutations, codons_for_sites):
    """Returns the wild type codons in the degenerate case"""
    wt_codons = []
    table = CodonTable.ambiguous_dna_by_id[1]
    for mutation, codons in zip(mutations, codons_for_sites):
        for codon in codons:
            non_deg_codons = non_deg_codon_transformation(codon)
            for cod in non_deg_codons:
                if mutation.old_amino == _translate_str(cod, table):
                    wt_codons.append(cod)
    return wt_codons

def check_set_cover(codons_for_site):
    """Checks if the set cover solution contains stop codons"""
    for site in codons_for_site:
        for codon in site:
            non_deg = non_deg_codon_transformation(codon)
            for cod in non_deg:
                if cod in ['TAA','TAG','TGA']:
                    return False
                else:
                    pass
    return True



def skip_wild_type_primer(primer_codons, wt_codons):
    """
    Function used for detecting primers which have only wild-type codons.
    Return true if both list match. Order is taken into account.
    :param primer_codons: List of codons [str]
    :param wt_codons: List of codons [str]
    :return: boolean
    """
    # if len(wt_for_sequence) < 2:
    #     return False
    assert len(primer_codons) == len(wt_codons)
    return all([wt == codon for wt, codon in zip(wt_codons, primer_codons)])

def solve_set_cover(config, aminos_for_sites):
    degeneracy = Degeneracy(config)
    codons_for_site = []
    for amino_set in aminos_for_sites:
        deg_solution = degeneracy(list(amino_set))
        codons_set = set([codon for codon, aminos in deg_solution.items()])
        codons_for_site.append(codons_set)
    return codons_for_site


def get_next_site_start(current_site, starts):
    """
    Computes start of next site in QCLM solution. If the current site is the last on in the solution,
    the method returns infinite. This is because we use this method in computing overlap with the next site by comparing
    end of current site and the start of next site. So infinite gives no overlap.
    :param current_site: current site set
    :param starts: list of starts from compute_starts method
    :return: start of the following site, if no site is following, we return infinite.
    """

    ind = [s[0] for s in starts].index(current_site)
    if ind+1 >= len(starts):
        return float("inf")

    return starts[ind+1][1]


def compute_starts(solution:QCLMSolution):
    """
    Create list of tupples:
        - qclm site
        - minimal starting value of primer for this site
    :param solution:
    :return: ordered list by site start
    """
    sites_boundaries = {}
    sorted_sites = sorted(solution.primers.keys(), key=lambda site: min(site))

    for s_site in sorted_sites:
        pair = (min([primer.spec.offset for primer in solution.primers[s_site]]), max([primer.spec.offset+primer.spec.length for primer in solution.primers[s_site]]))
        sites_boundaries[s_site]=(pair)
    return sites_boundaries


def check_for_overlap(sites_boundaries, site_id, start, end):

    for site_key in sites_boundaries.keys():
        # we cannot compare two frozen-sets, but we know that if the minimal value is the same, than it represents the same mutation site
        if min(site_key) != min(site_id):
            if sites_boundaries[site_key][0] <= start <= sites_boundaries[site_key][1] or \
               sites_boundaries[site_key][0] <= end <= sites_boundaries[site_key][1]:
                # the start or the end is inside of some mutation site boundaries -> there is overlap
                return True
    return False


class QCLMSolver:
    config: QCLMConfig
    temp_calculator: TemperatureCalculator
    sequence: str
    goi_offset: int

    def __init__(self, qclm_sequences: QCLMSequences, qclm_config: QCLMConfig) -> None:
        self.config = qclm_config
        if qclm_config.organism == "e-coli":
            self.usages = CodonUsage("e-coli")
        elif qclm_config.organism == "yeast":
            self.usages = CodonUsage("yeast")
        else:
            org = Organism(qclm_config.organism)
            self.usages = org.translation_table

        self.temp_calculator = qclm_config.temperature_config.create_calculator()
        self.sequence, self.goi_offset = qclm_sequences.get_full_sequence_with_offset()
        self.__hetero_bind_calculator = HeteroDimerCalculator(self.config.temperature_config.k,
                                                              self.config.temperature_config.mg,
                                                              self.config.temperature_config.dntp)

    def solve(self, input_data: QCLMInput, mutations: List[MutationSite]) \
            -> QCLMOutput:

        """
        Find a solution to the QCLM problem.

        :param input_data:
        :param mutations: A list of requested mutations
        :return:
        """

        mutations = sorted(mutations, key=lambda m: m.position)

        print("----------------------------------------START mutations:", ",".join([str(m) for m in mutations]))
        #
        # GENERATE CODONS FOR EACH MUTATION SITE
        #

        # Get a list of amino acid sets with wild types. Each set contains mutations required for one site.
        aminos_for_sites = [(set(AminoAcid(a) for a in mut.new_aminos))
                             for mut in mutations]

        print("----------------------------------------Aminos for site {}".format(",".join([str(am) for am in
                                                                                            aminos_for_sites])))


        # Compute the degenerate codon solution
        valid_set_cover = False
        codons_for_site = []
        wild_type_codons = []
        if self.config.use_degeneracy_codon:
            timeout = time.time() + 60 * 1  # setting up 1 min timer. After 2 mins it will switch to non-degenerate case
            while(not valid_set_cover):
                codons_for_site = solve_set_cover(self.config, aminos_for_sites)
                wild_type_codons = get_wildtype_codons_degenerate(mutations, codons_for_site)
                valid_set_cover = check_set_cover(codons_for_site)
                if time.time() > timeout:
                    break

        if not valid_set_cover:
            # Pick codons for the aminos randomly
            codons_for_site = self.pick_random_codons(aminos_for_sites,
                                                      self.usages,
                                                      self.config.codon_usage_frequency_threshold)
            wild_type_codons, codons_for_site = get_replace_wildtype_codons(mutations, codons_for_site, self.sequence)


        #
        # FIND POSSIBLE SPLITS OF THE MUTATION SITES TO SEQUENCES SUCH THAT EACH SEQUENCE CAN
        # BE COVERED BY A SINGLE PRIMER.
        #

        mutation_subsets_combinations: List[SetOfMutationSiteSequences] = \
            self.find_mutation_coverage_options(mutations)

        all_site_splits: SiteSplits = SiteSplits.from_list_of_SetOfMutationSiteSequences(mutation_subsets_combinations)

        # If the user requested non-overlapping primers, then we optimize primers separately for each mutation site split, as we have
        # to consider borders of other primers that will be part of the same solution.
        # Otherwise, we can optimize primers for a given site set independently, so iterating through site splits is not needed.
        sets_of_splits_to_optimize: List[SiteSplits]
        if self.config.non_overlapping_primers:
            sets_of_splits_to_optimize = []
            for site_split in all_site_splits.splits:
                single_split = SiteSplits()
                single_split.add(site_split)
                sets_of_splits_to_optimize.append(single_split)
        else:
            sets_of_splits_to_optimize = [all_site_splits]

        # Build an index for mutation site offsets
        mut_site_offsets = [Offset(m.position) for m in mutations]
        index_of_site = {offset: i for (i, offset) in enumerate(mut_site_offsets)}

        mutated_dna_sequence = DNASequenceForMutagenesis(self.sequence, mut_site_offsets)
        for site_splits in sets_of_splits_to_optimize:

            #
            # FIND CODONS DEFINING MUTATIONS IN PRIMERS, FOR EACH SITE SEQUENCE APPEARING IN ANY CONSIDERED SITE SPLIT
            #

            current_primers = QCLMPrimers(site_splits, mutated_dna_sequence, self.config, self.temp_calculator)

            # noinspection PyUnusedLocal
            seq: SiteSequence
            sorted_site_sequences = sorted(site_splits.get_site_sequences(), key=lambda s: min(s))
            for ind, seq in enumerate(sorted_site_sequences):
                print("Processing site sequence: {} ".format(",".join([str(site) for site in seq])))
                # Get a list of codon sets for the site sequence
                codons_for_sequence = []
                for offset in seq:
                    codons_for_sequence.append(codons_for_site[index_of_site[offset]])

                # Get a list of wild type codons for the site sequence
                wt_for_sequence = []
                for offset in seq:
                    wt_for_sequence.append(wild_type_codons[index_of_site[offset]])

                # Create primer definitions (sequences of codons) for the site sequence
                primer_codons: List[List[Codon]] = \
                    DegenerateTripletWithAminos.create_subsets_for_primers(codons_for_sequence)

                #
                # GENERATE PRIMERS OF MINIMUM PERMISSIBLE LENGTH FOR THESE PRIMER DEFINITIONS
                #

                # In case of non-overlapping solution, get the right limit (<) for primers for the previous site sequence.
                # This will be the minimum offset for primers for this site sequence.
                min_primer_start = current_primers.range(frozenset(sorted_site_sequences[ind-1]))[1] \
                                    if self.config.non_overlapping_primers and ind > 0 \
                                    else 0

                for primer in primer_codons:
                    current_primers.add_minimal_primers(frozenset(seq), primer, min_start=min_primer_start)

            #
            # GROW THE PRIMERS UNTIL THEY REACH A SELECTED TEMPERATURE THRESHOLD.
            # COLLECT A QCLM SOLUTION FOR EACH TEMPERATURE THRESHOLD.
            #

            solutions: List[QCLMSolution] = []
            score_fun = PrimerScoring(mutated_dna_sequence, self.config)

            eps = 1e-6
            step = self.config.temp_threshold_step
            for temp_threshold in np.arange(self.config.min_temperature, self.config.max_temperature + eps, step):
                current_primers.grow(temp_threshold)
                temperature = temp_threshold + step / 2.

                # Select best primers for each site sequence
                best_primers: Mapping[SiteSet, Sequence[ScoredPrimer]] = \
                    current_primers.collect_best_primers(score_fun, temperature)

                # Find the site split which provides the best solution when using the selected primers
                new_solution = \
                    self.select_best_site_split(best_primers, site_splits, temperature, mutations, self.config,
                                                mutated_dna_sequence)

                if new_solution.primers: # Solution is not empty
                    solutions.append(new_solution)

        #
        # SELECT THE BEST OVERALL SOLUTIONS.
        #

        sorted_solutions = sorted(solutions, key=lambda s: s.score())
        best_solution = sorted_solutions[0]

        print("FOUND SOLUTIONS: ====================================================================================")

        for sol in solutions:
            print(repr(sol))

        print("FOUND SOLUTIONS: ====================================================================================")

        output = self.create_new_output(input_data, best_solution)

        #
        # CHECK WHETHER THE SOLUTION FULFILLS ALL CONSTRAINTS.
        #

        failed_primers = best_solution.get_breaking_primers(self.sequence)
        mutation_coverage = best_solution.mutation_coverage()

        print(repr(best_solution))

        print_input = False
        print("\nSOLUTION DEFECTS:")
        if mutation_coverage < 1 - eps:
            print(f"Solution coverage for requested mutations is only {100 * mutation_coverage:.1f}%.")
            print_input = True

        if failed_primers:
            for primer in failed_primers:
                pprint(primer)
            print_input = True

        if print_input:
            pprint(self.sequence)
            print(output.input_data)
        else:
            print("NONE")
        print("\n")

        return output

    def select_best_site_split(self,
                               best_primers: Mapping[SiteSet, Sequence[ScoredPrimer]],
                               site_splits: SiteSplits,
                               temperature: float,
                               mutations: List[MutationSite], config: QCLMConfig,
                               base: DNASequenceForMutagenesis) \
            -> QCLMSolution:
        """ Creates a QCLM solution from selected primers, using a site split which provides
            the lowest score for the solution.
        """
        print("Selecting best splits")

        best_solution = QCLMSolution(mutations, temperature, config)
        best_score = math.inf

        for site_split in site_splits.splits:
            solution = QCLMSolution(mutations, temperature, config)
            for site_seq in site_split:
                site_set = frozenset(site_seq)

                # noinspection PyUnusedLocal
                primer: ScoredPrimer
                for primer in best_primers[site_set]:
                    hb_penalty = 0.0
                    if self.config.use_primer3:
                        hb_penalty = self.compute_hb_panalty(primer.spec, solution, site_set, base)
                    solution.add_primer(site_set, primer.spec, primer.tm, primer.score + hb_penalty)

            solution_score = solution.score()
            if solution_score < best_score:
                best_score = solution_score
                best_solution = solution

        if best_solution.primers:
            print("Best solution")
            pprint(best_solution)
        else:
            print("No solution found")

        return best_solution

    # Find set covers of all mutation sites consisting of mutually disjoint subsets of sites that can
    # be mutated by a single primer.
    def find_mutation_coverage_options(self, mutations: List[MutationSite]) \
            -> List[SetOfMutationSiteSequences]:
        print("Finding mutation possibilities for mutations {}".format(",".join([repr(m) for m in mutations])))
        sorted_mutations = list(mutations)
        sorted_mutations.sort(key=lambda x: x.position)
        mutation_boundaries = {sorted_mutations[ix]: self.find_boundaries(ix, sorted_mutations)
                               for ix in range(len(sorted_mutations))}
        mutation_options = [self.find_combination_possibilities(
            m, sorted_mutations, mutation_boundaries)
            for m in sorted_mutations]

        print("Mutation options:")
        pprint(mutation_options)

        collections_covering_all_sites = self.combine(mutation_options)

        print("Found covering options:")
        for col in collections_covering_all_sites:
            print(repr(col))
        return collections_covering_all_sites

    def create_new_output(self, input_data: QCLMInput, solution: QCLMSolution) \
            -> QCLMOutput:
        """
        Parse QCLM solution and create output object which can be automatically translated to json.
        """

        sites_boundaries = compute_starts(solution)
        results: List[QCLMMutationOutput] = []
        parsed_mutations = input_data.parse_mutations(self.goi_offset)


        for site_set, scored_primers in solution.primers.items():
            site_sequence = sorted(site_set)
            mutated_dna_sequence_with_primer_sites = \
                DNASequenceForMutagenesis(self.sequence, site_sequence)

            # noinspection PyUnusedLocal
            primer: ScoredPrimer
            for primer in scored_primers:
                primer_sequence = primer.spec.get_sequence(mutated_dna_sequence_with_primer_sites)

                primer_mutations: List[MutationSite] = [
                    parsed_mutation for parsed_mutation in parsed_mutations
                    if parsed_mutation.get_start() in site_sequence
                ]

                sorted_primer_mutations = sorted(primer_mutations, key=lambda mut: mut.position)

                user_mutation_strings: List[str] = []

                for mutation, codon in zip(sorted_primer_mutations, primer.spec.codons):
                    coded_aminos = DegenerateTriplet.degenerate_codon_to_aminos(codon, self.usages.table.forward_table)
                    user_code = mutation.user_string_with_aminos(coded_aminos)
                    user_mutation_strings.append(user_code)

                # check if we have overlap with any primers.
                if check_for_overlap(sites_boundaries, site_set, primer.spec.offset,primer.spec.offset + primer.spec.length):
                    overlap_with_next = True
                    print("We have an overlap")
                else:
                    overlap_with_next = False

                results.append(QCLMMutationOutput(
                    result_found=True,
                    mutations=user_mutation_strings,
                    primers=[PrimerOutput(
                        sequence=primer_sequence,
                        start=primer.spec.offset,
                        length=primer.spec.length,
                        temperature=round(primer.tm, ndigits=2),
                        gc_content=round(GC(primer_sequence), ndigits=2),
                        degenerate_codons=list(primer.spec.codons),
                        overlap_with_following=overlap_with_next
                    )]
                ))

        return QCLMOutput(
            results=results,
            full_sequence=self.sequence,
            goi_offset=self.goi_offset,
            input_data=input_data,
        )

    # Find the sequence range for primers for the (index)-th mutation site.
    # The range begins after the end of the previous mutation codon (or start of the sequence)
    # and ends before the beginning of the next mutated codon (or end of the sequence).
    def find_boundaries(self, index: int, sorted_mutations: List[MutationSite]) -> Tuple[int, int]:
        min_start = 0

        if index > 0:
            min_start = sorted_mutations[index - 1].get_end()

        max_end = len(self.sequence)

        if index < len(sorted_mutations) - 1:
            max_end = sorted_mutations[index + 1].get_start()

        return min_start, max_end

    # The input is a set of subsets of sequences of mutation sites. The function finds all combinations of
    # the subsets such that they include all mutation sites and are mutually disjoint.
    def combine(self, options: List[List[QCLMMutationSiteSequence]]) \
            -> List[SetOfMutationSiteSequences]:
        result: List[SetOfMutationSiteSequences] = []
        self.combine_recursive(result, [], options, len(options))
        return result

    def combine_recursive(self,
                          result_acc: List[SetOfMutationSiteSequences],
                          subresult_acc: List[QCLMMutationSiteSequence],
                          options: List[List[QCLMMutationSiteSequence]],
                          mutations_count: int) -> None:
        if len(options) == 0:
            combo = SetOfMutationSiteSequences(subresult_acc)
            # If all mutation are present
            if combo.get_mutation_site_combo_count() == mutations_count:
                if combo not in result_acc:
                    result_acc.append(combo)
        else:
            for option in options[0]:
                new_subresult = list(subresult_acc)
                if self.can_be_added(new_subresult, option):
                    new_subresult.append(option)
                self.combine_recursive(result_acc, new_subresult, options[1:], mutations_count)

    def can_be_added(self, current_combo: List[QCLMMutationSiteSequence],
                     new_option: QCLMMutationSiteSequence) -> bool:
        for option in current_combo:
            if option.has_overlap(new_option):
                return False
        return True

    # Find combinations of mutation sites which can be covered by a common primer.
    # For each combination, find possible non-degenerate codons that achieve the desired mutations.
    # Params:
    # mutation: Description of one mutation site which should always be covered.
    # others: All mutations specified as the QCLM input.
    # mutation_boundaries: Sequence ranges around each mutation site, computed by the found_boundaries() function.
    def find_combination_possibilities(self, mutation: MutationSite,
                                       other: List[MutationSite],
                                       mutation_boundaries: Dict[MutationSite,
                                                                 Tuple[int, int]]) \
            -> List[QCLMMutationSiteSequence]:
        boundary_offset = self.config.max_primer_size - mutation.length - \
                          self.config.min_five_end_size - self.config.min_three_end_size
        min_position = mutation.get_start() - boundary_offset
        max_position = mutation.get_end() + boundary_offset

        other_possibilities = [m for m in other
                               if ((m.get_start() >= min_position) and
                                   (m.get_end() <= max_position))]
        possibilities_count = len(other_possibilities)
        possibilities_positions = sorted([p.position for p in other_possibilities])

        if possibilities_count == 0:
            raise Exception("Invalid QCLM configuration")

        combos = []

        for size in range(1, possibilities_count + 1):
            for combination in itertools.combinations(other_possibilities, size):
                if mutation in combination:
                    # Check whether the combination is continuous
                    combination_positions = sorted([p.position for p in combination])
                    if (possibilities_positions.index(combination_positions[-1])
                        - possibilities_positions.index(combination_positions[0])) \
                            > (len(combination) - 1):

                        continue

                    combos.append(QCLMMutationSiteSequence(
                        combination, self.usages, self.config.codon_usage_frequency_threshold,
                        mutation_boundaries))
        return combos

    def compute_hb_panalty(self, this_primer: PrimerSpec, partial_solution: QCLMSolution, current_site: frozenset,
                           base: DNASequenceForMutagenesis):
        """
        Computes penalty for hetero dimers. The hetero dimer temperature is computed with Primer3 library.
        Configuration of hetero dimer calculator is taken from temperature configuration for the whole reaction.
        The penalty is applied once the hetero dimer temperature crosses safe temperature.
        Hetero dimer temperature calculation requires sequence of 2 primers. It adds penalty for every pair of
        primers which are over safe temperature. Pairs are current primer vs all other primers from different site.
        :param this_primer: primer specification
        :param partial_solution: partial QCLM solution against which we will compute penalty
        :param current_site: site of current primer
        :param base: DNA for mutagenesis, needed for extracting primer sequences
        :return: float penalty value
        """
        safe_self_bind_limit = partial_solution.temperature - 2 * self.config.temp_range_size
        penalty = 0.0
        for other_site in partial_solution.primers.keys():
            if other_site != current_site:
                for other_primer in partial_solution.primers[other_site]:
                    hb_tm = self.__hetero_bind_calculator(this_primer.get_sequence(base),
                                                          other_primer[0].get_sequence(base))
                    if hb_tm > safe_self_bind_limit:
                        penalty += self.config.hairpin_temperature_weight * (hb_tm - safe_self_bind_limit)
        return penalty

    @staticmethod
    def pick_random_codons(aminos_for_sites: List[Set[AminoAcid]], usage_table, threshold: float) -> List[Set[Codon]]:
        """
        TODO: This is somewhat a hack. The easiest way to map the existing data to what we have
              is to just do a random selection of a codon for each amino. This way we won't
              have to store the codon information throughout the computation.
        """
        return [
            {QCLMSolver.pick_random_codon(amino, usage_table, threshold) for amino in site}
            for site in aminos_for_sites
        ]

    @staticmethod
    def pick_random_codon(amino: AminoAcid, table: CodonUsage, threshold: float):
        codons = table.back_table[amino]
        candidate_codons = list(
            filter(lambda codon: table.usages[codon] > threshold,
                   codons))

        return random.choice(candidate_codons)
