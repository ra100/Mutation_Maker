/*   Copyright (c) 2020 Merck Sharp & Dohme Corp. a subsidiary of Merck & Co., Inc., Kenilworth, NJ, USA.
 *
 *   This file is part of the Mutation Maker, An Open Source Oligo Design Software For Mutagenesis and De Novo Gene Synthesis Experiments.
 *
 *   Mutation Maker is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import { flattenMutations, parseMutation, parseMutations } from './genes'
import { notUndefined } from './helpers'

test('parseMutations', () => {
  const mutationsString = 'E160X T164X'
  expect(parseMutations(mutationsString)).toEqual([
    {
      source: 'E',
      target: 'X',
      position: 160,
      identifier: 'E160X',
    },
    {
      source: 'T',
      target: 'X',
      position: 164,
      identifier: 'T164X',
    },
  ])
})

test('flattenMutations', () => {
  const mutations = ['A165K', 'A165P', 'A165E', 'A165R', 'R169L', 'R169I', 'R169K', 'R169Y']

  const parsedMutations = mutations.map(parseMutation).filter(notUndefined)

  const actual = flattenMutations(parsedMutations)

  const expected = [
    {
      source: 'A',
      position: 165,
      target: 'EKPR',
      identifier: 'A165EKPR',
    },
    {
      source: 'R',
      position: 169,
      target: 'IKLY',
      identifier: 'R169IKLY',
    },
  ]

  expect(actual).toEqual(expected)
})
