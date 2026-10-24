import { test, expect } from '@playwright/test'

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS

async function login(page) {
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.reload()
  await page.locator('input[type="password"]').fill(PASSWORD)
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await page.locator('form button[type="submit"]').click()
  await expect(page.locator('nav')).toBeVisible()
}

test.describe('进销存流水分页', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.locator('[data-testid="nav-transactions"]').click()
    await expect(page.locator('[data-testid="tx-total"]')).toBeVisible({ timeout: 10_000 })
  })

  test('分页条与顶部统计渲染正确', async ({ page }) => {
    // 顶部 3 卡
    await expect(page.locator('[data-testid="tx-total"]')).toBeVisible()
    await expect(page.locator('[data-testid="tx-sum-out"]')).toBeVisible()
    await expect(page.locator('[data-testid="tx-sum-in"]')).toBeVisible()
    // 3 个 tab
    await expect(page.locator('[data-testid="tx-tab-all"]')).toBeVisible()
    await expect(page.locator('[data-testid="tx-tab-out"]')).toBeVisible()
    await expect(page.locator('[data-testid="tx-tab-in"]')).toBeVisible()
    // 分页条
    await expect(page.locator('[data-testid="tx-page-prev"]')).toBeVisible()
    await expect(page.locator('[data-testid="tx-page-next"]')).toBeVisible()
  })

  test('切到"出库"tab 后表格只剩 OUT/REFUND', async ({ page }) => {
    await page.locator('[data-testid="tx-tab-out"]').click()
    await page.waitForTimeout(800)

    const rows = page.locator('table tbody tr')
    const count = await rows.count()

    if (count === 0) {
      await expect(
        page.getByText(/没有找到|No se encontraron|No inventory/i)
      ).toBeVisible()
      return
    }

    for (let i = 0; i < count; i++) {
      const cell = rows.nth(i).locator('td').nth(4)
      const text = (await cell.innerText()).trim()
      expect(text).toMatch(/OUT|SALIDA|出库|REFUND|REEMBOLSO|退款/i)
    }
  })

  test('翻页功能：点下一页数据变化（仅当有 2+ 页）', async ({ page }) => {
    const totalText = await page.locator('[data-testid="tx-total"]').innerText()
    const total = parseInt(totalText.replace(/[^\d]/g, ''), 10) || 0
    if (total <= 20) {
      test.skip(true, `只有 ${total} 条流水，不足一页翻页测试，跳过`)
      return
    }

    const firstRowBefore = await page.locator('table tbody tr').first().innerText()
    await page.locator('[data-testid="tx-page-next"]').click()
    await page.waitForTimeout(800)
    const firstRowAfter = await page.locator('table tbody tr').first().innerText()
    expect(firstRowAfter).not.toBe(firstRowBefore)

    await page.locator('[data-testid="tx-page-prev"]').click()
    await page.waitForTimeout(800)
    const firstRowBack = await page.locator('table tbody tr').first().innerText()
    expect(firstRowBack).toBe(firstRowBefore)
  })
})
