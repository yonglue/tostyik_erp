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
  const passwordInput = page.locator('input[type="password"]')
  await expect(passwordInput).toBeVisible({ timeout: 10_000 })
  
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await passwordInput.fill(PASSWORD)
  await page.locator('form button[type="submit"]').click()

  // 断言登录成功（密码框消失 + 侧边栏出现）
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

  // 切到黑夜模式 (假设 html 标签会加上 class="dark")
  const darkBtn = page.locator('[data-testid="theme-dark"]')
  await darkBtn.click()
  await expect(page.locator('html')).toHaveClass(/dark/)

  // 切回白天模式 (html 标签移除 dark)
  const lightBtn = page.locator('[data-testid="theme-light"]')
  await lightBtn.click()
  await expect(page.locator('html')).not.toHaveClass(/dark/)
})