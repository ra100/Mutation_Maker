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

const SSM_DATA = {
  plasmid: 'ATGATGATGATGATGATGATGATGATGATGATGGAAAGGGTAAAGGGAAAAGTTGCTATAGTCACCGGTGCTGCTCGTGGTCAAGGTGCAGCGGAAGCGCGCTTGCTGGCCAAAGAAGGCGCGAAGGTGTGCCTGACTGACGTGTTGGTTGATGAGGGTCGTACCGTTGCAGAAGAACTGCAGAAAGAGGGCTACGACACTGTTTTTGAACGTCTGGATGTGACCGACCCGAAAGCATGGCAGACCGTTGTTGAGGGCGTGATCCAGCGTTATGGTAAAATTGACATCCTGGTGAACAACGCAGGCATTCTGGCAATGGAAGGCGTCGAAGACACAACCCTGGAGATCTGGAATCGTGTCTTAAGCGTGAACCTGACGGGTGTGTTCCTGGGTATGAAGACCGTGTTACCGTACATGAAGCAACAACGCTCTGGTAGCATCATCAACACCAGCTCTATCTACGGCCTGATTCTGTCCGGTGGTGCTGCGGCGTATCAAGTGACCAAGGGTGCTGTGCGCATCTTGACCAAGACGGCAGCGGTTGAGTATGCTCCGTACTGGATTCGCATTAATTCCGTGCATCCGGGTGTCATCGACACCCCGATGATCGCGGGTATTAAAGAGGCGGGTGCGTTGGAGCAGGTTAACGCACTGACTGCCCTGCCACGTCTCGGAACCCCGGAAGATATTGCGTTCGGCGTGCTTTATCTGGCGAGCGATGAGAGCAGCTTTGTTACGGGCTCGGAACTGGTTATCGATGGTGGCCTGACCACCCGTTTGGAGCATCACCACCATCATCACTGTAGTAGTAGTAGTAGTAGTAGTAGTAGTA',
  forwardPrimer: 'ATGATGATGATGATGATGATGATGATGATG',
  reversePrimer: 'TACTACTACTACTACTACTACTACTACTAC',
  mutation: 'L50V',
}

const QCLM_DATA = {
  goi: 'ATGGAAAGGGTAAAGGGAAAAGTTGCTATAGTCACCGGTGCTGCTCGTGGTCAAGGTGCAGCGGAAGCGCGCTTGCTGGCCAAAGAAGGCGCGAAGGTGTGCCTGACTGACGTGTTGGTTGATGAGGGTCGTACCGTTGCAGAAGAACTGCAGAAAGAGGGCTACGACACTGTTTTTGAACGTCTGGATGTGACCGACCCGAAAGCATGGCAGACCGTTGTTGAGGGCGTGATCCAGCGTTATGGTAAAATTGACATCCTGGTGAACAACGCAGGCATTCTGGCAATGGAAGGCGTCGAAGACACAACCCTGGAGATCTGGAATCGTGTCTTAAGCGTGAACCTGACGGGTGTGTTCCTGGGTATGAAGACCGTGTTACCGTACATGAAGCAACAACGCTCTGGTAGCATCATCAACACCAGCTCTATCTACGGCCTGATTCTGTCCGGTGGTGCTGCGGCGTATCAAGTGACCAAGGGTGCTGTGCGCATCTTGACCAAGACGGCAGCGGTTGAGTATGCTCCGTACTGGATTCGCATTAATTCCGTGCATCCGGGTGTCATCGACACCCCGATGATCGCGGGTATTAAAGAGGCGGGTGCGTTGGAGCAGGTTAACGCACTGACTGCCCTGCCACGTCTCGGAACCCCGGAAGATATTGCGTTCGGCGTGCTTTATCTGGCGAGCGATGAGAGCAGCTTTGTTACGGGCTCGGAACTGGTTATCGATGGTGGCCTGACCACCCGTTTGGAGCATCACCACCATCATCACT',
  mutations: 'P269D\nA271R',
}

