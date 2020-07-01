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

import copy
import unittest

class MiscTest(unittest.TestCase):
    # This test is mainly as a sanity check to make sure
    # we don't use the library in an incorrect way.
    def test_deep_copy(self):
        data = [{"a", "b"}, {"c"}]

        copied = copy.deepcopy(data)

        copied.pop(1)
        copied[0].pop()

        self.assertEqual(len(copied), 1)
        self.assertEqual(data, [{"a", "b"}, {"c"}])

    def test_set_difference(self):
        self.assertEqual({1, 3}, {1, 2, 3} - {2})
        self.assertEqual({1, 2, 3}, {1, 2, 3} - {4})

