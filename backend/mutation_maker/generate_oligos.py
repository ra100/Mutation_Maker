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

import pprint

from mutation_maker.codon_usage_table import Organism
from mutation_maker.degenerate_codon import CodonUsage
from mutation_maker.usage_table import UsageTable
from mutation_maker.translation_scoring import TranslationScoring
from mutation_maker.degenerate_codon import DegenerateTriplet
from mutation_maker.motifs import Motifs
from Bio.Data import CodonTable
from typing import List, Dict, Tuple
import numpy as np
from operator import mul, getitem
from functools import reduce
from itertools import product, starmap
from mutation_maker.pas_types import PASConfig, PASOligo, PASMutationSite
from mutation_maker.pas_degeneracy_recursion import Degeneracy
from mutation_maker.pas_exceptions import PASNoSolutionException


def parse_input_config(config: PASConfig) -> Tuple[float, List[float], bool]:
    """ This function parses the PAS input"""

    threshold_usage = config.codon_usage_frequency_threshold
    gc_range = [config.min_gc_content, config.max_gc_content]
    use_degeneracy = config.use_degeneracy_codon
    return threshold_usage, gc_range, use_degeneracy


def parse_input_mutations(is_mutations_as_codons: bool, mutations: List[PASMutationSite]) -> List[Tuple]:
    """ This function parses mutations from PAS input"""

    mutations_list = []
    for mutation in mutations:
        for mut in mutation.mutations:
            if is_mutations_as_codons:
                temp = (mutation.position, str(mut)[:3], float(str(mut)[3:]))
            else:
                temp = (mutation.position, str(mut)[0], float(str(mut)[1:]))
            mutations_list.append(temp)
    return mutations_list


def mutations_on_fragments(start: int, end: int, mutations: List[Tuple], goi_offset: int) -> List[Tuple]:
    """ This function filters out mutations for a given fragment"""

    mutations_filtered = [mut for mut in mutations if
                          (((goi_offset + mut[0] * 3 - 2) >= start) and ((goi_offset + mut[0] * 3) <= end))]
    return mutations_filtered


def cartesian_dictionary(*args, fold=mul) -> Dict:
    """ Cartesian product of an arbitrary number of dictionaries. """

    return {ks: reduce(fold, starmap(getitem, zip(args, ks)))
            for ks in product(*args)}


def check_equal_probabilities(aminos: List[str], aminos_with_probabilities: Dict[str, float]) -> bool:
    """ Checks whether amino acids generated from the same degenerate codon have equal probability. """

    list_probabilities = [aminos_with_probabilities[amino] for amino in aminos]
    return len(set(list_probabilities)) <= 1


def modify_dictionary_probabilities(aminos_with_probabilities: Dict[str, float], list_of_aminos: List[str]):
    """ Modifies probabilities in the aminos_with_probabilities after the degeneracy was solved. """

    new_name = list_of_aminos[0]
    aminos_with_probabilities[new_name] = len(list_of_aminos) * float(aminos_with_probabilities[list_of_aminos[0]])
    for amino in list_of_aminos[1:]:
        del aminos_with_probabilities[amino]


def modify_dictionary_codons(aminos_with_codons: Dict[str, str], list_of_aminos: List[str], codon: str):
    """ Modifies codons in the aminos_with_codons after the degeneracy problem was solved. """

    for amino in list_of_aminos:
        aminos_with_codons[amino] = codon


def modify_lists(set_cover: List[str], aminos_with_probabilities: Dict[str, float], aminos_with_codons: Dict[str, str],
                 get_aa, forward_table):
    """ Modifies aminos_with_codons and aminos_with_probabilities with accordance to set cover problem solution. """

    for codon in set_cover:
        list_of_aminos = get_aa.degenerate_codon_to_aminos(codon, forward_table)
        if len(list_of_aminos) > 1 and check_equal_probabilities(list_of_aminos, aminos_with_probabilities):
            modify_dictionary_probabilities(aminos_with_probabilities, list_of_aminos)
            modify_dictionary_codons(aminos_with_codons, list_of_aminos, codon)
        else:
            pass


def find_candidates_for_set_cover(aminos_with_probabilities) -> List:
    """ Finds a combination of aminos (codons) for degeneracy check. They should share same probability """
    probabilities = set([value for key, value in aminos_with_probabilities.items()])
    list_of_candidates = []
    for probability in probabilities:
        temp = [amino for amino, prob in aminos_with_probabilities.items() if prob == probability]
        if len(temp) >= 2:
            list_of_candidates.append(temp)
    return list_of_candidates


def generate_oligos_from_combinations(mutations_combinations_with_probabilitites: Dict[str, float],
                                      chosen_codons_on_sites: List, dna: str, mutations_sites: List, start,
                                      goi_offset) -> List[PASOligo]:
    """ From combination of mutations generates a dna sequence with respective codons on mutation sites for all
    combinations. """

    oligos = []
    for combination in mutations_combinations_with_probabilitites:
        concentration = mutations_combinations_with_probabilitites[combination]
        for position, mutation in enumerate(combination):
            codon = chosen_codons_on_sites[position][mutation]
            dna = Codons.replace_codon(dna, mutations_sites[position], codon, start, goi_offset)
        oligos.append(PASOligo(sequence=dna, ratio=concentration))
    return oligos


