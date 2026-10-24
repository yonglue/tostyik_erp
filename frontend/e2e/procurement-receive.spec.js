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

test.describe('采购收货 B2', () => {
  test('创建采购单并收货入库，验证状态变化', async ({ page, request }) => {
    await login(page)
    
    const token = await page.evaluate(() => localStorage.getItem('tostiyk_token'))
    const authHeader = { Authorization: `Bearer ${token}` }
    
    // 1. 准备供应商
    let supplierId, supplierName
    const supRes = await request.get(`${API_BASE}/api/suppliers`, { headers: authHeader })
    const suppliers = await supRes.json()
    if (suppliers.length === 0) {
      supplierName = '测试供应商_AUTO'
      const newSup = await (await request.post(`${API_BASE}/api/suppliers`, { headers: authHeader, data: { name: supplierName } })).json()
      supplierId = newSup.id
    } else {
      supplierId = suppliers[0].id
      supplierName = suppliers[0].name
    }
    
    // 2. 创建采购单
    const poData = {
      supplier_id: supplierId,
      supplier_name: supplierName,
      items: [{ oem: 'TK-12345', name: 'ARANDELA TAPA VALVULA/100PC', brand: 'GENERAL', quantity: 10, unit_price: 50 }]
    }
    const createRes = await request.post(`${API_BASE}/api/purchase-orders`, { headers: authHeader, data: poData })
    const createJson = await createRes.json()
    const poNo = createJson.po_no

    // 3. 进入采购中心
    await page.locator('[data-testid="nav-procurement"]').click()
    const poRow = page.locator('tbody tr').filter({ hasText: poNo })
    await expect(poRow).toBeVisible({ timeout: 10000 })

    // 4. 点击收货
    await poRow.locator('button.bg-blue-600').click()
    
    // 5. 点击确认弹窗的红色按钮 (bg-rose-600 / bg-rose-500)
    const confirmBtn = page.locator('.fixed button.bg-rose-600, .fixed button.bg-rose-500, .fixed button.bg-red-600').last()
    await expect(confirmBtn).toBeVisible({ timeout: 3000 })
    await confirmBtn.click()

    // 6. 等待接口返回 200（通过抓包确认）
    const [response] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/receive') && res.request().method() === 'POST'),
      // 已经有确认按钮点击了，这里直接等响应
    ])
    expect(response.status()).toBe(200)

    // 7. API 层面验证该订单状态变成了 received
    const ordersRes = await request.get(`${API_BASE}/api/purchase-orders`, { headers: authHeader })
    const ordersData = await ordersRes.json()
    const targetOrder = ordersData.find(o => o.po_no === poNo)
    
    expect(targetOrder).toBeDefined()
    expect(targetOrder.status).toBe('received')
  })
})
