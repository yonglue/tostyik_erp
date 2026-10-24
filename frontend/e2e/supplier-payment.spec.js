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

test.describe('财务 - 供应商付款核销', () => {
  test('付款成功并减少欠款', async ({ page, request }) => {
    await login(page)
    
    const token = await page.evaluate(() => localStorage.getItem('tostiyk_token'))
    const authHeader = { Authorization: `Bearer ${token}` }
    
    // 1. 创建供应商
    const supName = `付款测试供应商_${Date.now()}`
    const newSupRes = await request.post(`${API_BASE}/api/suppliers`, { headers: authHeader, data: { name: supName } })
    const newSup = await newSupRes.json()
    const supplierId = newSup.id

    // 2. 🌟 用 SQL 直接把欠款调成 100 美元（跳过采购单流程，专注测付款）
    const dbPath = path.resolve(__dirname, '../../tostiyk_erp.db')
    execSync(`sqlite3 "${dbPath}" "UPDATE suppliers SET debt_usd = 100 WHERE id = ${supplierId};"`)

    // 3. 进入采购中心，切到供应商 Tab
    await page.locator('[data-testid="nav-procurement"]').click()
    await page.waitForTimeout(1000)
    
    // 刷新一下列表
    const refreshBtn = page.locator('button').filter({ hasText: /刷新|Actualizar|Refresh/i }).first()
    if (await refreshBtn.isVisible()) await refreshBtn.click()

    const supplierTab = page.locator('button, a').filter({ hasText: /供应商|Proveedores|Suppliers/i }).first()
    await supplierTab.click()
    
    // 4. 找到刚才创建的供应商行，验证欠款 $100
    const supRow = page.locator('tbody tr').filter({ hasText: supName })
    await expect(supRow).toBeVisible({ timeout: 10000 })
    await expect(supRow).toContainText('$ 100.00', { timeout: 5000 })

    // 5. 点击付款按钮
    await supRow.locator('button.bg-emerald-50').click()
    
    // 6. 在抽屉里输入付款金额 40
    const amountInput = page.locator('.fixed input[type="number"], .fixed input[type="text"]').first()
    await amountInput.fill('40')
    
    // 7. 点击抽屉里的“确认付款”按钮
    const submitBtn = page.locator('.fixed button.bg-emerald-600').filter({ hasText: /确认|Pagar|Confirm/i }).last()
    await submitBtn.click()

    // 8. 如果有通用的全局确认弹窗，点确定
    const globalConfirm = page.locator('.fixed button.bg-rose-600, .fixed button.bg-blue-600').filter({ hasText: /确定|Aceptar|Confirm/i }).last()
    if (await globalConfirm.isVisible({ timeout: 1000 }).catch(() => false)) {
      await globalConfirm.click()
    }

    // 9. 等待成功提示
    await expect(page.getByText(/付款成功|Pago exitoso|Payment successful/i)).toBeVisible({ timeout: 5000 })
    
    // 10. 刷新页面验证欠款变成 $60.00
    await page.reload()
    await page.locator('[data-testid="nav-procurement"]').click()
    await page.waitForTimeout(1000)
    await page.locator('button, a').filter({ hasText: /供应商|Proveedores|Suppliers/i }).first().click()
    
    const updatedRow = page.locator('tbody tr').filter({ hasText: supName })
    await expect(updatedRow).toContainText('$ 60.00', { timeout: 10000 })

    // 11. API 断言后端的 debt_usd 变成了 60
    const supListRes = await request.get(`${API_BASE}/api/suppliers`, { headers: authHeader })
    const supList = await supListRes.json()
    const targetSup = supList.find(s => s.id === supplierId)
    expect(targetSup.debt_usd).toBe(60)
  })
})