class Codons(object):
    """ Function class which contains different methods to work with codons  """

    @staticmethod
    def solve_set_cover(codons, degeneracy) -> List:
        """ Solves a set cover problem for a list of codons and returns a list of degenerate ones if possible. """
        return [codon for codon, aminos in degeneracy(codons).items()]

    @staticmethod
    def return_random_codon(codonUsage: CodonUsage, threshold_usage: float, usage_table: Dict[str, float],
                            amino_acid: str) -> str:
        """ Returns random codon for a given amino acid based on codon's usage frequency. """

        codons = codonUsage.get_all_possible_triplets_for_amino(amino_acid, threshold_usage)
        codons_with_frequency = {str(d): usage_table[str(d)] for d in codons}
        non_normalized_probabilities = list(codons_with_frequency.values())
        renormalized_probabilities = [freq/sum(non_normalized_probabilities) for freq in non_normalized_probabilities]
        return np.random.choice(list(codons_with_frequency.keys()), 1, replace=True, p=renormalized_probabilities)[0]

    @staticmethod
    def replace_codon(dna: str, position: int, codon: str, start: int, goi_offset: int) -> str:
        """ Replaces a given codon in dna sequence by another codon. """
        # TODO test this
        position = 3 * (position - 1) + goi_offset - start
        return dna[:position] + codon + dna[position + 3:]

    @staticmethod
    def get_wild_type_codon(position: int, sequence: str, start: int,  goi_offset: int) -> str:
        """ Finds a wildtype codon on a given position """
        # TODO tests this
        position = 3 * (position - 1) + goi_offset - start
        return sequence[position:position + 3]


class Mutations(object):
    """ Function object which contains methods to work with mutations on sites """

    @staticmethod
    def generate_mutation_combinations(mutations_with_probabilities: List) -> Dict:
        """ Generates different combinations of mutations for a given mutation site. It also returns concentration
        for a given combination. """

        return cartesian_dictionary(*mutations_with_probabilities)

    @staticmethod
    def list_of_mutation_sites(mutations_list: List[tuple]) -> List[int]:
        """ Returns a list of mutation sites.  """

        return list(set([item[0] for item in mutations_list]))


