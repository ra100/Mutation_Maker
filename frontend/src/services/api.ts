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

import Axios from 'axios'
import * as R from 'ramda'

import {
  JobDescription,
  JobResponse,
  JobStatus,
  QCLMRequestData,
  QCLMResponseData,
  SSMRequestConfig,
  SSMRequestData,
  SSMResponseData,
  PASRequestData,
  PASResponseData,
} from 'shared/lib/Api'
import { FormParameters, PASFormData, QCLMFormData, SSMFormData } from 'shared/lib/FormData'
import { Workflow } from 'shared/workflow'

const API_PREFIX = '/v1'

export const formParametersToRequestConfig = (parameters: FormParameters): SSMRequestConfig => ({
  min_primer_size: Number(parameters.sizeMin),
  max_primer_size: Number(parameters.sizeMax),

  min_gc_content: Number(parameters.gcContentMin),
  max_gc_content: Number(parameters.gcContentMax),

  min_three_end_size: Number(parameters.threePrimeSizeMin),
  max_three_end_size: Number(parameters.threePrimeSizeMax),

  min_five_end_size: Number(parameters.fivePrimeSizeMin),
  max_five_end_size: Number(parameters.fivePrimeSizeMax),

  min_overlap_size: Number(parameters.overlapSizeMin),
  max_overlap_size: Number(parameters.overlapSizeMax),

  three_end_temp_range: Number(parameters.maxTemperatureDifference),
  overlap_temp_range: Number(parameters.maxTemperatureDifference),

  min_overlap_temperature: Number(parameters.overlapTemperatureMin),
  max_overlap_temperature: Number(parameters.overlapTemperatureMax),

  min_three_end_temperature: Number(parameters.threePrimeTemperatureMin),
  max_three_end_temperature: Number(parameters.threePrimeTemperatureMax),

  separate_forward_reverse_temperatures: Boolean(parameters.separateForwardReverseTemperatures),
  use_primer3: Boolean(parameters.usePrimer3),
  use_fast_approximation_algorithm: Boolean(parameters.usePrimerGrowingAlgorithm),
  compute_hairpin_homodimer: Boolean(parameters.computeHairpinHomodimer),
  exclude_flanking_primers: Boolean(parameters.excludeFlankingPrimers),

  file_name: String(parameters.fileName),
  oligo_prefix: String(parameters.oligoPrefix),

  three_end_temp_weight: Number(parameters.threePrimeTemperatureWeight),
  three_end_size_weight: Number(parameters.threePrimeSizeWeight),
  overlap_temp_weight: Number(parameters.overlapTemperatureWeight),
  gc_content_weight: Number(parameters.gcContentWeight),
  hairpin_temperature_weight: Number(parameters.hairpinTemperatureWeight),
  primer_dimer_temperature_weight: Number(parameters.primerDimerTemperatureWeight),
})

/* TODO filter out unknown values */
// SSM
export const formDataToSsmRequest = (ssmFormData: SSMFormData): SSMRequestData => ({
  mutations: ssmFormData.mutations
    .trim()
    .split(/\s+/)
    .filter((e) => e.trim().length > 0),
  sequences: {
    gene_of_interest: ssmFormData.goiSequence,
    forward_primer: ssmFormData.forwardPrimerValue,
    reverse_primer: ssmFormData.reversePrimerValue,
    plasmid: {
      plasmid_sequence: ssmFormData.plasmidSequence,
    },
  },
  degenerate_codon: ssmFormData.degenerateCodon,
  config: formParametersToRequestConfig(ssmFormData),
})

