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

import ratioCounter from './ratioCounter'

describe('RatioCounter', () => {
  it('should return ratios for simple mutations', () => {
    const mutations = [
      {
        mutations: [{ source: 'R', target: 'V', position: 273, identifier: 'R273V' }],
        result_found: true,
        index: 0,
        ratio: 0
      },
      {
        mutations: [{ source: 'R', target: 'R', position: 273, identifier: 'R273R' }],
        result_found: true,
        index: 1,
        ratio: 0
      },
    ]

    const result = ratioCounter(mutations)

    expect(result[0].ratio).toBe(0.5)
    expect(result[1].ratio).toBe(0.5)
  })

  it('should return ratios for 2:1 mutation', () => {
    const mutations = [
      {
        mutations: [{ source: 'H', target: 'G', position: 83, identifier: 'H83G' }],
        result_found: true,
        index: 0,
        ratio: 0
      },
      {
        mutations: [{ source: 'H', target: 'H', position: 83, identifier: 'H83HN' }],
        result_found: true,
        index: 1,
        ratio: 0
      },
    ]

    const result = ratioCounter(mutations)

    expect(result[0].ratio).toBe(1 / 3)
    expect(result[1].ratio).toBe(2 / 3)
  })

  it('should count ratios for multisite mutation', () => {
    const mutations = [
      {
        mutations: [
          { source: 'V', target: 'T', position: 1, identifier: 'V1T' },
          { source: 'H', target: 'L', position: 2, identifier: 'H2L' },
        ],
        result_found: true,
        index: 0,
        ratio: 0
      },
      {
        mutations: [
          { source: 'V', target: 'G', position: 1, identifier: 'V1GV' },
          { source: 'H', target: 'L', position: 2, identifier: 'V2L' },
        ],
        result_found: true,
        index: 1,
        ratio: 0
      },
      {
        mutations: [
          { source: 'V', target: 'T', position: 1, identifier: 'V1T' },
          { source: 'H', target: 'Y', position: 2, identifier: 'H2Y' },
        ],
        result_found: true,
        index: 2,
        ratio: 0
      },
      {
        mutations: [
          { source: 'V', target: 'G', position: 1, identifier: 'V1GV' },
          { source: 'H', target: 'Y', position: 2, identifier: 'H2Y' },
        ],
        result_found: true,
        index: 3,
        ratio: 0
      },
    ]

    const result = ratioCounter(mutations)

    expect(result[0].index).toBe(0)
    expect(result[0].mutations[0].ratio).toBe(1 / 3)
    expect(result[0].mutations[1].ratio).toBe(1 / 2)
    expect(result[0].ratio).toBe(1 / 6)

    expect(result[1].index).toBe(1)
    expect(result[1].mutations[0].ratio).toBe(2 / 3)
    expect(result[1].mutations[1].ratio).toBe(1 / 2)
    expect(result[1].ratio).toBe(1 / 3)

    expect(result[2].index).toBe(2)
    expect(result[2].mutations[0].ratio).toBe(1 / 3)
    expect(result[2].mutations[1].ratio).toBe(1 / 2)
    expect(result[2].ratio).toBe(1 / 6)

    expect(result[3].index).toBe(3)
    expect(result[3].mutations[0].ratio).toBe(2 / 3)
    expect(result[3].mutations[1].ratio).toBe(1 / 2)
    expect(result[3].ratio).toBe(1 / 3)
  })
})
