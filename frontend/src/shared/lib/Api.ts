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

// Job
import {MutationPas} from "../genes";

export type JobResponse = {
  check_url: string
  forget_url: string
  cancel_url: string
  result_url: string
  export_url: string
}

export enum JobStatus {
  pending = 'PENDING',
  success = 'SUCCESS',
  failure = 'FAILURE',
}

export type JobDescription = {
  id: string
  jobResponse: JobResponse
}

// SSM
export type SSMRequestConfig = {
  min_primer_size: number
  max_primer_size: number

  min_gc_content: number
  max_gc_content: number

  min_three_end_size: number
  max_three_end_size: number

  min_five_end_size: number
  max_five_end_size: number

  min_overlap_size: number
  max_overlap_size: number

  three_end_temp_range: number
  overlap_temp_range: number

  min_three_end_temperature: number
  max_three_end_temperature: number

  min_overlap_temperature: number
  max_overlap_temperature: number

  separate_forward_reverse_temperatures: boolean
  use_primer3: boolean
  use_fast_approximation_algorithm: boolean
  compute_hairpin_homodimer: boolean
  exclude_flanking_primers: boolean

  file_name: string
  oligo_prefix: string

  three_end_temp_weight: number
  three_end_size_weight: number
  overlap_temp_weight: number
  gc_content_weight: number
  hairpin_temperature_weight: number
  primer_dimer_temperature_weight: number
}

export type SSMRequestData = {
  mutations: string[]
  sequences: {
    gene_of_interest: string
    forward_primer: string
    reverse_primer: string
    plasmid: {
      plasmid_sequence: string
    }
  }
  degenerate_codon?: string
  config: Partial<SSMRequestConfig>
}

export type SSMPrimerData = {
  direction: 'forward' | 'reverse'
  sequence: string
  normal_order_sequence: string
  normal_order_start: number
  start: number
  length: number
  three_end_temperature: number
  gc_content: number
  primer_temperature: number
}

export type SSMMutationPrimerSelectionReport = {
  primers_considered_from_primer3: number
  after_three_end_filtering: number
  after_gc_content_filtering: number
  after_three_end_temp_filtering: number
}

export type SSMMutationPairingReport = {
  all_pairs_count: number
  after_overlap_length_filtering: number
  after_overlap_temperature_filtering: number
  secondary_algorithm_used: boolean
}

export type SSMMutationData = {
  mutation: string
  result_found: boolean
  parameters_in_range: boolean
  non_optimality: number
  forward_primer: SSMPrimerData
  reverse_primer: SSMPrimerData
  overlap: {
    sequence: string
    length: number
    temperature: number
  }
}

export type SSMResponseData = {
  input_data: SSMRequestData
  results: SSMMutationData[]
  full_sequence: string
  goi_offset: number

  forward_flanking_primer_temperature: number
  reverse_flanking_primer_temperature: number

  min_forward_temperature: number
  opt_forward_temperature: number
  max_forward_temperature: number

  min_reverse_temperature: number
  opt_reverse_temperature: number
  max_reverse_temperature: number

  min_overlap_temperature: number
  opt_overlap_temperature: number
  max_overlap_temperature: number
}

// MSDM
export type MSDMRequestConfig = {
  min_primer_size: number
  opt_primer_size: number
  max_primer_size: number

  min_gc_content: number
  opt_gc_content: number
  max_gc_content: number

  min_three_end_size: number
  opt_three_end_size: number
  max_three_end_size: number

  min_five_end_size: number
  opt_five_end_size: number
  max_five_end_size: number

  min_temperature: number
  opt_temperature: number
  max_temperature: number

  temp_weight: number
  primer_size_weight: number
  three_end_size_weight: number
  five_end_size_weight: number
  gc_content_weight: number
  hairpin_temperature_weight: number
  primer_dimer_temperature_weight: number
  mutation_coverage_weight: number

  gc_clamp: number
  three_end_temp_range: number
  overlap_temp_range: number

  codon_usage: string
  taxonomy_id?: string
  codon_usage_frequency_threshold?: number
  use_degeneracy_codon?: boolean

  use_primer3: boolean
  non_overlapping_primers: boolean
  use_fast_approximation_algorithm: boolean
  file_name: string
  oligo_prefix: string
}

export type MSDMRequestData = {
  mutations: string[]
  sequences: {
    five_end_flanking_sequence: string
    gene_of_interest: string
    three_end_flanking_sequence: string
  }
  config: Partial<MSDMRequestConfig & {}>
}

export type MSDMPrimer = {
  sequence: string
  start: number
  length: number
  temperature: number
  gc_content: number
  degenerate_codons: string[]
  overlap_with_following?: boolean
}

export type MSDMMutationData = {
  mutations: string[]
  result_found: boolean
  primers: MSDMPrimer[]
}

export type MSDMResponseData = {
  input_data: MSDMRequestData
  results: MSDMMutationData[]
  full_sequence: string
  goi_offset: number
}

// PAS
export type PASRequestConfig = {
  min_gc_content: number
  opt_gc_content: number
  max_gc_content: number

  min_oligo_size: number
  opt_oligo_size: number
  max_oligo_size: number

  min_overlap_length: number
  opt_overlap_length: number
  max_overlap_length: number

  min_overlap_tm: number
  opt_overlap_tm: number
  max_overlap_tm: number

  temp_range_size: number
  temp_threshold_step: number

  organism: string
  taxonomy_id: string
  codon_usage_frequency_threshold?: number

  use_degeneracy_codon: boolean
  compute_hairpin_homodimer: boolean

  avoided_motifs: string[]

  file_name: string
  oligo_prefix: string
}

export type PASRequestData = {
  mutations: any[]
  sequences: {
    five_end_flanking_sequence: any
    gene_of_interest: any
    three_end_flanking_sequence: any
  }

  is_dna_sequence: boolean
  is_mutations_as_codons: boolean
  config: Partial<PASRequestConfig & {}>
}

export type PASResultsData = {
  mutations: any[]
  fragment: string
  start: number
  end: number
  length: number
  overlap: string
  overlap_Tm: number
  overlap_GC: number
  overlap_length: number
  oligos: any[]
}

export type PASResultFragment = {
  mutations: MutationPas[]
  fragment: string
  start: number
  end: number
  length: number
  overlap: string
  overlap_Tm: number
  overlap_GC: number
  overlap_length: number
  oligos: PASResultOligo[]
}


export type PASResultOligo = {
  "sequence": string
  "mix_ratio": number
  "mutations": number[]
  "reds": number[]
  "blues": number[]
}

export type PASResponseData = {
  input_data: PASRequestData
  results: PASResultsData[]
  full_sequence: string
  goi_offset: number
  message: string
}