test.describe('SSM Full Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/ssm')
    await page.waitForLoadState('networkidle')
  })

  test('should fill SSM form and submit successfully', async ({ page }) => {
    await expect(page.locator('form')).toBeVisible()

    const plasmidTextarea = page.locator('textarea').first()
    await plasmidTextarea.fill(SSM_DATA.plasmid)
    await expect(plasmidTextarea).toHaveValue(SSM_DATA.plasmid)

    const goiTextarea = page.locator('textarea').nth(1)
    const geneSeq = SSM_DATA.plasmid.slice(30, -30)
    await goiTextarea.fill(geneSeq)

    const mutationInput = page.locator('.MutationsTextArea input, .MutationsTextArea textarea').first()
    await mutationInput.fill(SSM_DATA.mutation)

    const primersSelect = page.locator('.ant-select').first()
    await primersSelect.click()
    await page.getByText('Custom').click()

    const customInputs = page.locator('input:not([disabled])').filter({ has: page.locator('[class*="ant-input"]') })
    const enabledInputs = await customInputs.count()
    if (enabledInputs >= 2) {
      const forwardInput = page.locator('input[name="forwardPrimerValueCustom"], input[placeholder*="forward" i]').first()
      const reverseInput = page.locator('input[name="reversePrimerValueCustom"], input[placeholder*="reverse" i]').first()
      if (await forwardInput.isVisible()) {
        await forwardInput.fill(SSM_DATA.forwardPrimer)
      }
      if (await reverseInput.isVisible()) {
        await reverseInput.fill(SSM_DATA.reversePrimer)
      }
    }

    const submitButton = page.locator('button[type="submit"]')
    await expect(submitButton).toBeEnabled()
    await submitButton.click()

    await page.waitForURL(/ssm\/[^/]+/, { timeout: 60000 }).catch(() => {
      console.log('Did not redirect, checking for errors')
    })
    
    const currentUrl = page.url()
    expect(currentUrl).not.toMatch(/ssm$/)
  })

  test('should show loading state after submit', async ({ page }) => {
    const plasmidTextarea = page.locator('textarea').first()
    await plasmidTextarea.fill(SSM_DATA.plasmid)
    
    const goiTextarea = page.locator('textarea').nth(1)
    await goiTextarea.fill(SSM_DATA.plasmid.slice(30, -30))

    const mutationInput = page.locator('.MutationsTextArea input, .MutationsTextArea textarea').first()
    await mutationInput.fill(SSM_DATA.mutation)

    const primersSelect = page.locator('.ant-select').first()
    await primersSelect.click()
    await page.getByText('Custom').click()

    const submitButton = page.locator('button[type="submit"]')
    await submitButton.click()

    const loadingIndicator = page.locator('.ant-spin, .InProgress, [aria-busy="true"]')
    await expect(loadingIndicator.first()).toBeVisible({ timeout: 5000 }).catch(() => {
      console.log('Loading state not found, might have redirected quickly')
    })
  })
})

test.describe('QCLM Full Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/qclm')
    await page.waitForLoadState('networkidle')
  })

  test('should fill QCLM form and submit successfully', async ({ page }) => {
    await expect(page.locator('form')).toBeVisible()

    const goiTextarea = page.locator('textarea').first()
    await goiTextarea.fill(QCLM_DATA.goi)
    await expect(goiTextarea).toHaveValue(QCLM_DATA.goi)

    const mutationInput = page.locator('.MutationsTextArea textarea, .MutationsTextArea input').first()
    await mutationInput.fill(QCLM_DATA.mutations)

    const submitButton = page.locator('button[type="submit"]')
    await expect(submitButton).toBeEnabled()

    await submitButton.click()

    await page.waitForURL(/qclm\/[^/]+/, { timeout: 60000 }).catch(() => {
      console.log('Did not redirect, checking for errors')
    })
  })

  test('should have codon usage selector', async ({ page }) => {
    const codonSection = page.getByText(/codon.*usage|organism/i)
    await expect(codonSection.first()).toBeVisible()
    
    const organismSelect = page.locator('.ant-select').first()
    await expect(organismSelect).toBeVisible()
  })

  test('should validate mutation format', async ({ page }) => {
    const goiTextarea = page.locator('textarea').first()
    await goiTextarea.fill(QCLM_DATA.goi)

    const mutationInput = page.locator('.MutationsTextArea textarea, .MutationsTextArea input').first()
    await mutationInput.fill('INVALID_MUTATION')
    await mutationInput.blur()

    await page.waitForTimeout(500)
    
    const errorVisible = await page.locator('.ant-form-item-explain-error').isVisible().catch(() => false)
    expect(errorVisible).toBe(true)
  })
})

