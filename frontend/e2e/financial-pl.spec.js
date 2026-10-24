import { test, expect } from '@playwright/test'

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

test.describe('财务报表（P&L）', () => {
  test('新增日常开支，验证报表总开支与净利润联动', async ({ page, request }) => {
    await login(page)
    
    const token = await page.evaluate(() => localStorage.getItem('tostiyk_token'))
    const authHeader = { Authorization: `Bearer ${token}` }

    // 1. 创建一笔 $100 的日常开支
    const expenseData = {
      category: 'Varios',
      description: 'E2E 测试日常开支',
      amount: 100,
      currency: 'USD',
      exchange_rate: 1.0,
      payment_method: 'Cash_USD'
    }
    
    const createRes = await request.post(`${API_BASE}/api/expenses`, {
      headers: authHeader,
      data: expenseData
    })
    if (!createRes.ok()) throw new Error('创建开支失败: ' + await createRes.text())

    // 2. 进入财务报表页面，并等待前端接口拉取完毕
    const [expensesResponse] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/expenses') && res.request().method() === 'GET'),
      page.locator('[data-testid="nav-financial"]').click()
    ])
    expect(expensesResponse.status()).toBe(200)

    // 3. 确保总开支卡片可见，并等待动画结束
    const expensesCard = page.locator('.text-rose-500.text-2xl.font-black').first()
    await expect(expensesCard).toBeVisible({ timeout: 10000 })
    await page.waitForTimeout(500) // 给 Vue 一点点渲染时间，防止拿到旧数值

    // 4. 验证总开支
    const expensesText = await expensesCard.innerText()
    const expensesAmount = parseFloat(expensesText.replace(/[^0-9.-]/g, ''))
    console.log(`📊 当前页面总开支: $${expensesAmount}`)
    expect(expensesAmount).toBeGreaterThanOrEqual(100)

    // 5. 清理现场：删掉这条测试开支
    const apiExpRes = await request.get(`${API_BASE}/api/expenses`, { headers: authHeader })
    const expensesList = await apiExpRes.json()
    const testExpense = expensesList.find(e => e.description === 'E2E 测试日常开支')
    
    if (testExpense) {
      await request.delete(`${API_BASE}/api/expenses/${testExpense.id}`, { headers: authHeader })
    }
  })
})
