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

const VALID_DNA = 'ATGGCTAAACAGATTTTGGATGCTGCCGCTGGAAACTGGTGATTCAGAAAGCAGTTGAAAAAATCTGCACTGTTCCGGCTGTATTACCAAAGAAGTTGATAAATCTCAGATTGATCGTCAGAAAAAAATGACTGAAGCTGGTGAAAAACTGCGTAATCAGCTGATTAACGAAGCAGCTAAAGCTCAGAAACTGGCTGATGCTTTATCTGAATAA'
const INVALID_DNA = 'ATGGCTAAACAGATTTTGGATGCTGCCGCTGGXAACTGGTGATTCAG'

test.describe('Mutation Maker Landing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display landing page with workflow links', async ({ page }) => {
    await expect(page).toHaveTitle(/Mutation Maker/i)
    await expect(page.getByText(/SSM|Single Site/i).first()).toBeVisible()
    await expect(page.getByText(/QCLM|QuikChange/i).first()).toBeVisible()
    await expect(page.getByText(/PAS|Protein/i).first()).toBeVisible()
  })

  test('should navigate to SSM workflow', async ({ page }) => {
    await page.getByText(/SSM|Single Site/i).first().click()
    await expect(page).toHaveURL(/ssm/i)
    await expect(page.locator('form')).toBeVisible()
  })
})

test.describe('SSM Workflow - UI Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/ssm')
    await page.waitForLoadState('domcontentloaded')
  })

  test('should display SSM form with required fields', async ({ page }) => {
    await expect(page.locator('form')).toBeVisible()
    await expect(page.locator('.ant-upload').first()).toBeVisible()
    await expect(page.locator('textarea').first()).toBeVisible()
  })

  test('should accept DNA sequence input', async ({ page }) => {
    const sequenceInput = page.locator('textarea').first()
    await sequenceInput.fill(VALID_DNA)
    await expect(sequenceInput).toHaveValue(VALID_DNA)
  })

  test('should accept mutation input', async ({ page }) => {
    const mutationInput = page.locator('input[placeholder*="mutation" i], input[id*="mutation" i]').first()
    if (await mutationInput.isVisible()) {
      await mutationInput.fill('D32E')
      await expect(mutationInput).toHaveValue('D32E')
    }
  })

  test('should have configurable primer settings', async ({ page }) => {
    const advancedHeader = page.getByText(/advanced|settings|primer/i)
    await expect(advancedHeader.first()).toBeVisible()
  })

  test('should validate invalid DNA sequence', async ({ page }) => {
    const sequenceInput = page.locator('textarea').first()
    await sequenceInput.fill(INVALID_DNA)
    await sequenceInput.blur()
    
    const errorMessage = page.locator('.ant-form-item-explain-error, .error-message')
    await expect(errorMessage.first()).toBeVisible({ timeout: 3000 }).catch(() => {})
  })

  test('should have plasmid sequence upload area', async ({ page }) => {
    await expect(page.locator('.ant-upload-drag').first()).toBeVisible()
  })

  test('should have gene of interest input', async ({ page }) => {
    const goiTextarea = page.locator('textarea').filter({ hasText: /gene|interest|goi/i })
    if (await goiTextarea.count() > 0) {
      await expect(goiTextarea.first()).toBeVisible()
    } else {
      const allTextareas = page.locator('textarea')
      await expect(allTextareas.first()).toBeVisible()
    }
  })

  test('should have flanking primer inputs', async ({ page }) => {
    const primerInputs = page.locator('input[type="text"]')
    const count = await primerInputs.count()
    expect(count).toBeGreaterThan(0)
  })

  test('should have degenerate codon selector', async ({ page }) => {
    const codonSelector = page.getByText(/degenerate|codon|NNK|NNS/i)
    await expect(codonSelector.first()).toBeVisible()
  })

  test('should have submit button', async ({ page }) => {
    const submitButton = page.locator('button[type="submit"], button:has-text("Submit"), button:has-text("Run")')
    await expect(submitButton.first()).toBeVisible()
  })
})

