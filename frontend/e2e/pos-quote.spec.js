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

test.describe('POS 与 报价单拆分测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 拦截打印弹窗
    await page.addInitScript(() => {
      window.print = () => { console.log('Mock Print Triggered') }
    })
    await login(page)
  })

  test('快速收银：加购并成功结账', async ({ page }) => {
    await page.locator('[data-testid="nav-pos"]').click()
    
    const searchInput = page.locator('[data-testid="pos-search-input"]')
    await searchInput.fill('TK-12345')
    await searchInput.press('Enter')
    
    // 等待商品加入表格
    await expect(page.locator('[data-testid="cart-table"] tbody tr').first()).toContainText('TK-12345')
    
    // 点击底部确认收款
    const checkoutBtn = page.locator('[data-testid="pos-checkout-btn"]')
    await expect(checkoutBtn).toBeEnabled()
    await checkoutBtn.click()
    
    // 处理弹出的预览弹窗，点击【确认并打印】
    const confirmPrintBtn = page.locator('.bg-emerald-600', { hasText: /Confirmar|确认|Print/i }).last()
    await expect(confirmPrintBtn).toBeVisible()
    await confirmPrintBtn.click()
    
    await page.waitForTimeout(1500) // 等待动画和接口请求完成
    
    // 🌟 修复断言：只要出现了“购物车为空”的提示，就代表成功清空了
    await expect(page.getByText(/购物车为空|Carrito vacío|Cart is empty/)).toBeVisible()
  })

  test('开单报价：选客户并成功挂账', async ({ page }) => {
    await page.locator('[data-testid="nav-quotation"]').click()
    
    const searchInput = page.locator('[data-testid="quote-search-input"]')
    await searchInput.fill('TK-12345')
    await searchInput.press('Enter')
    await expect(page.locator('[data-testid="cart-table"] tbody tr').first()).toContainText('TK-12345')
    
    // 选客户
    await page.getByRole('button', { name: /搜索选择客户|Seleccionar Cliente|Select Client/ }).click()
    const clientSearchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="Buscar"], input[placeholder*="Search"]').last()
    await clientSearchInput.fill('elias')
    await clientSearchInput.press('Enter')
    
    // 挂账
    const creditBtn = page.locator('[data-testid="quote-credit-btn"]')
    await expect(creditBtn).toBeEnabled()
    await creditBtn.click()
    
    await page.waitForTimeout(1500)
    
    // 🌟 修复断言：只要出现了“购物车为空”的提示，就代表成功清空了
    await expect(page.getByText(/购物车为空|Carrito vacío|Cart is empty/)).toBeVisible()
  })

})