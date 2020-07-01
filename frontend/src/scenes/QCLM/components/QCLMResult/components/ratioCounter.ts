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

import { Mutation } from 'shared/genes'
import { IndexedQCLMFlatResultRecord } from 'shared/lib/ResultData'

const getAminoAcidsFromIdentifier = (identifier: string): string[] =>
  identifier.replace(/^\w\d*/,'').split('')

type MutationPositionRatio = Record<number, number>

const getPositionMutations = (mutations: IndexedQCLMFlatResultRecord[]): MutationPositionRatio => {
  const positions: Record<number, Set<string>> = mutations[0].mutations.reduce((acc, mutation) => {
    acc[mutation.position] = acc[mutation.position] || new Set()
    return acc
  }, {})

  mutations.forEach(({ mutations }) =>
    mutations.forEach(({ position, identifier }) => {
      getAminoAcidsFromIdentifier(identifier).forEach(target => {
        positions[position].add(target)
      })
    }),
  )

  return Object.entries(positions).reduce((acc, [position, targets]) => {
    acc[position] = targets.size
    return acc
  }, {})
}

const getRatios = (mutations: IndexedQCLMFlatResultRecord[], ratios: MutationPositionRatio): IndexedQCLMFlatResultRecord[] =>
  mutations.map((mutation) => {
    const mutationMutations = mutation.mutations.map(positionMutation => ({
      ...positionMutation,
      ratio: getAminoAcidsFromIdentifier(positionMutation.identifier).length / ratios[positionMutation.position]
    }))

    return {
      ...mutation,
      mutations: mutationMutations,
      ratio: mutationMutations.reduce((acc, {ratio}) => acc * ratio, 1)
    }
  })

const getSiteIdFromMutations = (mutations: Mutation[]): string =>
  mutations
    .map((mutation) => mutation.position)
    .sort()
    .join('-')

const getSites = (
  records: IndexedQCLMFlatResultRecord[],
): Record<string, IndexedQCLMFlatResultRecord[]> =>
  records.reduce(
    (acc: Record<string, IndexedQCLMFlatResultRecord[]>, record: IndexedQCLMFlatResultRecord) => {
      const siteId = getSiteIdFromMutations(record.mutations)
      if (!acc[siteId]) {
        acc[siteId] = []
      }
      acc[siteId].push(record)

      return acc
    },
    {},
  )

const ratioCounter = (
  resultRecords: IndexedQCLMFlatResultRecord[],
): IndexedQCLMFlatResultRecord[] => {
  const sites = getSites(resultRecords)
  const result: IndexedQCLMFlatResultRecord[] = []

  Object.values(sites).forEach((mutations) => {
    const mutationsPerPosition = getPositionMutations(mutations)
    const mutationsWithRatios = getRatios(mutations, mutationsPerPosition)

    result.push(...mutationsWithRatios)
  })

  result.sort((a, b) => a.index - b.index)

  return result
}

export default ratioCounter
