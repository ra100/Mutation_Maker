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

from mutation_maker.basic_types import AminoAcid
from mutation_maker.degenerate_codon import CodonUsage
from mutation_maker.msdm import MSDMSolver, msdm_solve
from mutation_maker.msdm_types import MSDMInput
from tests.test_support import sample_msdm_sequences, random_msdm_mutations, sample_msdm_config, print_stats_msdm


class MsdmTest(unittest.TestCase):
    e_coli = CodonUsage("e-coli")

    # e. coli has two codons for "F", "TTT" with 0.51 and "TTC" with 0.49
    def test_pick_random_codon(self):
        for _ in range(10):
            codon = MSDMSolver.pick_random_codon(AminoAcid("F"), self.e_coli, 0.5)
            self.assertEqual("TTT", codon)

        # The probability that this fails is (1/2)^100 = 1e-31 ... good enough :)
        codons = set(MSDMSolver.pick_random_codon(AminoAcid("F"), self.e_coli, 0.4) for _ in range(100))
        self.assertEqual({"TTT", "TTC"}, codons)


    def test_monte_carlo(self, n=1):
        """ Generates random inputs for MSDM and checks whether the obtained solutions
            fulfills input constraints. """

        sequences = sample_msdm_sequences()

        for i in range(0, n):
            mutations = random_msdm_mutations(sequences, no_sites=5)

            mutation_strings = [m.orig_amino + str(m.codon_index) + m.target_amino
                                for m in mutations]

            print(f"\nTEST CASE NO. {i+1}, with Primer3\n")
            config = sample_msdm_config(use_primer3=True)
            msdm_data = MSDMInput(
                sequences=sequences,
                config=config,
                mutations=mutation_strings)
            self._run_test(msdm_data)

            print(f"\nTEST CASE NO. {i+1}, without Primer3\n")
            msdm_data.config.use_primer3 = False
            self._run_test(msdm_data)


    def _run_test(self, msdm_data):
        result = msdm_solve(msdm_data)

        print_stats_msdm(result)

        return result

