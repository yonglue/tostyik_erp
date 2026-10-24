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

test.describe('库存盘点 B1', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.locator('[data-testid="nav-inventory_audit"]').click()
  })

  test('提交盘点差异并生成历史流水', async ({ page }) => {
    // 等表格加载
    const row = page.locator('tbody tr').first()
    await expect(row).toBeVisible({ timeout: 10000 })

    // 填实盘数字（原来库存是 999，我们填 888）
    const input = row.locator('input[type="number"]')
    await input.fill('888')

    // 确认差异提示出现
    await expect(row.locator('.text-rose-600, .text-emerald-600').first()).toBeVisible()

    // 关掉可能残留的全局弹窗（防护）
    const closeBtn = page.locator('button:has-text("确定"), button:has-text("关闭"), button:has-text("OK")').first()
    if (await closeBtn.isVisible()) {
      await closeBtn.click()
    }

    // 点击提交
    const submitBtn = page.getByRole('button', { name: /提交盘点结果/ })
    await expect(submitBtn).toBeEnabled()
    await submitBtn.click({ force: true })

    // 等待成功弹窗
    await expect(page.getByText(/盘点完成/)).toBeVisible({ timeout: 5000 })

    // 切到历史 tab 验证流水存在
    await page.getByRole('button', { name: /历史盘点记录/ }).click()
    await expect(page.locator('tbody tr').first()).toBeVisible()
    // 断言历史里出现了盘点标记
    await expect(page.locator('tbody').first()).toContainText(/盘盈|盘亏/)
  })
})