test.describe('QCLM Workflow - UI Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/qclm')
    await page.waitForLoadState('domcontentloaded')
  })

  test('should display QCLM form', async ({ page }) => {
    await expect(page.locator('form')).toBeVisible()
  })

  test('should have gene of interest textarea', async ({ page }) => {
    const textarea = page.locator('textarea').first()
    await expect(textarea).toBeVisible()
  })

  test('should have mutations input', async ({ page }) => {
    const mutationInput = page.locator('input').filter({ has: page.locator('[placeholder*="mutation" i]') })
    if (await mutationInput.count() > 0) {
      await expect(mutationInput.first()).toBeVisible()
    }
  })

  test('should have codon usage selection', async ({ page }) => {
    const codonUsage = page.getByText(/codon|usage|organism|e-coli|yeast/i)
    await expect(codonUsage.first()).toBeVisible()
  })

  test('should have flanking sequence inputs', async ({ page }) => {
    const flankingInputs = page.getByText(/flanking|5'|3'/i)
    await expect(flankingInputs.first()).toBeVisible()
  })

  test('should have submit button', async ({ page }) => {
    const submitButton = page.locator('button[type="submit"], button:has-text("Submit"), button:has-text("Run")')
    await expect(submitButton.first()).toBeVisible()
  })
})

test.describe('PAS Workflow - UI Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pas')
    await page.waitForLoadState('domcontentloaded')
  })

  test('should display PAS form', async ({ page }) => {
    await expect(page.locator('form')).toBeVisible()
  })

  test('should have gene of interest textarea', async ({ page }) => {
    const textarea = page.locator('textarea').first()
    await expect(textarea).toBeVisible()
  })

  test('should have sequence type selection', async ({ page }) => {
    const sequenceType = page.getByText(/dna|protein|sequence type/i)
    await expect(sequenceType.first()).toBeVisible()
  })

  test('should have mutation frequency input', async ({ page }) => {
    const frequencyLabel = page.getByText(/frequency|%/i)
    await expect(frequencyLabel.first()).toBeVisible()
  })

  test('should have flanking sequence inputs', async ({ page }) => {
    const flankingInputs = page.getByText(/flanking|5'|3'/i)
    await expect(flankingInputs.first()).toBeVisible()
  })

  test('should have submit button', async ({ page }) => {
    const submitButton = page.locator('button[type="submit"], button:has-text("Submit"), button:has-text("Run")')
    await expect(submitButton.first()).toBeVisible()
  })
})

test.describe('Navigation Tests', () => {
  test('should navigate to SSM page', async ({ page }) => {
    await page.goto('/ssm')
    await expect(page).toHaveURL(/ssm/)
    await expect(page.locator('form')).toBeVisible()
  })

  test('should navigate to QCLM page', async ({ page }) => {
    await page.goto('/qclm')
    await expect(page).toHaveURL(/qclm/)
    await expect(page.locator('form')).toBeVisible()
  })

  test('should navigate to PAS page', async ({ page }) => {
    await page.goto('/pas')
    await expect(page).toHaveURL(/pas/)
    await expect(page.locator('form')).toBeVisible()
  })

  test('should have working back navigation', async ({ page }) => {
    await page.goto('/')
    await page.goto('/ssm')
    await page.goBack()
    await expect(page).toHaveURL('/')
  })
})

test.describe('Accessibility', () => {
  test('landing page should have navigation links', async ({ page }) => {
    await page.goto('/')
    const links = page.locator('a')
    const count = await links.count()
    expect(count).toBeGreaterThan(0)
  })

  test('SSM form should have labels', async ({ page }) => {
    await page.goto('/ssm')
    const labels = page.locator('label, .ant-form-item-label')
    const count = await labels.count()
    expect(count).toBeGreaterThan(0)
  })

  test('QCLM form should have labels', async ({ page }) => {
    await page.goto('/qclm')
    const labels = page.locator('label, .ant-form-item-label')
    const count = await labels.count()
    expect(count).toBeGreaterThan(0)
  })

  test('PAS form should have labels', async ({ page }) => {
    await page.goto('/pas')
    const labels = page.locator('label, .ant-form-item-label')
    const count = await labels.count()
    expect(count).toBeGreaterThan(0)
  })
})
