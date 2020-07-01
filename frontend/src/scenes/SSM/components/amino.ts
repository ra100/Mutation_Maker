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

import aminoToCodonMap from 'shared/DNA-codon-table.json'

const MAX_DURATION = 10 * 60 * 1000
const MAX_NUMBER_OF_COMBINATIONS = 100

const substitutions = {
  A: 'A',
  AC: 'M',
  ACG: 'V',
  ACGT: 'N',
  ACT: 'H',
  AG: 'R',
  AGT: 'D',
  AT: 'W',
  C: 'C',
  CG: 'S',
  CGT: 'B',
  CT: 'Y',
  G: 'G',
  GT: 'K',
  T: 'T',
}

const defaultAvoid = [...aminoToCodonMap.STOP]

const singleLetterCodes = {
  A: ['A'],
  B: ['C', 'G', 'T'],
  C: ['C'],
  D: ['A', 'G', 'T'],
  G: ['G'],
  H: ['A', 'C', 'T'],
  K: ['G', 'T'],
  M: ['A', 'C'],
  N: ['A', 'C', 'G', 'T'],
  X: ['A', 'C', 'G', 'T'],
  R: ['A', 'G'],
  S: ['C', 'G'],
  T: ['T'],
  V: ['A', 'C', 'G'],
  W: ['A', 'T'],
  Y: ['C', 'T'],
}

let combinationsCount: number

const getMissingRequired = (required: string[], generated: string[]): string[] =>
  required.filter(codon => generated.indexOf(codon) < 0)

const getCodonCombinations = (amino: string[]): string[] => {
  const out = new Set<string>()
  for (var i = 0; i < amino.length; i++) {
    const codons = aminoToCodonMap[amino[i]]
    for (let j = 0; j < codons.length; j++) {
      out.add(codons[j])
    }
  }

  return [...out].sort()
}

const getNucleotidesOnPositions = (codons: string[]): string[] => {
  const combinations: Set<string>[] = [new Set<string>(), new Set<string>(), new Set<string>()]

  for (let i = 0; i < codons.length; i++) {
    const letters = codons[i].split('')
    combinations[0].add(letters[0])
    combinations[1].add(letters[1])
    combinations[2].add(letters[2])
  }

  const out: Array<string> = []

  for (let i = 0; i < combinations.length; i++) {
    const set = [...combinations[i]].sort().join('')
    out.push(set)
  }

  return out
}

const getDegenerateCodons = (nucleotides: string[]): string =>
  nucleotides.map(letters => substitutions[letters]).join('')

const recursiveCombinations = (input: string[][], combinations: string[]): string[] => {
  if (input.length === 0) {
    return combinations
  }

  const [current = [], ...rest] = input
  if (combinations.length === 0) {
    return recursiveCombinations(rest, current)
  }

  return recursiveCombinations(
    rest,
    current.reduce(
      (acc: string[], letter: string) => [...acc, ...combinations.map((l: string) => l + letter)],
      [],
    ),
  )
}

export const generateCombinationsFromDegenerateCodon = (degenerateCodon: string): string[] =>
  recursiveCombinations(
    degenerateCodon.split('').map(letter => singleLetterCodes[letter]),
    [],
  )

const isGrammarWithoutAvoided = (grammar: string, avoidedCodons: string[]) => {
  const generatedCodons = generateCombinationsFromDegenerateCodon(grammar)

  return !avoidedCodons.find(codon => generatedCodons.indexOf(codon) > -1)
}

const getGeneratedCombination = (degenerate: string) =>
  degenerate
    .split(',')
    .map(generateCombinationsFromDegenerateCodon)
    .reduce((acc, curr) => [...acc, ...curr], [])

const joinGrammars = (grammars: string, grammarToAdd: string): string => {
  const generatedCodons = getGeneratedCombination(grammars)
  const newSet = generateCombinationsFromDegenerateCodon(grammarToAdd)

  if (newSet.every(codon => generatedCodons.indexOf(codon) >= 0)) {
    return grammars
  }

  return [grammars, grammarToAdd].join(',')
}

