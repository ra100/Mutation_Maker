/*
 * Copyright (c) 2020 Merck Sharp & Dohme Corp. a subsidiary of Merck & Co., Inc., Kenilworth, NJ, USA.
 *
 * This file is part of the Mutation Maker, An Open Source Oligo Design Software For Mutagenesis and De Novo Gene Synthesis Experiments.
 *
 * Mutation Maker is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import { test, expect } from '@playwright/test'

const API_BASE = 'http://localhost:8000/v1'

export const TEST_SEQUENCES = {
  SSM: {
    forwardPrimer: 'CAAGGAATGGTGCATGCAAG',
    reversePrimer: 'GAACGTGGCGAGAAAGGAAG',
    geneOfInterest: 'ATGACTTGCTGGCGCGTAATGGCTAAACAGATTTTGGATGCTGCCGCTGGAAACTGGTGATTCAGAAAGCAGTTGAAAAAATCTGCACTGTTCCGGCTGTATTACCAAAGAAGTTGATAAATCTCAGATTGATCGTCAGAAAAAAATGACTGAAGCTGGTGAAAAACTGCGTAATCAGCTGATTAACGAAGCAGCTAAAGCTCAGAAACTGGCTGATGCTTTATCTGAATAA',
    plasmidSequence: 'CAAGGAATGGTGCATGCAAGATGACTTGCTGGCGCGTAATGGCTAAACAGATTTTGGATGCTGCCGCTGGAAACTGGTGATTCAGAAAGCAGTTGAAAAAATCTGCACTGTTCCGGCTGTATTACCAAAGAAGTTGATAAATCTCAGATTGATCGTCAGAAAAAAATGACTGAAGCTGGTGAAAAACTGCGTAATCAGCTGATTAACGAAGCAGCTAAAGCTCAGAAACTGGCTGATGCTTTATCTGAATAAGAACGTGGCGAGAAAGGAAG',
  },
  QCLM: {
    fiveEndFlanking: 'ATGCGTACGTAGCTAGCTAGCTAGCTAGC',
    geneOfInterest: 'ATGTGGCTAATCAGTAGGCTTATGCTACGGCGACGTTTGAGTTACGCCGATTGTTGTTCGGTCAGTCCGAGTTGGTCTTCAGCGATAATAATTGCCCTGATGCCCCAAGGTGTCCTGACGTGCCACGACCTACTGAAGGGTTCTTCATGA',
    threeEndFlanking: 'GCTAGCTAGCTAGCTAGCACGTACGCAT',
  },
  PAS: {
    fiveEndFlanking: 'ATGCGTACGTAGCTAGCTAGC',
    geneOfInterest: 'ATGTGGCTAATCAGTAGGCTTATGCTACGGCGACGTTTGAGTTACGCCGATTGTTGTTCGGTCAGTCCGAGTTGGTCTTCAGCGATAATAATTGCCCTGATGCCCCAAGGTGTCCTGACGTGCCACGACCTACTGAAGGGTTCTTCATGA',
    threeEndFlanking: 'GCTAGCTAGCTAGCTAGCAC',
  },
}

export const TEST_MUTATIONS = {
  SSM: {
    valid: 'D32E',
    multiple: 'D32E K45R',
    degenerate: 'D32X',
  },
  QCLM: {
    valid: 'E15W',
    multiple: 'E15W V20L',
  },
}

test.describe('SSM API Tests', () => {
  test('should submit SSM job via API', async ({ request }) => {
    const response = await request.post(`${API_BASE}/ssm`, {
      data: {
        mutations: [TEST_MUTATIONS.SSM.valid],
        sequences: {
          gene_of_interest: TEST_SEQUENCES.SSM.geneOfInterest,
          forward_primer: TEST_SEQUENCES.SSM.forwardPrimer,
          reverse_primer: TEST_SEQUENCES.SSM.reversePrimer,
          plasmid: { plasmid_sequence: TEST_SEQUENCES.SSM.plasmidSequence },
        },
        degenerate_codon: 'NNK',
        config: { min_primer_size: 25, max_primer_size: 60 },
      },
    })
    expect(response.status()).toBe(200)
    const data = await response.json()
    expect(data).toHaveProperty('check_url')
  })

  test('should accept degenerate mutation', async ({ request }) => {
    const response = await request.post(`${API_BASE}/ssm`, {
      data: {
        mutations: [TEST_MUTATIONS.SSM.degenerate],
        sequences: {
          gene_of_interest: TEST_SEQUENCES.SSM.geneOfInterest,
          forward_primer: TEST_SEQUENCES.SSM.forwardPrimer,
          reverse_primer: TEST_SEQUENCES.SSM.reversePrimer,
          plasmid: { plasmid_sequence: TEST_SEQUENCES.SSM.plasmidSequence },
        },
        degenerate_codon: 'NNK',
        config: {},
      },
    })
    expect(response.status()).toBe(200)
  })

  test('should accept multiple mutations', async ({ request }) => {
    const response = await request.post(`${API_BASE}/ssm`, {
      data: {
        mutations: TEST_MUTATIONS.SSM.multiple.split(' '),
        sequences: {
          gene_of_interest: TEST_SEQUENCES.SSM.geneOfInterest,
          forward_primer: TEST_SEQUENCES.SSM.forwardPrimer,
          reverse_primer: TEST_SEQUENCES.SSM.reversePrimer,
          plasmid: { plasmid_sequence: TEST_SEQUENCES.SSM.plasmidSequence },
        },
        degenerate_codon: 'NNK',
        config: {},
      },
    })
    expect(response.status()).toBe(200)
  })

  test('should accept invalid mutation format (validated by worker)', async ({ request }) => {
    const response = await request.post(`${API_BASE}/ssm`, {
      data: {
        mutations: ['INVALID_FORMAT'],
        sequences: {
          gene_of_interest: TEST_SEQUENCES.SSM.geneOfInterest,
          forward_primer: TEST_SEQUENCES.SSM.forwardPrimer,
          reverse_primer: TEST_SEQUENCES.SSM.reversePrimer,
          plasmid: { plasmid_sequence: TEST_SEQUENCES.SSM.plasmidSequence },
        },
        degenerate_codon: 'NNK',
        config: {},
      },
    })
    expect(response.status()).toBe(200)
  })

  test('should accept invalid sequence (validated by worker)', async ({ request }) => {
    const response = await request.post(`${API_BASE}/ssm`, {
      data: {
        mutations: ['D32E'],
        sequences: {
          gene_of_interest: 'ATGXATG',
          forward_primer: 'ATG',
          reverse_primer: 'CAT',
          plasmid: { plasmid_sequence: 'ATGATGXATGCAT' },
        },
        degenerate_codon: 'NNK',
        config: {},
      },
    })
    expect(response.status()).toBe(200)
  })
})

test.describe('QCLM API Tests', () => {
  test('should submit QCLM job via API', async ({ request }) => {
    const response = await request.post(`${API_BASE}/qclm`, {
      data: {
        mutations: [TEST_MUTATIONS.QCLM.valid],
        sequences: {
          five_end_flanking_sequence: TEST_SEQUENCES.QCLM.fiveEndFlanking,
          gene_of_interest: TEST_SEQUENCES.QCLM.geneOfInterest,
          three_end_flanking_sequence: TEST_SEQUENCES.QCLM.threeEndFlanking,
        },
        config: { min_primer_size: 33, max_primer_size: 60, codon_usage: 'e-coli' },
      },
    })
    expect(response.status()).toBe(200)
    const data = await response.json()
    expect(data).toHaveProperty('check_url')
  })

  test('should submit QCLM job and check status', async ({ request }) => {
    const response = await request.post(`${API_BASE}/qclm`, {
      data: {
        mutations: [TEST_MUTATIONS.QCLM.valid],
        sequences: {
          five_end_flanking_sequence: TEST_SEQUENCES.QCLM.fiveEndFlanking,
          gene_of_interest: TEST_SEQUENCES.QCLM.geneOfInterest,
          three_end_flanking_sequence: TEST_SEQUENCES.QCLM.threeEndFlanking,
        },
        config: { codon_usage: 'e-coli' },
      },
    })
    expect(response.status()).toBe(200)
    const data = await response.json()
    
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    const statusResponse = await request.get(`${API_BASE}${data.check_url}`)
    expect([200, 202, 404]).toContain(statusResponse.status())
  })
})

test.describe('PAS API Tests', () => {
  test('should submit PAS job via API', async ({ request }) => {
    const response = await request.post(`${API_BASE}/pas`, {
      data: {
        mutations: [{ position: 10, target: 'R', mutants: ['K'], frequency: 0.5 }],
        sequences: {
          five_end_flanking_sequence: TEST_SEQUENCES.PAS.fiveEndFlanking,
          gene_of_interest: TEST_SEQUENCES.PAS.geneOfInterest,
          three_end_flanking_sequence: TEST_SEQUENCES.PAS.threeEndFlanking,
        },
        is_dna_sequence: true,
        config: { min_oligo_size: 40, max_oligo_size: 60, organism: 'e-coli' },
      },
    })
    expect(response.status()).toBe(200)
  })

  test('should submit PAS job with multiple mutations', async ({ request }) => {
    const response = await request.post(`${API_BASE}/pas`, {
      data: {
        mutations: [
          { position: 15, target: 'L', mutants: ['W'], frequency: 0.5 },
          { position: 20, target: 'K', mutants: ['R', 'M'], frequency: 0.3 },
        ],
        sequences: {
          five_end_flanking_sequence: TEST_SEQUENCES.PAS.fiveEndFlanking,
          gene_of_interest: TEST_SEQUENCES.PAS.geneOfInterest,
          three_end_flanking_sequence: TEST_SEQUENCES.PAS.threeEndFlanking,
        },
        is_dna_sequence: true,
        config: {},
      },
    })
    expect(response.status()).toBe(200)
  })
})