export const dataToSSMFormData = (data: SSMResponseData): Partial<SSMFormData> => {
  const ssmRequestData = data.input_data

  return {
    mutations: ssmRequestData.mutations.join(' '),
    goiSequence: ssmRequestData.sequences.gene_of_interest,
    forwardPrimerValue: ssmRequestData.sequences.forward_primer,
    reversePrimerValue: ssmRequestData.sequences.reverse_primer,
    plasmidSequence: ssmRequestData.sequences.plasmid.plasmid_sequence,
    degenerateCodon: ssmRequestData.degenerate_codon,

    sizeMin: ssmRequestData.config.min_primer_size,
    sizeMax: ssmRequestData.config.max_primer_size,
    gcContentMin: ssmRequestData.config.min_gc_content,
    gcContentMax: ssmRequestData.config.max_gc_content,
    threePrimeSizeMin: ssmRequestData.config.min_three_end_size,
    threePrimeSizeMax: ssmRequestData.config.max_three_end_size,
    overlapSizeMin: ssmRequestData.config.min_overlap_size,
    overlapSizeMax: ssmRequestData.config.max_overlap_size,
    maxTemperatureDifference: ssmRequestData.config.three_end_temp_range,
    threePrimeTemperatureMin: ssmRequestData.config.min_three_end_temperature,
    threePrimeTemperatureMax: ssmRequestData.config.max_three_end_temperature,
    overlapTemperatureMin: ssmRequestData.config.min_overlap_temperature,
    overlapTemperatureMax: ssmRequestData.config.max_overlap_temperature,
    overlapTemperatureWeight: ssmRequestData.config.overlap_temp_weight,
    threePrimeTemperatureWeight: ssmRequestData.config.three_end_temp_weight,
    threePrimeSizeWeight: ssmRequestData.config.three_end_size_weight,
    gcContentWeight: ssmRequestData.config.gc_content_weight,
    hairpinTemperatureWeight: ssmRequestData.config.hairpin_temperature_weight,
    primerDimerTemperatureWeight: ssmRequestData.config.primer_dimer_temperature_weight,
    oligoPrefix: ssmRequestData.config.oligo_prefix,
  }
}

// QCLM
export const formDataToQclmRequest = (qclmFormData: QCLMFormData): QCLMRequestData => ({
  mutations: qclmFormData.mutations
    .trim()
    .split(/\s+/)
    .filter((e) => e.trim().length > 0),
  sequences: {
    five_end_flanking_sequence: qclmFormData.fivePrimeFlankingSequence,
    three_end_flanking_sequence: qclmFormData.threePrimeFlankingSequence,
    gene_of_interest: qclmFormData.goiSequence,
  },
  config: {
    min_primer_size: Number(qclmFormData.sizeMin),
    max_primer_size: Number(qclmFormData.sizeMax),
    min_gc_content: Number(qclmFormData.gcContentMin),
    max_gc_content: Number(qclmFormData.gcContentMax),
    min_three_end_size: Number(qclmFormData.threePrimeSizeMin),
    max_three_end_size: Number(qclmFormData.threePrimeSizeMax),
    min_five_end_size: Number(qclmFormData.fivePrimeSizeMin),
    max_five_end_size: Number(qclmFormData.fivePrimeSizeMax),
    min_temperature: Number(qclmFormData.temperatureMin),
    max_temperature: Number(qclmFormData.temperatureMax),

    temp_weight: Number(qclmFormData.temperatureWeight),
    primer_size_weight: Number(qclmFormData.totalSizeWeight),
    three_end_size_weight: Number(qclmFormData.threePrimeSizeWeight),
    five_end_size_weight: Number(qclmFormData.fivePrimeSizeWeight),
    gc_content_weight: Number(qclmFormData.gcContentWeight),
    hairpin_temperature_weight: Number(qclmFormData.hairpinTemperatureWeight),
    primer_dimer_temperature_weight: Number(qclmFormData.primerDimerTemperatureWeight),
    mutation_coverage_weight: Number(qclmFormData.mutationCoverageWeight),

    codon_usage: formatCodonUsage(qclmFormData.codonUsage, qclmFormData.customCodonUsage),
    taxonomy_id: qclmFormData.taxonomyId,
    codon_usage_frequency_threshold: qclmFormData.codonUsageFrequencyThresholdPct / 100, // must be normalized to [0, 1] range
    use_degeneracy_codon: qclmFormData.useDegeneracyCodon,

    use_primer3: Boolean(qclmFormData.usePrimer3),
    non_overlapping_primers: Boolean(qclmFormData.nonOverlappingPrimers),
    file_name: String(qclmFormData.fileName),
    oligo_prefix: String(qclmFormData.oligoPrefix),
  },
})

export const dataToQCLMFormData = (data: QCLMResponseData): Partial<QCLMFormData> => {
  const qclmRequestData = data.input_data

  return {
    mutations: qclmRequestData.mutations.join(' '),
    fivePrimeFlankingSequence: qclmRequestData.sequences.five_end_flanking_sequence,
    threePrimeFlankingSequence: qclmRequestData.sequences.three_end_flanking_sequence,
    goiSequence: qclmRequestData.sequences.gene_of_interest,
    sizeMin: qclmRequestData.config.min_primer_size,
    sizeMax: qclmRequestData.config.max_primer_size,
    gcContentMin: qclmRequestData.config.min_gc_content,
    gcContentMax: qclmRequestData.config.max_gc_content,
    threePrimeSizeMin: qclmRequestData.config.min_three_end_size,
    threePrimeSizeMax: qclmRequestData.config.max_three_end_size,
    fivePrimeSizeMin: qclmRequestData.config.min_five_end_size,
    fivePrimeSizeMax: qclmRequestData.config.max_five_end_size,
    temperatureMin: qclmRequestData.config.min_temperature,
    temperatureMax: qclmRequestData.config.max_temperature,
    codonUsage: qclmRequestData.config.codon_usage,
    customCodonUsage:
      qclmRequestData.config.codon_usage &&
      formatCustomCodonUsage(qclmRequestData.config.codon_usage),
    taxonomyId: qclmRequestData.config.taxonomy_id,
    codonUsageFrequencyThresholdPct:
      (qclmRequestData.config.codon_usage_frequency_threshold || 0) * 100,
    useDegeneracyCodon: qclmRequestData.config.use_degeneracy_codon,
    nonOverlappingPrimers: qclmRequestData.config.non_overlapping_primers,
  }
}

