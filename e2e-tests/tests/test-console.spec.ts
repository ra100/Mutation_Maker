import { test, expect } from '@playwright/test'

test('check console errors', async ({ page }) => {
  const errors: string[] = []
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text())
    }
  })
  page.on('pageerror', err => {
    errors.push(err.message)
  })
  
  await page.goto('http://localhost:3000')
  await page.waitForTimeout(3000)
  
  console.log('Console errors:', errors)
  expect(errors).toEqual([])
})
