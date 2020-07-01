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

import { compute } from './amino'

import testData from './amino.test.data.json'

const acidsAvailable = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']

const getAvoid = (include: string[]): string[] => acidsAvailable.filter(acid => !include.includes(acid))

describe('amino.worker - amino acids to codons', () => {
  for (const [include, results] of Object.entries(testData)) {
    const included = include.split('')
    const avoid = getAvoid(included)

    describe(`for included ${included.join(',')} and avoided ${avoid.join(',')}`, () => {
      const degenerated = compute(included, avoid)

      describe(`degenerated codon ${degenerated}`, () => {
        it(`should be one of ${results.join(',')}`, () => {
          expect(results.includes(degenerated)).toBe(true)
        })
      })
    })
  }
})
