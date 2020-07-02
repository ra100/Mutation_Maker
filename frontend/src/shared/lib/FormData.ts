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

export type FormParameters = {
  sizeMin: number
  sizeOpt: number
  sizeMax: number

  threePrimeSizeMin: number
  threePrimeSizeMax: number

  fivePrimeSizeMin: number
  fivePrimeSizeMax: number

  overlapSizeMin: number
  overlapSizeMax: number

  gcContentMin: number
  gcContentMax: number

  temperatureMin: number
  temperatureMax: number

  threePrimeTemperatureMin: number
  threePrimeTemperatureMax: number

  overlapTemperatureMin: number
  overlapTemperatureMax: number

  threePrimeTemperatureWeight: number
  threePrimeSizeWeight: number
  overlapTemperatureWeight: number
  gcContentWeight: number
  hairpinTemperatureWeight: number
  primerDimerTemperatureWeight: number

  maxTemperatureDifference: number

  separateForwardReverseTemperatures: boolean
  usePrimer3: boolean
  usePrimerGrowingAlgorithm: boolean
  computeHairpinHomodimer: boolean
  excludeFlankingPrimers: boolean

  fileName: string
  oligoPrefix: string
}

export type SSMFormData = {
  plasmidSequence: string
  goiSequence: string
  mutations: string
  forwardPrimerType: string
  forwardPrimerValue: string
  reversePrimerType: string
  reversePrimerValue: string
  degenerateCodon: string
  aminoAcids: object[]
} & FormParameters

export type MSDMFormData = {
  fivePrimeFlankingSequence: string
  goiSequence: string
  threePrimeFlankingSequence: string
  mutations: string
  codonUsage: string
  customCodonUsage: string
  taxonomyId: string
  codonUsageFrequencyThresholdPct: number
  useDegeneracyCodon: boolean

  sizeMin: number
  sizeMax: number

  threePrimeSizeMin: number
  threePrimeSizeMax: number

  fivePrimeSizeMin: number
  fivePrimeSizeMax: number

  gcContentMin: number
  gcContentMax: number

  temperatureMin: number
  temperatureMax: number

  temperatureWeight: number
  totalSizeWeight: number
  threePrimeSizeWeight: number
  fivePrimeSizeWeight: number
  gcContentWeight: number
  hairpinTemperatureWeight: number
  primerDimerTemperatureWeight: number
  mutationCoverageWeight: number

  maxTemperatureDifference: number

  usePrimer3: boolean
  nonOverlappingPrimers: boolean
  fileName: string
  oligoPrefix: string
}

export type PASFormData = {
  inputSequenceType: string
  fivePrimeFlankingSequence: string
  goiSequence: string
  threePrimeFlankingSequence: string
  inputMutationsType: string
  inputMutations: {mutations: any[]}
  useDegeneracyCodon: boolean
  computeHairpinHomodimer: boolean
  codonUsage: string
  customCodonUsage: string
  taxonomyId: string
  codonUsageFrequencyThresholdPct: number

  oligoLengthMin: number
  oligoLengthMax: number

  overlappingTmMin: number
  overlappingTmOpt: number
  overlappingTmMax: number

  overlappingLengthMin: number
  overlappingLengthOpt: number
  overlappingLengthMax: number

  gcContentMin: number
  gcContentMax: number

  fileName: string
  oligoPrefix: string

  avoidMotifs: string[]
}
