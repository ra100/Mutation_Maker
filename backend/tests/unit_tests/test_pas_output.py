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
import unittest
from pprint import pprint

from mutation_maker.pas import pas_solve
from mutation_maker.pas_output import get_codon_on_position
from tests.test_support import generate_pas_input


class TestBackTracking(unittest.TestCase):

    def test_pas_solve_json(self):
        """
        This test verifies that the output json contains all required data and fields in correct format.
        It checks for:
            - even number of fragments
            - mandatory fields on the fragment like start, end, overlap, length, temperatures, mutations, oligos...
            - for each fragment it checks that each oligo has right amount of mutations and red+blue indices
                            (number of reds+blues==number of mutation positions for fragment)
        :return:
        """
        pas_data = generate_pas_input(3)
        pas_data.config.organism='Acholeplasma palmae'
        pas_data.config.use_degeneracy_codon = False
        print("----------------------------- INPUT ----------------------------")
        pprint(pas_data.to_json())

        result = pas_solve(pas_data)
        print("----------------------------- OUTPUT ----------------------------")
        pprint(result)

        print("--------------------------------------------------------------------")
        print("----------------------------- Fragments ----------------------------")
        print("--------------------------------------------------------------------")

        mandatory_fields = ["fragment", "start", "end", "length", "overlap", "overlap_Tm", "overlap_GC", "overlap_length", "mutations", "oligos"]

        # check that we actually got some result
        self.assertIsNotNone(result["results"])

        # check that we have even number of fragments
        self.assertTrue(len(result["results"])%2==0)

        # iterate over all fragments,
        # first print the fragment data and check if we have all mandatory fields
        for i_fragment, fragment in enumerate(result["results"]):
            pprint(fragment)
            # check that it contains all required fields
            for field in mandatory_fields:
                self.assertIn(field, fragment.keys())

            # find wild type oligo index
            wt_mutations_indeces = []
            mutation_places = {}
            for mut_ind, mutation in enumerate(fragment["mutations"]):
                if mutation["wild_type"]:
                    wt_mutations_indeces.append(mut_ind)
                if mutation["position"] in mutation_places.keys():
                    mutation_places[mutation["position"]] += 1
                else:
                    mutation_places[mutation["position"]] = 1

            # check that we have all combinations of mutations present
            # np prob creates product of all values in list
            # in our dictionary we have how many mutation are there for single mutation position
            self.assertEqual(len(fragment["oligos"]), np.prod(list(mutation_places.values())),
                             "Fragment number {} has incorrect number of oligos!".format(i_fragment))

            wt_oligo = ""
            for i_oligo, oligo in enumerate(fragment["oligos"]):
                # check if numeber of reds and blues matches number of mutation places
                self.assertEqual(len(mutation_places.keys()), len(oligo["blues"]) + len(oligo["reds"]),
                                 "Oligo nr. {} at fragment id.{} has missing reds/blues".format(i_oligo, i_fragment))

                # store wild type sequence
                # wild type oligo is when there are no mutations
                #   or all mutations on the oligo are wild type mutations
                if oligo["mutations"] == [] or (len(wt_mutations_indeces) == len(oligo["mutations"]) and all(wt_ind in oligo["mutations"] for wt_ind in wt_mutations_indeces)):
                    wt_oligo = oligo["sequence"]


            # check if the wild type oligo matches the fragment sequence
            frag_seq = fragment["fragment"]
            self.assertEqual(frag_seq, wt_oligo)



    def test_get_codon_on_position(self):
        end_3 = "GGGGGGGGG"
        end_5 = "CCCCCCCCCCC"
        goi = "AAATTTTTTT"
        sequence = end_5 + goi + end_3
        position = 1
        start = 0
        goi_offset = len(end_5)
        codon =  get_codon_on_position(position, sequence, start, goi_offset)
        self.assertEqual(codon, "AAA")