const getGrammarFromCodons = (codons: string[]): string =>
  getDegenerateCodons(getNucleotidesOnPositions(codons))

const modifyGrammar = (
  includedCodons: string[],
  avoidedCodons: string[],
  excluded: string[],
  maxLength: number,
) => {
  const grammar = getGrammarFromCodons(includedCodons)

  if (isGrammarWithoutAvoided(grammar, avoidedCodons)) {
    return grammar
  }

  const [excludedCodon, ...included] = includedCodons
  const newExcluded = [...excluded, excludedCodon]

  const modifiedGrammar = modifyGrammar(included, avoidedCodons, newExcluded, maxLength)

  if (modifiedGrammar === null) {
    return null
  }

  const modifiedExcludedGrammar = modifyGrammar(newExcluded, avoidedCodons, [], maxLength)
  if (modifiedExcludedGrammar === null) {
    return null
  }

  const joinedGrammars = joinGrammars(modifiedGrammar, modifiedExcludedGrammar)

  if (joinedGrammars.length > maxLength) {
    return null
  }

  const generated = getGeneratedCombination(joinedGrammars)
  if (getMissingRequired(includedCodons, generated).length > 0) {
    return null
  }

  return joinedGrammars
}

function recursiveCodonCombinations(include: string[][], codons: string[]): string[][] {
  if (combinationsCount > MAX_NUMBER_OF_COMBINATIONS) {
    throw new Error('Reached maximum depth')
  }

  if (include.length === 0) {
    combinationsCount++
    return [codons]
  }

  const first = include[0]
  const rest = include.slice(1)
  const combinations: string[][] = []

  for (let i = 0; i < first.length; i++) {
    const codon = first[i]
    try {
      const generatedCodons = recursiveCodonCombinations(rest, [...codons, codon])
      for (let j = 0; j < generatedCodons.length; j++) {
        const generated = generatedCodons[j]
        combinations.push(generated)
      }
    } catch (e) {
      return combinations
    }
  }

  return combinations
}

const getAminoAcidsCodons = (acids: string[]) =>
  acids.map<string[]>(acid => aminoToCodonMap[acid]).sort((a, b) => b.length - a.length)

const sortCombinationInMultipleWays = (combinations: string[][]) => {
  const result: string[][] = []
  for (let i = 0; i < combinations.length; i++) {
    result.push([...combinations[i]].sort((a, b) => a.localeCompare(b)))
    result.push([...combinations[i]].sort((a, b) => b.localeCompare(a)))
  }
  return result
}

export const compute = (include: string[], avoid: string[]) => {
  const codonsIncluded = getCodonCombinations(include)
  const codonsAvoided = [...getCodonCombinations(avoid), ...defaultAvoid]
  const targetLength = include.length
  const codons = getAminoAcidsCodons(include)

  let currentBestLength = Number.MAX_VALUE

  combinationsCount = 0

  const startCombinations = recursiveCodonCombinations(codons, [])
  const combinations = sortCombinationInMultipleWays(startCombinations)

  let result = codonsIncluded.join(',')

  const startTime = Date.now()

  for (const codons of combinations) {
    if (Date.now() - startTime > MAX_DURATION) {
      return result
    }

    const codonsToCode = [...codons]
    const degenerateCodons = modifyGrammar(codonsToCode, codonsAvoided, [], result.length)

    if (degenerateCodons) {
      const generatedCodons = getGeneratedCombination(degenerateCodons)

      if (generatedCodons.length < currentBestLength || degenerateCodons.length < result.length) {
        currentBestLength = generatedCodons.length
        result = degenerateCodons
      }

      if (generatedCodons.length === targetLength && degenerateCodons.split(',').length === 1) {
        return result
      }
    }
  }

  return result
}