// PAS
const formatPasMutationsRequest = (mutations: any[]) => {
  const mutationsBody: any[] = []
  mutations.forEach((value) => {
    mutationsBody.push({
      frequency: value.mtp / 100,
      mutants: value.mt.split(',').map((mt: string) => {
        return mt.trim().toUpperCase()
      }),
      position: parseInt(value.target.slice(1)),
      target: value.target.slice(0, 1),
    })
  })
  return mutationsBody
}

const formatPasMutationsResponse = (mutations: any[]) => {
  const mutationsBody: any[] = []
  mutations.forEach((value) => {
    mutationsBody.push({
      mtp: value.frequency * 100,
      mt: value.mutants.join(', '),
      target: value.target + value.position,
    })
  })
  return { mutations: mutationsBody }
}

const formatString = (text: string) => {
  if (text) {
    const formattedText = text.trim().toUpperCase()
    if (formattedText.length > 0) {
      return formattedText
    }
  }

  return null
}

const formatCodonUsage = (codonUsage: string, customCodonUsage: string = '') => {
  if (codonUsage === 'custom') {
    return customCodonUsage
  } else if (codonUsage === 'e-coli' || codonUsage === 'yeast') {
    return codonUsage
  } else return 'custom'
}

const formatCustomCodonUsage = (codonUsage: string) => {
  if (codonUsage !== 'e-coli' && codonUsage !== 'yeast') {
    return codonUsage
  } else {
    return ''
  }
}

export const formDataToPasRequest = (pasFormData: PASFormData): PASRequestData => ({
  mutations: formatPasMutationsRequest(pasFormData.inputMutations.mutations),

  sequences: {
    five_end_flanking_sequence: formatString(pasFormData.fivePrimeFlankingSequence),
    three_end_flanking_sequence: formatString(pasFormData.threePrimeFlankingSequence),
    gene_of_interest: formatString(pasFormData.goiSequence),
  },

  is_dna_sequence: Boolean(pasFormData.inputSequenceType === 'dna'),
  is_mutations_as_codons: Boolean(pasFormData.inputMutationsType === 'dna'),

  config: {
    min_gc_content: Number(pasFormData.gcContentMin),
    max_gc_content: Number(pasFormData.gcContentMax),

    min_oligo_size: Number(pasFormData.oligoLengthMin),
    max_oligo_size: Number(pasFormData.oligoLengthMax),

    min_overlap_length: Number(pasFormData.overlappingLengthMin),
    opt_overlap_length: Number(pasFormData.overlappingLengthOpt),
    max_overlap_length: Number(pasFormData.overlappingLengthMax),

    min_overlap_tm: Number(pasFormData.overlappingTmMin),
    opt_overlap_tm: Number(pasFormData.overlappingTmOpt),
    max_overlap_tm: Number(pasFormData.overlappingTmMax),

    organism: formatCodonUsage(pasFormData.codonUsage, pasFormData.customCodonUsage),
    taxonomy_id: pasFormData.taxonomyId,
    codon_usage_frequency_threshold: Number(
      (pasFormData.codonUsageFrequencyThresholdPct || 0) / 100,
    ),

    use_degeneracy_codon: Boolean(pasFormData.useDegeneracyCodon),
    compute_hairpin_homodimer: Boolean(pasFormData.computeHairpinHomodimer),

    avoided_motifs: pasFormData.avoidMotifs || [],

    file_name: pasFormData.fileName,
    oligo_prefix: pasFormData.oligoPrefix,
  },
})

