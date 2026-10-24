import { test } from '@playwright/test'

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS

const TABS = [
  'quotation', 'quotations', 'cash_register',
  'staff', 'audit_logs', 'backup',
]

async function login(page) {
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.reload()
  await page.locator('input[type="password"]').fill(PASSWORD)
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await page.locator('form button[type="submit"]').click()
  await page.locator('nav').waitFor({ state: 'visible', timeout: 15000 })
}

test('dark mode audit — 剩余6个页面', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await login(page)

  await page.evaluate(() => {
    localStorage.setItem('theme', 'dark')
    document.documentElement.classList.add('dark')
  })

  const captured = []
  const skipped = []

  for (const key of TABS) {
    const btn = page.locator(`[data-testid="nav-${key}"]`)
    
    try {
      await btn.waitFor({ state: 'attached', timeout: 3000 })
    } catch (e) {
      skipped.push(key)
      continue
    }
    
    await btn.click({ force: true })
    await page.waitForTimeout(1000)
    await page.screenshot({
      path: `test-results/dark-audit/${key}.png`,
      fullPage: true,
    })
    captured.push(key)
  }

  console.log('\n📸 已截图:', captured.join(', '))
  if (skipped.length) console.log('⏭️  确实没有此菜单:', skipped.join(', '))
})
