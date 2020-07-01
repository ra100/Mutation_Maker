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
import sys
from mutation_maker.reverse_translation import Translator
from mutation_maker.degenerate_codon import DegenerateTriplet, CodonUsage

sys.path.append('../')


class TestTranslator(unittest.TestCase):
    e_coli = CodonUsage("e-coli")

    def protein_from_dna(self, dna_sequence):

        get_aa = DegenerateTriplet()
        AA = []
        for i in range(0, len(dna_sequence) - 1, 3):
            codon = dna_sequence[i:i + 3]
            aa = get_aa.degenerate_codon_to_aminos(str(codon),self.e_coli.table.forward_table)[0]
            AA.append(aa)
        return ''.join(AA)

    def test_correctness_of_translation(self):
        translate = Translator(0.11, [40, 60], ['AarI', 'AatII', 'NCT'], 0.05, 600, 'e-coli')
        protein = 'ACDEFGHIKLMNPQRSTVWY'
        dna_sequence = translate(protein)
        protein_back = self.protein_from_dna(dna_sequence)

        self.assertEqual(protein, protein_back)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
