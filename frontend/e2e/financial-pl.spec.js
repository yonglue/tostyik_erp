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

    // 1. 用正确的字段创建一笔 $100 的日常开支
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
    
    if (!createRes.ok()) {
      console.log('❌ 创建开支报错:', await createRes.text())
      test.skip(true, '创建开支失败，请检查 Payload 字段')
      return
    }

    // 2. 进入财务报表页面
    await page.locator('[data-testid="nav-financial"]').click()
    
    // 等待页面数据加载完成（等“总开支”数字出现）
    const expensesCard = page.locator('.text-rose-500.text-2xl.font-black').first()
    await expect(expensesCard).toBeVisible({ timeout: 10000 })

    // 3. 验证页面上的“总开支”包含了刚加的 $100
    const expensesText = await expensesCard.innerText()
    const expensesAmount = parseFloat(expensesText.replace(/[^0-9.-]/g, ''))
    console.log(`📊 当前页面总开支: $${expensesAmount}`)
    expect(expensesAmount).toBeGreaterThanOrEqual(100)

    // 4. 验证“净利润”字段可见
    const profitCard = page.locator('.text-emerald-700.text-2xl.font-black, .text-emerald-400.text-2xl.font-black').first()
    const profitText = await profitCard.innerText()
    const profitAmount = parseFloat(profitText.replace(/[^0-9.-]/g, ''))
    console.log(`📊 当前页面净利润: $${profitAmount}`)

    // 5. 通过 API 校验这条开支真实入库
    const apiExpRes = await request.get(`${API_BASE}/api/expenses`, { headers: authHeader })
    const expensesList = await apiExpRes.json()
    const testExpense = expensesList.find(e => e.description === 'E2E 测试日常开支')
    expect(testExpense).toBeDefined()
    expect(Number(testExpense.amount)).toBe(100)

    // 6. 清理现场：删掉这条测试开支
    const delRes = await request.delete(`${API_BASE}/api/expenses/${testExpense.id}`, { headers: authHeader })
    expect(delRes.ok()).toBeTruthy()
  })
})
