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

const SSM_SAMPLE_SEQUENCE = `ATGGCTAAACAGATTTTGGATGCTGCCGCTGGAAACTGGTGATTCAGAAAGCAGTTGAAAAAATCTGCACTGTTCCGGCTGTATTACCAAAGAAGTTGATAAATCTCAGATTGATCGTCAGAAAAAAATGACTGAAGCTGGTGAAAAACTGCGTAATCAGCTGATTAACGAAGCAGCTAAAGCTCAGAAACTGGCTGATGCTTTATCTGAAGCTCAGAAACTGGCTGATGCTTTATCTGAAGCTCAGAAACTGGCTGATGCTTTATCTGAATAA`

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

test.describe('SSM Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/ssm')
    await page.waitForLoadState('networkidle')
  })

  test('should display SSM form with required fields', async ({ page }) => {
    const form = page.locator('form')
    await expect(form).toBeVisible()
    
    await expect(page.locator('.ant-upload').first()).toBeVisible()
    await expect(page.locator('textarea').first()).toBeVisible()
  })

  test('should accept DNA sequence input', async ({ page }) => {
    const sequenceInput = page.locator('textarea').first()
    await sequenceInput.fill(SSM_SAMPLE_SEQUENCE)
    
    await expect(sequenceInput).toHaveValue(SSM_SAMPLE_SEQUENCE)
  })

  test('should display mutation input field', async ({ page }) => {
    const mutationLabel = page.getByText(/mutation/i)
    await expect(mutationLabel.first()).toBeVisible()
  })

  test('should have collapsible primer settings', async ({ page }) => {
    const primerSettingsHeader = page.getByText(/primer|settings|advanced/i)
    await expect(primerSettingsHeader.first()).toBeVisible()
  })
})

test.describe('Navigation', () => {
  test('should navigate between workflows', async ({ page }) => {
    await page.goto('/')
    
    await page.goto('/ssm')
    await expect(page).toHaveURL(/ssm/)
    
    await page.goto('/qclm')
    await expect(page).toHaveURL(/qclm/)
    
    await page.goto('/pas')
    await expect(page).toHaveURL(/pas/)
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
})
