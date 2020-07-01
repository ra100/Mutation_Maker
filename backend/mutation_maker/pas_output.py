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
import random
from typing import List

import numpy as np
from Bio.Seq import reverse_complement
from Bio.SeqUtils import GC

from mutation_maker.codon_usage_table import Organism
from mutation_maker.degenerate_codon import DegenerateTriplet, CodonUsage
from mutation_maker.generate_oligos import OligoGenerator, Codons
from mutation_maker.pas_solution import PASSolution, PASFragment
from mutation_maker.pas_types import PASSequences, PASResult, PASMutationSite, \
    PASMutationFormattedInput, PASMutationFormatted, PASOligoOutput, PASMutation, PASConfig
from mutation_maker.translation_scoring import TranslationScoring
from mutation_maker.usage_table import UsageTable


def format_mutations_input(mutation_sites_on_fragment: List, mutations_on_fragment: [PASMutationSite]) -> [PASMutationFormattedInput]:
    """ Gets a list of mutations on a gene to reflect them in the input part of json file """
    mutations_on_fragment_formatted = []
    for position in mutation_sites_on_fragment:
        list_mutations_on_sites = []
        for mut in mutations_on_fragment:
            mutations = [m.mutation for m in mut.mutations]
            frequency = float(mut.mutations[0].frequency)
            if position == mut.position:
                for mutat in mutations:
                    list_mutations_on_sites.append(mutat)
            else:
                pass
        mutations_on_position_formatted = PASMutationFormattedInput(mutants = list_mutations_on_sites, position = position, frequency = frequency)
        mutations_on_fragment_formatted.append(mutations_on_position_formatted)
    print(mutations_on_fragment_formatted)
    return mutations_on_fragment_formatted

def get_codon_on_position(position: int, oligo_sequence: str, oligo_start: int, goi_offset: int) -> str:
    """ Finds a codon on a given position in oligo (fragment)
    :param position: position of mutation as in the Front-end
    :param oligo_sequence:
    :param oligo_start: start position of oligo sequence in the full gene sequence (full gene sequence = 5'end + gene of interest + 3'end)
    :param goi_offset: offset of gene of interest -> lenght of 5'end sequence
    :return:

    """
    relative_pos = 3 * (position-1) + goi_offset - oligo_start
    return oligo_sequence[relative_pos: relative_pos + 3]

def combine_oligos_list(oligos_group, mutations_on_fragment_formatted, mutation_sites_on_fragment: List, goi_offset: int, pas_fragment: PASFragment) -> List:
    """ Combines a list of oligos with corresponding mutations as indeces from the list of mutations on fragment """
    list_oligos = []
    for oligo in oligos_group:
        mutations = []
        reds = []
        blues = []
        for site in mutation_sites_on_fragment:
            codon = get_codon_on_position(site, oligo.sequence, pas_fragment.get_start(), goi_offset)
            for index, mutation in enumerate(mutations_on_fragment_formatted):
                if(site == mutation.position and codon == mutation.mutated_codon):
                    mutations.append(index)
                    # compute mutation relative position on the fragment
                    mut_rel_position = 3 * (mutation.position - 1) + goi_offset - pas_fragment.get_start()
                    if mutation.wild_type and mut_rel_position not in blues:
                        blues.append(mut_rel_position)
                    elif mut_rel_position not in reds:
                        reds.append(mut_rel_position)
                else:
                    pass
        oligo_temp = PASOligoOutput(sequence=oligo.sequence, mix_ratio=oligo.ratio, mutations=mutations,
                                    reds=sorted(reds), blues=sorted(blues))
        list_oligos.append(oligo_temp)
    return list_oligos


def sort_func(elem):
    return elem.position