export const dataToPASFormData = (data: PASResponseData): Partial<PASFormData> => {
  const pasRequestData = data.input_data

  return {
    fivePrimeFlankingSequence: pasRequestData.sequences.five_end_flanking_sequence,
    threePrimeFlankingSequence: pasRequestData.sequences.three_end_flanking_sequence,
    goiSequence: pasRequestData.sequences.gene_of_interest,
    gcContentMin: pasRequestData.config.min_gc_content,
    gcContentMax: pasRequestData.config.max_gc_content,
    overlappingTmMin: pasRequestData.config.min_overlap_tm,
    overlappingTmOpt: pasRequestData.config.opt_overlap_tm,
    overlappingTmMax: pasRequestData.config.max_overlap_tm,
    overlappingLengthMin: pasRequestData.config.min_overlap_length,
    overlappingLengthOpt: pasRequestData.config.opt_overlap_length,
    overlappingLengthMax: pasRequestData.config.max_overlap_length,
    oligoLengthMin: pasRequestData.config.min_oligo_size,
    oligoLengthMax: pasRequestData.config.max_oligo_size,
    avoidMotifs: pasRequestData.config.avoided_motifs,
    inputMutationsType: pasRequestData.is_mutations_as_codons ? 'dna' : 'protein',
    inputSequenceType: pasRequestData.is_dna_sequence ? 'dna' : 'protein',
    codonUsageFrequencyThresholdPct:
      (pasRequestData.config.codon_usage_frequency_threshold || 0) * 100,
    useDegeneracyCodon: pasRequestData.config.use_degeneracy_codon,
    codonUsage: pasRequestData.config.organism && formatCodonUsage(pasRequestData.config.organism),
    customCodonUsage:
      pasRequestData.config.organism && formatCustomCodonUsage(pasRequestData.config.organism),
    taxonomyId: pasRequestData.config.taxonomy_id,
    inputMutations: formatPasMutationsResponse(pasRequestData.mutations),
    computeHairpinHomodimer: pasRequestData.config.compute_hairpin_homodimer,
  }
}

// Job
const dataToJobResponse = (data: object): JobResponse => data as JobResponse /* TODO */

export const submitJob = (endpoint: string, requestData: any): Promise<JobResponse> =>
  Axios.post(`${API_PREFIX}/${endpoint}`, JSON.stringify(requestData), {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((response) => dataToJobResponse(response.data))

export const fetchJobStatus = (jobId: string): Promise<JobStatus> =>
  Axios.get(`${API_PREFIX}/check/${jobId}`).then(
    (response) => response.data as JobStatus /* TODO */,
  )

export const fetchJobResultData = (jobId: string): Promise<any> =>
  Axios.get(`${API_PREFIX}/result/${jobId}`).then((response) => response.data)

const delay = (timeout: number) =>
  new Promise<void>((resolve) => setTimeout(() => resolve(), timeout))

export const pollWhilePending = (jobId: string, pollInterval: number): Promise<JobStatus> =>
  fetchJobStatus(jobId).then((jobStatus) => {
    if (jobStatus === JobStatus.pending) {
      return delay(pollInterval).then(() => pollWhilePending(jobId, pollInterval))
    }

    return jobStatus
  })

const getJobId = (job: JobResponse): string => R.last(job.result_url.split('/'))! // TODO bang

export const submitRequest = (endpoint: string, requestData: any): Promise<JobDescription> =>
  submitJob(endpoint, requestData).then((jobResponse) => ({
    id: getJobId(jobResponse),
    jobResponse,
  }))

const sortSSMResponseResults = (data: SSMResponseData): SSMResponseData => {
  return R.over(R.lensProp('results'), R.sortBy(R.prop('mutation')), data)
}
const dataToSSMResponseData = (data: any): SSMResponseData => {
  // TODO
  if (typeof data === 'string') {
    throw new Error(`Request failed: ${data}`)
  }

  return sortSSMResponseResults(data as SSMResponseData /* TODO */)
}

export const submitSSMRequest = (requestData: SSMRequestData): Promise<JobDescription> =>
  submitRequest('ssm', requestData)

export const fetchSSMResponseData = (id: string): Promise<SSMResponseData> =>
  fetchJobResultData(id).then(dataToSSMResponseData)

const dataToQCLMResponseData = (data: any): QCLMResponseData => {
  // TODO
  if (typeof data === 'string') {
    throw new Error(`Request failed: ${data}`)
  }

  return data as QCLMResponseData
}

export const submitQCLMRequest = (requestData: QCLMRequestData): Promise<JobDescription> =>
  submitRequest('qclm', requestData)

export const fetchQCLMResponseData = (id: string): Promise<QCLMResponseData> =>
  fetchJobResultData(id).then(dataToQCLMResponseData)

export const getExportUrl = (workflow: Workflow, jobId: string) =>
  `${API_PREFIX}/export_${workflow}/${jobId}.xlsx`
