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

from mutation_maker.pas import PASSolver, extract_mutations
from tests.test_support import *


class TestBackTracking(unittest.TestCase):

    def test_finding_solution_1(self):
        """
        find_solution(proto_frags: [PASProtoFragment], T_min: int, offsets: [Offset],
                sites: [MutationSite], gene: DNASequenceForMutagenesis, config: PASConfig,
                  temp_solution: PASSolution, current_end: int) -> PASSolution:

        :return:
        """
        index = 1
        workflow_input = generate_pas_input(index)
        solver = PASSolver(workflow_input.config,
                           workflow_input.is_dna_sequence,
                           workflow_input.is_mutations_as_codons)

        mutations = extract_mutations(workflow_input)

        sequence, offset = sample_pas_sequences(index).get_full_sequence_with_offset()
        offsets = [3*(m.position-1)+offset for m in mutations]

        solver.find_solution(workflow_input.sequences, mutations)

        self.assertIsNotNone(solver.best_solution, "We did not find any solution")
        found_sites = set()

        for frag in solver.best_solution.get_fragments():
            print(frag)
            if frag.sites:
                found_sites.update(frag.sites)
        for offset in offsets:
            print(offset)
        self.assertEqual(solver.best_solution.get_length(), len(sequence))
        self.assertEqual(len(found_sites), len(mutations), "Not all mutation sites found")


    def test_finding_solution_2(self):
        """
        find_solution(proto_frags: [PASProtoFragment], T_min: int, offsets: [Offset],
                sites: [MutationSite], gene: DNASequenceForMutagenesis, config: PASConfig,
                  temp_solution: PASSolution, current_end: int) -> PASSolution:

        :return:
        """
        index = 2
        workflow_input = generate_pas_input(index)
        solver = PASSolver(workflow_input.config,
                           workflow_input.is_dna_sequence,
                           workflow_input.is_mutations_as_codons)

        mutations = extract_mutations(workflow_input)

        sequence, offset = sample_pas_sequences(index).get_full_sequence_with_offset()
        offsets = [3*m.position+offset for m in mutations]
        solver.find_solution(workflow_input.sequences, mutations)

        self.assertIsNotNone(solver.best_solution, "We did not find any solution")
        found_sites = set()

        for frag in solver.best_solution.get_fragments():
            print(frag)
            if frag.sites:
                found_sites.update(frag.sites)
        for offset in offsets:
            print(offset)
        self.assertEqual(solver.best_solution.get_length(), len(sequence))
        self.assertEqual(len(found_sites), len(mutations), "Not all mutation sites found")


    def test_finding_solution_3(self):
        """
        find_solution(proto_frags: [PASProtoFragment], T_min: int, offsets: [Offset],
                sites: [MutationSite], gene: DNASequenceForMutagenesis, config: PASConfig,
                  temp_solution: PASSolution, current_end: int) -> PASSolution:

        :return:
        """
        index = 3
        workflow_input = generate_pas_input(index)
        solver = PASSolver(workflow_input.config,
                           workflow_input.is_dna_sequence,
                           workflow_input.is_mutations_as_codons)

        mutations = extract_mutations(workflow_input)
        solver.find_solution(workflow_input.sequences, mutations)

        sequence, offset = sample_pas_sequences(index).get_full_sequence_with_offset()
        offsets = [3*m.position+offset - 3 for m in mutations]
        calc = solver.best_solution.config.temperature_config.create_calculator()

        self.assertIsNotNone(solver.best_solution, "We did not find any solution")
        found_sites = []
        for i, frag in enumerate(solver.best_solution.get_fragments()):
            print(frag, frag.get_sequence(solver.best_solution.gene.sequence))
            # collect all fragment mutations
            if frag.sites:
                found_sites.extend(frag.sites)
            if i < len(solver.best_solution.get_fragments()) - 1:
                temp = calc(solver.best_solution.gene.sequence[solver.best_solution.fragments[i+1].get_start():frag.get_end()])
                print("Overlap length {} with temperature {}".format(frag.get_end() - solver.best_solution.fragments[i + 1].get_start() + 1, temp))

        for offset in offsets:
            print(offset)
        self.assertEqual(solver.best_solution.get_length(), len(sequence))
        self.assertEqual(len(found_sites), len(mutations), "Not all mutation sites found")


    def test_finding_solution_4(self):
        """
        Amino sequence
        :return:
        """
        index = 5
        workflow_input = generate_pas_input(index)
        solver = PASSolver(workflow_input.config,
                           workflow_input.is_dna_sequence,
                           workflow_input.is_mutations_as_codons)

        mutations = extract_mutations(workflow_input)
        solver.find_solution(workflow_input.sequences, mutations)

        sequence = solver.gene.sequence
        offset = sample_pas_sequences(index).get_goi_offset()
        offsets = [3*m.position+offset - 3 for m in mutations]
        calc = solver.best_solution.config.temperature_config.create_calculator()

        self.assertIsNotNone(solver.best_solution, "We did not find any solution")
        found_sites = []
        for i, frag in enumerate(solver.best_solution.get_fragments()):
            print(frag, frag.get_sequence(solver.best_solution.gene.sequence))
            # collect all fragment mutations
            if frag.sites:
                found_sites.extend(frag.sites)
            if i < len(solver.best_solution.get_fragments()) - 1:
                temp = calc(solver.best_solution.gene.sequence[solver.best_solution.fragments[i+1].get_start():frag.get_end()])
                print("Overlap length {} with temperature {}".format(frag.get_end()-solver.best_solution.fragments[i+1].get_start() + 1, temp))

        for offset in offsets:
            print(offset)
        self.assertEqual(solver.best_solution.get_length(), len(sequence))
        self.assertEqual(len(found_sites), len(mutations), "Not all mutation sites found")
