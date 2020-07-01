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

from mutation_maker.pas_degeneracy_recursion import Degeneracy
from tests.test_support import sample_pas_sequences, sample_pas_mutations, sample_pas_config
import sys
sys.path.append('../')
import unittest
import random


class DegeneracyTest(unittest.TestCase):

    def test_check_set_cover(self):
        sys.setrecursionlimit(10000)
        index = 1
        config = sample_pas_config(index)
        degeneracy = Degeneracy(config, 'e-coli')
        aminos = ['F', 'L', 'Y', 'H', 'Q', 'I', 'M', 'N', 'K', 'V', 'D', 'E', 'S', 'C', 'W', 'P', 'R', 'T', 'A', 'G']

        for i in range(100):
            number_of_aminos = random.randint(1,5)
            random_aminos = random.sample(aminos, number_of_aminos)
            solution = degeneracy(random_aminos)
            print(solution, random_aminos)

            aminos_generated = []
            for codon, aminos_i in solution.items():
                for a in aminos_i:
                    aminos_generated.append(a)

            with self.subTest(i=i):
                self.assertEqual(set(aminos_generated), set(random_aminos))
