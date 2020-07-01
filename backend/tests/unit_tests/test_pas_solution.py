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

from mutation_maker.basic_types import DNASequenceForMutagenesis
from mutation_maker.pas import compute_tm_distances, extract_mutations
from mutation_maker.temperature_calculator import TemperatureConfig
from tests.test_support import generate_pas_input

fragments = ["PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING",
             "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING",
             "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING",
             "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"]

in_goi = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"



class TestPASSolver(unittest.TestCase):
    def test_create_proto_segments(self):
        pass


    def test_compute_tm_distances(self):
        workflow_input = generate_pas_input()
        mutations = extract_mutations(workflow_input)
        sequence, offset = workflow_input.sequences.get_full_sequence_with_offset()
        gene = DNASequenceForMutagenesis(sequence, [m.position*3+offset for m in mutations])
        temp_calculator = TemperatureConfig().create_calculator()
        distances = compute_tm_distances(gene, temp_calculator)

        self.assertEqual(len(distances),len(mutations)-1,"There should be one distances less than there are mutations")

        for dist in distances:
            self.assertIsNotNone(dist)

    # @mock.patch('mutation_maker.pas.PASSolver', new_callable=mock.PropertyMock)
    # @mock.patch('mutation_maker.pas.PASSolver.gene', new_callable=mock.PropertyMock)
    # def test_create_proto_fragments_between(self, mock_gene=None, mock_config=None):
    #     """
    #     Test verifies that "temperature" distance between proto-fragments is
    #     greater that overlap temperature.
    #     :return:
    #     """
    #     # TODO mock this!
        # mock_config.return_value = sample_pas_config()
        # mock_gene.return_value = sample_pas_gene()
        #
        # temp_calculator = TemperatureConfig().create_calculator()
        # solver = PASSolver(sample_pas_config(), True, True)
        #
        # pas_seq = sample_pas_sequences()
        # mutations = sample_pas_mutations()
        # seq, offset = pas_seq.get_full_sequence_with_offset()
        # offsets = [m.position * 3 + offset for m in mutations]
        #
        # for t_min in range(40, 65):
        #     # need to call it to initialize some variables
        #     prot_frags = solver.generate_proto_fragments(t_min, offsets)
        #     if prot_frags:
        #         # we want to make sure, that temperature difference between proto-fragmetns is higher than overlap temperature
        #         for i,current in enumerate(prot_frags[:-1]):
        #             inbetween_seq = seq[current.get_last_mut_site_position():prot_frags[i+1].get_first_mut_site_position()]
        #             temp = temp_calculator(inbetween_seq)
        #             self.assertGreater(temp, t_min, "Temperature should be higher")

    # TODO mock this!
    # def test_create_proto_fragments_inside(self):
    #     """
    #     Test verifies that "temperature" distance inside proto-fragments is
    #     less than overlap temperature.
    #     :return:
    #     """
    #     temp_calculator = TemperatureConfig().create_calculator()
    #     solver = PASSolver(sample_pas_config(), True, True)
    #     pas_seq = sample_pas_sequences()
    #     mutations = sample_pas_mutations()
    #     seq, offset = pas_seq.get_full_sequence_with_offset()
    #     offsets = [m.position * 3 + offset for m in mutations]
    #     # need to call it to initialize some variables
    #     solver.solve(pas_seq, mutations)
    #
    #     for t_min in range(10, 80):
    #         prot_frags = solver.generate_proto_fragments(t_min, offsets)
    #         if prot_frags:
    #             # we want to make sure, that temperature difference between proto-fragmetns is higher than overlap temperature
    #             for proto_frag in prot_frags:
    #                 sites = proto_frag.get_sites()
    #                 for i, site in enumerate(sites[:-1]):
    #                     tmp_seq = seq[site.position:sites[i+1].position]
    #                     temp = temp_calculator(tmp_seq)
    #                     self.assertLess(temp, t_min, "Temperature should be higher")