class OligoGenerator(object):
    """ Function object for oligos generation for the fragment. """
    threshold_usage: float  # threshold for the codon frequency
    gc_range: List[int]  # desired GC content range
    organism: str  # organism chosen to use as codon frequency reference
    dna: str  # initial dna fragment
    mutations: List  # list of mutations, including mutation sites and probabilities
    aminos_with_probabilities: Dict  # dictionary of mutations with their probabilities grouped by mutation sites
    aminos_with_codons: Dict  # dictionary of mutations with corresponding codons grouped by mutation sites

    def __init__(self, config: PASConfig, is_mutations_as_codons, organism='e-coli'):
        """ Initializing a class instance """
        self.dna_by_name = CodonTable.unambiguous_dna_by_name["Standard"]
        self.threshold_usage, self.gc_range, self.use_degeneracy = parse_input_config(config)
        self.get_aa = DegenerateTriplet()  # this instance is needed to later get the list of amino acids generated
        # by a given codon
        if organism == 'e-coli':
            self.usage_table = UsageTable().ecoli_usage  # e_coli organism is chosen
            self.fw_table = CodonTable.unambiguous_dna_by_name["Standard"].forward_table
            self.codonUsage = CodonUsage(organism)
            self.scoring = TranslationScoring(self.threshold_usage, self.gc_range, self.codonUsage,
                                              self.usage_table)  # initializing scoring instance
        elif organism == 'yeast':
            self.usage_table = UsageTable().yeast_usage  # yeast organism is chosen
            self.codonUsage = CodonUsage(organism)
            self.fw_table = CodonTable.unambiguous_dna_by_name["Standard"].forward_table
            self.scoring = TranslationScoring(self.threshold_usage, self.gc_range, self.codonUsage,
                                              self.usage_table)  # initializing scoring instance

        else:
            org = Organism(organism)
            self.usage_table = org.codon_table  # other by name organism is chosen
            self.codonUsage = CodonUsage(organism)
            self.fw_table = org.translation_table.forward_table
            self.scoring = TranslationScoring(self.threshold_usage, self.gc_range, self.codonUsage,
                                              self.usage_table)

        self.get_motifs = Motifs()
        self.avoided_motifs = self.get_motifs(config.avoided_motifs)  # getting list of avoided motifs
        self.degeneracy = Degeneracy(config, organism)
        self.is_mutations_as_codons = is_mutations_as_codons

    def generate_solution(self, dna: str, mutations_list: List[tuple], start, goi_offset) -> List[PASOligo]:
        """ Main logic of solution's generation is implemented here:

        1. For a given mutation site generate random codons 2. For these codons solve set cover problem 3. Check if
        aminos from same degenerate codon share same probability 3.1 If yes: 4. In the list of aminos with their
        probabilities keep only one amino from the ones sharing probabilities, and multiply it's probability to the
        number of covered aminos 3.2 If no: Leave codons from p.1 5. Proceed to next mutation site and repeat pp 1. -
        4. 6. Generate combinations with concetrations for different sites with the help of cartesian multiplication
        7. For every combination replace aminos on mutation sites with selected previousely codons (degenerete or
        normal ones)
        """

        mutations_sites = Mutations.list_of_mutation_sites(
            mutations_list)  # get a list of mutation sites for a given fragment
        mutations_on_site_with_prob = []
        chosen_codons_on_sites = []
        for site in mutations_sites:
            aminos_with_codons = {}
            aminos_with_probabilities = {}
            for item in mutations_list:
                if item[0] == site:
                    if self.is_mutations_as_codons:
                        am = self.get_aa.degenerate_codon_to_aminos(item[1], self.fw_table)[
                            0]  # getting amino for a chosen by user codon
                        aminos_with_codons[am] = item[
                            1]  # generating a dictionary storing aminos with corresponding randomly chosen codons
                        # grouped by mutation sites
                        aminos_with_probabilities[am] = item[
                            2]  # generating dictionary storing aminos with corresponding probabilities grouped by
                        # mutation sites
                    else:
                        aminos_with_codons[item[1]] = Codons.return_random_codon(self.codonUsage, self.threshold_usage,
                                                                                 self.usage_table, item[
                                                                                     1])  # generating a dictionary
                        # storing aminos with corresponding randomly chosen codons grouped by mutation sites
                        aminos_with_probabilities[item[1]] = item[
                            2]  # generating dictionary storing aminos with corresponding probabilities grouped by
                        # mutation sites

            sum_of_probabilities = sum(
                aminos_with_probabilities.values())  # checking if we need to take into account wild type codon
            if sum_of_probabilities != 1:
                wild_type_prob = 1 - sum_of_probabilities
                wild_type_codon = Codons.get_wild_type_codon(site, dna, start, goi_offset)
                wild_type_amino = self.get_aa.degenerate_codon_to_aminos(wild_type_codon,
                                                                         self.fw_table)[0]
                aminos_with_codons[
                    wild_type_amino] = wild_type_codon  # creating wild type record with corresponding codon
                aminos_with_probabilities[
                    wild_type_amino] = wild_type_prob  # creating wild type record with corresponding probability

            if self.use_degeneracy:
                # pprint.pprint(aminos_with_probabilities)
                candidates_for_set_cover = find_candidates_for_set_cover(aminos_with_probabilities)
                for candidate in candidates_for_set_cover:
                    set_cover = Codons.solve_set_cover(candidate, self.degeneracy)
                    if len(aminos_with_codons) > len(set_cover):
                        modify_lists(set_cover, aminos_with_probabilities, aminos_with_codons,
                                     self.get_aa, self.fw_table)  # if the degeneracy problem is solved successfully - modify
                        # aminos_with_codons and aminos_with_probabilities dictionaries to reflect the result (
                        # recalculating the probabilities as well)

            mutations_on_site_with_prob.append(
                aminos_with_probabilities)  # generate the final list of mutations on sites
            chosen_codons_on_sites.append(aminos_with_codons)  # generate the final list of corresponding codons

        mutations_combinations_with_probabilitites = Mutations.generate_mutation_combinations(
            mutations_on_site_with_prob)  # find all combinations of mutations for a given fragment and calculate the
        # concentrations
        return generate_oligos_from_combinations(mutations_combinations_with_probabilitites, chosen_codons_on_sites,
                                                 dna, mutations_sites, start,
                                                 goi_offset)  # generate oligos from the combinations

    def __call__(self, dna: str, mutations, frag, goi_offset, niter: int) -> List[PASOligo]:
        """ Generates niter number of solutions and chooses the one with minimal number of oligos. """
        start = frag.get_start()
        end = frag.get_end()
        mutations_list = parse_input_mutations(self.is_mutations_as_codons, mutations)
        mutations_list = mutations_on_fragments(start, end, mutations_list, goi_offset)
        if len(mutations_list) != 0:
            solutions = []
            i = 0
            while len(solutions) < 100 and i < niter:
                i += 1
                solution = self.generate_solution(dna, mutations_list, start, goi_offset)
                motifs_in_dna = [motif for motif in self.avoided_motifs if motif.search(dna)]  # list of avoided motifs which is contained in generated dna sequence
                if len(motifs_in_dna) == 0:
                    solutions.append(solution)

                if len(solutions) < 100 and i == niter:
                    raise PASNoSolutionException('Not possible to avoid specified combination of motifs!')

            solution = min(solutions, key=len)  # choose the solution with minimal number of oligos
            solution: List[PASOligo]
            return solution
        else:
            return [PASOligo(sequence=dna, ratio=1)]