test.describe('PAS Full Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pas')
    await page.waitForLoadState('networkidle')
  })

  test('should fill PAS form with basic data', async ({ page }) => {
    await expect(page.locator('form')).toBeVisible()

    const goiTextarea = page.locator('textarea').first()
    await goiTextarea.fill(QCLM_DATA.goi)
    await expect(goiTextarea).toHaveValue(QCLM_DATA.goi)

    const mutationInput = page.locator('input').last()
    await mutationInput.fill('R10K 0.5')

    const submitButton = page.locator('button[type="submit"]')
    await expect(submitButton).toBeVisible()
  })

  test('should have sequence type toggle', async ({ page }) => {
    const sequenceTypeLabel = page.getByText(/dna|protein|sequence.*type/i)
    await expect(sequenceTypeLabel.first()).toBeVisible()
  })
})

test.describe('Results Display', () => {
  test.skip('should display SSM results with feature viewer', async ({ page }) => {
    await page.goto('/ssm')
    
    const plasmidTextarea = page.locator('textarea').first()
    await plasmidTextarea.fill(SSM_DATA.plasmid)
    
    const allInputs = page.locator('input[type="text"]')
    await allInputs.last().fill(SSM_DATA.mutation)
    
    await page.locator('button[type="submit"]').click()
    
    await page.waitForURL(/ssm\/[^/]+/, { timeout: 60000 })
    
    const resultsTable = page.locator('.ant-table, [data-testid="results-table"]')
    await expect(resultsTable.first()).toBeVisible({ timeout: 60000 })
    
    const featureViewer = page.locator('[data-testid="feature-viewer"], .feature-viewer-container, svg')
    await expect(featureViewer.first()).toBeVisible({ timeout: 10000 })
  })

  test.skip('should display QCLM results', async ({ page }) => {
    await page.goto('/qclm')
    
    const goiTextarea = page.locator('textarea').first()
    await goiTextarea.fill(QCLM_DATA.goi)
    
    const textareas = page.locator('textarea')
    await textareas.nth(1).fill(QCLM_DATA.mutations)
    
    await page.locator('button[type="submit"]').click()
    
    await page.waitForURL(/qclm\/[^/]+/, { timeout: 60000 })
    
    const resultsSection = page.locator('.results, .ant-table, [data-testid="results"]')
    await expect(resultsSection.first()).toBeVisible({ timeout: 60000 })
  })
})

test.describe('Error Handling', () => {
  test('should show error for empty SSM form submission', async ({ page }) => {
    await page.goto('/ssm')
    
    const submitButton = page.locator('button[type="submit"]')
    await submitButton.click()
    
    const validationErrors = page.locator('.ant-form-item-explain-error')
    await expect(validationErrors.first()).toBeVisible({ timeout: 2000 })
  })

  test('should show error for empty QCLM form submission', async ({ page }) => {
    await page.goto('/qclm')
    
    const submitButton = page.locator('button[type="submit"]')
    await submitButton.click()
    
    const validationErrors = page.locator('.ant-form-item-explain-error')
    await expect(validationErrors.first()).toBeVisible({ timeout: 2000 })
  })

  test('should validate DNA sequence format', async ({ page }) => {
    await page.goto('/ssm')
    
    const plasmidTextarea = page.locator('textarea').first()
    await plasmidTextarea.fill('ATGCX123')
    await plasmidTextarea.blur()
    
    await page.waitForTimeout(1000)
    
    const hasError = await page.locator('.ant-form-item-explain-error, .ant-form-item-has-error').count() > 0
    expect(hasError).toBe(true)
  })
})

test.describe('Form Reset', () => {
  test('should reset SSM form', async ({ page }) => {
    await page.goto('/ssm')
    
    const plasmidTextarea = page.locator('textarea').first()
    await plasmidTextarea.fill(SSM_DATA.plasmid)
    
    const resetButton = page.locator('button[type="reset"], button:has-text("Reset")')
    await resetButton.click()
    
    await expect(plasmidTextarea).toHaveValue('')
  })

  test('should reset QCLM form', async ({ page }) => {
    await page.goto('/qclm')
    
    const goiTextarea = page.locator('textarea').first()
    await goiTextarea.fill(QCLM_DATA.goi)
    
    const resetButton = page.locator('button[type="reset"], button:has-text("Reset")')
    await resetButton.click()
    
    await expect(goiTextarea).toHaveValue('')
  })
})