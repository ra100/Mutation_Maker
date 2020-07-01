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

import sys

from tests.test_support import sample_pas_config, sample_pas_sequences, sample_pas_mutations, generate_pas_input

sys.path.append('../')
import unittest

from mutation_maker.pas import PASSolver, extract_mutations
from mutation_maker.generate_oligos import OligoGenerator
from mutation_maker.degenerate_codon import DegenerateTriplet, CodonUsage
from mutation_maker.generate_oligos import mutations_on_fragments, parse_input_mutations


class TestOligos(unittest.TestCase):

    def generate_example(self):
        """ Function which generates example input """

        sys.setrecursionlimit(10000)
        index = 1
        pas_seq = sample_pas_sequences(index)
        config = sample_pas_config(index)
        workflow_input = generate_pas_input(index)
        solver = PASSolver(workflow_input.config,
                           workflow_input.is_dna_sequence,
                           workflow_input.is_mutations_as_codons)

        mutations = extract_mutations(workflow_input)

        is_mutations_as_codons = False
        _, goi_offset = pas_seq.get_full_sequence_with_offset()
        solver.find_solution(pas_seq, mutations)
        return pas_seq, config, is_mutations_as_codons, mutations, solver.best_solution.fragments, solver.best_solution, goi_offset


    def get_mutations_on_sites(self, mutations_list):
        """ Function which creates a dictionary of mutations on a particular mutation site """

        mutation_sites = list(set([item[0] for item in mutations_list]))
        mutations = {}
        for site in mutation_sites:
            list_mut = []
            for item in mutations_list:
                if item[0] == site:
                    list_mut.append(item[1])
            mutations[site] = list_mut
        return mutations


    def get_codon_on_position(self, position, dna, goi_offset, start):
        """ Function which returns a codon on a given position on a fragment. Indexes are recalculated to access string positions which start from 0. """

        dna_list = list(dna)
        codon = [dna_list[3*position + goi_offset - start - i] for i in range(3,0,-1)]
        return ''.join(codon)


     def test_mutations_on_sites(self):
        """ Assures that on every site, the generated mutations coincide with user's input """

        pas_seq, config, is_mutations_as_codons, mutations, fragments, solution, goi_offset = self.generate_example()
        mutations_list = parse_input_mutations(is_mutations_as_codons,mutations) # list of mutations is generated from the input
        sequence, goi_offset = pas_seq.get_full_sequence_with_offset() # full sequence, offset value
        generator = OligoGenerator(config, is_mutations_as_codons, config.organism)
        codon_usage = CodonUsage("e-coli")

        for i, frag in enumerate(solution.get_fragments()):
            oligos_set = generator(frag.get_sequence(
                solution.gene.sequence), mutations, frag, goi_offset, 250)
            mutations_on_fragment = mutations_on_fragments(frag.get_start(), frag.get_end(), mutations_list, goi_offset) # filtering out mutations on this fragment
            mutations_on_site = self.get_mutations_on_sites(mutations_on_fragment) # get list of mutations for every mutation site
            for site, mutations_i in mutations_on_site.items():
                wild_type_codon = self.get_codon_on_position(site, frag.get_sequence(sequence), goi_offset, frag.get_start()) # for every mutation site get wild codons on this position
                mutated_codons_on_site = [] # list of mutated codons on this site
                for oligo in oligos_set:
                    mutated_codons_on_site.append(self.get_codon_on_position(site, oligo.sequence, goi_offset, frag.get_start())) # get all codons on this site from all oligos together
                try:
                    mutated_codons_on_site.remove(wild_type_codon) # remove wild codons if present
                except:
                    pass
                created_mutations = [] # list of mutated amino acids on a particular mutation site
                for codon in set(mutated_codons_on_site):
                    temp_list = DegenerateTriplet.degenerate_codon_to_aminos(codon, codon_usage.table.forward_table) # codons to amino acids
                    for i in temp_list:
                        created_mutations.append(i)
                with self.subTest(i=site):
                    self.assertEqual(set(created_mutations), set(mutations_i))


    def test_concentrations(self):
        """ Assures that calculated concentrations sum up to 1 """

        pas_seq, config, is_mutations_as_codons, mutations, fragments, solution, goi_offset = self.generate_example()
        generator = OligoGenerator(config, is_mutations_as_codons, config.organism)
        for i, fragment in enumerate(fragments):
            oligos_group = generator(fragment.get_sequence(
                solution.gene.sequence), mutations, fragment, goi_offset, 250)
            ratios = [oligo.ratio for oligo in oligos_group]
            with self.subTest(i=i):
                self.assertEqual(int(sum(ratios)), 1)
