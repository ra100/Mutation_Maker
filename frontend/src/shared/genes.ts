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

import * as R from 'ramda'
import { notUndefined } from './helpers'

import codonTableJson from './DNA-codon-table.json'
import aminoAcidsJson from './amino-acids.json'

type CodonTable = Record<string, string[]>
type AminoAcidsMap = Record<string, { symbol3?: string; name: string }>

export const codonTable: CodonTable = codonTableJson
export const aminoAcids: AminoAcidsMap = aminoAcidsJson

export type Primer = {
  start: number
  size: number
  description?: string
}

type Aminoacid = {
  codon: string
  symbol: string
  symbol3?: string
  name: string
}

export const gcContent =
  (window: number) =>
  (gene: string): number[] => {
    const result = []
    let range = (window / 2) | 0
    for (let i = 0; i < gene.length; i++) {
      let gc = 0
      //we count how many things we have counted
      let eff_win = 0

      for (let w = i - range; w < i + range; w++) {
        if (w > 0 && w < gene.length) {
          eff_win++
          if (gene[w] === 'G' || gene[w] === 'C') {
            gc++
          }
        }
      }

      result.push(gc / eff_win)
    }

    return result
  }

export const aminoAcidToCodons = (aminoAcid: string): string[] => {
  return [...codonTable[aminoAcid]]
}

export const codonTableIncludes = (aminoAcid: string): boolean => {
  return aminoAcid in codonTable
}

export const codonToAminoAcid = (codon: string): Aminoacid | undefined => {
  for (const symbol in codonTable) {
    const codons: string[] = codonTable[symbol]
    if (codons && codons.includes(codon)) {
      return {
        codon,
        symbol,
        ...aminoAcids[symbol],
      }
    }
  }
  return undefined
}

export const toCodons = (gene: string) => {
  const go = (genePart: string, codons: string[] = []): string[] =>
    genePart.length < 3 ? codons : go(genePart.slice(3), [...codons, genePart.slice(0, 3)])

  // must begin with ATG
  // must end with TAA TAG TGA
  return go(gene)
}

export type Mutation = {
  source: string
  target: string
  position: number
  identifier: string
  ratio?: number
  concentrations?: string
}

export type MutationPas = {
  position: number
  mutated_amino: string
  wild_type_amino: string
  wild_type_codon: string
  mutated_codon: string
  frequency: number
  wild_type: boolean
  identifier: string
  ratio?: number
  concentrations?: string
}

export const parseMutation = (mutationString: string): Mutation | undefined => {
  if (mutationString) {
    const match = mutationString.match(/([A-Z])(\d+)([A-Z])/)
    return match
      ? {
          source: match[1],
          target: match[3],
          position: Number(match[2]),
          identifier: mutationString,
        }
      : undefined
  }
  return undefined
}

export const parseMutations = (mutationsString: string): Mutation[] =>
  // must be in valid format already
  mutationsString.split(' ').map(parseMutation).filter(notUndefined)

export const mutationToString = (mutation: Mutation) =>
  `${mutation.source}${mutation.position}${mutation.target}`

export const subSequence =
  (sequence: string) =>
  (primer: Primer): string =>
    sequence.slice(
      primer.size > 0 ? primer.start : primer.start + primer.size,
      primer.size > 0 ? primer.start + primer.size - 1 : primer.start,
    )

export enum PrimersType {
  pETseq1 = 'pETseq1',
  custom = 'custom',
}

export const getForwardPrimer = (primersType: PrimersType) => {
  switch (primersType) {
    case PrimersType.pETseq1:
      return 'CAAGGAATGGTGCATGCAAG'
    default:
      return ''
  }
}

export const getReversePrimer = (primersType: PrimersType) => {
  switch (primersType) {
    case PrimersType.pETseq1:
      return 'GAACGTGGCGAGAAAGGAAG'
    default:
      return ''
  }
}

export const flattenMutations = (mutations: Mutation[]): Mutation[] => {
  const groups: Mutation[][] = R.groupWith<Mutation>(
    (left, right) => left.source === right.source && left.position === right.position,
    mutations,
  )

  const sortedGroups = groups.map((group) => R.sortBy<Mutation>(R.prop('target'), group))

  return sortedGroups
    .map((group) =>
      !R.isEmpty(group)
        ? R.tail(group).reduce(({ target: accTarget }, { source, position, target }) => {
            const newTarget = `${accTarget}${target}`
            return {
              source,
              position,
              target: newTarget,
              identifier: `${source}${position}${newTarget}`,
            }
          }, R.head(group)!)
        : undefined,
    )
    .filter(notUndefined)
}
