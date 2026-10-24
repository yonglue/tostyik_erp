import { test, expect } from '@playwright/test'
import { execSync } from 'child_process'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS
const API_BASE = 'http://localhost:8000'

async function login(page) {
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.reload()
  await page.locator('input[type="password"]').fill(PASSWORD)
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await page.locator('form button[type="submit"]').click()
  await expect(page.locator('nav')).toBeVisible()
}

test.describe('财务 - 客户应收还款核销', () => {
  test('客户还款后欠款正确扣减', async ({ page, request }) => {
    await login(page)
    
    const token = await page.evaluate(() => localStorage.getItem('tostiyk_token'))
    const authHeader = { Authorization: `Bearer ${token}` }

    // 1. 准备测试客户
    const clientName = `测试客户应收_${Date.now()}`
    const newClient = await (await request.post(`${API_BASE}/api/clients`, {
      headers: authHeader,
      data: { name: clientName }
    })).json()
    
    // 2. 用 SQL 把他的欠款设为 100 美元
    const dbPath = path.resolve(__dirname, '../../tostiyk_erp.db')
    execSync(`sqlite3 "${dbPath}" "UPDATE client SET debt = 100 WHERE name = '${clientName}';"`)

    // 3. 进入客户页面
    await page.locator('[data-testid="nav-clients"]').click()
    await page.waitForTimeout(1000)
    
    // 找到刚才的客户行
    const clientRow = page.locator('tbody tr').filter({ hasText: clientName })
    await expect(clientRow).toBeVisible({ timeout: 10000 })
    await expect(clientRow).toContainText('$ 100.00')

    // 4. 点击该客户行，打开详情 Drawer
    await clientRow.click()

    // 5. 在 Drawer 里点击“还款/收款”按钮
    const repayBtn = page.locator('.fixed button').filter({ hasText: /还款|收款|Cobrar|Abonar/i }).first()
    await expect(repayBtn).toBeVisible({ timeout: 5000 })
    await repayBtn.click()

    // 6. 输入金额 40
    const amountInput = page.locator('.fixed input[type="number"]').first()
    await amountInput.fill('40')
    
    // 7. 点击确认还款
    const submitBtn = page.locator('.fixed button').filter({ hasText: /确认还款|确认|Confirmar|Pagar/i }).last()
    await submitBtn.click()

    // 8. 处理可能的全局确认弹窗
    const globalConfirm = page.locator('.fixed button.bg-rose-600, .fixed button.bg-blue-600').filter({ hasText: /确定|Aceptar|Confirm/i }).last()
    if (await globalConfirm.isVisible({ timeout: 1000 }).catch(() => false)) {
      await globalConfirm.click()
    }

    // 9. 等待成功提示
    await expect(page.getByText(/成功|exitoso|success/i)).toBeVisible({ timeout: 5000 })
    
    // 10. 刷新页面验证欠款变成 60
    await page.reload()
    await page.locator('[data-testid="nav-clients"]').click()
    
    const updatedRow = page.locator('tbody tr').filter({ hasText: clientName })
    await expect(updatedRow).toContainText('$ 60.00', { timeout: 10000 })

    // 11. API 验证后端的 debt 变成了 60
    const clientsRes = await request.get(`${API_BASE}/api/clients`, { headers: authHeader })
    const clients = await clientsRes.json()
    const targetClient = clients.find(c => c.name === clientName)
    expect(targetClient.debt).toBe(60)
  })
})
