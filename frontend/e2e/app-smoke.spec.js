// frontend/e2e/app-smoke.spec.js
import { test, expect } from '@playwright/test'

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS

if (!PASSWORD) {
  throw new Error('缺少环境变量 PW_ADMIN_PASS，请先 export PW_ADMIN_PASS=<admin密码>')
}

// 提取公共的登录逻辑，避免每个 test 里重复写
async function login(page) {
  await page.goto('/')
  
  // 🌟 强制清空本地存储，防止残留 Token 直接跳过登录
  await page.evaluate(() => localStorage.clear())
  await page.reload()

  const passwordInput = page.locator('input[type="password"]')
  await expect(passwordInput).toBeVisible({ timeout: 10_000 })
  
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await passwordInput.fill(PASSWORD)
  await page.locator('form button[type="submit"]').click()

  await expect(page.locator('input[type="password"]')).toHaveCount(0, { timeout: 10_000 })
  await expect(page.locator('nav')).toBeVisible({ timeout: 5_000 })
}

test('admin 登录后进入主界面', async ({ page }) => {
  await login(page)
})

test('侧边栏能切换 tab 且激活状态正确', async ({ page }) => {
  await login(page)

  // 初始应该在 Dashboard
  const dashboardBtn = page.locator('[data-testid="nav-dashboard"]')
  await expect(dashboardBtn).toHaveClass(/bg-blue-600/)

  // 切到商品库存 (Parts)
  const partsBtn = page.locator('[data-testid="nav-parts"]')
  await partsBtn.click()
  
  // 断言：Parts 按钮变为激活状态 (蓝色背景)
  await expect(partsBtn).toHaveClass(/bg-blue-600/)
  // 断言：原 Dashboard 按钮失去激活状态
  await expect(dashboardBtn).not.toHaveClass(/bg-blue-600/)

  // 切到客户与账本 (Clients)
  const clientsBtn = page.locator('[data-testid="nav-clients"]')
  await clientsBtn.click()
  await expect(clientsBtn).toHaveClass(/bg-blue-600/)
  await expect(partsBtn).not.toHaveClass(/bg-blue-600/)
})

test('主题能在 light / dark 间切换', async ({ page }) => {
  await login(page)

  // 现在的主题切换器只有一个按钮，我们通过 aria-label 或 class 来定位它
  const themeBtn = page.locator('button[title*="点击切换"]')
  
  // 1. 强行切到深色模式
  // 因为它是循环的（Light -> Dark -> System），我们点两次确保到达 Dark
  // 或者直接判断 html 是否有了 dark 类
  await themeBtn.click() // 可能到了 dark
  await themeBtn.click() // 可能到了 system
  
  // 最好写个循环直到变成 dark（防止初始状态不是 light）
  // 简单点，直接看 html 元素有没有 dark 类
  for (let i = 0; i < 3; i++) {
    const isDark = await page.locator('html').evaluate(el => el.classList.contains('dark'))
    if (isDark) break
    await themeBtn.click()
  }
  
  await expect(page.locator('html')).toHaveClass(/dark/)

  // 2. 继续点击，切回白天模式 (直到 class 里没有 dark)
  for (let i = 0; i < 3; i++) {
    const isDark = await page.locator('html').evaluate(el => el.classList.contains('dark'))
    if (!isDark) break
    await themeBtn.click()
  }
  
  await expect(page.locator('html')).not.toHaveClass(/dark/)
})


