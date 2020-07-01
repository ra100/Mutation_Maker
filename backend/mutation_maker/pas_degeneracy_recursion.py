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

import numpy as np
from mutation_maker.degenerate_codon import CodonUsage
from mutation_maker.usage_table import UsageTable
from mutation_maker.translation_scoring import TranslationScoring
from mutation_maker.degenerate_codon import DegenerateTriplet
from Bio.Data import CodonTable
from mutation_maker.pas_types import PASConfig
from typing import List, Dict, Any, Tuple
from mutation_maker.degeneracy_lookup import lookup
import itertools


def parse_input_config(config: PASConfig) -> Tuple[Any, list]:
    """ This function parses the PAS input"""

    threshold_usage = config.codon_usage_frequency_threshold
    gc_range = [config.min_gc_content, config.max_gc_content]
    return threshold_usage, gc_range


def find_best_union(aminos: List[str], codonUsage: CodonUsage, threshold_usage: float, usageTable: UsageTable) -> Dict:
    """ Calculation cycle with a given combination of oligos is performed here:
        1. 500 random combinations of codons are created
        2. For every combination, union of these codons is found
        3. Then we check for solutions with minimal number of amino acids produced by a given union of codons
        4. We find all unions with minimal number of amino acids and we choose the one with max product of usage frequencies"""
    solutions = {}
    for i in range(50):
        random_codons = [Codons.return_random_codon(codonUsage, threshold_usage, usageTable, amino) for amino in aminos]
        union = Codons.get_union(random_codons)
        aminos_generated = Codons.degenerate_codon_to_aminos(union, codonUsage)
        solutions[union] = aminos_generated

    solution = min(solutions.items(), key=lambda x: len(x[1]))

    appropriate_solutions = {}

    for cod, sol in solutions.items():
        if len(sol) == len(solution[1]):
            appropriate_solutions[cod] = Codons.get_degenerate_frequency(cod, usageTable)

    final_solution = max(appropriate_solutions, key=appropriate_solutions.get)
    solution_formatted = {final_solution: solutions[final_solution]}
    return solution_formatted


def diff(li1: List, li2: List) -> list:
    return list(set(li1) - set(li2))


def solve_degeneracy(max_combination_size, aminos: List[str], codonUsage: CodonUsage, threshold_usage: float,
                     usageTable: UsageTable) -> Dict:
    """ Main algorithm is implemented here:
    1. Choose combination of amino acids to solve the degeneracy problem (
    first choice - all amino acids, last choice - all pairs, and intermediate combinations)
    2. For every combination
    of amino acids run cycle of getting the solutions (500 random solutions)
    3. Check if the generated list of amino
    acids, together with amino acids out of current combination (on which we also run solve_degeneracy() function),
    gives the initial list of amino acids, meaning that set cover problem was solved

     Return value:
     For a given list of amino acids returns a dictionary with degenerate codons as keys and corresponding amino
     acids as values

     :param codonUsage: refers to organism's usage table instance
     :param usageTable: object needed to get usage frequencies tables
     :param threshold_usage: a threshold of usage frequencies to filter out rare codons
     :param codonUsage: object from degenerete_codon.py which is needed to do different operations on codons
     :param aminos: list of amino acids to find solution for
     :param max_combination_size: defines which combinations should be checked to not check same combinations multiple
      times"""
    for i in range(max_combination_size, 0, -1):
        if i < 2:
            solution = {}
            for amino in aminos:
                solution[Codons.return_random_codon(codonUsage, threshold_usage, usageTable, amino)] = [amino]
            return solution
        else:
            aminos_new = list(itertools.combinations(aminos, i))
            for combination in aminos_new:
                aminos_new_new = [amino for amino in combination]
                solution = find_best_union(aminos_new_new, codonUsage, threshold_usage, usageTable)
                difference = diff(aminos, aminos_new_new)

                if len(difference) != 0:
                    solution.update(solve_degeneracy(i, difference, codonUsage, threshold_usage, usageTable))

                final_aminos = []
                for codon, amins in solution.items():
                    for amino in amins:
                        final_aminos.append(amino)

                if set(final_aminos) == set(aminos):
                    return solution
                else:
                    pass


class Codons(object):

    @staticmethod
    def degenerate_codon_to_aminos(codon: str, codonUsage) -> List:
        """
        Converts a degenerate codon string to a list of aminos generated by that codon.
        """
        assert len(codon) == 3
        non_degenerate_codons = DegenerateTriplet.get_all_non_degenerate_codons(codon)
        coded_aminos = []
        for c in non_degenerate_codons:
            try:
                coded_aminos.append(codonUsage.table.forward_table[c])
            except:
                pass

        return list(set(coded_aminos))

    @staticmethod
    def return_random_codon(codonUsage: CodonUsage, threshold_usage: float, usage_table: UsageTable,
                            amino_acid: str) -> str:
        """ Returns random codon for a given amino acid based on codon's usage frequency. """

        codons = codonUsage.get_all_possible_triplets_for_amino(amino_acid, threshold_usage)
        codons_with_frequency = {str(d): usage_table[str(d)] for d in codons}
        non_normalized_probabilities = list(codons_with_frequency.values())
        renormalized_probabilities = [freq/sum(non_normalized_probabilities) for freq in non_normalized_probabilities]
        return np.random.choice(list(codons_with_frequency.keys()), 1, replace=True, p=renormalized_probabilities)[0]

    @staticmethod
    def get_union(random_codons):
        """ Takes a list of codons and returns their union using degenerate nucleotides """
        codon = []
        for i in range(0, 3):
            nucleotides = [codon[i] for codon in random_codons]
            union = lookup[nucleotides[0]]
            for j in range(1, len(nucleotides)):
                union = union.union(lookup[nucleotides[j]])
            codon.append(str(union))
        return "".join(codon)

    @staticmethod
    def get_degenerate_frequency(codon, usage_table):
        codons = []
        for nuc in codon:
            codons.append(list(lookup[nuc].bases))
        combinations = []
        for element in itertools.product(*codons):
            combinations.append(''.join(list(element)))
        frequencies = []
        for combination in combinations:
            frequencies.append(usage_table[combination])
        product = np.product(frequencies)
        return product


class Degeneracy(object):

    def __init__(self, config: PASConfig, organism_name='e-coli'):
        self.threshold_usage, self.gc_range = parse_input_config(config)
        self.codonUsage = CodonUsage(organism_name)  # codon usage table for e-coli is initialized
        self.usage_table = self.codonUsage.usages  # e-coli organism is chosen
        self.dna_by_name = self.codonUsage.table

        self.scoring = TranslationScoring(self.threshold_usage, self.gc_range, self.codonUsage,
                                              self.usage_table)  # initializing scoring instance
            # self.codonUsage = CodonUsage(CodonTable.unambiguous_dna_by_name["Standard"], UsageTable().ecoli_usage)

    def __call__(self, aminos: List) -> Dict:
        return solve_degeneracy(len(aminos), aminos, self.codonUsage, self.threshold_usage, self.usage_table)