class Output:
    def __init__(self, config, is_dna_sequence, is_mutations_as_codons):
        self.config = config
        self.is_dna_sequence = is_dna_sequence
        self.is_mutations_as_codons = is_mutations_as_codons
        self.wild_dna_sequence = ""
        self.temp_calculator = config.temperature_config.create_calculator()
        self.gene = None
        # problem 1 specific
        # for future
        self.tm_distances = []
        self.avoided_motifs = config.avoided_motifs
        self.get_aa = DegenerateTriplet()

        if config.organism == 'e-coli':
            self.usage_table = UsageTable().ecoli_usage  # e_coli organism is chosen
            self.codonUsage = CodonUsage(config.organism)

        elif config.organism == 'yeast':
            self.usage_table = UsageTable().yeast_usage  # yeast organism is chosen
            self.codonUsage = CodonUsage(config.organism)

        else:
            org = Organism(config.organism)
            self.usage_table = org.codon_table  # other by name organism is chosen
            self.codonUsage = CodonUsage(config.organism)


    def combine_mutations_list(self, fragment: PASFragment, oligos_group, mutation_sites_on_fragment: List,
                               mutations_on_fragment: [PASMutationSite], sequence=None, goi_offset=None) -> List:
        """ Combines a list of mutations on a fragment with additional details needed for frontend """
        list_of_mutations = []
        # Create mutated oligos
        for mut_site in mutations_on_fragment:
            for mutt in mut_site.mutations:
                if self.is_mutations_as_codons:
                    mutation = self.get_aa.degenerate_codon_to_aminos(str(mutt.mutation),
                                                                      self.codonUsage.table.forward_table)[0]
                else:
                    mutation = str(mutt.mutation)
                position = mut_site.position
                frequency = float(mutt.frequency)
                wild_type_codon = Codons.get_wild_type_codon(position, sequence, fragment.get_start(),
                                                             goi_offset)
                wild_type_amino = self.get_aa.degenerate_codon_to_aminos(wild_type_codon,
                                                                         self.codonUsage.table.forward_table)[0]
                mutated_codon = ""

                # extreact mutated codons from the changed oligos
                for oligo in oligos_group:
                    codon_on_position = get_codon_on_position(position, oligo.sequence, fragment.get_start(), goi_offset)
                    amino_on_position = self.get_aa.degenerate_codon_to_aminos(codon_on_position,
                                                                               self.codonUsage.table.forward_table)
                    if mutation in amino_on_position:
                        mutated_codon = codon_on_position

                sublist_of_mutation = PASMutationFormatted(position=position, mutated_amino=mutation,
                                                           wild_type_amino=wild_type_amino, wild_type_codon=wild_type_codon,
                                                           mutated_codon=mutated_codon, frequency=frequency,
                                                           wild_type=False)
                list_of_mutations.append(sublist_of_mutation)

        # Adding wild type mutations
        for site in mutation_sites_on_fragment:
            frequencies = []
            for mut in mutations_on_fragment:
                if mut.position == site:
                    frequencies.append(mut.mutations[0].frequency)
            if np.sum(frequencies) < 1:
                frequency = 1 - np.sum(frequencies)
                position = site
                wild_type_codon = Codons.get_wild_type_codon(site, sequence, fragment.get_start(),
                                                             goi_offset)
                wild_type_amino = self.get_aa.degenerate_codon_to_aminos(wild_type_codon,
                                                                         self.codonUsage.table.forward_table)[0]
                mutated_codon = wild_type_codon
                mutated_amino = wild_type_amino
                sublist_of_mutation = PASMutationFormatted(position=position, mutated_amino=mutated_amino,
                                                           wild_type_amino=wild_type_amino,
                                                           wild_type_codon=wild_type_codon, mutated_codon=mutated_codon,
                                                           frequency=frequency, wild_type=True)
                list_of_mutations.append(sublist_of_mutation)

        list_of_mutations.sort(key=sort_func)
        return list_of_mutations


    def __call__(self, best_solution: PASSolution, mutations: [PASMutationSite], sequences: PASSequences) -> [PASResult]:
        """
        Returns list of results
        """

        # two shifted iterators to iterate over fragment and next fragment in the same time
        # in purpose to calculate overlaps
        frag_current_it = iter(best_solution.get_fragments())
        frag_lagged_it = iter(best_solution.get_fragments())
        next(frag_lagged_it)
        results = []
        goi_offset = sequences.get_goi_offset()
        # sorted list of all mutations sites
        mutation_sites = list(set([mut.position for mut in mutations]))
        mutation_sites.sort()

        # creating the output values for every fragment
        for i, frag_current in enumerate(frag_current_it):

            # getting oligos for a fragment, and fragment parameters
            generator = OligoGenerator(self.config, self.is_mutations_as_codons, self.config.organism)
            oligos_group = generator(frag_current.get_sequence(
                best_solution.gene.sequence), mutations, frag_current, goi_offset, 250)

            fragment_sequence = frag_current.get_sequence(best_solution.gene.sequence)

            # getting list of mutations on a fragment a prepare it in a desired json format
            mutation_sites_on_fragment = [site for site in mutation_sites if ((goi_offset + (site - 1) * 3) >= frag_current.get_start() and (goi_offset + (site - 1) * 3 + 2) <= frag_current.get_end())]
            mutations_on_fragment = [mut for mut in mutations if mut.position in mutation_sites_on_fragment]
            mutations_on_fragment_formatted = self.combine_mutations_list(frag_current, oligos_group, mutation_sites_on_fragment, mutations_on_fragment, fragment_sequence, goi_offset)
            list_oligos = combine_oligos_list(oligos_group, mutations_on_fragment_formatted, mutation_sites_on_fragment, goi_offset, frag_current)
            # getting overlap and its parameters
            try:
                frag_next = next(frag_lagged_it)
                overlap = frag_current.get_overlap_seq(frag_next, sequences.get_full_sequence())
                overlap_Tm = best_solution.temp_calculator(overlap)
                overlap_GC = GC(overlap)
                overlap_length = len(overlap)
            except: # when lagged iterator returns None set all overlaps info to None
                overlap = overlap_Tm = overlap_GC = overlap_length = None

            # every fragment at even position should be reverse complement of the original sub-sequence
            # doing it here because previous code requires fragment in original forward direction
            if i % 2 == 1:
                for oligo in list_oligos:
                    oligo.make_reverse_complement()
                fragment_sequence = reverse_complement(fragment_sequence)
            # combining the results together
            result_oligo = PASResult(fragment=fragment_sequence, start=frag_current.get_start(), end=frag_current.get_end(), length = frag_current.get_length(), overlap=overlap,
                                     overlap_Tm=overlap_Tm, overlap_GC=overlap_GC, overlap_length = overlap_length, mutations=mutations_on_fragment_formatted, oligos=list_oligos)
            results.append(result_oligo)

        # preparing input data for final json
        # list of all mutation on a gene in a desired json format

        # returning output json
        return results